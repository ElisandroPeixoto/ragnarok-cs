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

`map_screen(map_data, character)` é um componente (`@ft.component`) com três estados: `show_places` (marcadores visíveis), `selected_area_id` (área cujos NPCs aparecem) e `selected_route_key` (rota destacada).

```
┌ sidebar ┬──────────────────────────────────────────────────────────────┐
│         │ [avatar] Nome / zeny                          [Safe Zone]    │
│         │ Novice - Lv: 1 / HP: 50/50                                   │
│         │ ─────────────────────────────────────────────────────────── │
│         │ ┌──────── map_frame (800 × 462) ────────┐  👁 Hide Places    │
│         │ │ Título + "Recommended Level"           │                   │
│         │ │   (Academy) (Main Square) (Port) ...   │                   │
│         │ └────────────────────────────────────────┘                   │
│         │ ┌ In the area ─────────────────┐ ┌ Routes ────────────────┐ │
│         │ │ [Main Square] [Port] [House] │ │ Training Field 1    [↗] │ │
│         │ │ npc_card (Hostess · Talk)    │ │ Academy (Building)      │ │
│         │ └──────────────────────────────┘ └─────────────────────────┘ │
│         │ ┌ Monsters nearby (só em mapas com monstros) ─────── [Hunt] ┐ │
│         │ └────────────────────────────────────────────────────────────┘ │
└─────────┴──────────────────────────────────────────────────────────────┘
```

- **Largura**: o conteúdo é limitado a `BATTLE_CONTENT_WIDTH` (importado de `pages/battle_page.py`, 1446 px), centralizado, com rolagem vertical.
- **`header(character, zone)`**: avatar do job (`badge_selector`), nome, zeny, "Job - Lv" e HP; à direita, a zona do mapa (`zone_tag`), e uma linha divisória embaixo.
- **`map_frame`**: a imagem tem **tamanho fixo em todos os mapas**, `MAP_IMAGE_WIDTH × MAP_IMAGE_HEIGHT` (800 × 462, proporção das artes 1358 × 784), com borda dourada. O título e "Recommended Level" ficam no canto superior esquerdo, sobre `MAP_TITLE_OVERLAY`.
- **Marcadores (`place_marker`)**: um por lugar de `map_data["places"]`, centrado em `x`/`y` (frações da imagem). Ícone + nome numa pílula escura; o selecionado fica dourado (`MAP_SELECTED`).
- **"View Places" / "Hide Places"** (`view_places_button`): mostra ou esconde os marcadores. Eles começam visíveis, então o botão começa como "Hide Places".
- **Seções (`section`)**: card escuro com ícone + título, divisor e conteúdo. "In the area" e "Routes" dividem a largura em 7 : 5.

### Lugares, áreas e rotas

Os lugares vêm do backend (`map_places`) com um `kind`:

| kind | No mapa | Embaixo | Clique (marcador ou card) |
|---|---|---|---|
| `area` | marcador | aba em "In the area" (`area_chip`) | seleciona a área e mostra os NPCs dela (`npc_card`: imagem, nome, `greeting` e botão **Talk**) |
| `building` | marcador | card em "Routes": "Safe Zone", "Building", sem seta | destaca o card (entrar no prédio vem depois) |
| `exit` | marcador | card em "Routes" com o mapa de destino: nível, zona, direção e a seta ↗ | destaca o card; a seta chama `change_place(character, map_id)` |

- A área inicial é a primeira com NPCs (`default_area_id`); sem ninguém na área, aparece "No one around".
- `build_routes` monta "Routes": saídas primeiro, depois prédios, e por último conexões de `navigation` que não têm marcador de saída (sem zona nem direção).
- O botão **Talk** ainda não faz nada (tooltip "Coming soon").
- Ícones: `PLACE_ICONS` traduz a chave `icon` do lugar (`square`, `port`, `house`, `building`, `exit`, `training`) para um ícone do Flet. **TODO**: trocar pelos PNG/SVG do projeto.
- Zonas: `ZONES` traduz `zone` (`safe`, `hostile_passive`, `hostile_aggressive`) para o rótulo, o ícone e a cor (`MAP_ZONE_SAFE` / `MAP_ZONE_HOSTILE`).

### "Monsters nearby" e o botão Hunt

Só aparece em mapas com monstros. `monsters_nearby(map_id, monsters, character)` mostra um card por monstro (`item_card` + `monster_sprite`, com o `spawn_rate` como subtítulo, ex.: `"40%"`) e o botão **Hunt** à direita.

`hunt_button(map_id, character)` → `handle_hunt` → `start()`:
1. `BattleService.start_battle(character["id"], map_id)` → `POST /api/v1/battles/`.
2. Em caso de `ApiError`, imprime no console e fica na tela.
3. Com sucesso, chama `navigate_to_battle(map_route(map_id), setup)`.

> O Hunt abre a caçada com os monstros do mapa; as ondas sorteiam os monstros pela chance (`spawn_rate`) de cada um.

## Mapas existentes (seed)

| id | Nome | Nível | Zona | Lugares | NPCs | Monstros (peso) | Conecta com |
|---|---|---|---|---|---|---|---|
| `novice_academy` | Novice Academy | 1 - 10 | `safe` | Main Square, Port, 3× House (áreas); Academy (prédio); Training Camp (saída, Northwest) | Hostess (Main Square), Sailor (Port) | nenhum | `training_field_1` |
| `training_field_1` | Training Field 1 | 1 - 10 | `hostile_passive` | Training Grounds (área); Academy Road (saída, Southeast) | Trainer (Training Grounds) | Poring (40), Lunatic (40), Wilow (20) | `novice_academy` |

Todo personagem novo começa em `novice_academy`. Sempre que o personagem muda de mapa pela seta de uma rota, `PATCH /api/v1/characters/{id}/place` grava o novo `current_map` e `current_map_id`, e o personagem da sessão é atualizado com a resposta. Assim o botão **Enter** do perfil leva ao último mapa visitado. Se a chamada falhar, a navegação não acontece.
