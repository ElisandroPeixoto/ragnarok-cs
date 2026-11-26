import flet as ft
import themes as t


def stat_row(label: str, value: str, value_color: str = t.NORMAL_TEXT, size: int = 14):
    return ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
        ft.Text(label, size=size, color=t.NORMAL_TEXT, font_family="Cinzel"),
        ft.Text(value, size=size, color=value_color, font_family="Cinzel", weight=ft.FontWeight.BOLD),
    ])


def drop_row(drop: dict, lost: bool = False):
    """An item the hunt dropped: icon, name and amount (lost = it did not fit in the bag)"""
    icon = ft.Image(src=drop["icon"], width=24, height=24, filter_quality=ft.FilterQuality.NONE) if drop.get("icon") \
        else ft.Container(width=24, height=24)
    color = t.MUTED_TEXT if lost else t.NORMAL_TEXT
    return ft.Row(spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
        icon,
        ft.Text(drop["name"], size=13, color=color, font_family="Cinzel", expand=True),
        ft.Text(f"x{drop['amount']}", size=13, color=color, font_family="Cinzel", weight=ft.FontWeight.BOLD),
    ])


def battle_result_dialog(result: dict, on_close):
    """Pop up shown on the map after a battle. result = {"victory", "damage_dealt", "monsters": [{"name",
    "damage"}], "damage_taken", "exp_gained", "exp_lost", "level_up", "drops", "drops_lost"} (built by
    battle_page.finish_battle; drops = [{"item_id", "name", "icon", "amount"}])."""
    victory = result["victory"]
    rows = [
        stat_row("Total damage dealt", str(result["damage_dealt"])),
        ft.Container(padding=ft.Padding(left=14), content=ft.Column(spacing=2, controls=[
            stat_row(monster["name"], str(monster["damage"]), size=13) for monster in result["monsters"]])),
        stat_row("Damage received", str(result["damage_taken"]), t.DAMAGE_TEXT),
        ft.Divider(height=1, thickness=1, color=t.MAP_DIVIDER),
    ]
    if victory:
        rows.append(stat_row("EXP gained", f"+{result['exp_gained']}", t.VICTORY_TEXT))
        if result.get("level_up"):
            rows.append(stat_row("Level up", f"Level {result['level_up']}", t.LEVEL_UP_TEXT))
        rows.append(ft.Divider(height=1, thickness=1, color=t.MAP_DIVIDER))
        rows.append(ft.Text("Items", size=14, color=t.NORMAL_TEXT, font_family="Cinzel"))
        drops = result.get("drops", [])
        if drops:
            rows.append(ft.Container(padding=ft.Padding(left=14), content=ft.Column(
                spacing=4, controls=[drop_row(drop) for drop in drops])))
        else:
            rows.append(ft.Container(padding=ft.Padding(left=14), content=ft.Text(
                "No items dropped", size=13, color=t.MUTED_TEXT, font_family="Cinzel")))
        if result.get("drops_lost"):
            rows.append(ft.Text("Bag full, left behind:", size=13, color=t.DEFEAT_TEXT, font_family="Cinzel"))
            rows.append(ft.Container(padding=ft.Padding(left=14), content=ft.Column(
                spacing=4, controls=[drop_row(drop, lost=True) for drop in result["drops_lost"]])))
    else:
        rows.append(stat_row("EXP lost", f"-{result['exp_lost']}", t.DEFEAT_TEXT))

    return ft.AlertDialog(
        modal=True,
        bgcolor=t.PANEL_BG,
        title=ft.Text("Victory!" if victory else "Defeat", size=30, weight=ft.FontWeight.BOLD, font_family="Cinzel",
                      color=t.VICTORY_TEXT if victory else t.DEFEAT_TEXT, text_align=ft.TextAlign.CENTER),
        content=ft.Container(width=360, content=ft.Column(tight=True, spacing=8, controls=rows)),
        actions=[ft.Button(content=ft.Text("CLOSE", font_family="Cinzel", color=t.NORMAL_TEXT),
                           bgcolor=t.BUTTON_SECONDARY, on_click=on_close)],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
