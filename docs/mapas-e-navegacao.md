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
│         │ ┌ title_card (800 × 64) ──────┐ ┌ In the area ────────────┐ │
│         │ │ Título + "Recommended Level"│ │ [Main Square] [Port] .. │ │
│         │ └─────────────────────────────┘ │ npc_card (Hostess·Talk) │ │
│         │ ┌ town_frame (800 × 600) ─────┐ └─────────────────────────┘ │
│         │ │          [👁 Hide Places]   │ ┌ Routes ─────────────────┐ │
│         │ │  (Academy) (Main Square)    │ │ Training Field 1    [↗] │ │
│         │ │     (Port) (House) ...      │ │ Academy (Building)      │ │
│         │ └─────────────────────────────┘ │                         │ │
│         │ ┌ Monsters nearby (só em mapas│ │                         │ │
│         │ │ com monstros) ──── [Hunt] ──┐ └─────────────────────────┘ │
│         │ └─────────────────────────────┘                             │
└─────────┴──────────────────────────────────────────────────────────────┘
```

- **Largura**: o conteúdo é limitado a `BATTLE_CONTENT_WIDTH` (importado de `pages/battle_page.py`, 1446 px), centralizado, com rolagem vertical.
- **`header(character, zone)`**: avatar do job (`badge_selector`), nome, zeny, "Job - Lv" e HP; à direita, "Safe Zone" quando o mapa é seguro (`zone_tag`; em qualquer outra zona não aparece nada), e uma linha divisória embaixo.
- **Duas colunas**: à esquerda, uma coluna de `LEFT_WIDTH = 800` px com o **card do título em cima**, o **mapa da cidade** e, nos mapas com monstros, o card **"Monsters nearby" embaixo do mapa**; à direita, "In the area" e "Routes" empilhados, com a **mesma altura da coluna da esquerda** (`TOP_HEIGHT`, mais `MONSTERS_HEIGHT` + `GAP` quando há monstros) e cada card ocupando metade (`expand=1`). Um conteúdo maior que o card rola dentro dele (`section(..., scroll=True)`). Os cantos são arredondados (`FRAME_RADIUS = 8`) e o espaço entre os blocos é `GAP = 16`.
- **`title_card`**: o nome do mapa (dourado, `MAP_TITLE_TEXT`) e, nos prédios, o nome do mapa onde ficam (`parent_map`) com o ícone de localização; o "Recommended Level" (omitido quando o `level_range` é vazio, como nos prédios) num card escuro de `LEFT_WIDTH × TITLE_HEIGHT` (800 × 64) com borda dourada discreta (`MAP_PANEL_BORDER`). **Os mapas não têm mais arte de capa**: o mapa da cidade é a imagem do local.
- **`town_frame`**: o mapa da cidade (`maps.town_image`) em `LEFT_WIDTH × TOWN_HEIGHT` (800 × 600, proporção 4:3, então a imagem inteira aparece sem cortar), com borda discreta (`MAP_SECTION_BORDER`). Os marcadores ficam por cima dele. **Mapa sem `town_image`** (hoje o Training Field 1) mostra um **quadrado vazio** do mesmo tamanho, sem marcadores nem botão; as áreas e as rotas continuam funcionando pelas abas e pelos cards.
- **Marcadores (`place_marker`)**: um por lugar de `map_data["places"]`, centrado em `x`/`y` (frações do **mapa da cidade**). Ícone + nome numa pílula escura; o selecionado fica dourado (`MAP_SELECTED`). Ao posicionar, deixe o ponto um pouco **acima** da construção, para o rótulo não cobri-la.
- **"View Places" / "Hide Places"** (`view_places_button`): pílula no canto superior direito do mapa da cidade; mostra ou esconde os marcadores. Eles começam visíveis, então o botão começa como "Hide Places".
- **Zoom do mapa da cidade**: de **1×** (imagem inteira, como antes) a **3×**, sempre dentro da mesma moldura de 800 × 600.
  - **Roda do mouse** sobre o mapa: cada giro multiplica o zoom por 1,15 (`WHEEL_STEP`), mantendo parado o ponto que está sob o cursor.
  - **Botões** abaixo do "Hide Places": **−**, **+** (fator 1,4, `BUTTON_STEP`, em volta do centro) e **Reset** (volta a 1×).
  - **Arrastar** com o mouse move a imagem; ela nunca sai da moldura (`clamp_view`).
  - Os **rótulos mantêm o tamanho** em qualquer zoom: só a imagem cresce, e cada marcador é reposicionado (`map_zoom.to_viewport`). Marcadores que saem da vista não são desenhados, e os que ficam continuam clicáveis.
  - A matemática é pura e fica em `services/map_zoom.py` (`zoom_at`, `pan`, `image_rect`, `to_viewport`); o estado `(zoom, cx, cy)` é um `use_state` de `map_screen`, e o `town_frame` usa um `ft.GestureDetector` (`on_scroll`, `on_pan_update`). Mapas sem `town_image` não têm zoom.
- **Seções (`section`)**: card escuro com ícone + título, divisor e conteúdo. "In the area" e "Routes" têm a mesma altura (metade da coluna cada). "Monsters nearby" fica **sob o mapa da cidade**, na largura da coluna da esquerda, com altura fixa (`MONSTERS_HEIGHT = 176`) e rolagem interna se houver muitos monstros.
- **Janela estreita**: a coluna da esquerda tem largura fixa e a da direita encolhe; com uma janela de uns 1500 px os cards da direita ficam com ~520 px; em janelas menores que uns 1300 px eles ficam apertados (o mapa não encolhe).

### Lugares, áreas e rotas

Os lugares vêm do backend (`map_places`) com um `kind`:

| kind | No mapa | Embaixo | Clique (marcador ou card) |
|---|---|---|---|
| `area` | marcador | aba em "In the area" (`area_chip`) | seleciona a área e mostra os NPCs dela (`npc_card`: imagem, nome, `greeting` e botão **Talk**) |
| `building` | marcador | card em "Routes": "Safe Zone", "Building", sem seta | destaca o card (entrar no prédio vem depois) |
| `exit` | marcador | card em "Routes" com o mesmo ícone do marcador antes do nome, o mapa de destino: nível, zona, direção e a seta ↗ | destaca o card; a seta chama `change_place(character, map_id)` (ver "Viagem entre mapas") |

- A área inicial é a primeira com NPCs (`default_area_id`); sem ninguém na área, aparece "No one around".
- **Viagem entre mapas**: `change_place` (`services/map_router_manager.py`) abre um pop up modal (`components/travel_dialog.py`) com a animação do personagem andando para a direita (clip `walk_se` da sheet do job), parado no lugar, e um botão **Cancel** logo abaixo. O pop up fica aberto por `TRAVEL_SECONDS = 5` (duração provisória); só então o novo lugar é gravado no backend (`PATCH .../place`), o pop up fecha e o mapa de destino abre (a gravação leva uma fração de segundo a mais). **Cancel** fecha o pop up antes disso: nada é gravado, nenhuma navegação acontece e o personagem continua no mapa atual. Se a gravação falhar, o pop up fecha e o jogador também continua no mapa atual. **Entrar em um prédio** (rota cujo destino tem `parent_map`, `is_building` no `target`) **ou sair dele** para o mapa onde fica é instantâneo: `change_place(..., instant=True)` grava o lugar e abre o mapa, sem pop up nem os 5 segundos. O pop up não é um `@ft.component` (ele é criado fora de um render): o contêiner recebe os quadros num loop assíncrono que é cancelado ao fechar.
- `build_routes` monta "Routes": saídas primeiro, depois prédios, e por último conexões de `navigation` que não têm marcador de saída (sem zona nem direção).
- O botão **Talk** ainda não faz nada (tooltip "Coming soon").
- Ícones: `PLACE_ICONS` traduz a chave `icon` do lugar (`square`, `port`, `house`, `building`, `exit`, `training`) para um ícone do Flet. **TODO**: trocar pelos PNG/SVG do projeto.
- Zonas: `ZONES` só tem `safe` (rótulo "Safe Zone", ícone e cor `MAP_ZONE_SAFE`). `zone_tag` devolve `None` para as outras (`hostile_passive`, `hostile_aggressive`), e então o cabeçalho e os cards de rota simplesmente não mostram a indicação. O valor continua guardado em `maps.zone`.

### "Monsters nearby" e o botão Hunt

Só aparece em mapas com monstros, embaixo do mapa da cidade. `monsters_nearby(map_id, monsters, character)` mostra um card por monstro (`item_card` + `monster_sprite`, com o `spawn_rate` como subtítulo, ex.: `"40%"`) e o botão **Hunt** à direita.

`hunt_button(map_id, character)` → `handle_hunt` → `start()`:
1. `BattleService.start_battle(character["id"], map_id)` → `POST /api/v1/battles/`.
2. Em caso de `ApiError`, imprime no console e fica na tela.
3. Com sucesso, chama `navigate_to_battle(map_route(map_id), setup)`.

> O Hunt abre uma caçada com 1 a 6 monstros do mapa, sorteados pela chance (`spawn_rate`) de cada um. Ao fim da batalha (vitória ou derrota) o jogador volta para este mapa e vê o pop up de resultado (`battle_result_dialog`, aberto por `map_screen`).

## Mapas existentes (seed)

| id | Nome | Nível | Zona | Lugares | NPCs | Monstros (peso) | Conecta com |
|---|---|---|---|---|---|---|---|
| `novice_academy` | Novice Island | 1 - 10 | `safe` | Main Square, Port, 2× House (áreas); Academy (saída, "Building", para `academy`); Training Field 1 (saída, Northwest) | Hostess (Main Square), Sailor (Port) | nenhum | `training_field_1`, `academy` |
| `training_field_1` | Training Field 1 | 1 - 10 | `hostile_passive` | Training Grounds (área); Novice Island (saída, Southeast); Training Field 2 (saída, Northeast, para `training_field_2`) | Trainer (Training Grounds) | Poring (50), Lunatic (25), Fabre (25) | `novice_academy`, `training_field_2` |
| `training_field_2` | Training Field 2 | 1 - 10 | `hostile_passive` | Camp (área); Training Field 1 (saída, Southwest) | nenhum | Wilow (40), Poring (40), Lunatic (20) | `training_field_1` |
| `academy` | Academy | (vazio) | `safe` | nenhum (só a imagem por enquanto) | nenhum | nenhum | `novice_academy` |

Todo personagem novo começa em `novice_academy`. Sempre que o personagem muda de mapa pela seta de uma rota, `PATCH /api/v1/characters/{id}/place` grava o novo `current_map` e `current_map_id`, e o personagem da sessão é atualizado com a resposta. Assim o botão **Enter** do perfil leva ao último mapa visitado. Se a chamada falhar, a navegação não acontece.
