import pytest

from gdc_maf_tool import chunk_iterator, ids_from_manifest


@pytest.mark.parametrize(
    "given,expected,chunk_size",
    [
        ("abcdefg", ["a", "b", "c", "d", "e", "f", "g"], 1),
        ("abcdefg", ["ab", "cd", "ef", "g"], 2),
        ("abcdefg", ["abc", "def", "g"], 3),
    ],
)
def test_chunk_iterator(given, expected, chunk_size):
    assert list(chunk_iterator(given, chunk_size)) == expected


def test_ids_from_manifest(fake_manifest):
    filename, expected_ids = fake_manifest
    ids = ids_from_manifest(filename)

    assert ids == expected_ids
