import argparse
import io

from aliquot_level_maf.aggregation import AliquotLevelMaf, aggregate_mafs
from aliquot_level_maf.selection import (
    PrimaryAliquotSelectionCriterion,
    SampleCriterion,
    select_primary_aliquots,
)

from gdc_maf_tool import download_maf, ids_from_manifest, log_fatal, query_hits


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="----GDC MAF Concatenation Tool v1.0----",
    )
    parser.add_argument(
        "-p",
        "--project",
        dest="project_id",
        help="Project from which to gather MAF files.",
    )

    parser.add_argument(
        "-f", "--file-manifest", help="Specify MAF files with GDC Manifest"
    )
    parser.add_argument(
        "-c",
        "--case-manifest",
        help="Specify case ids associated with MAF files with GDC Manifest",
    )
    parser.add_argument(
        "-t",
        "--token",
        default=None,
        type=argparse.FileType("r"),
        help="GDC user token required for controlled access data",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_filename",
        default="outfile.gz",
        help="Output file name for the resulting aggregate MAF.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    token = None
    if args.token:
        token = args.token.read()
    mafs = []

    case_ids = []
    file_ids = []
    if args.case_manifest:
        case_ids = ids_from_manifest(args.case_manifest)
    elif args.file_manifest:
        file_ids = ids_from_manifest(args.file_manifest)

    hit_map = {h["case_id"]: h for h in query_hits(args.project_id, file_ids, case_ids)}

    # Confirm that there's only one project_id in the list of hits.
    project_ids = {h["project_id"] for h in hit_map.values()}
    if len(project_ids) > 1:
        log_fatal(
            "Can only have one project id. Project ids included: {}".format(
                ", ".join(project_ids)
            )
        )

    # {case_id: PrimaryAliquot(id, sample_id)}
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

    selections = select_primary_aliquots(criteria)

    for case_id, primary_aliquot in selections.items():
        hit = hit_map[case_id]
        sample_id = hit["samples"][primary_aliquot.sample_id]["aliquot_submitter_id"]

        maf_file_contents = download_maf(
            primary_aliquot.id, md5sum=hit["md5sum"], token=token,
        )
        mafs.append(
            AliquotLevelMaf(
                file=io.BytesIO(maf_file_contents),
                tumor_aliquot_submitter_id=sample_id,
            )
        )

    with open(args.output_filename, "wb") as f:
        aggregate_mafs(mafs, f)


if __name__ == "__main__":
    main()
