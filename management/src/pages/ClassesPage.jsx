import { useEffect, useState } from "react";
import Window, { EmptyState, Section } from "../components/Window.jsx";
import { ShieldIcon } from "../components/Icons.jsx";
import { scrollToDetails } from "../components/scrollToDetails.js";
import SpritePreview, { defaultClip } from "../components/SpritePreview.jsx";
import { NumberField, SaveBar, SelectField, TextField, changedFields } from "../components/Fields.jsx";
import { api, assetUrl } from "../api.js";

const EDITABLE = ["sheet", "avatar", "max_ap"];
const draftOf = (job) => Object.fromEntries(EDITABLE.map((key) => [key, job[key]]));

// Classes (jobs): the sprite sheet used in battle and on the profile, the battle card avatar and the AP
export default function ClassesPage({ jobs, setJobs, characters, options, sheets, notify }) {
  const [selectedName, setSelectedName] = useState(jobs[0]?.name ?? null);
  const selected = jobs.find((job) => job.name === selectedName) ?? null;

  return (
    <div className="page-grid">
      <Window icon={<ShieldIcon />} title="Classes" subtitle="Jobs the characters can have"
              actions={<span className="counter">{jobs.length}</span>}>
        <div className="card-grid">
          {jobs.map((job) => (
            <button key={job.name} type="button" className={`card ${job.name === selectedName ? "selected" : ""}`}
                    onClick={() => { setSelectedName(job.name); scrollToDetails(); }}>
              <div className="card-sprite tall">
                <SpritePreview sheet={sheets[`characters/${job.sheet}`]} clip="stand_s" />
              </div>
              <strong>{job.name}</strong>
              <span className="muted">{characters.filter((c) => c.job === job.name).length} characters</span>
            </button>
          ))}
        </div>
        <p className="note">New classes come with the job change system; for now they are added in seed_data.py.</p>
      </Window>

      {selected ? (
        <ClassDetails key={selected.name} job={selected} options={options} sheets={sheets} notify={notify}
                      onSaved={(saved) => setJobs((list) => list.map((j) => (j.name === saved.name ? saved : j)))} />
      ) : (
        <Window title="Class Details"><EmptyState>Select a class.</EmptyState></Window>
      )}
    </div>
  );
}

function ClassDetails({ job, options, sheets, notify, onSaved }) {
  const [draft, setDraft] = useState(() => draftOf(job));
  const [saving, setSaving] = useState(false);
  const [clip, setClip] = useState(null);
  useEffect(() => setDraft(draftOf(job)), [job]);

  const saved = draftOf(job);
  const changes = changedFields(saved, draft);
  const dirty = Object.keys(changes).length > 0;
  const set = (key) => (value) => setDraft((current) => ({ ...current, [key]: value }));
  const sheet = sheets[`characters/${draft.sheet}`];
  const shownClip = clip && sheet?.clips?.[clip] ? clip : defaultClip(sheet);

  async function save() {
    setSaving(true);
    try {
      const result = await api.updateJob(job.name, changes);
      onSaved(result);
      notify(`${result.name} saved.`);
    } catch (error) {
      notify(error.message, "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Window id="details" className="details" title="Class Details" subtitle={job.name}
            footer={<><span>Class {job.name}</span><span>RAGNAROK CHAOS SAGA</span></>}>
      <div className="details-hero">
        <div className="portrait large">
          <SpritePreview sheet={sheet} clip={shownClip} scale={1.4} />
        </div>
        <div className="hero-stats">
          <SelectField label="Sprite sheet" value={draft.sheet} onChange={(value) => { set("sheet")(value); setClip(null); }}
                       options={options.sheets.characters.map((name) => ({ value: name, label: name }))} />
          <SelectField label="Preview" value={shownClip ?? ""} onChange={setClip}
                       options={Object.keys(sheet?.clips ?? {}).map((name) => ({ value: name, label: name }))} />
        </div>
      </div>

      <Section title="Battle">
        <NumberField label="Max AP" hint="action points per turn" value={draft.max_ap} onChange={set("max_ap")} />
        <TextField label="Avatar" hint="path under assets/" value={draft.avatar} onChange={set("avatar")} />
        {draft.avatar && (
          <div className="avatar-preview">
            <img src={assetUrl(draft.avatar)} alt="" />
            <span className="muted">Shown on the battle unit card</span>
          </div>
        )}
      </Section>

      <SaveBar dirty={dirty} saving={saving} onSave={save} onReset={() => setDraft(saved)} />
    </Window>
  );
}
