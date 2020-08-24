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
        help=(
            "Output file name for the resulting aggregate MAF (default:"
            " outfile.maf.gz)."
        ),
    )
    parser.add_argument(
        "-d",
        "--disable-aliquot-selection",
        action="store_true",
        help="Disable primary aliquot selection logic",
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

    mafs = gdc_api_client.collect_mafs(
        args.project_id, args.disable_aliquot_selection, case_ids, file_ids, token
    )

    with open(args.output_filename, "wb") as f:
        aggregate_mafs(mafs, f)

    failed_downloads = [
        {
            "case_id": m.file.case_id,
            "file_id": m.file.uuid,
            "reason": m.file.failed_reason,
        }
        for m in mafs
        if m.file.failed_reason
    ]
    if failed_downloads:
        logger.warning(
            "There are %d failed downloads. Please check %s for details",
            len(failed_downloads),
            gdc_api_client.FAILED_DOWNLOAD_FILENAME,
        )
        gdc_api_client.write_failed_download_manifest(failed_list=failed_downloads)
    logger.info("Successfully downloaded %s files", len(mafs) - len(failed_downloads))


if __name__ == "__main__":
    main()
