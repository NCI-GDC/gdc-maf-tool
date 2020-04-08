import datetime
import os
import uuid

import mock
import pytest
from defusedcsv import csv
from httmock import HTTMock
from tests import mocks

from gdc_maf_tool import gdc_api_client


@pytest.mark.parametrize("hit_key", ["file_id", "case_id"])
def test__check_for_missing_ids(fake_hitmap, hit_key):

    extra_uuid = str(uuid.uuid4())
    expected_ids = [h[hit_key] for h in fake_hitmap.values()] + [extra_uuid]

    gdc_api_client.check_for_missing_ids(fake_hitmap, expected_ids, hit_key)

    # date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # filename = "failed-downloads-{}.tsv".format(date)
    assert os.path.exists(gdc_api_client.FAILED_DOWNLOAD_FILENAME)

    with open(gdc_api_client.FAILED_DOWNLOAD_FILENAME) as f:
        uuids = [row[hit_key] for row in csv.DictReader(f, delimiter="\t")]
        assert len(uuids) == 1
        assert uuids[0] == extra_uuid

    os.remove(gdc_api_client.FAILED_DOWNLOAD_FILENAME)
