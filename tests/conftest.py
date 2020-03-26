import os
import tempfile
import uuid

import pytest


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
