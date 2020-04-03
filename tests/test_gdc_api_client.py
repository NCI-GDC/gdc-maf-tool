import datetime
import os
import uuid

import mock
import pytest
from freezegun import freeze_time
from httmock import HTTMock
from tests import mocks

from defusedcsv import csv
from gdc_maf_tool import gdc_api_client


@pytest.mark.parametrize(
    "uuid, token, expected_result",
    [
        ("one", mocks.VALID_TOKEN, True),
        ("two", None, False),
        ("three", mocks.INVAVLID_TOKEN, False),
    ],
)
def test__can_download_maf(uuid, token, expected_result):
    with HTTMock(mocks.download_mock):
        can_download = gdc_api_client.can_download_maf(uuid, token)

    assert can_download == expected_result


@freeze_time("2020-03-14 01:02:03.456")
@pytest.mark.parametrize("hit_key", ["file_id", "case_id"])
def test__check_for_missing_ids(fake_hitmap, hit_key):

    extra_uuid = str(uuid.uuid4())
    expected_ids = [h[hit_key] for h in fake_hitmap.values()] + [extra_uuid]

    with pytest.raises(SystemExit):
        gdc_api_client.check_for_missing_ids(fake_hitmap, expected_ids, hit_key)

    date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = "failed-downloads-{}.tsv".format(date)
    assert os.path.exists(filename)

    with open(filename) as f:
        uuids = [row[hit_key] for row in csv.DictReader(f, delimiter="\t")]
        assert len(uuids) == 1
        assert uuids[0] == extra_uuid

    os.remove(filename)
