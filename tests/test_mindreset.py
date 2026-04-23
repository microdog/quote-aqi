import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


class FakeBaseModel:
    def __init__(self, **data):
        for key, value in data.items():
            setattr(self, key, value)

    @classmethod
    def model_validate_json(cls, content):
        return cls(**json.loads(content))


def fake_field(default=None, **_kwargs):
    return default


def import_mindreset():
    fake_pydantic = types.ModuleType("pydantic")
    fake_pydantic.BaseModel = FakeBaseModel
    fake_pydantic.Field = fake_field

    fake_requests = types.ModuleType("requests")
    fake_requests.Session = lambda: None

    spec = importlib.util.spec_from_file_location(
        "mindreset_under_test", SRC / "quote_aqi" / "mindreset.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load quote_aqi.mindreset")

    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(
        sys.modules, {"pydantic": fake_pydantic, "requests": fake_requests}
    ):
        spec.loader.exec_module(module)
    return module


class RecordingResponse:
    content = b'{"message": "ok"}'

    def raise_for_status(self):
        pass


class RecordingSession:
    def __init__(self):
        self.headers = {}
        self.post_calls = []

    def post(self, url, **kwargs):
        self.post_calls.append({"url": url, **kwargs})
        return RecordingResponse()


class DummyImageAPIRequest:
    deviceId = "quote/0 1"

    def __init__(self):
        self.dump_kwargs = None

    def model_dump(self, **kwargs):
        self.dump_kwargs = kwargs
        payload = {
            "deviceId": self.deviceId,
            "image": "base64-image",
            "ditherType": "NONE",
        }
        for key in kwargs.get("exclude", set()):
            payload.pop(key, None)
        return payload


class DotClientTest(unittest.TestCase):
    def test_image_api_posts_to_new_device_endpoint_without_device_id_body(self):
        mindreset = import_mindreset()
        session = RecordingSession()
        mindreset.requests.Session = lambda: session

        client = mindreset.DotClient("dot-token", timeout=3)
        request = DummyImageAPIRequest()

        response = client.image_api(request)

        self.assertEqual(response.message, "ok")
        self.assertEqual(session.headers["Authorization"], "Bearer dot-token")
        self.assertEqual(
            session.post_calls,
            [
                {
                    "url": (
                        "https://dot.mindreset.tech/api/authV2/open/device/"
                        "quote%2F0%201/image"
                    ),
                    "json": {
                        "image": "base64-image",
                        "ditherType": "NONE",
                    },
                    "timeout": 3,
                }
            ],
        )
        self.assertEqual(
            request.dump_kwargs,
            {
                "exclude": {"deviceId"},
                "exclude_none": True,
                "by_alias": True,
            },
        )


if __name__ == "__main__":
    unittest.main()
