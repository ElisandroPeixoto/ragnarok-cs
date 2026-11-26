// A panel in the style of the game's windows: light header with icon, title, a small caps subtitle and
// optional controls on the right; white body; optional footer. `icon` is an image path (e.g. an item icon)
// or an SVG element from components/Icons.jsx.
export default function Window({ icon, title, subtitle, actions, footer, className = "", id, children }) {
  return (
    <section className={`window ${className}`} id={id}>
      <header className="window-header">
        {icon && (typeof icon === "string"
          ? <img className="window-icon" src={icon} alt="" />
          : <span className="window-icon svg">{icon}</span>)}
        <div className="window-titles">
          <h2>{title}</h2>
          {subtitle && <span className="window-subtitle">{subtitle}</span>}
        </div>
        {actions && <div className="window-actions">{actions}</div>}
      </header>
      <div className="window-body">{children}</div>
      {footer && <footer className="window-footer">{footer}</footer>}
    </section>
  );
}

export function Section({ title, children }) {
  return (
    <div className="section">
      {title && <h3 className="section-title">{title}</h3>}
      {children}
    </div>
  );
}

export function EmptyState({ children }) {
  return <div className="empty-state">{children}</div>;
}
