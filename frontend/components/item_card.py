import flet as ft
import themes as t


def item_card(leading: ft.Control, label: str, subtitle: str | None = None, on_click=None,
              width: int = 155, height: int = 100, tooltip: str | None = None):
    """Card horizontal dos painéis de mapa: imagem/ícone à esquerda, nome (e subtítulo) à direita.
    Usado para NPCs, monstros, lugares (This Area) e mapas vizinhos (Nearby)."""
    texts = [ft.Text(label, size=14, weight=ft.FontWeight.BOLD, color=t.MAP_LIGHT_TEXT, font_family="Cinzel",
                     text_align=ft.TextAlign.CENTER)]
    if subtitle:
        texts.append(ft.Text(subtitle, size=12, color=t.MAP_LIGHT_TEXT, font_family="Cinzel",
                             text_align=ft.TextAlign.CENTER))

    return ft.Container(
        width=width,
        height=height,
        bgcolor=t.MAP_PANEL_BG,
        border=ft.Border.all(1, t.MAP_ITEM_BORDER),
        border_radius=10,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        on_click=on_click,
        tooltip=tooltip,
        content=ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                leading,
                ft.Column(expand=True, spacing=2, alignment=ft.MainAxisAlignment.CENTER,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=texts),
            ],
        ),
    )


def card_image(src: str, width: int = 51, height: int = 88) -> ft.Image:
    return ft.Image(src=src, width=width, height=height, fit=ft.BoxFit.CONTAIN)
