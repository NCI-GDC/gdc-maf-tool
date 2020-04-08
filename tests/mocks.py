from httmock import urlmatch

VALID_TOKEN = "valid-token"  # nosec
INVAVLID_TOKEN = "bad-token"  # nosec


@urlmatch(path=".*/data/(.*)$")
def download_mock(url, request):
    if request.headers.get("X-Auth-Token", "") == VALID_TOKEN:
        return {"status_code": 200, "content": "test content"}
    return {"status_code": 403, "content": "failed request"}
