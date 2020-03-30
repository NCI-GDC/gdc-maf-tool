import hashlib
import io
from typing import Callable, Optional

import requests

ResponseProvider = Callable[[], requests.Response]


class DeferredRequestReader(io.BufferedIOBase):
    """Defer a request until the caller is ready to read the response.

    Attributes:
        provider: A function that returns a response object.
        md5sum: An optional md5 digest in hex format.
    """

    def __init__(self, provider: ResponseProvider, md5sum: Optional[str] = None):
        self._provider = provider
        self._md5sum = md5sum

        self._response = None
        self._content_position = 0
        self._content_length = 0

    def _realize(self):
        """Realize the response."""
        if self._response:
            return

        response = self._provider()
        response.raise_for_status()
        self._validate_checksum(response.content)

        self._content_position = 0
        self._content_length = len(response.content)
        self._response = response

    def _validate_checksum(self, content):
        if not self._md5sum:
            return

        hash_md5 = hashlib.md5()
        hash_md5.update(content)
        md5 = hash_md5.hexdigest()
        if self._md5sum != md5:
            raise ValueError(f"Failed checksum. Expected {self._md5sum}.  Got {md5}.")

    @property
    def response(self) -> requests.Response:
        self._realize()
        return self._response

    def readable(self):
        return True

    def read(self, size=-1):
        """Read from the response."""
        self._realize()

        if self._content_position >= self._content_length:
            return b""

        if size == -1:
            start = self._content_position
            self._content_position = self._content_length
            return self.response.content[start:]

        if size == 0:
            return b""

        start = self._content_position
        end = start + size
        self._content_position = end
        return self.response.content[start:end]
