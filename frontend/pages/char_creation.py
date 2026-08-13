import flet as ft
import themes as t


@ft.component
def character_creation():

    name_value, set_name_value = ft.use_state("")

    title = ft.Text(
        "Character Creation",
        size=32,
        weight=ft.FontWeight.BOLD,
        font_family="Cinzel",
        color=t.TITLE_TEXT,
    )

    character_preview = ft.Container(
        width=140,
        height=200,
        bgcolor="#1A1712",
        border=ft.Border.all(1, t.BUTTON_PRIMARY),
        border_radius=4,
        alignment=ft.Alignment.CENTER,
        content=ft.Image(
            src="sprites/0.Novice_Idle.gif",
            width=62,
            height=133,
            fit=ft.BoxFit.CONTAIN,
        ),
    )

    name_label = ft.Text(
        "Name:",
        size=16,
        font_family="Cinzel",
        color=t.TITLE_TEXT,
    )

    name_field = ft.TextField(
        value=name_value,
        on_change=lambda e: set_name_value(e.control.value),
        width=200,
        height=32,
        bgcolor="#0F1233",
        border_color=t.BUTTON_PRIMARY,
        color=t.NORMAL_TEXT,
        text_size=14,
        content_padding=8,
    )

    create_button = ft.Button(
        content=ft.Text(
            "Create",
            font_family="Cinzel",
            weight=ft.FontWeight.BOLD,
            size=14,
        ),
        bgcolor=t.BUTTON_SECONDARY,
        color=t.NORMAL_TEXT,
        width=140,
        height=44,
        on_click=lambda e: ft.context.page.navigate("/char_selection"),
    )

    return_button = ft.Button(
        content=ft.Text(
            "Back",
            font_family="Cinzel",
            weight=ft.FontWeight.BOLD,
            size=14,
        ),
        bgcolor=t.BUTTON_PRIMARY,
        color=t.NORMAL_TEXT,
        width=140,
        height=44,
        on_click=lambda e: ft.context.page.navigate("/char_selection"),
    )

    page_content = ft.Column(
        controls=[
            title,
            ft.Container(height=120),  # Spacer
            character_preview,
            ft.Container(height=20),  # Spacer
            name_label,
            name_field,
            ft.Container(height=20),  # Spacer
            ft.Row(controls=[create_button, return_button],
                   alignment=ft.MainAxisAlignment.CENTER),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=8,
    )

    background_layer = ft.Container(
        expand=True,
        opacity=0.1,
        image=ft.DecorationImage(
            src="background.png",
            fit=ft.BoxFit.COVER,
        ),
    )

    foreground_layer = ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        content=page_content,
    )

    return ft.Container(
        expand=True,
        bgcolor=t.BACKGROUND_OPACITY,
        content=ft.Stack(
            controls=[background_layer, foreground_layer],
            expand=True,
        ),
    )