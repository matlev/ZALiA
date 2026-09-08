"use strict";
// Source-defined presets only. This does not run GML or resolve a saved scene.
const palettePresets = window.CATALOG.palettes?.presets || [];
const paletteByName = new Map(palettePresets.map(p => [p.name, p]));
const paletteChoices = new Map();
let activePalette = "";
let activeVariant = "";
const coloredFrames = new Map();

function presetsForSlot(slot) {
  const prefix = slot.startsWith("PI_MOB_") ? slot.replace("PI_", "PAL_")
    : slot === "PI_PC1" ? "PAL_PC_" : slot === "PI_GUI1" ? "PAL_GUI" : null;
  return prefix ? palettePresets.filter(p => p.name.startsWith(prefix)) : [];
}

function rememberPalette() {
  if (current) paletteChoices.set(current.name, {palette:activePalette, variant:activeVariant});
}

function paletteControls(asset, pane) {
  coloredFrames.clear();
  const saved = paletteChoices.get(asset.name);
  activeVariant = saved?.variant || "";
  activePalette = saved?.palette || "";
  const section = el("section", undefined, "palette-controls");
  section.append(el("h3", "Colors & versions"));
  const variants = [...new Map((asset.variants || []).map(v => [v.key, v])).values()];
  const versionLabel = el("label", "Source-linked object version");
  const version = el("select"); version.id = "variant";
  version.setAttribute("aria-label", "Object version");
  const none = el("option", "Manual palette preview"); none.value = ""; version.append(none);
  for (const v of variants) {
    const option = el("option", `${v.key} · ${v.slot.replace("PI_", "")}`);
    option.value = v.key; version.append(option);
  }
  version.value = activeVariant; version.disabled = !variants.length;
  versionLabel.append(version); section.append(versionLabel);
  const label = el("label", "Palette preview"); const select = el("select"); select.id = "palette";
  select.setAttribute("aria-label", "Palette preview"); label.append(select); section.append(label);
  const detail = el("p", "", "fine"); detail.id = "palette-detail"; section.append(detail);
  const swatches = el("div", undefined, "palette-swatches"); section.append(swatches);
  section.append(el("p", "Versions come from placement sprites, registered callback references, or item sprite assignments. Shared artwork may serve several versions. This changes colors only; scene overrides, multipart drawing and behavior are not simulated.", "fine"));
  pane.append(section);

  function refresh() {
    version.value = activeVariant;
    select.replaceChildren();
    const raw = el("option", "Original source colors"); raw.value = ""; select.append(raw);
    const variant = variants.find(v => v.key === activeVariant);
    const matching = variant ? presetsForSlot(variant.slot) : [];
    for (const [title, entries] of [["Related source presets", matching],
      ["All source presets · manual experiments", palettePresets.filter(p => !matching.includes(p))]]) {
      if (!entries.length) continue;
      const group = el("optgroup"); group.label = title;
      for (const p of entries) {
        const option = el("option", p.name.replace(/^PAL_/, "").replaceAll("_", " ")
          + (p.description ? " · " + p.description : ""));
        option.value = p.name; group.append(option);
      }
      select.append(group);
    }
    select.value = activePalette;
    detail.replaceChildren();
    if (variant) {
      detail.append(link(`${variant.key} registration · line ${variant.line}`, variant.url),
        document.createTextNode(matching.length ? ". Slot presets can differ by scene. "
          : ". Palette slot unresolved here; select a manual preset. "));
    }
    const preset = paletteByName.get(activePalette);
    if (preset) detail.append(link(`${preset.name} · line ${preset.line}`, preset.url));
    else detail.append(document.createTextNode("Unmodified PNG colors."));
    swatches.replaceChildren();
    const base = window.CATALOG.palettes?.base || [];
    (preset?.colors || base).forEach((color, i) => {
      const chip = el("span", "WRBGYMKC"[i]); chip.style.backgroundColor = `rgb(${color.slice(0,3).join(",")})`;
      chip.title = `${"WRBGYMKC"[i]} → RGB ${color.slice(0,3).join(", ")}`; swatches.append(chip);
    });
    rememberPalette(); drawPreview();
  }
  version.onchange = () => {
    activeVariant = version.value;
    const variant = variants.find(v => v.key === activeVariant);
    const matching = variant ? presetsForSlot(variant.slot) : [];
    // A named source preset, not an inferred current-scene palette.
    activePalette = matching.find(p => p.name === "PAL_MOB_PUR2")?.name || matching[0]?.name || "";
    refresh();
  };
  select.onchange = () => { activePalette = select.value; refresh(); };
  refresh();
}

function paletteImage(image) {
  const preset = paletteByName.get(activePalette);
  if (!preset) return image;
  const key = image.src + "|" + activePalette;
  if (coloredFrames.has(key)) return coloredFrames.get(key);
  const canvas = document.createElement("canvas");
  canvas.width = image.naturalWidth; canvas.height = image.naturalHeight;
  const ctx = canvas.getContext("2d"); ctx.drawImage(image, 0, 0);
  const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const base = window.CATALOG.palettes.base;
  for (let i = 0; i < pixels.data.length; i += 4) {
    const d = pixels.data;
    // shd_pal_swapper: special alpha-cutout before exact RGBA base-color matching.
    if (d[i] === 127 && d[i+1] === 127 && d[i+2] === 127) { d[i+3] = 0; continue; }
    const index = base.findIndex(c => c.every((value, j) => value === d[i+j]));
    if (index >= 0) d.set(preset.colors[index], i);
  }
  ctx.putImageData(pixels, 0, 0);
  // Bound memory during long inspections with many frame/preset combinations.
  if (coloredFrames.size >= 32) coloredFrames.delete(coloredFrames.keys().next().value);
  coloredFrames.set(key, canvas); return canvas;
}
