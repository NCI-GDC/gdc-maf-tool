import hashlib
import io
from typing import Callable, Optional

import requests

from gdc_maf_tool.log import logger

ResponseProvider = Callable[[], requests.Response]


class DeferredRequestReader(io.BufferedIOBase):
    """Defer a request until the caller is ready to read the response.

    Attributes:
        provider: A function that returns a response object.
        md5sum: An optional md5 digest in hex format.
    """

    def __init__(
        self, provider: ResponseProvider, uuid: str, md5sum: Optional[str] = None
    ):
        self.uuid = uuid
        self.failed_reason = None
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
        if response.status_code == 403:
            logger.warn("[403] Unable to downoad %s. Skipping...", self.uuid)
            self.failed_reason = "Not authorized"
            return

        if response.status_code == 404:
            logger.warn("[404] File not found %s. Skipping...", self.uuid)
            self.failed_reason = "File not found"
            return

        if response.status_code != 200:
            logger.warn(
                "[%s] Uncaught error %s. Skipping...", response.status_code, self.uuid
            )
            self.failed_reason = "Uncaught error code: {}".format(response.status_code)
            return

        self._validate_checksum(response)

        self._content_position = 0
        self._content_length = len(response.content)
        self._response = response

    def _validate_checksum(self, response):
        if not self._md5sum:
            return

        hash_md5 = hashlib.md5()  # nosec
        hash_md5.update(response.content)
        md5 = hash_md5.hexdigest()
        if self._md5sum != md5:
            raise ValueError(
                f"Failed checksum for {response.url}. "
                f"Expected {self._md5sum}. Got {md5}."
            )

    @property
    def response(self) -> Optional[requests.Response]:
        self._realize()
        return self._response

    def readable(self):
        return True

    def read(self, size=-1):
        """Read from the response."""
        self._realize()

        if not self._response:
            return b""

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
