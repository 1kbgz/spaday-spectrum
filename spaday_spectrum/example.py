import asyncio
import logging

import transports
import uvicorn
from pydantic import BaseModel
from spaday import CallEndpoint, Sequence, SetField, concat, cond, element, eq, field, item, not_, obj
from spaday.backends.starlette import serve
from spaday.components.shell import App, Body, Each, Main, Nav, Row, Show
from starlette.responses import JSONResponse
from starlette.routing import Route, WebSocketRoute

from spaday_spectrum import (
    SpButton,
    SpCheckbox,
    SpClearButton,
    SpCloseButton,
    SpSwitch,
    SpTab,
    SpTabPanel,
    SpTabs,
    SpTextfield,
    SpTheme,
    package,
)

logger = logging.getLogger("uvicorn.error")

CHANNELS = ("web", "social", "email", "print")
INCOMING = [
    ("Hero banner, autumn", "Mara Lind", "image"),
    ("Product teaser cut", "Ravi Shah", "video"),
    ("Newsletter header", "Ingrid Costa", "image"),
    ("Launch keynote deck", "Tomás Ruiz", "document"),
]


def asset(number: int, name: str, owner: str, kind: str, progress: int = 100, status: str = "Needs review") -> dict:
    return {"id": f"AS-{number}", "name": name, "owner": owner, "kind": kind, "progress": progress, "status": status}


class ReviewFeed(BaseModel):
    assets: list[dict] = [
        asset(101, "Campaign key visual", "Mara Lind", "image"),
        asset(102, "Social cutdowns, 15s", "Ravi Shah", "video", 60, "Uploading"),
        asset(103, "Retail shelf wobbler", "Ingrid Costa", "print"),
        asset(100, "Brand guidelines v4", "Tomás Ruiz", "document", status="Approved"),
    ]
    activity: list[dict] = [{"id": "e0", "text": "Review board opened"}]
    waiting: int = 0
    approved: int = 0


feed = ReviewFeed()
session = transports.Session()
session.host(feed)
server = transports.Server(session)


def refresh_totals() -> None:
    feed.waiting = sum(row["status"] == "Needs review" for row in feed.assets)
    feed.approved = sum(row["status"] == "Approved" for row in feed.assets)


refresh_totals()


def log(text: str) -> None:
    number = max(int(entry["id"].removeprefix("e")) for entry in feed.activity) + 1
    feed.activity = [{"id": f"e{number}", "text": text}, *feed.activity][:8]


def next_number() -> int:
    return max(int(row["id"].removeprefix("AS-")) for row in feed.assets) + 1


