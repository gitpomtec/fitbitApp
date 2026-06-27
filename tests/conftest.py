import json
import os

import pytest

import fitbitApp

CONFIG_DIR = os.environ.get(
    "FITBIT_APP_CONFIG_DIR",
    os.path.dirname(os.path.abspath(__file__)) + "/",
)
if not CONFIG_DIR.endswith("/"):
    CONFIG_DIR += "/"


@pytest.fixture(scope="session")
def app():
    with open(f"{CONFIG_DIR}Config.json") as f:
        config = json.load(f)
    with open(f"{CONFIG_DIR}Token.json") as f:
        token = json.load(f)

    return fitbitApp.app(
        token["access_token"],
        token["refresh_token"],
        config["CLIENT_ID"],
        CONFIG_DIR,
    )


def assert_no_error(response: dict):
    assert "error" not in response, f"APIエラー: {response.get('error')}"
