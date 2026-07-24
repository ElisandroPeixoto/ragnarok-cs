import flet as ft
from routes import routes


def app():
    return ft.Router(routes=routes, manage_views=True)

def main(page: ft.Page):
    page.title = "Ragnarok C.S"
    page.render_views(app)


ft.run(main=main, assets_dir="assets")
