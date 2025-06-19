import os
import zipfile
from io import BytesIO


def test_download_zip(temp_env, monkeypatch):
    env = temp_env
    fetcher = env["reload"]("japanpost_backend.file_fetcher")

    data = BytesIO()
    with zipfile.ZipFile(data, "w") as z:
        z.writestr("dummy.txt", "hello")
    content = data.getvalue()

    class DummyResp:
        def __init__(self, data):
            self.content = data
        def raise_for_status(self):
            pass

    def fake_get(url, timeout=30):
        return DummyResp(content)

    monkeypatch.setattr(fetcher.requests, "get", fake_get)

    path = fetcher.download_zip("http://example.com/test.zip")
    assert os.path.basename(path) == "test.zip"
    assert os.path.exists(path)
    assert zipfile.is_zipfile(path)
