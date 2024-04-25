from io import BytesIO
from pathlib import Path

import pytest

from ..config import settings
from .conftest import TestClient, TestUser, assets

textures_url = "http://testserver/textures/"
steve_file = assets / "good/64x64.png"
steve_url = "http://assets.mojang.com/SkinTemplates/steve.png"
steve_hash = textures_url + steve_file.with_suffix(".txt").read_text().strip()


def build_request_kwargs(file: str | Path) -> tuple[str, dict]:
    if isinstance(file, Path):
        return "PUT", {
            "data": {"type": "skin"},
            "files": {"file": (file.name, file.read_bytes(), "image/png")},
        }
    return "POST", {
        "json": {"file": file, "type": "skin"},
    }


@pytest.mark.parametrize(
    "file_or_url, hash_url",
    [
        [steve_file, steve_hash],
        [steve_url, steve_hash],
    ],
)
def test_texture_upload_post(
    file_or_url: Path | str, hash_url, client: TestClient, user: TestUser
):
    method, kwargs = build_request_kwargs(file_or_url)
    upload_resp = client.request(
        method, "/api/v1/textures", headers=user.auth_header, **kwargs
    )
    assert upload_resp.status_code == 200, upload_resp.json()

    user_resp = client.get("/api/v1/textures", headers=user.auth_header)
    assert user_resp.status_code == 200, user_resp.json()
    textures = user_resp.json()
    skin = textures["skin"]

    assert skin["url"] == hash_url
    assert not skin["metadata"]

    anon_resp = client.get(f"/api/v1/user/{user.uuid}")
    assert anon_resp.status_code == 200, anon_resp.json()
    assert anon_resp.json()["textures"] == textures


def test_unknown_user_textures(client: TestClient, user: TestUser):
    resp = client.get(f"/api/v1/user/{user.uuid}")
    assert resp.status_code == 404


@pytest.mark.parametrize(
    "file_or_url",
    [steve_file, steve_url],
)
def test_unauthenticated_user_texture_upload(file_or_url, client: TestClient):
    method, kwargs = build_request_kwargs(file_or_url)
    upload_resp = client.request(method, "/api/v1/textures", **kwargs)
    assert upload_resp.status_code == 401, upload_resp.json()


def test_non_image_upload(client: TestClient, user: TestUser):
    resp = client.put(
        "/api/v1/textures",
        headers=user.auth_header,
        data={"type": "skin"},
        files={"file": ("file.txt", BytesIO(b"bad file"))},
    )
    assert resp.status_code == 400, resp.json()
    assert "cannot identify image file" in resp.json()["detail"]


def test_very_large_upload(client: TestClient, user: TestUser):
    ten_megabytes_of_zeros = b"\0" * 10_000_000
    resp = client.put(
        "/api/v1/textures",
        headers={
            **user.auth_header,
            # lie about the content-length
            "content-length": "1000",
        },
        data={"type": "skin"},
        files={"file": ("file.txt", BytesIO(ten_megabytes_of_zeros))},
    )
    assert resp.status_code == 413, resp.json()  # Request entity too large


def test_env():
    assert not settings.env.isprod
