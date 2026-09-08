"use strict";
const $ = id => document.getElementById(id);
const assets = window.CATALOG.assets;
const byName = new Map(assets.map(a => [a.name, a]));
let current = null, frame = 0, page = 0, matches = [], animation = null;
let previewImage = null, scale = 4, showOrigin = true, showBounds = false, showGrid = false;
let previewRevision = 0;
const pageSize = 48;
const selected = new Set();
const tileNotes = new Map();
try {
  for (const name of JSON.parse(localStorage.getItem("zalia-atlas-selection") || "[]")) {
    if (byName.has(name)) selected.add(name);
  }
} catch { /* Browsers may disallow storage on file://. The catalog still works. */ }

function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function button(text, action, className) {
  const node = el("button", text, className); node.type = "button"; node.onclick = action; return node;
}
function link(text, url) {
  const node = el("a", text); node.href = url; node.target = "_blank"; node.rel = "noopener"; return node;
}
let toastTimer;
function toast(text) {
  $("toast").textContent = text; $("toast").style.display = "block";
  clearTimeout(toastTimer); toastTimer = setTimeout(() => $("toast").style.display = "none", 2300);
}
async function copy(text) {
  try { await navigator.clipboard.writeText(text); toast("Copied to clipboard"); }
  catch { window.prompt("Copy this reference:", text); }
}
function persist() {
  $("selection-count").textContent = selected.size;
  try { localStorage.setItem("zalia-atlas-selection", JSON.stringify([...selected])); } catch { }
}
function filter(reset = true) {
  if (reset) page = 0;
  const words = $("search").value.toLowerCase().trim().split(/\s+/).filter(Boolean);
  matches = assets.filter(a => ($("unregistered").checked || a.registered)
    && (!$("kind").value || a.kind === $("kind").value)
    && (!$("group").value || a.group === $("group").value)
    && words.every(word => (a.name + " " + a.group).toLowerCase().includes(word)));
  page = Math.max(0, Math.min(page, Math.ceil(matches.length / pageSize) - 1));
  renderCards();
}
function renderCards() {
  const grid = $("grid"); grid.replaceChildren();
  const zoom = Number($("zoom").value);
  for (const a of matches.slice(page * pageSize, (page + 1) * pageSize)) {
    const card = button("", () => inspect(a), "card" + (a === current ? " active" : ""));
    card.setAttribute("aria-label", "Inspect " + a.name);
    card.setAttribute("aria-pressed", String(a === current));
    const thumb = el("div", undefined, "thumb checker");
    const first = a.frames[0];
    if (first?.exists) {
      const img = el("img"); img.src = first.url; img.alt = a.name; img.loading = "lazy";
      img.style.width = a.width * zoom + "px"; img.style.height = a.height * zoom + "px";
      img.onerror = () => thumb.replaceChildren(el("span", "Image unavailable", "fine"));
      thumb.append(img);
    } else thumb.append(el("span", "Missing image", "fine"));
    const info = el("div", undefined, "card-info");
    info.append(el("div", a.kind + (a.registered ? "" : " · unregistered"), "tag"),
      el("div", a.name, "asset-name"),
      el("div", `${a.width} × ${a.height} · ${a.frames.length} frame${a.frames.length === 1 ? "" : "s"}`, "card-meta"));
    card.append(thumb, info); grid.append(card);
  }
  if (!matches.length) grid.append(el("p", "No matching assets. Clear a filter or include unregistered files.", "no-results"));
  $("results").textContent = `${matches.length.toLocaleString()} matches / ${assets.length.toLocaleString()} source assets`;
  $("page").textContent = matches.length ? `Page ${page + 1} of ${Math.ceil(matches.length / pageSize)}` : "0 results";
  $("prev").disabled = page === 0; $("next").disabled = (page + 1) * pageSize >= matches.length;
}
function checkbox(text, checked, action) {
  const label = el("label"); const input = el("input"); input.type = "checkbox";
  input.checked = checked; input.onchange = () => action(input.checked);
  label.append(input, document.createTextNode(text)); return label;
}
function stopAnimation() { clearInterval(animation); animation = null; }
function inspect(a, setHash = true) {
  stopAnimation(); current = a; frame = 0; previewImage = null; previewRevision++;
  scale = a.kind === "background" ? 2 : 4;
  if (setHash) history.replaceState(null, "", "#" + encodeURIComponent(a.name));
  const pane = $("inspector"); pane.replaceChildren();
  pane.append(el("p", "RESOURCE INSPECTOR", "eyebrow"), el("h2", a.name, "inspect-name"),
    el("p", a.group + (a.registered ? "" : " · not in project manifest"), "inspect-group"));
  const actions = el("div", undefined, "inspect-actions");
  actions.append(button("Copy name", () => copy(a.name)));
  const add = button(selected.has(a.name) ? "✓ In brief" : "+ Add to brief", () => {
    if (selected.has(a.name)) selected.delete(a.name); else selected.add(a.name);
    persist(); add.textContent = selected.has(a.name) ? "✓ In brief" : "+ Add to brief";
  }); actions.append(add); pane.append(actions);
  const wrap = el("div", undefined, "preview-wrap checker");
  const canvas = el("canvas", "Asset preview"); canvas.className = "preview"; canvas.id = "preview";
  canvas.setAttribute("aria-label", "Enlarged preview of " + a.name);
  wrap.append(canvas); pane.append(wrap);
  const controls = el("div", undefined, "controls");
  const zoomLabel = el("label", "Zoom"); const zoom = el("select"); zoom.setAttribute("aria-label", "Inspector zoom");
  for (const n of [1, 2, 4, 8]) { const o = el("option", n + "×"); o.value = n; zoom.append(o); }
  zoom.value = scale; zoom.onchange = () => { scale = Number(zoom.value); drawPreview(); };
  zoomLabel.append(zoom); controls.append(zoomLabel);
  if (a.origin) {
    controls.append(checkbox("Origin", showOrigin, v => { showOrigin = v; drawPreview(); }),
      checkbox("Sprite bounds", showBounds, v => { showBounds = v; drawPreview(); }));
  } else controls.append(checkbox("Tile grid", showGrid, v => { showGrid = v; drawPreview(); }));
  pane.append(controls);
  const readout = el("p", "", "tile-readout"); readout.id = "tile-readout"; pane.append(readout);
  canvas.onclick = event => {
    if (!previewImage) return;
    const bounds = canvas.getBoundingClientRect();
    const x = Math.floor((event.clientX - bounds.left) * a.width / bounds.width);
    const y = Math.floor((event.clientY - bounds.top) * a.height / bounds.height);
    let note = `${a.name}: pixel (${x}, ${y}), frame ${a.frames[frame].index}`;
    const t = a.tile;
    if (t && t.tilewidth > 0 && t.tileheight > 0) {
      const dx = x - t.tilexoff, dy = y - t.tileyoff;
      const sx = t.tilewidth + t.tilehsep, sy = t.tileheight + t.tilevsep;
      const col = Math.floor(dx / sx), row = Math.floor(dy / sy);
      const columns = Math.floor((a.width - t.tilexoff + t.tilehsep) / sx);
      const rows = Math.floor((a.height - t.tileyoff + t.tilevsep) / sy);
      if (dx >= 0 && dy >= 0 && col < columns && row < rows
          && dx % sx < t.tilewidth && dy % sy < t.tileheight) {
        const index = row * columns + col;
        note = `${a.name}: tile ${index} (0x${index.toString(16).toUpperCase()}), column ${col}, row ${row} (zero-based)`;
      } else note = `${a.name}: pixel (${x}, ${y}) is outside a complete tile or in spacing`;
    }
    readout.textContent = note; tileNotes.set(a.name, note);
  };
  const frameControls = el("div", undefined, "controls");
  if (a.frames.length > 1) {
    const play = button("Play frames", () => {
      if (animation) { stopAnimation(); play.textContent = "Play frames"; }
      else { animation = setInterval(() => { frame = (frame + 1) % a.frames.length; loadPreview(); }, 200); play.textContent = "Pause"; }
    }); frameControls.append(play, el("span", "5 fps · preview timing", "fine")); pane.append(frameControls);
  }
  const strip = el("div", undefined, "frames");
  a.frames.forEach((f, i) => {
    const b = button("", () => { stopAnimation(); if (frameControls.firstChild) frameControls.firstChild.textContent = "Play frames"; frame = i; loadPreview(); }, "frame-button");
    b.setAttribute("aria-label", "Frame " + f.index); b.dataset.frame = i;
    if (f.exists) { const img = el("img"); img.src = f.url; img.alt = ""; img.loading = "lazy"; b.append(img); }
    b.append(document.createTextNode(f.index)); strip.append(b);
  }); pane.append(strip);
  const meta = el("div", undefined, "meta");
  const addMeta = (label, value) => { const item = el("div"); item.append(el("span", label), document.createTextNode(value)); meta.append(item); };
  addMeta("Dimensions", `${a.width} × ${a.height}`); addMeta("Resource frames", String(a.frames.length));
  if (a.origin) { addMeta("Origin (x, y)", a.origin.join(", ")); addMeta("Bounds L,T,R,B", a.bbox.join(", ")); }
  if (a.tile) addMeta("GMX tile size", `${a.tile.tilewidth} × ${a.tile.tileheight}`);
  pane.append(meta, el("p", a.kind === "sprite"
    ? "Bounds are GMX sprite metadata, not engine combat hitboxes. Animation may use several different sprite resources."
    : "Tile numbers use GMX dimensions, offset and spacing; not map GIDs. Runtime g.dm_tileset settings can differ. Click a tile to retain its coordinates in your brief.", "fine"));
  const sources = el("p", undefined, "fine"); sources.append(link("Open GMX", a.sourceUrl), document.createTextNode(" · "));
  const pngLink = link("Open current PNG", a.frames[0]?.url || a.sourceUrl); pngLink.id = "png-link"; sources.append(pngLink); pane.append(sources);
  const refs = el("details"); refs.append(el("summary", `${a.objects.length} object references · ${a.mentions.length} script mentions`));
  refs.append(el("p", "Text mentions include comments and inactive code; they do not establish runtime use.", "fine"));
  const list = el("ul", undefined, "references");
  for (const obj of a.objects) { const li = el("li"); li.append(link(obj.path + " (" + obj.field + ")", obj.url)); list.append(li); }
  for (const ref of a.mentions) { const li = el("li"); li.append(link(ref.path, ref.url), document.createTextNode(" · lines " + ref.lines.join(", "))); list.append(li); }
  refs.append(list); pane.append(refs); loadPreview(); renderCards();
  if (matchMedia("(max-width:700px)").matches) pane.scrollIntoView({behavior:"smooth", block:"start"});
}
function loadPreview() {
  const revision = ++previewRevision;
  const f = current.frames[frame]; previewImage = null;
  document.querySelectorAll(".frame-button").forEach(b => b.setAttribute("aria-pressed", String(Number(b.dataset.frame) === frame)));
  if (!f?.exists) { drawPreview(); return; }
  $("png-link").href = f.url;
  const img = new Image();
  img.onload = () => { if (revision === previewRevision) { previewImage = img; drawPreview(); } };
  img.onerror = () => { if (revision === previewRevision) { drawPreview(); $("tile-readout").textContent = "Image could not be loaded."; } };
  img.src = f.url;
}
function drawPreview() {
  const canvas = $("preview"); if (!canvas || !current) return;
  const a = current;
  const actualScale = Math.min(scale, 4096 / Math.max(a.width, a.height, 1));
  canvas.width = Math.max(1, Math.round(a.width * actualScale)); canvas.height = Math.max(1, Math.round(a.height * actualScale));
  const ctx = canvas.getContext("2d"); ctx.imageSmoothingEnabled = false;
  if (!previewImage) { ctx.fillStyle = "#e7eee7"; ctx.font = "12px sans-serif"; ctx.fillText("Image unavailable", 5, 18); return; }
  ctx.drawImage(previewImage, 0, 0, canvas.width, canvas.height);
  ctx.lineWidth = 1; ctx.strokeStyle = "#f6b785";
  if (a.bbox && showBounds) { const [l,t,r,b] = a.bbox; ctx.strokeRect(l*actualScale+.5,t*actualScale+.5,(r-l+1)*actualScale-1,(b-t+1)*actualScale-1); }
  if (a.origin && showOrigin) {
    const x = a.origin[0]*actualScale+.5, y = a.origin[1]*actualScale+.5;
    ctx.strokeStyle = "#d8ed92"; ctx.beginPath(); ctx.moveTo(x-8,y);ctx.lineTo(x+8,y);ctx.moveTo(x,y-8);ctx.lineTo(x,y+8);ctx.stroke();
  }
  if (a.tile && showGrid) {
    const t = a.tile, sx = t.tilewidth+t.tilehsep, sy = t.tileheight+t.tilevsep;
    if (t.tilewidth > 0 && t.tileheight > 0 && sx > 0 && sy > 0) {
      ctx.strokeStyle = "#d8ed9277";
      for (let y=t.tileyoff; y+t.tileheight<=a.height; y+=sy)
        for (let x=t.tilexoff; x+t.tilewidth<=a.width; x+=sx)
          ctx.strokeRect(x*actualScale+.5,y*actualScale+.5,t.tilewidth*actualScale-1,t.tileheight*actualScale-1);
    }
  }
}
function renderBrief() {
  const list = $("brief-assets"); list.replaceChildren();
  for (const name of selected) {
    const row = el("div", undefined, "brief-row"); row.append(el("span", name), button("Remove", () => { selected.delete(name); persist(); renderBrief(); if (current?.name === name) inspect(current); })); list.append(row);
  }
  if (!selected.size) list.append(el("p", "No assets selected yet. You can still download a blank brief.", "fine"));
}
function downloadBrief() {
  const lines = ["# " + ($("brief-title").value.trim() || "ZALiA content idea"), "", "## Desired change", "",
    $("brief-desired").value.trim() || "Describe the desired result and what should remain unchanged.", "", "## Reproduction context", "",
    "- Logical scene: " + ($("brief-scene").value || "unknown"), "- Tile filename: " + ($("brief-tile").value || "unknown"),
    "- Object / version: " + ($("brief-object").value || "unknown"), "- Quest / settings: " + ($("brief-settings").value || "unknown"),
    "- Commit / save conditions / player coordinates: record if relevant", "", "## Asset references", ""];
  for (const name of selected) {
    const a = byName.get(name); lines.push("### `" + name + "`", "", "- Resource: `" + a.path + "`",
      `- Source dimensions: ${a.width} x ${a.height}; resource frames: ${a.frames.length}`);
    if (tileNotes.has(name)) lines.push("- Inspection: " + tileNotes.get(name));
    lines.push("- PNG: `" + (a.frames[0]?.path || "missing") + "`", "");
  }
  if (!selected.size) lines.push("Add exact resource names or describe what to look for.", "");
  lines.push("## Images", "", ...(window.referenceFilename ? ["- Original image: `" + window.referenceFilename + "`", "- Annotated image: `annotated-reference.png` (download separately using the image button)", ""] : []), "Place your screenshots or sketch alongside this file. List their filenames here.",
    "Explain arrows, colors, scale, and which image shows current versus desired behavior.", "", "## Acceptance", "",
    "- [ ] Describe a visible, testable outcome.", "- [ ] Preserve the intended unchanged behavior.",
    "- [ ] Record runtime tests separately from static inspection.", "", "## Constraints", "",
    "Use the existing ZALiA GMS 1.4.9999 infrastructure and docs/codex cookbooks.",
    "Catalog images show source colors and frames, not a verified in-game appearance.", "");
  const url = URL.createObjectURL(new Blob([lines.join("\n")], {type:"text/markdown;charset=utf-8"}));
  const a = el("a"); a.href = url; a.download = "request.md"; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  toast("Reference brief downloaded");
}
for (const name of [...new Set(assets.map(a => a.group))].sort()) { const o = el("option", name); o.value = name; $("group").append(o); }
for (const id of ["search", "kind", "group", "unregistered"]) $(id).addEventListener("input", () => filter());
$("zoom").onchange = renderCards;
$("prev").onclick = () => { page--; renderCards(); };
$("next").onclick = () => { page++; renderCards(); };
$("open-brief").onclick = () => { renderBrief(); $("brief-dialog").showModal(); };
$("download").onclick = downloadBrief;
$("diagnostics-title").textContent = `Generator diagnostics · ${window.CATALOG.warnings.length} warnings`;
$("diagnostics-body").textContent = window.CATALOG.warnings.join("\n") || "No missing images or malformed resources found.";
window.addEventListener("hashchange", () => { try { const a = byName.get(decodeURIComponent(location.hash.slice(1))); if (a) inspect(a, false); } catch { } });
document.addEventListener("visibilitychange", () => { if (document.hidden && animation) { stopAnimation(); if (current) inspect(current, false); } });
persist(); filter();
try { const a = byName.get(decodeURIComponent(location.hash.slice(1))); if (a) inspect(a, false); } catch { }
