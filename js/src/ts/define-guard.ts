/** Tolerate another bundle having already registered elements this bundle also registers.
 *
 * This bundle registers every Spectrum element it serves at import. An application that also ships
 * Spectrum Web Components — its own selection, or another copy at a different version — registers
 * the same tag names, and whichever bundle loads second would throw from `customElements.define`
 * and die entirely, taking the whole catalog with it. Importing this module FIRST makes `define`
 * idempotent (skip names that already exist); `restoreDefine()` puts the real one back immediately
 * after the upstream imports, so the guard never leaks to other scripts.
 *
 * First registration wins, so this keeps the page alive; it does not make two copies agree.
 */

const define = customElements.define.bind(customElements);
const lookup = customElements.get.bind(customElements);
// names this bundle registered itself
const ours = new Set<string>();

customElements.define = (
  name: string,
  ctor: CustomElementConstructor,
  options?: ElementDefinitionOptions,
) => {
  if (lookup(name)) return;
  define(name, ctor, options);
  ours.add(name);
};

/** Put the real `define` back, and warn if another copy had already registered any of `tags`, the
 * elements this bundle serves: the page keeps that copy's, which need not match the version this
 * package serves and its catalog describes. `served` names that version, e.g.
 * "@awesome.me/webawesome 3.12.0". A tag that is registered, but not by this bundle, is another
 * copy's -- whether the library skipped it just now or defines its elements later. */
export function restoreDefine(
  served: string,
  tags: readonly string[] = [],
): void {
  customElements.define = define;
  const taken = tags.filter((tag) => lookup(tag) && !ours.has(tag));
  if (!taken.length) return;
  const shown = taken
    .slice(0, 3)
    .map((tag) => `<${tag}>`)
    .join(", ");
  const more = taken.length > 3 ? ` and ${taken.length - 3} more` : "";
  console.warn(
    `${served}: another copy on the page already registered ${shown}${more}; the page keeps that copy's elements, which may not match this version`,
  );
}
