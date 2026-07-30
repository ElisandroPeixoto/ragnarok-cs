import flet as ft
from routes import routes
import os


ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

def app():
    return ft.Router(routes=routes, manage_views=True)

def main(page: ft.Page):
    page.title = "Ragnarok C.S"
    page.fonts = {"Cinzel": "fonts/Cinzel-Regular.ttf", }
    page.render_views(app)
    page.update()


ft.run(main=main, assets_dir=ASSETS_DIR)
