import pytest
import uuid

from gdc_maf_tool import defer


def test_deferredrequestreader__read(fake_response):
    def provider():
        return fake_response(status_code=200, content="one\ntwo\nthree")

    reader = defer.DeferredRequestReader(provider, str(uuid.uuid4()))
    lines = [line for line in reader]
    assert lines == [b"one\n", b"two\n", b"three"]


def test_deferredrequestreader__failed_request(fake_response):
    def provider():
        return fake_response(status_code=400, content="")

    reader = defer.DeferredRequestReader(provider, str(uuid.uuid4()))
    lines = [line for line in reader]
    assert not lines


def test_deferredrequestreader__md5_match(fake_response):
    def provider():
        return fake_response(status_code=200, content="md5_match\n")

    reader = defer.DeferredRequestReader(
        provider, str(uuid.uuid4()), "d8ab26d704d5d89a5356609ec42c2691"
    )
    assert reader.read() == b"md5_match\n"


def test_deferredrequestreader__md5_mismatch(fake_response):
    def provider():
        return fake_response(status_code=200, content="md5_mismatch\n")

    with pytest.raises(ValueError):
        reader = defer.DeferredRequestReader(
            provider, str(uuid.uuid4()), "d8ab26d704d5d89a5356609ec42c2691"
        )
        reader.read()
