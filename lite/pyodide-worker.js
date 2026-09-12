const PYODIDE_VERSION = "314.0.4";
const requestedExample = new URL(self.location.href).searchParams.get(
  "example",
);
const exampleName = requestedExample === "gallery" ? "gallery" : "example";
let pyodide;

const ready = (async () => {
  self.postMessage({ type: "status", message: "Loading Pyodide…" });
  const { loadPyodide } = await import(
    `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/pyodide.mjs`
  );
  pyodide = await loadPyodide();
  await pyodide.loadPackage(["micropip", "anyio"]);

  self.postMessage({ type: "status", message: `Installing ${exampleName}…` });
  const response = await fetch(new URL("./wheels.json", self.location.href));
  if (!response.ok)
    throw new Error(`wheel manifest returned ${response.status}`);
  const wheels = await response.json();
  const urls = Object.fromEntries(
    Object.entries(wheels).map(([name, path]) => [
      name,
      new URL(path, self.location.href).href,
    ]),
  );
  pyodide.globals.set("wheels_json", JSON.stringify(urls));
  pyodide.globals.set("example_name", exampleName);
  return pyodide.runPythonAsync(`
import asyncio
import importlib
import json
import re
import micropip

wheels = json.loads(wheels_json)
requirements = [wheels["spaday"], "starlette"]
if example_name == "example":
    requirements.extend([wheels["transports"], "uvicorn"])
await micropip.install(requirements)
await micropip.install(wheels["spectrum"], deps=False)

example = importlib.import_module(f"spaday_spectrum.{example_name}")

connection = "browser"
server = getattr(example, "server", None)

def local_wires(messages):
    return list(messages.get(connection, []))

def receive_wire(frame):
    if server is None:
        return "[]"
    return json.dumps(local_wires(server.recv(connection, frame)))

def flush_server():
    if server is None:
        return "[]"
    return json.dumps(local_wires(server.flush()))

class LocalRequest:
    def __init__(self, body=None, path_params=None):
        self._body = body
        self.path_params = path_params or {}

    async def json(self):
        return self._body

async def call_endpoint(path, body_json):
    body = json.loads(body_json) if body_json else None
    if path == "/api/briefs":
        response = await example.submit_brief(LocalRequest(body))
    elif match := re.fullmatch(r"/api/assets/([^/]+)/(approve|changes)", path):
        response = await example.decide(LocalRequest(path_params={"id": match.group(1), "decision": match.group(2)}))
    else:
        raise ValueError(f"unsupported local endpoint: {path}")
    return json.dumps({
        "status": response.status_code,
        "body": json.loads(bytes(response.body).decode()),
        "wires": local_wires(server.flush()),
    })

opening = server.open(connection, "json") if server is not None else []
if hasattr(example, "stream_reviews"):
    asyncio.create_task(example.stream_reviews())

json.dumps({
    "tree": example.page.to_node(),
    "style": example.styles,
    "store": getattr(example, "initial_store", {}),
    "wires": opening,
    "wire": server is not None,
})
`);
})();

let queue = Promise.resolve();

async function handle(message) {
  const snapshot = await ready;
  if (message.type === "start") {
    self.postMessage({ type: "snapshot", payload: JSON.parse(snapshot) });
  } else if (message.type === "wire") {
    pyodide.globals.set("wire_frame", message.frame);
    const wires = JSON.parse(pyodide.runPython("receive_wire(wire_frame)"));
    if (wires.length) self.postMessage({ type: "wires", wires });
  } else if (message.type === "flush") {
    const wires = JSON.parse(pyodide.runPython("flush_server()"));
    if (wires.length) self.postMessage({ type: "wires", wires });
  } else if (message.type === "endpoint") {
    pyodide.globals.set("endpoint_path", message.path);
    pyodide.globals.set("body_json", JSON.stringify(message.body));
    const result = JSON.parse(
      await pyodide.runPythonAsync(
        "await call_endpoint(endpoint_path, body_json)",
      ),
    );
    self.postMessage({ type: "endpoint", id: message.id, ...result });
  }
}

self.addEventListener("message", (event) => {
  queue = queue
    .then(() => handle(event.data))
    .catch((error) => {
      self.postMessage({ type: "error", message: String(error) });
    });
});
