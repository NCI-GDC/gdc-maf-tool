import pytest
import requests

from gdc_maf_tool import defer


def test_deferredrequestreader__read():
    class FakeResponse(requests.Response):
        @property
        def content(self):
            return b"one\ntwo\nthree"

        def raise_for_status(self):
            return

    def provider():
        return FakeResponse()

    reader = defer.DeferredRequestReader(provider)
    lines = [line for line in reader]
    assert lines == [b"one\n", b"two\n", b"three"]


def test_deferredrequestreader__failed_request():
    class FakeResponse(requests.Response):
        def raise_for_status(self):
            raise requests.HTTPError()

    def provider():
        return FakeResponse()

    with pytest.raises(requests.HTTPError):
        reader = defer.DeferredRequestReader(provider)
        reader.read()


def test_deferredrequestreader__md5_match():
    class FakeResponse(requests.Response):
        @property
        def content(self):
            return b"md5_match\n"

        def raise_for_status(self):
            return

    def provider():
        return FakeResponse()

    reader = defer.DeferredRequestReader(provider, "d8ab26d704d5d89a5356609ec42c2691")
    assert reader.read() == b"md5_match\n"


def test_deferredrequestreader__md5_mismatch():
    class FakeResponse(requests.Response):
        @property
        def content(self):
            return b"md5_mismatch\n"

        def raise_for_status(self):
            return

    def provider():
        return FakeResponse()

    with pytest.raises(ValueError):
        reader = defer.DeferredRequestReader(
            provider, "d8ab26d704d5d89a5356609ec42c2691"
        )
        reader.read()
