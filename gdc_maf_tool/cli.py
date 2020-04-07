import argparse
from typing import List

from aliquot_level_maf.aggregation import aggregate_mafs
from defusedcsv import csv

from gdc_maf_tool import __version__, gdc_api_client, log
from gdc_maf_tool.log import logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="----GDC MAF Concatenation Tool v{}----".format(__version__),
    )
    # Must pick a project-id, case-manifest, or file-manifest
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-p",
        "--project",
        dest="project_id",
        help="Project from which to gather MAF files.",
    )

    group.add_argument(
        "-f", "--file-manifest", help="Specify MAF files with GDC Manifest"
    )
    group.add_argument(
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
        default="outfile.maf.gz",
        help="Output file name for the resulting aggregate MAF (default: outfile.maf.gz).",
    )
    return parser.parse_args()


def ids_from_manifest(manifest_name: str) -> List[str]:
    """
    Reads in a GDC Manifest to parse out UUIDs
    """

    id_list = []
    with open(manifest_name) as f:
        id_list = [r["id"] for r in csv.DictReader(f, delimiter="\t") if r.get("id")]
        if not id_list:
            log.fatal(
                "Input must be valid GDC Manifest. For a valid manifest "
                "visit https://portal.gdc.cancer.gov/"
            )

    return id_list


def main() -> None:
    args = parse_args()
    token = None
    if args.token:
        token = args.token.read()

    case_ids = []
    file_ids = []
    if args.case_manifest:
        case_ids = ids_from_manifest(args.case_manifest)
    elif args.file_manifest:
        file_ids = ids_from_manifest(args.file_manifest)

    mafs = gdc_api_client.collect_mafs(args.project_id, case_ids, file_ids, token)

    with open(args.output_filename, "wb") as f:
        aggregate_mafs(mafs, f)

        failed = {
            m.file.uuid: m.file.failed_reason for m in mafs if m.file.failed_reason
        }
        if failed:
            logger.warning(
                "The following uuids will not be downloaded or included in the output MAF file."
            )
            logger.warning(", ".join(failed.keys()))
            gdc_api_client.write_failed_download_manifest(
                fieldnames=["file_id", "reason"],
                failed_list=[
                    {"file_id": uuid, "reason": reason}
                    for uuid, reason in failed.items()
                ],
            )
        logger.info("Successfully downloaded %s files", len(mafs) - len(failed))
        if failed:
            logger.info("Failed to download %s files", len(failed))


if __name__ == "__main__":
    main()
