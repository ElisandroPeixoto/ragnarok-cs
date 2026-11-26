// A panel in the style of the game's windows: light header with icon, title, a small caps subtitle and
// optional controls on the right; white body; optional footer.
export default function Window({ icon, title, subtitle, actions, footer, className = "", children }) {
  return (
    <section className={`window ${className}`}>
      <header className="window-header">
        {icon && <img className="window-icon" src={icon} alt="" />}
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
