import flet as ft
import themes as t


def stat_row(label: str, value: str, value_color: str = t.NORMAL_TEXT, size: int = 14):
    return ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
        ft.Text(label, size=size, color=t.NORMAL_TEXT, font_family="Cinzel"),
        ft.Text(value, size=size, color=value_color, font_family="Cinzel", weight=ft.FontWeight.BOLD),
    ])


def battle_result_dialog(result: dict, on_close):
    """Pop up shown on the map after a battle. result = {"victory", "damage_dealt", "monsters": [{"name",
    "damage"}], "damage_taken", "exp_gained", "exp_lost", "level_up"} (built by battle_page.finish_battle)."""
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
