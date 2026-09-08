"use strict";
// Local reference annotation only; independent of game resources and runtime.
(() => {
  const canvas = document.getElementById("reference-canvas"), ctx = canvas.getContext("2d");
  const input = document.getElementById("reference-image");
  const status = document.getElementById("image-status");
  const undo = document.getElementById("undo-mark"), exportButton = document.getElementById("export-image");
  let source = null, marks = [], draft = null, revision = 0;
  function drawMark(context, mark, unit) {
    context.strokeStyle = mark.color; context.fillStyle = mark.color;
    context.lineWidth = unit; context.lineCap = "round";
    if (mark.tool === "text") {
      context.font = `bold ${Math.max(16, unit * 6)}px sans-serif`;
      context.strokeStyle = "#111"; context.lineWidth = unit * 1.5;
      context.strokeText(mark.text, mark.x, mark.y); context.fillText(mark.text, mark.x, mark.y); return;
    }
    if (mark.tool === "box") { context.strokeRect(mark.x,mark.y,mark.endX-mark.x,mark.endY-mark.y); return; }
    const angle = Math.atan2(mark.endY-mark.y,mark.endX-mark.x), head = unit*5;
    context.beginPath(); context.moveTo(mark.x,mark.y); context.lineTo(mark.endX,mark.endY);
    context.moveTo(mark.endX-head*Math.cos(angle-.5),mark.endY-head*Math.sin(angle-.5));
    context.lineTo(mark.endX,mark.endY); context.lineTo(mark.endX-head*Math.cos(angle+.5),mark.endY-head*Math.sin(angle+.5)); context.stroke();
  }
  function draw() {
    if (!source) return;
    ctx.clearRect(0,0,canvas.width,canvas.height); ctx.drawImage(source,0,0);
    const unit = Math.max(2, canvas.width / 350);
    for (const mark of marks) drawMark(ctx,mark,unit);
    if (draft) drawMark(ctx,draft,unit);
    undo.disabled = !marks.length;
  }
  input.onchange = () => {
    const file = input.files[0]; if (!file) return;
    const id = ++revision;
    if (!/^image\/(png|jpeg|webp)$/.test(file.type)) { status.textContent = "Use a PNG, JPEG or WebP image."; return; }
    const url = URL.createObjectURL(file), image = new Image();
    image.onload = () => {
      URL.revokeObjectURL(url); if (id !== revision) return;
      if (image.width*image.height > 20000000) { status.textContent = "Image exceeds 20 megapixels. Resize it first."; return; }
      source = image; marks = []; draft = null;
      canvas.width = image.width; canvas.height = image.height; canvas.hidden = false;
      window.referenceFilename = file.name;
      status.textContent = `${file.name} · ${image.width} × ${image.height}. PNG export includes the context entered above.`;
      exportButton.disabled = false; draw();
    };
    image.onerror = () => { URL.revokeObjectURL(url); if (id === revision) status.textContent = "Could not read this image."; };
    image.src = url;
  };
  function point(event) {
    const rect = canvas.getBoundingClientRect();
    return {x: Math.max(0,Math.min(canvas.width,(event.clientX-rect.left)*canvas.width/rect.width)),
            y: Math.max(0,Math.min(canvas.height,(event.clientY-rect.top)*canvas.height/rect.height))};
  }
  canvas.onpointerdown = event => {
    if (!source || event.button !== 0) return;
    const p = point(event), tool = document.getElementById("mark-tool").value;
    const mark = {...p, endX:p.x, endY:p.y, tool, color:document.getElementById("mark-color").value,
                  text:document.getElementById("mark-label").value};
    if (tool === "text") { if (mark.text.trim()) { marks.push(mark); draw(); } else status.textContent = "Enter a text label before placing it."; return; }
    draft = mark; canvas.setPointerCapture(event.pointerId);
  };
  canvas.onpointermove = event => { if (draft) { const p=point(event); draft.endX=p.x;draft.endY=p.y;draw(); } };
  canvas.onpointerup = event => {
    if (!draft) return;
    const p=point(event); draft.endX=p.x;draft.endY=p.y;
    if (Math.hypot(draft.endX-draft.x,draft.endY-draft.y)>2) marks.push(draft);
    draft=null; canvas.releasePointerCapture(event.pointerId);draw();
  };
  canvas.onpointercancel = () => { draft=null;draw(); };
  undo.onclick = () => { marks.pop();draw(); };
  exportButton.onclick = () => {
    if (!source) return;
    const output = document.createElement("canvas");
    // A minimum footer width keeps labels readable even for tiny source sprites.
    output.width = Math.max(canvas.width,640); output.height = canvas.height+112;
    const c=output.getContext("2d"); c.fillStyle="#101a1c";c.fillRect(0,0,output.width,output.height);
    draw();c.drawImage(canvas,0,0); c.font="14px sans-serif";c.fillStyle="#e7eee7";
    const value = id => document.getElementById(id).value.trim() || "unknown";
    const rows=["ZALiA reference · " + value("brief-title"),
      "Scene: " + value("brief-scene") + " | Tile file: " + value("brief-tile"),
      "Object/version: " + value("brief-object"), "Quest/settings: " + value("brief-settings")];
    rows.forEach((text,i) => {
      while (c.measureText(text).width > output.width-24 && text.length > 1) text=text.slice(0,-2)+"…";
      c.fillText(text,12,canvas.height+24+i*24);
    });
    output.toBlob(blob => {
      if (!blob) return;
      const url=URL.createObjectURL(blob), a=document.createElement("a");
      a.href=url;a.download="annotated-reference.png";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
      status.textContent="Annotated PNG downloaded. Download request.md too, and keep them together.";
    },"image/png");
  };
})();
