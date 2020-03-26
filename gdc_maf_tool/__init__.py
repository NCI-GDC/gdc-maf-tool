import csv
import hashlib
import json
import sys
from typing import Any, Dict, Iterator, List

import cdislogging
import requests

logger = cdislogging.get_logger("gdc-maf-tool", log_level="info")


def log_fatal(message: str):
    """
    Report the error and exit the program.

    Python's logger.fatal does not exit the program.
    """
    logger.fatal(message)
    sys.exit(2)


def ids_from_manifest(manifest_name: str) -> List[str]:
    """
    Reads in a GDC Manifest to parse out UUIDs
    """

    id_list = []
    with open(manifest_name) as f:
        id_list = [r["id"] for r in csv.DictReader(f, delimiter="\t") if r.get("id")]
        if not id_list:
            log_fatal(
                "Input must be valid GDC Manifest. For a valid manifest "
                "visit https://portal.gdc.cancer.gov/"
            )

    return id_list


def query_hits(
    project_id: str, file_uuids: List[str], case_uuids: List[str], page_size: int = 5000
) -> List[Dict[str, Any]]:
    """
    Retrieves IDs when provided a project_id or list of UUIDs
    """

    # All queries start out as filtering on a MAF file that's a Masked Somatic Mutation.
    # Adding the analysis.workflow_type filter will ensure we don't get extra mafs we don't want
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
        log_fatal("No project_id or list of UUIDs provided")

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
        log_fatal("Unable to perform request {}".format(resp.json()))
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


def download_maf(uuid: str, md5sum: str, token: str = None, retry_amount: int = 3):
    """
    Downloads each MAF file and returns the resulting bytes of response content.

    Verify that the MD5 matches the maf metadata.
    """
    headers = {}
    if token:
        headers = {"X-Auth-Token": token}

    for _ in range(retry_amount):
        # progress bar?
        logger.info("Downloading File: %s ", uuid)
        resp = requests.get(
            "https://api.gdc.cancer.gov/data/{}".format(uuid), headers=headers,
        )
        if resp.status_code == 200:
            break
        if resp.status_code == 403:
            logger.warning("You do not have access to %s", uuid)
            continue
        logger.info("Retrying Download...")

    else:
        log_fatal("Maximum retries exceeded")

    if not check_md5sum(resp.content, md5sum):
        log_fatal("md5sum not matching expected value for {}".format(uuid))
    else:
        return resp.content

    return ""


def chunk_iterator(iterator: Any, size: int = 4096) -> Iterator:
    for i in range(0, len(iterator), size):
        yield iterator[i : i + size]


def check_md5sum(contents: bytes, expected_md5: str, chunk_size: int = 4096) -> bool:
    """
    Checks the MD5SUM matches the one in the GDC index
    """
    hash_md5 = hashlib.md5()
    for chunk in chunk_iterator(contents, size=chunk_size):
        hash_md5.update(chunk)

    return expected_md5 == hash_md5.hexdigest()
