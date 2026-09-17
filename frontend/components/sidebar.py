import flet as ft
import themes as t


SIDEBAR_WIDTH = 240
SIDEBAR_WIDTH_COLLAPSED = 72
SIDEBAR_BG = "#0A0C14"


def sidebar_item(icon: str, label: str, on_click=None, collapsed: bool = False):
    return ft.Container(padding=ft.Padding(left=20, top=10, right=20, bottom=10) if not collapsed else ft.Padding.all(10),
                        alignment=ft.Alignment.CENTER if collapsed else None,
                        bgcolor=t.CARD_BG,
                        border_radius=6,
                        on_click=on_click,
                        content=ft.Row(spacing=12, controls=[
                            ft.Image(src=icon, width=23, height=26),
                            *([] if collapsed else [
                                ft.Text(label, size=15, font_family="Cinzel", color=t.TITLE_TEXT),
                            ])
                        ]))

def sidebar(collapsed: bool, on_toggle):
    toggle_button = ft.Container(alignment=ft.Alignment.CENTER if collapsed else None,
                                 padding=ft.Padding(left=10 if not collapsed else 0, top=16, right=10, bottom=0),
                                 on_click=on_toggle,
                                 content=ft.Icon(ft.Icons.MENU_OPEN if not collapsed else ft.Icons.MENU,
                                                 size=22,
                                                 color=t.MUTED_TEXT))
    logo = ft.Container(alignment=ft.Alignment.CENTER,
                        padding=ft.Padding.symmetric(vertical=16),
                        content=ft.Container(
                            width=50 if collapsed else 90,
                            height=50 if collapsed else 90,
                            border_radius=35,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Image(src="Icon.png")
                        ))
    nav_items = ft.Column(spacing=4,
                          controls=[
                              sidebar_item("icons/profile.png", "Profile", collapsed=collapsed, on_click=lambda e: ft.context.page.navigate("/profile_page")),
                              sidebar_item("icons/quests.png", "Quests", collapsed=collapsed),
                              sidebar_item("icons/inventory.png", "Inventory", collapsed=collapsed),
                              sidebar_item("icons/map.png", "World Map", collapsed=collapsed),
                              sidebar_item("icons/instances.png", "Instances", collapsed=collapsed),
                              sidebar_item("icons/wiki.png", "Wiki", collapsed=collapsed),
                              sidebar_item("icons/change_char.png", "Change Character", collapsed=collapsed,
                                           on_click=lambda e: ft.context.page.navigate("/char_selection"))])

    return ft.Container(width=SIDEBAR_WIDTH_COLLAPSED if collapsed else SIDEBAR_WIDTH,
                        bgcolor=SIDEBAR_BG,
                        padding=ft.Padding(left=10, right=10, top=0, bottom=20),
                        animate=ft.Animation(duration=250, curve=ft.AnimationCurve.EASE_IN_OUT),
                        content=ft.Column(controls=[toggle_button, logo, nav_items], spacing=0))
