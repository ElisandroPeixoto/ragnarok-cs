import { useState } from "react";
import Window, { EmptyState, Section } from "../components/Window.jsx";
import SpritePreview, { defaultClip } from "../components/SpritePreview.jsx";
import { FieldRow, SelectField, StatRow } from "../components/Fields.jsx";
import { api, assetUrl } from "../api.js";

const GROUP_LABELS = { characters: "Classes", monsters: "Monsters" };

// Sprite sheets on disk (assets/sprites/<group>/<name>/), every clip playable, and an upload form for sheets made
// with tools/ro_to_sheet.py. Which sheet a monster or class uses is chosen on the Monsters and Classes pages.
export default function SpritesPage({ spriteList, onUploaded, monsters, jobs, notify }) {
  const [selectedKey, setSelectedKey] = useState(spriteList[0] ? `${spriteList[0].group}/${spriteList[0].name}` : null);
  const selected = spriteList.find((entry) => `${entry.group}/${entry.name}` === selectedKey) ?? null;

  const usedBy = (entry) => (entry.group === "monsters"
    ? monsters.filter((monster) => monster.sheet === entry.name).map((monster) => monster.name)
    : jobs.filter((job) => job.sheet === entry.name).map((job) => job.name));

  return (
    <div className="page-grid">
      <Window icon="/assets/icons/wiki.png" title="Sprite Sheets" subtitle="assets/sprites"
              actions={<span className="counter">{spriteList.length}</span>}>
        {Object.entries(GROUP_LABELS).map(([group, label]) => (
          <div key={group} className="group">
            <h3 className="section-title">{label}</h3>
            <div className="card-grid">
              {spriteList.filter((entry) => entry.group === group).map((entry) => {
                const key = `${entry.group}/${entry.name}`;
                return (
                  <button key={key} type="button" className={`card ${key === selectedKey ? "selected" : ""}`}
                          onClick={() => setSelectedKey(key)}>
                    <div className={`card-sprite ${group === "characters" ? "tall" : ""}`}>
                      <SpritePreview sheet={entry.json} clip={defaultClip(entry.json)} />
                    </div>
                    <strong>{entry.name}</strong>
                    <span className="muted">{usedBy(entry).join(", ") || "not in use"}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
        <UploadForm notify={notify} onUploaded={(entry) => { onUploaded(entry); setSelectedKey(`${entry.group}/${entry.name}`); }} />
      </Window>

      {selected ? (
        <SheetDetails key={selectedKey} entry={selected} usedBy={usedBy(selected)} />
      ) : (
        <Window title="Sheet Details"><EmptyState>Select a sprite sheet.</EmptyState></Window>
      )}
    </div>
  );
}

function SheetDetails({ entry, usedBy }) {
  const sheet = entry.json;
  const [clip, setClip] = useState(defaultClip(sheet));
  const clipData = sheet.clips[clip];
  return (
    <Window className="details" title="Sheet Details" subtitle={`${GROUP_LABELS[entry.group]} · ${entry.name}`}
            footer={<><span>{sheet.src}</span><span>RAGNAROK CHAOS SAGA</span></>}>
      <div className="details-hero">
        <div className="portrait large">
          <SpritePreview sheet={sheet} clip={clip} scale={1.6} />
        </div>
        <div className="hero-stats">
          <SelectField label="Clip" value={clip} onChange={setClip}
                       options={Object.keys(sheet.clips).map((name) => ({ value: name, label: name }))} />
          <StatRow label="Frames" value={`${clipData.frames} @ ${clipData.fps} fps`} />
          <StatRow label="Loop" value={clipData.loop === false ? "no" : "yes"} />
        </div>
      </div>
      <Section title="Sheet">
        <StatRow label="Frame size" value={`${sheet.frame_w} × ${sheet.frame_h}`} />
        <StatRow label="Grid" value={`${sheet.cols} × ${sheet.rows}`} />
        <StatRow label="Anchor (feet)" value={`${sheet.anchor_x}, ${sheet.anchor_y}`} />
        <StatRow label="Clips" value={Object.keys(sheet.clips).length} />
        <StatRow label="Used by" value={usedBy.join(", ") || "—"} />
      </Section>
      <Section title="Full sheet">
        <div className="sheet-image">
          <img className="pixel" src={assetUrl(sheet.src)} alt={`${entry.name} sheet`} />
        </div>
      </Section>
    </Window>
  );
}

function readFile(file, asDataUrl) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error);
    if (asDataUrl) reader.readAsDataURL(file); else reader.readAsText(file);
  });
}

// Upload of a sheet made with tools/ro_to_sheet.py: <name>_sheet.png + <name>.json. Same name = replace
function UploadForm({ notify, onUploaded }) {
  const [group, setGroup] = useState("monsters");
  const [name, setName] = useState("");
  const [png, setPng] = useState(null);
  const [json, setJson] = useState(null);
  const [busy, setBusy] = useState(false);

  async function upload(event) {
    event.preventDefault();
    if (!name || !png || !json) {
      notify("Fill in the name and pick the PNG and the JSON.", "error");
      return;
    }
    setBusy(true);
    try {
      const dataUrl = await readFile(png, true);
      const sheetJson = JSON.parse(await readFile(json, false));
      const result = await api.uploadSprite(group, name, dataUrl.split(",")[1], sheetJson);
      onUploaded(result);
      notify(`Sheet ${group}/${name} uploaded.`);
      setName(""); setPng(null); setJson(null);
      event.target.reset();
    } catch (error) {
      notify(error instanceof SyntaxError ? "The JSON file is not valid JSON." : error.message, "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="upload" onSubmit={upload}>
      <h3 className="section-title">Upload a sheet</h3>
      <p className="note">Files made by tools/ro_to_sheet.py. Using an existing name replaces that sheet.</p>
      <SelectField label="Group" value={group} onChange={setGroup}
                   options={[{ value: "monsters", label: "Monsters" }, { value: "characters", label: "Classes" }]} />
      <FieldRow label="Name" hint="lowercase, digits and _">
        <input type="text" value={name} placeholder="e.g. fabre"
               onChange={(event) => setName(event.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ""))} />
      </FieldRow>
      <FieldRow label="Sheet PNG">
        <input type="file" accept="image/png" onChange={(event) => setPng(event.target.files[0] ?? null)} />
      </FieldRow>
      <FieldRow label="Sheet JSON">
        <input type="file" accept="application/json,.json" onChange={(event) => setJson(event.target.files[0] ?? null)} />
      </FieldRow>
      <div className="upload-actions">
        <button type="submit" className="button primary" disabled={busy}>{busy ? "Uploading…" : "Upload"}</button>
      </div>
    </form>
  );
}