async def stream_reviews() -> None:
    """Uploads advance every tick until they are ready for review; every third tick an asset arrives."""
    tick = 0
    while True:
        await asyncio.sleep(2)
        tick += 1
        rows = []
        for row in feed.assets:
            if row["status"] == "Uploading":
                progress = min(100, row["progress"] + 20)
                row = {**row, "progress": progress, "status": "Needs review" if progress == 100 else "Uploading"}
                if progress == 100:
                    log(f"{row['owner']} finished uploading {row['name']}")
            rows.append(row)
        if tick % 3 == 0:
            name, owner, kind = INCOMING[(tick // 3) % len(INCOMING)]
            rows = [asset(next_number(), name, owner, kind, 0, "Uploading"), *rows]
            decided = [row for row in rows if row["status"] in ("Approved", "Changes requested")]
            if len(rows) > 8 and decided:
                rows.remove(decided[-1])
            log(f"{owner} started uploading {name}")
        feed.assets = rows
        refresh_totals()


async def decide(request):
    target, decision = request.path_params["id"], request.path_params["decision"]
    status = {"approve": "Approved", "changes": "Changes requested"}.get(decision)
    row = next((row for row in feed.assets if row["id"] == target), None)
    if status is None or row is None or row["status"] != "Needs review":
        return JSONResponse({"message": f"{target} is not waiting for review."}, status_code=409)
    feed.assets = [{**row, "status": status} if existing is row else existing for existing in feed.assets]
    log(f"You marked {row['name']} as {status.lower()}")
    refresh_totals()
    return JSONResponse({"message": f"{status}: {row['name']}"})


async def submit_brief(request):
    body = await request.json()
    logger.info("Brief from browser: %s", body)
    name = (body.get("campaign") or "").strip()
    email = (body.get("email") or "").strip()
    if not name or "@" not in email:
        return JSONResponse({"message": "A brief needs a campaign name and an owner email."}, status_code=422)
    channels = [channel for channel in CHANNELS if body.get(f"channel_{channel}")] or ["no channels yet"]
    timing = "launching as soon as it is approved" if body.get("launch_now") else "held for scheduling"
    log(f"You filed the {name} brief")
    return JSONResponse({"message": f"Filed {name} for {email}: {', '.join(channels)}, {timing}."})


def stat(label: str, value_field: str):
    return element("article", element("span").text(label), element("strong").bind("textContent", value_field), class_="stat")


asset_row = element(
    "div",
    element(
        "div",
        element("strong").compute("textContent", concat(item("id"), " · ", item("name"))),
        element("span", class_="muted").compute("textContent", concat(item("owner"), " · ", item("kind"))),
        # no progress bar in this slice of Spectrum, so the row draws its upload progress
        element("div", class_="progress").compute("style", concat("--progress: ", item("progress"), "%")),
        class_="asset-main",
    ),
    element("span", class_="status").compute("textContent", item("status")).compute("data-status", item("status")),
    SpButton(variant="accent", treatment="outline", size="s")
    .text("Approve")
    .compute("disabled", not_(eq(item("status"), "Needs review")))
    .on("click", CallEndpoint("POST", concat("/api/assets/", item("id"), "/approve"), result="decision")),
    SpButton(variant="negative", treatment="outline", size="s")
    .text("Request changes")
    .compute("disabled", not_(eq(item("status"), "Needs review")))
    .on("click", CallEndpoint("POST", concat("/api/assets/", item("id"), "/changes"), result="decision")),
    class_="asset",
).compute("data-id", item("id"))

assets_panel = element(
    "section",
    Row(stat("Waiting for review", "waiting"), stat("Approved", "approved"), gap="1rem", align="stretch", class_="stats"),
    element("div", Each(asset_row, field="assets", key="id"), id="assets", class_="assets"),
    element("p", id="decision", class_="muted").compute("textContent", field("decision.body.message")),
    class_="panel",
)


def captioned(caption: str, control, wide: bool = False):
    # sp-textfield's label is its accessible name; showing one takes sp-field-label, which this slice
    # of Spectrum leaves out, so the page writes the caption itself
    return element("div", element("span", class_="caption").text(caption), control, class_="field wide" if wide else "field")


brief_panel = element(
    "section",
    element(
        "div",
        captioned(
            "Campaign name",
            Row(
                SpTextfield(id="campaign", label="Campaign name", placeholder="Autumn launch").bind("value", "campaign", mode="two-way"),
                SpClearButton(label="Clear the campaign name", size="m").on("click", SetField("campaign", "")),
                gap=".25rem",
                align="start",
            ),
        ),
        captioned(
            "Owner email",
            SpTextfield(id="email", type="email", label="Owner email", placeholder="you@example.com", required=True)
            .bind("value", "email", mode="two-way")
            .compute("invalid", eq(field("brief.status"), 422))
            .child_in("negative-help-text", element("span").text("Add a campaign name and a valid email.")),
        ),
        captioned(
            "Brief",
            SpTextfield(id="notes", label="Brief", multiline=True, rows=3, placeholder="What should the assets say?").bind(
                "value", "notes", mode="two-way"
            ),
            wide=True,
        ),
        class_="form-grid",
    ),
    element(
        "fieldset",
        element("legend").text("Channels"),
        *(SpCheckbox(id=f"channel-{c}").text(c.title()).bind("checked", f"channel_{c}", mode="two-way") for c in CHANNELS),
    ),
    SpSwitch(id="launch-now").text("Launch as soon as it is approved").bind("checked", "launch_now", mode="two-way"),
    Row(
        SpButton(variant="secondary", treatment="outline").text("Review assets").on("click", SetField("tab", "assets")),
        SpButton(id="submit", variant="accent", pending_label="Filing the brief")
        .text("File brief")
        .bind("pending", "saving")
        .on(
            "click",
            Sequence(
                SetField("saving", True),
                CallEndpoint(
                    "POST",
                    "/api/briefs",
                    obj(
                        {
                            "campaign": field("campaign"),
                            "email": field("email"),
                            "notes": field("notes"),
                            "launch_now": field("launch_now"),
                            **{f"channel_{c}": field(f"channel_{c}") for c in CHANNELS},
                        }
                    ),
                    result="brief",
                ),
                SetField("saving", False),
            ),
        ),
        gap=".75rem",
        justify="end",
    ),
    Show(
        element(
            "div",
            element("span", id="brief-message").compute("textContent", field("brief.body.message")),
            SpCloseButton(label="Dismiss", size="s").on("click", SetField("brief", {})),
            class_="callout",
        ),
        when=field("brief.ok"),
    ),
    class_="panel",
)

activity_panel = element(
    "section",
    Each(element("div", class_="entry").compute("textContent", item("text")), field="activity", key="id"),
    id="activity",
    class_="panel activity",
)

page = (
    SpTheme(
        App(
            Nav(
                element("strong", class_="brand").text("Spectrum review board"),
                Row(
                    SpSwitch(id="dark").text("Dark").bind("checked", "dark", mode="two-way"),
                    SpSwitch(id="large").text("Large scale").bind("checked", "large", mode="two-way"),
                    gap="1rem",
                ),
            ),
            Body(
                Main(
                    Show(
                        element(
                            "div",
                            element("span").text("Assets and activity stream from Python; every control is a typed Spectrum web component."),
                            SpCloseButton(id="dismiss-banner", label="Dismiss", size="s").on("click", SetField("banner", False)),
                            class_="callout",
                        ),
                        field="banner",
                    ),
                    SpTabs(
                        SpTab(label="Assets", value="assets"),
                        SpTab(label="Brief", value="brief"),
                        SpTab(label="Activity", value="activity"),
                        id="tabs",
                        label="Review board",
                    )
                    .bind("selected", "tab", mode="two-way")
                    .child_in("tab-panel", SpTabPanel(assets_panel, value="assets"))
                    .child_in("tab-panel", SpTabPanel(brief_panel, value="brief"))
                    .child_in("tab-panel", SpTabPanel(activity_panel, value="activity")),
                    class_="page",
                ),
            ),
        ),
        id="theme",
        system="spectrum",
    )
    .compute("color", cond(field("dark"), "dark", "light"))
    .compute("scale", cond(field("large"), "large", "medium"))
)

styles = """
<style>
  body { margin: 0; }
  /* spaday-spectrum ships no mapping of spaday's shell palette yet, so the page maps it onto Spectrum's
     tokens here, inside the theme that defines them */
  sp-theme { display: block; font-family: var(--spectrum-sans-font-family-stack, system-ui); color: var(--spectrum-neutral-content-color-default);
    background: var(--spectrum-background-layer-1-color);
    --spa-surface: var(--spectrum-background-layer-2-color); --spa-surface-2: var(--spectrum-background-layer-1-color);
    --spa-border: var(--spectrum-gray-300); --spa-muted: var(--spectrum-neutral-subdued-content-color-default);
    --spa-accent: var(--spectrum-accent-content-color-default); --spa-success: var(--spectrum-positive-visual-color);
    --spa-warning: var(--spectrum-notice-visual-color); --spa-danger: var(--spectrum-negative-visual-color); }
  spa-nav { justify-content: space-between; }
  /* a tab panel lays out its content as a flex row */
  sp-tab-panel > .panel { flex: 1; min-width: 0; }
  .brand { font-size: 1.1rem; }
  .page { box-sizing: border-box; width: 100%; max-width: 70rem; margin: 0 auto; padding: 1.5rem 1rem;
    display: grid; grid-template-columns: minmax(0, 1fr); align-content: start; gap: 1rem; }
  .callout { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: .5rem .5rem .5rem 1rem;
    border-radius: 8px; border: 1px solid var(--spa-border); border-left: 4px solid var(--spa-accent); background: var(--spa-surface); }
  .panel { display: grid; gap: 1rem; padding-block: 1rem; }
  .muted { color: var(--spa-muted); }
  .stats { flex-wrap: wrap; }
  .stat { flex: 1 1 12rem; display: grid; gap: .25rem; padding: 1rem; border-radius: 8px; border: 1px solid var(--spa-border); background: var(--spa-surface); }
  .stat span { color: var(--spa-muted); }
  .stat strong { font-size: 1.75rem; }
  .assets, .activity { display: grid; gap: .5rem; }
  .asset { display: grid; grid-template-columns: minmax(0, 1fr) 9rem auto auto; align-items: center; gap: 1rem; padding: .75rem 1rem;
    border-radius: 8px; border: 1px solid var(--spa-border); background: var(--spa-surface); }
  .asset-main { display: grid; gap: .25rem; min-width: 0; }
  .progress { height: 4px; border-radius: 2px; background: linear-gradient(to right, var(--spa-accent) var(--progress), var(--spa-border) 0); }
  .status[data-status="Approved"] { color: var(--spa-success); }
  .status[data-status="Changes requested"] { color: var(--spa-danger); }
  .form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem 1.5rem; }
  .field { display: grid; gap: .35rem; }
  .field.wide { grid-column: 1 / -1; }
  .caption { color: var(--spa-muted); font-size: .85rem; }
  .form-grid sp-textfield { width: 100%; }
  .form-grid spa-row sp-textfield { flex: 1; }
  fieldset { display: flex; flex-wrap: wrap; gap: 1rem; margin: 0; padding: .5rem 1rem 1rem; border-radius: 8px; border: 1px solid var(--spa-border); }
  .entry { padding: .5rem 0; border-bottom: 1px solid var(--spa-border); }
  @media (max-width: 720px) {
    .form-grid { grid-template-columns: 1fr; }
    .asset { grid-template-columns: 1fr 1fr; }
    .asset-main { grid-column: 1 / -1; }
  }
</style>
"""

app = serve(
    page,
    packages=[package],
    wire="transports",
    routes=[
        WebSocketRoute("/ws", transports.ws_endpoint(server)),
        Route("/api/briefs", submit_brief, methods=["POST"]),
        Route("/api/assets/{id}/{decision}", decide, methods=["POST"]),
    ],
    background=[transports.autosync(server), stream_reviews()],
    store={
        "dark": False,
        "large": False,
        "banner": True,
        "tab": "assets",
        "campaign": "Autumn launch",
        "email": "",
        "notes": "",
        "channel_web": True,
        "channel_social": True,
        "channel_email": False,
        "channel_print": False,
        "launch_now": False,
        "saving": False,
        "brief": {},
        "decision": {"body": {"message": ""}},
    },
    head=styles,
    title="spaday-spectrum example",
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8028)
