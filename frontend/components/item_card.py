import flet as ft
import themes as t


def item_card(image: str, label: str, subtitle: str | None = None, on_click=None, image_size: int = 100, image_fit: ft.BoxFit = ft.BoxFit.CONTAIN):
    """Small square card used for NPCs, Navigation and Monster entries."""
    controls = [
        ft.Container(
            width=image_size,
            height=image_size,
            border_radius=6,
            bgcolor="#1A1712",
            image=ft.DecorationImage(src=image, fit=image_fit),
        ),
        ft.Text(label, size=13, color=t.NORMAL_TEXT, font_family="Cinzel",
                text_align=ft.TextAlign.CENTER),
    ]

    if subtitle:
        controls.append(
            ft.Text(subtitle, size=11, color=t.MUTED_TEXT, font_family="Cinzel",
                    text_align=ft.TextAlign.CENTER)
        )

    return ft.Container(
        width=100,
        bgcolor=t.CARD_BG,
        border=ft.Border.all(1, t.CARD_BORDER),
        border_radius=6,
        padding=10,
        on_click=on_click,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=controls,
        ),
    )