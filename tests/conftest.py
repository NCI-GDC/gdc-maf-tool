import os
import tempfile
import uuid

import pytest
import requests


@pytest.fixture
def fake_manifest(request):
    uuids = [str(uuid.uuid4()) for _ in range(5)]

    file_object = tempfile.NamedTemporaryFile(mode="wt", delete=False)
    file_object.write("id\n")
    file_object.write("\n".join(uuids))
    file_object.close()

    def tear_down():
        if os.path.exists(file_object.name):
            os.remove(file_object.name)

    request.addfinalizer(tear_down)
    return file_object.name, uuids


@pytest.fixture
def fake_hitmap():
    case_ids = [str(uuid.uuid4()) for _ in range(5)]
    file_ids = [str(uuid.uuid4()) for _ in range(5)]
    hit_map = {}
    for file_id, case_id in zip(file_ids, case_ids):
        hit_map.update({file_id: {"file_id": file_id, "case_id": case_id}})
    return hit_map


class FakeResponse(requests.Response):
    def __init__(self, status_code=200, content=None):
        self.status_code = status_code
        self.url = "fake_url"
        self._content = content
        super()

    @property
    def content(self):
        return bytes(self._content.encode())

    def raise_for_status(self):
        return


@pytest.fixture
def fake_response():
    return FakeResponse
