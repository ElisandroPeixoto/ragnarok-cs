# Mapas e navegação

## Rotas de mapa

Cada mapa do banco vira uma rota `/map/<map_id>`. O registro acontece **uma vez, na importação** de `frontend/routes.py`:

```python
routes += [
    ft.Route(path=map_route(map_id),
             component=view_wrapper(build_map_page(map_id), map_route(map_id), appbar_visible=False))
    for map_id in MapService.get_map_ids_sync()
]
```

Consequências:
- O backend precisa estar no ar antes de abrir o frontend.
- Um mapa adicionado ao banco só ganha rota quando o frontend é reiniciado.

Helpers em `services/map_router_manager.py`:

| Função | Faz |
|---|---|
| `map_route(map_id)` | monta `"/map/<map_id>"` |
| `navigate_to_map(map_id)` | navega para o mapa |
| `navigate_to_battle(return_route, setup)` | guarda a rota de retorno e o setup da batalha em `session_state` e navega para `/battle` |
| `navigate_back_from_battle()` | volta para a rota guardada (ou `/profile_page` se não houver) |

## Tela de mapa: `pages/map_screen.py`

`build_map_page(map_id)` é uma **fábrica**: devolve um componente `_map_page` já preso àquele `map_id`. É assim que cada rota sabe qual mapa carregar.

### Carregamento (`_map_page`)

1. Estados: `collapsed` (sidebar), `map_data` e `loading`.
2. Ao montar, `fetch()` chama `MapService.get_map(map_id)` → `GET /api/v1/maps/{map_id}`.
3. Enquanto carrega, mostra um `ProgressRing`. Sem personagem selecionado, mostra "No character selected". Se o mapa não vier, mostra "Map '<id>' not found".
4. Com tudo certo, renderiza `map_screen(map_data, character)` ao lado da `sidebar`.

### Layout (`map_screen`)

```
┌ sidebar ┬──────────────────────────────────────────────────────┐
│         │ [character_badge] [zeny_badge]                       │
│         │ ┌──────────────── map_banner ──────────────────────┐ │
│         │ │ Título + "Level: x - y" sobre a imagem do mapa    │ │
│         │ └───────────────────────────────────────────────────┘ │
│         │ ┌ People in the area ┐┌ Monsters ┐┌ Go To ──────────┐ │
│         │ │ npc_item...        ││ cards    ││ This Area       │ │
│         │ │                    ││ [Hunt]   ││ Nearby          │ │
│         │ └────────────────────┘└──────────┘└─────────────────┘ │
└─────────┴──────────────────────────────────────────────────────┘
```

- **Largura**: o conteúdo é limitado a `BATTLE_CONTENT_WIDTH` (importado de `pages/battle_page.py`, 1446 px), centralizado. Em janelas mais estreitas ele encolhe.
- **`map_banner(map_data)`**: altura fixa `BANNER_HEIGHT = 494`, imagem em `COVER`, sombra no topo e caixa com título e faixa de nível.
- **Painéis**: `section_panel(title, content, expand)` (`components/section_panel.py`), de altura fixa (`PANEL_HEIGHT = 295`) e cabeçalho dourado. As larguras seguem a proporção do Figma, 348 / 348 / 483.
- **Cards**: `item_card` e `card_image` (`components/item_card.py`), montados por:
  - `npc_item`: NPCs (sem ação).
  - `monster_item`: monstros, com `spawn_rate` como subtítulo (`"40%"`).
  - `place_item`: lugares de "This Area" (tooltip "Coming soon", sem ação).
  - `navigation_item`: mapas vizinhos de "Nearby"; o clique navega para `map_route(item["map_id"])`.

### Painel Monsters e o botão Hunt

`monsters_content(map_id, monsters, character)`:
- **Com monstros**: grade de cards com rolagem e, abaixo, o botão **Hunt** centralizado (`hunt_button`, cor `BUTTON_PRIMARY`).
- **Sem monstros**: mostra "Safe Zone" com um escudo.

`hunt_button(map_id, character)` → `handle_hunt` → `start()`:
1. `BattleService.start_battle(character["id"], map_id)` → `POST /api/v1/battles/`.
2. Em caso de `ApiError`, imprime no console e fica na tela. Isso acontece, por exemplo, se só houver monstros sem `sheet`.
3. Com sucesso, chama `navigate_to_battle(map_route(map_id), setup)`.

> O painel lista todos os monstros do mapa, mas o Hunt só sorteia entre os que têm dados de batalha. No Training Field 1 hoje sempre sai o Poring.

### "Go To"

`go_to_content(map_data)` tem duas seções:
- **This Area**: lugares do dicionário `MAP_PLACES`, que fica **no frontend** (TODO: levar para o backend). Hoje só a Novice Academy tem um lugar ("Academy"), e o botão não tem destino.
- **Nearby**: vem de `map_data["navigation"]`, ou seja, de `map_connections` no banco.

## Mapas existentes (seed)

| id | Nome | Nível | NPCs | Monstros (peso) | Conecta com |
|---|---|---|---|---|---|
| `novice_academy` | Novice Academy | 1 - 10 | Hostess, Sailor | nenhum (Safe Zone) | `training_field_1` |
| `training_field_1` | Training Field 1 | 1 - 10 | Trainer | Poring (40), Lunatic (40), Wilow (20) | `novice_academy` |

Todo personagem novo começa em `novice_academy`. Como nenhuma rota altera `current_map_id`, o botão **Enter** do perfil sempre leva ao mapa inicial, mesmo que o jogador tenha andado por outros.
