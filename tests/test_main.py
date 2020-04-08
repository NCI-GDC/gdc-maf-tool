from gdc_maf_tool import cli


def test_ids_from_manifest(fake_manifest):
    filename, expected_ids = fake_manifest
    ids = cli.ids_from_manifest(filename)

    assert ids == expected_ids
