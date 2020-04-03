import pytest
from httmock import HTTMock
from tests import mocks

from gdc_maf_tool import gdc_api_client


@pytest.mark.parametrize(
    "uuid, token, expected_result",
    [
        ("one", mocks.VALID_TOKEN, True),
        ("two", None, False),
        ("three", mocks.INVAVLID_TOKEN, False),
    ],
)
def test_can_download_maf(uuid, token, expected_result):
    with HTTMock(mocks.download_mock):
        can_download = gdc_api_client.can_download_maf(uuid, token)

    assert can_download == expected_result
