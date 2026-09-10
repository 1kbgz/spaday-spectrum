import asyncio

import httpx
import pytest

from spaday_spectrum import example


async def request(method: str, path: str, **kwargs):
    transport = httpx.ASGITransport(app=example.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://example") as client:
        return await client.request(method, path, **kwargs)


def run_ticks(monkeypatch, ticks: int):
    """Run the review stream for ``ticks`` iterations."""
    sleeps = 0

    class Done(Exception):
        pass

    async def sleep(_delay):
        nonlocal sleeps
        sleeps += 1
        if sleeps > ticks:
            raise Done

    monkeypatch.setattr(example.asyncio, "sleep", sleep)
    with pytest.raises(Done):
        asyncio.run(example.stream_reviews())


def test_example_serves_the_review_board():
    response = asyncio.run(request("GET", "/tree.json"))
    assert response.status_code == 200
    for tag in ("sp-theme", "sp-tabs", "sp-tab-panel", "sp-textfield", "sp-checkbox", "sp-switch", "sp-close-button", "spa-each"):
        assert tag in response.text


def test_uploads_finish_and_assets_arrive(monkeypatch):
    uploading = [row["id"] for row in example.feed.assets if row["status"] == "Uploading"]
    arriving = f"AS-{example.next_number()}"
    run_ticks(monkeypatch, 3)
    rows = {row["id"]: row for row in example.feed.assets}
    assert all(rows[key]["progress"] > 0 for key in uploading if key in rows)
    assert rows[arriving]["status"] == "Uploading"  # every third tick an asset arrives
    assert example.feed.activity[0]["text"].endswith("started uploading " + rows[arriving]["name"])
    assert example.feed.waiting == sum(row["status"] == "Needs review" for row in example.feed.assets)


def test_reviewing_an_asset_decides_it_once():
    row = next(row for row in example.feed.assets if row["status"] == "Needs review")
    response = asyncio.run(request("POST", f"/api/assets/{row['id']}/changes"))
    assert response.json() == {"message": f"Changes requested: {row['name']}"}
    assert next(r for r in example.feed.assets if r["id"] == row["id"])["status"] == "Changes requested"
    assert asyncio.run(request("POST", f"/api/assets/{row['id']}/approve")).status_code == 409
    assert asyncio.run(request("POST", f"/api/assets/{row['id']}/delete")).status_code == 409


def test_filing_a_brief_checks_it_first():
    rejected = asyncio.run(request("POST", "/api/briefs", json={"campaign": "Autumn", "email": "nope"}))
    assert rejected.status_code == 422
    brief = {"campaign": "Autumn launch", "email": "mara@example.com", "channel_web": True, "channel_print": True, "launch_now": True}
    response = asyncio.run(request("POST", "/api/briefs", json=brief))
    assert response.json() == {"message": "Filed Autumn launch for mara@example.com: web, print, launching as soon as it is approved."}
    assert example.feed.activity[0]["text"] == "You filed the Autumn launch brief"
