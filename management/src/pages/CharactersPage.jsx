import { useEffect, useMemo, useState } from "react";
import Window, { EmptyState, Section } from "../components/Window.jsx";
import { UsersIcon } from "../components/Icons.jsx";
import { scrollToDetails } from "../components/scrollToDetails.js";
import SpritePreview, { defaultClip } from "../components/SpritePreview.jsx";
import { NumberField, SaveBar, SelectField, StatRow, TextField, changedFields } from "../components/Fields.jsx";
import { api } from "../api.js";

const EDITABLE = ["name", "job", "level", "zeny", "hp", "max_hp", "max_sp", "current_map_id"];

function draftOf(character) {
  const draft = Object.fromEntries(EDITABLE.map((key) => [key, character[key]]));
  draft.zeny = Number(character.zeny);   // the API sends zeny as a decimal string
  return draft;
}

// Characters: the list on the left, the selected character's sheet on the right
export default function CharactersPage({ characters, setCharacters, options, sheets, jobs, notify }) {
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(characters[0]?.id ?? null);
  const visible = useMemo(() => {
    const text = query.trim().toLowerCase();
    return characters.filter((character) =>
      !text || character.name.toLowerCase().includes(text) || character.job.toLowerCase().includes(text));
  }, [characters, query]);
  const selected = characters.find((character) => character.id === selectedId) ?? null;

  return (
    <div className="page-grid">
      <Window icon={<UsersIcon />} title="Characters" subtitle="Every character in the game"
              actions={<span className="counter">{characters.length}</span>}>
        <div className="search">
          <input placeholder="Search by name or class…" value={query} onChange={(e) => setQuery(e.target.value)} />
        </div>
        <p className="note">Accounts are not in the game yet; every character is listed here.</p>
        <table className="table">
          <thead>
            <tr><th>Name</th><th>Class</th><th>Level</th><th>Zeny</th><th>Map</th></tr>
          </thead>
          <tbody>
            {visible.map((character) => (
              <tr key={character.id} className={character.id === selectedId ? "selected" : ""}
                  onClick={() => { setSelectedId(character.id); scrollToDetails(); }}>
                <td><strong>{character.name}</strong><span className="muted"> #{character.id}</span></td>
                <td>{character.job}</td>
                <td>{character.level}</td>
                <td>{Number(character.zeny).toLocaleString()}z</td>
                <td>{character.current_map}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {visible.length === 0 && <EmptyState>No character matches the search.</EmptyState>}
      </Window>

      {selected ? (
        <CharacterDetails key={selected.id} character={selected} options={options} sheets={sheets} jobs={jobs}
                          notify={notify}
                          onSaved={(saved) => setCharacters((list) => list.map((c) => (c.id === saved.id ? saved : c)))} />
      ) : (
        <Window title="Character Details"><EmptyState>Select a character.</EmptyState></Window>
      )}
    </div>
  );
}

function CharacterDetails({ character, options, sheets, jobs, notify, onSaved }) {
  const [draft, setDraft] = useState(() => draftOf(character));
  const [saving, setSaving] = useState(false);
  useEffect(() => setDraft(draftOf(character)), [character]);

  const saved = draftOf(character);
  const changes = changedFields(saved, draft);
  const dirty = Object.keys(changes).length > 0;
  const set = (key) => (value) => setDraft((current) => ({ ...current, [key]: value }));
  const job = jobs.find((entry) => entry.name === draft.job);
  const sheet = job ? sheets[`characters/${job.sheet}`] : null;

  async function save() {
    setSaving(true);
    try {
      const result = await api.updateCharacter(character.id, changes);
      onSaved(result);
      notify(`${result.name} saved.`);
    } catch (error) {
      notify(error.message, "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Window id="details" className="details" title="Character Details" subtitle={`Character #${character.id}`}
            footer={<><span>Total EXP {character.exp.toLocaleString()}</span><span>RAGNAROK CHAOS SAGA</span></>}>
      <div className="details-hero">
        <div className="portrait">
          <SpritePreview sheet={sheet} clip={defaultClip(sheet)} scale={1.4} />
        </div>
        <div className="hero-stats">
          <StatRow label="Level" value={character.level} />
          <StatRow label="EXP in level" value={`${character.exp_progress} / ${character.exp_needed || "MAX"}`} />
          <StatRow label="HP" value={`${character.hp} / ${character.max_hp}`} />
          <StatRow label="Map" value={character.current_map} />
        </div>
      </div>

      <Section title="Identity">
        <TextField label="Name" value={draft.name} onChange={set("name")} />
        <SelectField label="Class" value={draft.job} onChange={set("job")}
                     options={options.jobs.map((name) => ({ value: name, label: name }))} />
        <SelectField label="Map" value={draft.current_map_id} onChange={set("current_map_id")}
                     options={options.maps.map((map) => ({ value: map.id, label: map.name }))} />
      </Section>

      <Section title="Progress">
        <NumberField label="Level" hint="sets the EXP to the start of the level" min={1} max={99}
                     value={draft.level} onChange={set("level")} />
        <NumberField label="Zeny" value={draft.zeny} onChange={set("zeny")} />
      </Section>

      <Section title="Status">
        <NumberField label="HP" hint="capped at Max HP" value={draft.hp} onChange={set("hp")} />
        <NumberField label="Max HP" min={1} value={draft.max_hp} onChange={set("max_hp")} />
        <NumberField label="Max SP" value={draft.max_sp} onChange={set("max_sp")} />
      </Section>

      <SaveBar dirty={dirty} saving={saving} onSave={save} onReset={() => setDraft(saved)} />
    </Window>
  );
}
