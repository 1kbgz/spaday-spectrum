// the guard must execute before the Spectrum imports register their elements
import { restoreDefine } from "./define-guard";
import { version } from "@spectrum-web-components/theme/package.json";
import "@spectrum-web-components/theme/sp-theme.js";
import "@spectrum-web-components/theme/theme-light.js";
import "@spectrum-web-components/theme/theme-dark.js";
import "@spectrum-web-components/theme/scale-medium.js";
import "@spectrum-web-components/theme/scale-large.js";
import "@spectrum-web-components/button/sp-button.js";
import "@spectrum-web-components/button/sp-clear-button.js";
import "@spectrum-web-components/button/sp-close-button.js";
import "@spectrum-web-components/checkbox/sp-checkbox.js";
import "@spectrum-web-components/switch/sp-switch.js";
import "@spectrum-web-components/tabs/sp-tab.js";
import "@spectrum-web-components/tabs/sp-tab-panel.js";
import "@spectrum-web-components/tabs/sp-tabs.js";
import "@spectrum-web-components/tabs/sp-tabs-overflow.js";
import "@spectrum-web-components/textfield/sp-textfield.js";

restoreDefine(`@spectrum-web-components ${version}`, [
  "sp-theme",
  "sp-button",
  "sp-clear-button",
  "sp-close-button",
  "sp-checkbox",
  "sp-switch",
  "sp-tab",
  "sp-tab-panel",
  "sp-tabs",
  "sp-tabs-overflow",
  "sp-textfield",
]);
