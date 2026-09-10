/* Resolved manifests for the Spectrum packages this package bundles.
 *
 * Spectrum publishes one package per component, and the Custom Elements Manifest analyzer only
 * inlines inherited attributes from within a package. An element whose superclass or mixins live in
 * another package is published without what they contribute: `size` from base's SizedMixin,
 * `disabled` from shared's Focusable, `checked` on sp-switch from checkbox's CheckboxBase. This walks
 * each bundled element's superclass and mixins through the manifests of the packages declaring them
 * and appends their attributes, events and slots, marked `inheritedFrom`, as the analyzer does within
 * a package.
 *
 * base and shared name a manifest in their package.json but do not ship one, and help-text's leaves
 * out the mixin textfield uses, so unpublished.json carries the declarations these elements need
 * from them, transcribed from their sources. A class found in neither is reported and fails the run,
 * so an upgrade that introduces one cannot slip through. Run through `make catalog`, which also
 * regenerates the Python modules.
 */
import fs from "fs";
import path from "path";

const PACKAGES = ["button", "checkbox", "switch", "tabs", "textfield", "theme"];
const OUT = "../spaday_spectrum/manifests";
const UNPUBLISHED = JSON.parse(
  fs.readFileSync("tools/unpublished.json", "utf8"),
);
// platform and Lit bases contribute nothing an author sets
const PLATFORM = new Set(["HTMLElement", "LitElement", "ReactiveElement"]);
const MERGED = ["attributes", "events", "slots"];

const readJson = (file) => JSON.parse(fs.readFileSync(file, "utf8"));

function packageName(spec) {
  const parts = spec.split("/");
  return parts.slice(0, spec.startsWith("@") ? 2 : 1).join("/");
}

/** The manifest of package `name` as resolved from `fromDir`, falling back to unpublished.json. */
function manifestOf(name, fromDir) {
  let dir = fs.realpathSync(fromDir);
  for (;;) {
    const pkgDir = path.join(dir, "node_modules", name);
    if (fs.existsSync(path.join(pkgDir, "package.json"))) {
      const { customElements = "custom-elements.json" } = readJson(
        path.join(pkgDir, "package.json"),
      );
      const file = path.join(pkgDir, customElements);
      if (fs.existsSync(file))
        return { manifest: readJson(file), dir: pkgDir, name };
      break; // named in package.json, never shipped
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return UNPUBLISHED[name]
    ? { manifest: UNPUBLISHED[name], dir: fromDir, name }
    : null;
}

function declaration(manifest, name) {
  for (const mod of manifest.modules ?? []) {
    for (const decl of mod.declarations ?? [])
      if (decl.name === name) return decl;
  }
  return null;
}

/** `decl`'s superclass and mixins, and theirs, nearest first. */
function ancestors(decl, owner, missing) {
  const found = [];
  for (const ref of [decl.superclass, ...(decl.mixins ?? [])]) {
    if (
      !ref ||
      PLATFORM.has(ref.name) ||
      /^(lit|@lit\/)/.test(ref.package ?? "")
    )
      continue;
    const source = ref.package
      ? manifestOf(packageName(ref.package), owner.dir)
      : owner;
    // a shipped manifest can still leave a mixin out (help-text's omits ManageHelpText)
    const target =
      source &&
      (declaration(source.manifest, ref.name) ??
        declaration(UNPUBLISHED[source.name] ?? {}, ref.name));
    if (!target) {
      missing.add(`${ref.name} (${ref.package ?? owner.name})`);
      continue;
    }
    found.push(
      { decl: target, from: { name: ref.name, package: source.name } },
      ...ancestors(target, source, missing),
    );
  }
  return found;
}

function resolve(decl, owner, missing) {
  const out = structuredClone(decl);
  for (const key of MERGED) out[key] ??= [];
  for (const { decl: ancestor, from } of ancestors(decl, owner, missing)) {
    for (const key of MERGED) {
      const have = new Set(out[key].map((entry) => entry.name));
      for (const entry of ancestor[key] ?? []) {
        if (have.has(entry.name)) continue; // the nearer declaration wins
        out[key].push({ ...entry, inheritedFrom: entry.inheritedFrom ?? from });
        have.add(entry.name);
      }
    }
  }
  return out;
}

const missing = new Set();
fs.mkdirSync(OUT, { recursive: true });
for (const pkg of PACKAGES) {
  const owner = manifestOf(`@spectrum-web-components/${pkg}`, ".");
  const modules = owner.manifest.modules
    .map((mod) => ({
      kind: mod.kind,
      path: mod.path,
      declarations: (mod.declarations ?? [])
        .filter((decl) => decl.customElement && decl.tagName)
        .map((decl) => resolve(decl, owner, missing)),
    }))
    .filter((mod) => mod.declarations.length);
  const manifest = { schemaVersion: owner.manifest.schemaVersion, modules };
  fs.writeFileSync(
    path.join(OUT, `${pkg}.json`),
    `${JSON.stringify(manifest, null, 2)}\n`,
  );
}
if (missing.size) {
  console.error(
    `no manifest declares: ${[...missing].join(", ")} -- add them to tools/unpublished.json`,
  );
  process.exitCode = 1;
}
