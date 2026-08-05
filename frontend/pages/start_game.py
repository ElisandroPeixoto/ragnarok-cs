import flet as ft
import themes as t
import asyncio


@ft.component
def start_game():

    visible, set_visible = ft.use_state(False)
    def on_mount():
        async def reveal():
            await asyncio.sleep(0.1)
            set_visible(True)

        task = ft.context.page.run_task(reveal)
        return None

    ft.use_effect(on_mount, [])

    logo = ft.Container(
        content=ft.Image(
            src="logo_with_words.png",
            width=350,
            height=350,
            fit=ft.BoxFit.CONTAIN,
        ),
        opacity=1 if visible else 0,
        scale=1 if visible else 0.7,
        animate_opacity=ft.Animation(duration=900, curve=ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(duration=900, curve=ft.AnimationCurve.EASE_OUT_BACK),
    )

    start_button = ft.Button(content=ft.Text("Start Adventure",
                                             font_family="Cinzel",
                                             size=16
                                             ),
                             bgcolor=t.BUTTON_PRIMARY,
                             color=t.NORMAL_TEXT,
                             on_click=lambda e: ft.context.page.navigate("/char_selection")
                             )

    footer_disclaimer = ft.Text("FAN-MADE. NOT AFFILIATED WITH GRAVITY.CO",
                                size=13,
                                color=t.NORMAL_TEXT,
                                font_family="Cinzel",
                                )

    page_content = ft.Column(controls=[logo,
                                       start_button,
                                       ft.Container(height=80),  # Spacer
                                       footer_disclaimer],
                             alignment=ft.MainAxisAlignment.CENTER,
                             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                             spacing=30
                             )

    background_layer = ft.Container(
        expand=True,
        opacity=0.1,  # 10% visibility
        image=ft.DecorationImage(
            src="background.png",
            fit=ft.BoxFit.COVER
        ),
    )

    foreground_layer = ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        content=page_content
    )

    return ft.Container(
        expand=True,
        bgcolor=t.BACKGROUND_OPACITY,  # solid base color behind the faded image
        content=ft.Stack(
            controls=[background_layer, foreground_layer],
            expand=True,
        ),
    )