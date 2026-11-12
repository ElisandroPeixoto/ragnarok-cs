import flet as ft


# BACKGROUND
BACKGROUND_OPACITY = "#05070F"
CARD_BG = "#0D0F17"
PANEL_BG = "#0D0F17"


# BUTTONS
BUTTON_PRIMARY = "#52451C"
BUTTON_SECONDARY = "#141B33"
BUTTON_ALERT = "#5A1B22"


# TEXT
NORMAL_TEXT = "#FFFFFF"
TITLE_TEXT = "#D4C48A"
MUTED_TEXT = "#7A7568"
DAMAGE_TEXT = "#FF1A1A"


# BORDERS
CARD_BORDER_SELECTED = "#D4AF37"
BUTTON_CREATE_BORDER = "#3A4A7A"
BUTTON_DELETE_BORDER = "#8A2E38"
CARD_BORDER = "#2A2410"


# STATUS BARS
STAT_BAR_BG = "#1A1712"
HP_BAR_COLOR = "#B3261E"
EXP_BAR_COLOR = "#52451C"


# MAP SCREEN
MAP_PANEL_BORDER = "#C8A532"        # gold frame around the map image
MAP_TITLE_TEXT = "#C8A532"
MAP_LIGHT_TEXT = "#E0E0E0"
# Dark wood-brown fill behind the map title: translucent, but dark enough to read over bright maps
MAP_TITLE_OVERLAY = ft.Colors.with_opacity(0.72, "#2B2117")
MAP_SECTION_BG = ft.Colors.with_opacity(0.85, "#0F1018")   # "In the area" / "Routes" / "Monsters nearby"
MAP_SECTION_BORDER = "#3D3523"       # dim gold outline of sections and their cards
MAP_DIVIDER = "#34343E"              # line under the header and under each section title
MAP_MUTED_TEXT = "#9C9AA6"           # greetings, route direction, "Building"
MAP_MARKER_BG = ft.Colors.with_opacity(0.78, "#0D0E14")    # place labels drawn over the map image
MAP_MARKER_BORDER = "#5A5A66"        # place chips / markers when not selected
MAP_SELECTED = "#E2B93B"             # selected place chip, marker and route card
MAP_LEVEL_TEXT = "#C8A532"           # "Lv 1-10" on route cards
MAP_ZONE_SAFE = "#2BD45F"            # "Safe Zone"
MAP_ZONE_HOSTILE = "#E5484D"         # "Hostile Area"


# BATTLE BOARD
GRID_LINE_COLOR = "#C4C4C4"
# Single tile color: the battlefield's ground tone (~#837654), kept translucent and subtle
TILE_COLOR = ft.Colors.with_opacity(0.15, "#837654")
PAGE_BACKGROUND_COLOR = "#05070F"
PLACEHOLDER_BACKGROUND_COLOR = "#1A1712"
BOARD_BORDER_COLOR = "#2A2410"
VALID_TILE_COLOR = ft.Colors.with_opacity(0.40, "#D4AF37")
INVALID_TILE_COLOR = ft.Colors.with_opacity(0.40, "#B3261E")
ATTACK_TILE_COLOR = ft.Colors.with_opacity(0.35, "#E5484D")   # selected skill's range