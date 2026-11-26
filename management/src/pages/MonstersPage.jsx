import { useEffect, useState } from "react";
import Window, { EmptyState, Section } from "../components/Window.jsx";
import { MonsterIcon } from "../components/Icons.jsx";
import { scrollToDetails } from "../components/scrollToDetails.js";
import SpritePreview, { defaultClip } from "../components/SpritePreview.jsx";
import { NumberField, SaveBar, SelectField, changedFields } from "../components/Fields.jsx";
import { api, assetUrl } from "../api.js";

const EDITABLE = ["sheet", "ai", "level", "base_exp", "max_hp", "max_ap", "drops"];
const draftOf = (monster) => Object.fromEntries(EDITABLE.map((key) => [key, monster[key]]));

// Monsters: a grid of animated slots; the details panel edits the sheet, the combat mode, the stats and the drops
export default function MonstersPage({ monsters, setMonsters, items, setItems, options, sheets, notify }) {
  const [selectedId, setSelectedId] = useState(monsters[0]?.id ?? null);
  const selected = monsters.find((monster) => monster.id === selectedId) ?? null;
  const aiLabel = (id) => options.ai_modes.find((mode) => mode.id === id)?.label ?? id;

  return (
    <div className="page-grid">
      <Window icon={<MonsterIcon />} title="Monsters" subtitle="Battle data, combat mode and drops"
              actions={<span className="counter">{monsters.length}</span>}>
        <div className="card-grid">
          {monsters.map((monster) => (
            <button key={monster.id} type="button"
                    className={`card ${monster.id === selectedId ? "selected" : ""}`}
                    onClick={() => { setSelectedId(monster.id); scrollToDetails(); }}>
              <div className="card-sprite">
                <SpritePreview sheet={sheets[`monsters/${monster.sheet}`]} clip="idle_sw" />
              </div>
              <strong>{monster.name}</strong>
              <span className="muted">Lv {monster.level} · {aiLabel(monster.ai)}</span>
              <span className="tag">{monster.drops.length} drops</span>
            </button>
          ))}
        </div>
      </Window>

      {selected ? (
        <MonsterDetails key={selected.id} monster={selected} items={items} options={options} sheets={sheets}
                        notify={notify}
                        onSaved={(saved) => {
                          setMonsters((list) => list.map((m) => (m.id === saved.id ? saved : m)));
                          // "dropped by" on the items page follows the new drop list
                          api.items().then(setItems).catch(() => {});
                        }} />
      ) : (
        <Window title="Monster Details"><EmptyState>Select a monster.</EmptyState></Window>
      )}
    </div>
  );
}

function MonsterDetails({ monster, items, options, sheets, notify, onSaved }) {
  const [draft, setDraft] = useState(() => draftOf(monster));
  const [saving, setSaving] = useState(false);
  const [clip, setClip] = useState(null);
  const [newDrop, setNewDrop] = useState("");
  useEffect(() => setDraft(draftOf(monster)), [monster]);

  const saved = draftOf(monster);
  const changes = changedFields(saved, draft);
  const dirty = Object.keys(changes).length > 0;
  const set = (key) => (value) => setDraft((current) => ({ ...current, [key]: value }));
  const sheet = sheets[`monsters/${draft.sheet}`];
  const shownClip = clip && sheet?.clips?.[clip] ? clip : defaultClip(sheet);
  const mode = options.ai_modes.find((entry) => entry.id === draft.ai);
  const itemById = Object.fromEntries(items.map((item) => [item.id, item]));
  const addable = items.filter((item) => !draft.drops.includes(item.id));

  async function save() {
    setSaving(true);
    try {
      const result = await api.updateMonster(monster.id, changes);
      onSaved(result);
      notify(`${result.name} saved.`);
    } catch (error) {
      notify(error.message, "error");
    } finally {
      setSaving(false);
    }
  }

  function addDrop() {
    const itemId = newDrop || addable[0]?.id;
    if (itemId) set("drops")([...draft.drops, itemId].sort());
    setNewDrop("");
  }

  return (
    <Window id="details" className="details" title="Monster Details" subtitle={monster.name}
            footer={<><span>Monster ID {monster.id}</span><span>RAGNAROK CHAOS SAGA</span></>}>
      <div className="details-hero">
        <div className="portrait large">
          <SpritePreview sheet={sheet} clip={shownClip} scale={1.6} />
        </div>
        <div className="hero-stats">
          <SelectField label="Sprite sheet" value={draft.sheet} onChange={(value) => { set("sheet")(value); setClip(null); }}
                       options={options.sheets.monsters.map((name) => ({ value: name, label: name }))} />
          <SelectField label="Preview" value={shownClip ?? ""} onChange={setClip}
                       options={Object.keys(sheet?.clips ?? {}).map((name) => ({ value: name, label: name }))} />
        </div>
      </div>

      <Section title="Combat mode">
        <div className="mode-list">
          {options.ai_modes.map((entry) => (
            <label key={entry.id} className={`mode ${draft.ai === entry.id ? "active" : ""}`}>
              <input type="radio" name="ai" value={entry.id} checked={draft.ai === entry.id}
                     onChange={() => set("ai")(entry.id)} />
              <span>
                <strong>{entry.label}</strong>
                <small>{entry.description}</small>
              </span>
            </label>
          ))}
        </div>
        {!mode && <p className="note warning">Unknown mode "{draft.ai}": pick one of the list.</p>}
      </Section>

      <Section title="Stats">
        <NumberField label="Level" min={1} value={draft.level} onChange={set("level")} />
        <NumberField label="Base EXP" hint="EXP for a kill at a similar level" value={draft.base_exp} onChange={set("base_exp")} />
        <NumberField label="Max HP" min={1} value={draft.max_hp} onChange={set("max_hp")} />
        <NumberField label="Max AP" value={draft.max_ap} onChange={set("max_ap")} />
      </Section>

      <Section title="Drops">
        {draft.drops.length === 0 && <p className="note">This monster drops nothing.</p>}
        <ul className="drop-list">
          {draft.drops.map((itemId) => {
            const item = itemById[itemId];
            return (
              <li key={itemId}>
                {item?.icon && <img className="pixel" src={assetUrl(item.icon)} alt="" />}
                <span className="drop-name">{item?.name ?? itemId}</span>
                <span className="tag">{item ? `${item.drop_rate}%` : "?"}</span>
                <button type="button" className="icon-button" title="Remove drop"
                        onClick={() => set("drops")(draft.drops.filter((id) => id !== itemId))}>×</button>
              </li>
            );
          })}
        </ul>
        {addable.length > 0 && (
          <div className="add-row">
            <select value={newDrop || addable[0].id} onChange={(event) => setNewDrop(event.target.value)}>
              {addable.map((item) => <option key={item.id} value={item.id}>{item.name} ({item.drop_rate}%)</option>)}
            </select>
            <button type="button" className="button" onClick={addDrop}>Add drop</button>
          </div>
        )}
        <p className="note">The drop rate belongs to the item: change it on the Items page.</p>
      </Section>

      <SaveBar dirty={dirty} saving={saving} onSave={save} onReset={() => setDraft(saved)} />
    </Window>
  );
}
