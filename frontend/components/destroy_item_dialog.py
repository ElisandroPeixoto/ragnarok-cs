import flet as ft
import themes as t


def destroy_item_dialog(item: dict, amount: int, on_confirm, on_cancel):
    """Asks before destroying an inventory item (the whole pile). Opened by the inventory's Destroy button."""
    what = f"{item['name']} x{amount}" if amount > 1 else item["name"]
    icon = ft.Image(src=item["icon"], width=38, height=38, filter_quality=ft.FilterQuality.NONE) \
        if item.get("icon") else ft.Container(width=38, height=38)
    return ft.AlertDialog(
        modal=True,
        bgcolor=t.PANEL_BG,
        title=ft.Text("Destroy item", font_family="Cinzel", color=t.TITLE_TEXT),
        content=ft.Row(tight=True, spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
            icon,
            ft.Text(f"Are you sure you want to destroy {what}? This cannot be undone.",
                    font_family="Cinzel", color=t.NORMAL_TEXT, width=320),
        ]),
        actions=[
            ft.Button(content=ft.Text("CANCEL", font_family="Cinzel", color=t.NORMAL_TEXT),
                      bgcolor=t.BUTTON_SECONDARY, on_click=on_cancel),
            ft.Button(content=ft.Text("DESTROY", font_family="Cinzel", color=t.NORMAL_TEXT),
                      bgcolor=t.BUTTON_ALERT, on_click=on_confirm),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
