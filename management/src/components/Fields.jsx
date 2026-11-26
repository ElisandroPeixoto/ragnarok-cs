// Small form controls laid out as "label ... value" rows, like the stats in the game's item details window.

export function FieldRow({ label, hint, children }) {
  return (
    <label className="field-row">
      <span className="field-label">
        {label}
        {hint && <small className="field-hint">{hint}</small>}
      </span>
      <span className="field-control">{children}</span>
    </label>
  );
}

export function NumberField({ label, hint, value, onChange, min = 0, max, step = 1 }) {
  return (
    <FieldRow label={label} hint={hint}>
      <input
        type="number"
        value={value ?? ""}
        min={min}
        max={max}
        step={step}
        onChange={(event) => onChange(event.target.value === "" ? "" : Number(event.target.value))}
      />
    </FieldRow>
  );
}

export function TextField({ label, hint, value, onChange }) {
  return (
    <FieldRow label={label} hint={hint}>
      <input type="text" value={value ?? ""} onChange={(event) => onChange(event.target.value)} />
    </FieldRow>
  );
}

export function SelectField({ label, hint, value, onChange, options }) {
  return (
    <FieldRow label={label} hint={hint}>
      <select value={value ?? ""} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </FieldRow>
  );
}

export function StatRow({ label, value }) {
  return (
    <div className="stat-row">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

// Save / discard bar shown under a form while it has unsaved changes
export function SaveBar({ dirty, saving, onSave, onReset }) {
  return (
    <div className="save-bar">
      <span className={dirty ? "save-status dirty" : "save-status"}>{dirty ? "Unsaved changes" : "All saved"}</span>
      <button type="button" className="button ghost" disabled={!dirty || saving} onClick={onReset}>
        Discard
      </button>
      <button type="button" className="button primary" disabled={!dirty || saving} onClick={onSave}>
        {saving ? "Saving…" : "Save"}
      </button>
    </div>
  );
}

// Only the fields that differ from the saved record, so a PATCH sends just the edits
export function changedFields(saved, draft) {
  const changes = {};
  for (const [key, value] of Object.entries(draft)) {
    if (JSON.stringify(value) !== JSON.stringify(saved[key])) changes[key] = value;
  }
  return changes;
}
