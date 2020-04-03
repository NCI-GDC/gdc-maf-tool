import datetime
import json
from typing import Any, Dict, List

import requests
from aliquot_level_maf.aggregation import AliquotLevelMaf
from aliquot_level_maf.selection import (
    PrimaryAliquotSelectionCriterion,
    SampleCriterion,
    select_primary_aliquots,
)

from gdc_maf_tool import defer, log
from gdc_maf_tool.log import logger


def query_hits(
    project_id: str, file_uuids: List[str], case_uuids: List[str], page_size: int = 5000
) -> List[Dict[str, Any]]:
    """
    Retrieves IDs when provided a project_id or list of UUIDs
    """

    # All queries start out as filtering on a MAF file that's a Masked Somatic Mutation.
    # Adding the analysis.workflow_type filter will ensure we don't get extra mafs we
    # don't want
    base_content = [
        {"op": "in", "content": {"field": "files.data_format", "value": ["MAF"]}},
        {
            "op": "in",
            "content": {
                "field": "files.data_type",
                "value": ["Masked Somatic Mutation"],
            },
        },
        {
            "op": "in",
            "content": {
                "field": "analysis.workflow_type",
                "value": ["Aliquot Ensemble Somatic Variant Merging and Masking"],
            },
        },
    ]

    # Prioritize UUIDs from a manifest over a project_id.
    if file_uuids:
        base_content.append(
            {"op": "in", "content": {"field": "files.file_id", "value": file_uuids}}
        )
    elif case_uuids:
        base_content.append(
            {"op": "in", "content": {"field": "cases.case_id", "value": case_uuids}},
        )
    elif project_id:
        base_content.append(
            {
                "op": "in",
                "content": {"field": "cases.project.project_id", "value": [project_id]},
            },
        )

    else:
        log.fatal("No project_id or list of UUIDs provided")

    filters = {
        "op": "and",
        "content": base_content,
    }

    fields = [
        "file_id",
        "md5sum",
        "file_size",
        "created_datetime",
        "cases.case_id",
        "cases.project.project_id",
        "cases.samples.sample_type",
        "cases.samples.tissue_type",
        "cases.samples.portions.analytes.aliquots.submitter_id",
    ]

    query = {
        "fields": ",".join(fields),
        "filters": json.dumps(filters),
        "from": "0",
        "size": str(page_size),
    }
    data = _files_query(query)
    hits = [_parse_hit(hit) for hit in data["hits"]]

    while data["pagination"]["page"] < data["pagination"]["pages"]:
        # Prep the query to get the next page.
        query["from"] = str(int(query["from"]) + page_size)
        data = _files_query(query)
        hits += [_parse_hit(hit) for hit in data["hits"]]

    return hits


def _files_query(query: Dict) -> Dict:
    resp = requests.post("https://api.gdc.cancer.gov/files", json=query)
    if resp.status_code != 200:
        log.fatal("Unable to perform request {}".format(resp.json()))
    return resp.json()["data"]


def _parse_hit(hit: Dict) -> Dict:
    return {
        "file_id": hit["file_id"],
        "md5sum": hit["md5sum"],
        "file_size": hit["file_size"],
        "created_datetime": hit["created_datetime"],
        "case_id": hit["cases"][0]["case_id"],
        "project_id": hit["cases"][0]["project"]["project_id"],
        "samples": {
            sample["portions"][0]["analytes"][0]["aliquots"][0]["submitter_id"]: {
                "sample_type": sample["sample_type"],
                "tissue_type": sample["tissue_type"],
                "aliquot_submitter_id": sample["portions"][0]["analytes"][0][
                    "aliquots"
                ][0]["submitter_id"],
            }
            for sample in hit["cases"][0]["samples"]
        },
    }


def download_maf(
    uuid: str, md5sum: str, token: str = None
) -> defer.DeferredRequestReader:
    """
    Downloads each MAF file and returns the resulting bytes of response content.

    Verify that the MD5 matches the maf metadata.
    """

    def provider() -> requests.Response:
        headers = {}
        if token:
            headers = {"X-Auth-Token": token}

        logger.info("Downloading File: %s ", uuid)
        return requests.get(f"https://api.gdc.cancer.gov/data/{uuid}", headers=headers,)

    return defer.DeferredRequestReader(provider, md5sum)


def only_one_project_id(hit_map: Dict) -> None:
    """ Confirm that there's only one project_id in the list of hits."""
    project_ids = {h["project_id"] for h in hit_map.values()}
    if len(project_ids) > 1:
        log.fatal(
            "Can only have one project id. Project ids included: {}".format(
                ", ".join(project_ids)
            )
        )


def collect_criteria(hit_map: Dict) -> List[PrimaryAliquotSelectionCriterion]:
    criteria = []
    for hit in hit_map.values():
        sample_criteria = [
            SampleCriterion(
                id=sample["aliquot_submitter_id"], sample_type=sample["sample_type"]
            )
            for sample in hit["samples"].values()
        ]

        criteria.append(
            PrimaryAliquotSelectionCriterion(
                id=hit["file_id"],
                samples=sample_criteria,
                case_id=hit["case_id"],
                maf_creation_date=hit["created_datetime"],
            )
        )
    return criteria


def collect_mafs(
    project_id: str, case_ids: List[str], file_ids: List[str], token: str
) -> List[AliquotLevelMaf]:
    """Put together a list of mafs given one of: project_id, case_ids, file_ids.

    - If a list of ids is provided then ensure that those ids share the same project_id.
    - If case_ids then gather all the mafs related to those cases.
    - If file_ids then gather all the mafs of those file_ids.
    - If a project_id is provided then gather all the aliquot level mafs for that
    project.
    """

    hit_map = _build_hit_map(query_hits(project_id, file_ids, case_ids))
    return _select_mafs(hit_map, token)


def _build_hit_map(hits):
    return {h["file_id"]: h for h in hits}


def _select_mafs(hit_map, token):
    mafs = []
    only_one_project_id(hit_map)

    criteria = collect_criteria(hit_map)
    selections = select_primary_aliquots(criteria)

    failed_uuids = []
    for primary_aliquot in selections.values():
        hit = hit_map[primary_aliquot.id]
        sample_id = hit["samples"][primary_aliquot.sample_id]["aliquot_submitter_id"]

        if can_download_maf(primary_aliquot.id, token):
            maf_file_contents = download_maf(
                primary_aliquot.id, md5sum=hit["md5sum"], token=token,
            )
            mafs.append(
                AliquotLevelMaf(
                    file=maf_file_contents, tumor_aliquot_submitter_id=sample_id,
                )
            )
        else:
            failed_uuids.append(primary_aliquot.id)

    if failed_uuids:
        logger.warning(
            "You do not have access to these uuids. "
            "They will not be downloaded or included in the output MAF file."
        )
        logger.warning(", ".join(failed_uuids))
        date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = "failed-downloads-{}.tsv".format(date)
        logger.warning("Writing failed download ids to file: %s", filename)

        with open(filename, "w") as f:
            f.write("id\n")
            f.write("\n".join(failed_uuids))

    return mafs


def can_download_maf(node_id: str, token: str) -> bool:
    """Start a download to see if a user has access to a file"""

    headers = {
        "X-Auth-Token": token,
        "Range": "bytes=0-1",
    }
    resp = requests.get(
        f"https://api.gdc.cancer.gov/data/{node_id}", headers=headers, stream=True
    )
    resp.close()
    if resp.status_code == 403:
        logger.warning("You do not have access to this file: %s, skipping.", node_id)
        return False
    return True
