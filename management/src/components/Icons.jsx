// Simple line icons (24x24, stroke = currentColor) for the menu and the window headers.
function Icon({ size = 20, children, ...props }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
         strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>
      {children}
    </svg>
  );
}

// Characters: a person
export const UsersIcon = (props) => (
  <Icon {...props}>
    <circle cx="9" cy="8" r="3.5" />
    <path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6" />
    <path d="M16 4.6a3.5 3.5 0 0 1 0 6.8" />
    <path d="M18 14.3c2.1.7 3.5 2.8 3.5 5.7" />
  </Icon>
);

// Monsters: a ghost-like blob
export const MonsterIcon = (props) => (
  <Icon {...props}>
    <path d="M5 20V11a7 7 0 0 1 14 0v9l-2.3-1.6L14.3 20 12 18.4 9.7 20l-2.4-1.6Z" />
    <circle cx="9.5" cy="11" r="1" fill="currentColor" />
    <circle cx="14.5" cy="11" r="1" fill="currentColor" />
  </Icon>
);

// Classes: a shield
export const ShieldIcon = (props) => (
  <Icon {...props}>
    <path d="M12 3 4.5 6v5.5c0 4.6 3.2 8 7.5 9.5 4.3-1.5 7.5-4.9 7.5-9.5V6Z" />
    <path d="m9 12 2 2 4-4" />
  </Icon>
);

// Items & Drops: a box
export const BoxIcon = (props) => (
  <Icon {...props}>
    <path d="M3.5 7.5 12 3l8.5 4.5v9L12 21l-8.5-4.5Z" />
    <path d="M3.5 7.5 12 12l8.5-4.5" />
    <path d="M12 12v9" />
  </Icon>
);

// Sprite sheets: a picture
export const ImageIcon = (props) => (
  <Icon {...props}>
    <rect x="3" y="4" width="18" height="16" rx="2.5" />
    <circle cx="9" cy="9.5" r="1.8" />
    <path d="m4 18 5.5-5.5 4 4 2.5-2.5 4 4" />
  </Icon>
);

// Management (menu window): a gear
export const GearIcon = (props) => (
  <Icon {...props}>
    <circle cx="12" cy="12" r="3" />
    <path d="M12 2.8v2.4M12 18.8v2.4M2.8 12h2.4M18.8 12h2.4M5.5 5.5l1.7 1.7M16.8 16.8l1.7 1.7M5.5 18.5l1.7-1.7M16.8 7.2l1.7-1.7" />
  </Icon>
);

export const ReloadIcon = (props) => (
  <Icon {...props}>
    <path d="M20 11a8 8 0 1 0-2.3 5.7" />
    <path d="M20 4v7h-7" />
  </Icon>
);
