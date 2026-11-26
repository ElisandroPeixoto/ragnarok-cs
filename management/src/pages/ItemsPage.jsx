import { useEffect, useMemo, useState } from "react";
import Window, { EmptyState, Section } from "../components/Window.jsx";
import { BoxIcon } from "../components/Icons.jsx";
import { scrollToDetails } from "../components/scrollToDetails.js";
import { NumberField, SaveBar, SelectField, StatRow, TextField, changedFields } from "../components/Fields.jsx";
import { api, assetUrl } from "../api.js";

const EDITABLE = ["name", "type", "description", "drop_rate"];
const draftOf = (item) => Object.fromEntries(EDITABLE.map((key) => [key, item[key]]));
const SLOTS = 40;   // the grid always shows at least a full bag, like the game's inventory

// Items: an inventory-like grid of icons; the details panel shows the collection picture and edits the item,
// including its drop rate (the chance, in percent, that a monster which drops it leaves it)
export default function ItemsPage({ items, setItems, options, notify }) {
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(items[0]?.id ?? null);
  const visible = useMemo(() => {
    const text = query.trim().toLowerCase();
    return items.filter((item) => !text || item.name.toLowerCase().includes(text));
  }, [items, query]);
  const selected = items.find((item) => item.id === selectedId) ?? null;
  const empty = Math.max(0, SLOTS - visible.length);

  return (
    <div className="page-grid">
      <Window icon={<BoxIcon />} title="Items" subtitle="Item catalogue and drop rates"
              actions={<span className="counter">{items.length}</span>}>
        <div className="search">
          <input placeholder="Search items…" value={query} onChange={(event) => setQuery(event.target.value)} />
        </div>
        <div className="slot-grid">
          {visible.map((item) => (
            <button key={item.id} type="button" title={`${item.name} (${item.drop_rate}%)`}
                    className={`slot ${item.id === selectedId ? "selected" : ""}`}
                    onClick={() => { setSelectedId(item.id); scrollToDetails(); }}>
              {item.icon ? <img className="pixel" src={assetUrl(item.icon)} alt={item.name} /> : <span>?</span>}
              <span className="slot-badge">{item.drop_rate}%</span>
            </button>
          ))}
          {Array.from({ length: empty }, (_, index) => <div key={`empty-${index}`} className="slot empty" />)}
        </div>
      </Window>

      {selected ? (
        <ItemDetails key={selected.id} item={selected} itemTypes={options.item_types} notify={notify}
                     onSaved={(saved) => setItems((list) => list.map((i) => (i.id === saved.id ? saved : i)))} />
      ) : (
        <Window title="Item Details"><EmptyState>Select an item.</EmptyState></Window>
      )}
    </div>
  );
}

function ItemDetails({ item, itemTypes, notify, onSaved }) {
  const [draft, setDraft] = useState(() => draftOf(item));
  const [saving, setSaving] = useState(false);
  useEffect(() => setDraft(draftOf(item)), [item]);

  const saved = draftOf(item);
  const changes = changedFields(saved, draft);
  const dirty = Object.keys(changes).length > 0;
  const set = (key) => (value) => setDraft((current) => ({ ...current, [key]: value }));

  async function save() {
    setSaving(true);
    try {
      const result = await api.updateItem(item.id, changes);
      onSaved(result);
      notify(`${result.name} saved.`);
    } catch (error) {
      notify(error.message, "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Window id="details" className="details" icon={assetUrl(item.icon)} title="Item Details" subtitle={item.name}
            footer={<><span>Item ID {item.id}</span><span>RAGNAROK CHAOS SAGA</span></>}>
      <div className="details-hero">
        <div className="portrait collection">
          {item.collection ? <img className="pixel" src={assetUrl(item.collection)} alt="" /> : <span>no picture</span>}
        </div>
        <div className="hero-stats">
          <StatRow label="Type" value={item.type} />
          <StatRow label="Drop rate" value={`${item.drop_rate}%`} />
          <StatRow label="Dropped by" value={item.dropped_by.length || "—"} />
        </div>
      </div>

      <Section>
        <p className="description">{item.description}</p>
      </Section>

      <Section title="Drop">
        <NumberField label="Drop rate (%)" hint="0 to 100; cards use 0.2" min={0} max={100} step={0.1}
                     value={draft.drop_rate} onChange={set("drop_rate")} />
        {item.dropped_by.length > 0 ? (
          <div className="chips">
            {item.dropped_by.map((name) => <span key={name} className="chip">{name}</span>)}
          </div>
        ) : (
          <p className="note">No monster drops this item. Add it to a monster on the Monsters page.</p>
        )}
      </Section>

      <Section title="Item">
        <TextField label="Name" value={draft.name} onChange={set("name")} />
        <SelectField label="Type" value={draft.type} onChange={set("type")}
                     options={itemTypes.map((type) => ({ value: type, label: type }))} />
        <label className="field-block">
          <span className="field-label">Description</span>
          <textarea rows={3} value={draft.description} onChange={(event) => set("description")(event.target.value)} />
        </label>
      </Section>

      <SaveBar dirty={dirty} saving={saving} onSave={save} onReset={() => setDraft(saved)} />
    </Window>
  );
}
