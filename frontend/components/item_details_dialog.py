import flet as ft
import themes as t


COLLECTION_SCALE = 1.5   # collection pictures are 75x100 pixel art


def item_details_dialog(item: dict, amount: int, on_close):
    """Pop up with an item's details: the collection picture, name, type and description.
    Opened from the inventory (right click on an item, or select it and press the Details button)."""
    picture = ft.Container(width=75 * COLLECTION_SCALE, height=100 * COLLECTION_SCALE,
                           border=ft.Border.all(1, t.MAP_SECTION_BORDER), border_radius=4,
                           content=ft.Image(src=item["collection"], width=75 * COLLECTION_SCALE,
                                            height=100 * COLLECTION_SCALE, fit=ft.BoxFit.CONTAIN,
                                            filter_quality=ft.FilterQuality.NONE)
                           if item.get("collection") else None)
    info = ft.Column(expand=True, tight=True, spacing=8, controls=[
        ft.Text(item["name"], size=20, weight=ft.FontWeight.BOLD, font_family="Cinzel", color=t.TITLE_TEXT),
        ft.Text(f"Type: {item['type']}", size=13, color=t.MUTED_TEXT, font_family="Cinzel"),
        *([ft.Text(f"Amount: {amount}", size=13, color=t.MUTED_TEXT, font_family="Cinzel")] if amount > 1 else []),
        ft.Divider(height=1, thickness=1, color=t.MAP_DIVIDER),
        ft.Text(item.get("description") or "", size=14, color=t.NORMAL_TEXT),
    ])

    return ft.AlertDialog(
        modal=True,
        bgcolor=t.PANEL_BG,
        content=ft.Container(width=440, content=ft.Row(spacing=18, vertical_alignment=ft.CrossAxisAlignment.START,
                                                      controls=[picture, info])),
        actions=[ft.Button(content=ft.Text("CLOSE", font_family="Cinzel", color=t.NORMAL_TEXT),
                           bgcolor=t.BUTTON_SECONDARY, on_click=on_close)],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
