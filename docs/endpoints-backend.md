# Endpoints do backend

Todas as rotas ficam sob o prefixo `/api/v1` (`settings.API_V1_STR`) e respondem em `http://localhost:8001`. Com o servidor no ar, `http://localhost:8001/docs` mostra a documentação interativa gerada pelo FastAPI (Swagger), onde dá para testar cada rota.

## Como as rotas são montadas

1. `backend/main.py` cria o `FastAPI` e inclui `api_router` com o prefixo `/api/v1`.
2. `backend/api/v1/api.py` monta um roteador por domínio:

| Prefixo | Roteador | Arquivo |
|---|---|---|
| `/characters` | `characters_router` | `api/v1/endpoints/characters.py` |
| `/maps` | `maps_router` | `api/v1/endpoints/maps.py` |
| `/battles` | `battles_router` | `api/v1/endpoints/battles.py` |

3. Cada endpoint recebe a sessão do banco com `db: AsyncSession = Depends(get_session)` (`core/deps.py`).
4. O formato de entrada e saída é validado pelos schemas Pydantic de `backend/schemas/`. Um corpo inválido gera **422 Unprocessable Entity** automaticamente.

Erros de negócio usam `HTTPException` e chegam ao cliente como `{"detail": "<mensagem>"}`.

---

## Personagens: `api/v1/endpoints/characters.py`

### `POST /api/v1/characters/`: criar personagem

Função: `post_character`. Status de sucesso: **201**.

Corpo (`CharacterSchemaCreate`):
```json
{ "name": "Midrway" }
```

Só o nome é enviado. Todo o resto vem dos `default` de `CharacterModel`: job `Novice`, level 1, exp 0, hp/max_hp 50, max_sp 10, zeny 0, mapa atual `Novice Island` (`novice_academy`). A bolsa começa vazia.

Resposta (`CharacterSchemaResponse`):
```json
{
  "id": 1, "name": "Midrway", "job": "Novice", "level": 1, "exp": 0, "exp_progress": 0, "exp_needed": 100,
  "hp": 50, "max_hp": 50, "max_sp": 10, "zeny": "0.00",
  "current_map": "Novice Island", "current_map_id": "novice_academy"
}
```

> `zeny` é `Numeric(10, 2)` no banco e `Decimal` no schema, então chega como texto (`"0.00"`).

Não há validação de nome vazio, tamanho ou duplicidade no backend. O frontend só impede nome em branco.

### `GET /api/v1/characters/`: listar personagens

Função: `get_characters`. Status: **200**. Devolve uma lista de `CharacterSchemaResponse` com todos os personagens do banco. Não há separação por conta ou usuário.

### `GET /api/v1/characters/{character_id}`: buscar um personagem

Função: `get_character_by_id`. Status: **200**, ou **404** `{"detail": "Character not found"}`.

O frontend ainda não usa esta rota.

### `POST /api/v1/characters/{character_id}/battle-result`: fechar uma caçada

Função: `post_battle_result`. Status: **200**, **404** (`Character not found` ou `Monster '<nome>' not found`) ou **422** (corpo inválido, ou vitória com menos de 3 ou mais de 6 monstros).

Corpo: `{ "victory": true, "kills": ["Poring", "Lunatic", "Wilow"] }`. `victory` diz como a caçada acabou; `kills` são os nomes dos monstros da caçada (3 a 6) e só importam na vitória. O cliente **não envia EXP**:
- **Vitória**: o backend calcula o ganho de cada monstro pela diferença de nível (`core/exp_rule.py`), soma ao `exp` do personagem e recalcula o `level` (`core/level_progression.py`, pode subir vários).
- **Derrota**: os nomes são ignorados; o backend tira 20% da EXP acumulada no nível atual (nunca perde nível).

Na vitória, o backend também sorteia os drops de cada monstro morto e coloca os itens na bolsa (ver [Inventário](inventario.md#drops)).

Resposta: `{ "character": {…CharacterSchemaResponse…, com `exp_progress` e `exp_needed`…}, "exp_gained": 24, "exp_lost": 0, "drops": [{ "item_id": "jellopy", "name": "Jellopy", "icon": "items/jellopy/icon.png", "amount": 2 }], "drops_lost": [] }`. `drops` são os itens que foram para a bolsa; `drops_lost`, os que não couberam (bolsa cheia). Na derrota os dois vêm vazios. O frontend chama esta rota **uma vez**, quando a batalha termina por vitória ou derrota (o botão Leave não chama). Veja [Regra de experiência](regra-de-experiencia.md).

### `PATCH /api/v1/characters/{character_id}/place`: registrar mudança de local

Função: `patch_character_place`. Status: **200**, ou **404** (`Character not found` / `Map not found`).

Corpo: `{ "map_id": "training_field_1" }`. Grava `current_map` (nome do mapa) e `current_map_id` do personagem e devolve o `CharacterSchemaResponse` atualizado. O frontend chama esta rota ao trocar de mapa pela seta de uma rota (seção "Routes").

---

## Inventário: `api/v1/endpoints/inventory.py`

Montado com o prefixo `/characters`, ao lado das rotas de personagem. Regras dos slots em [Inventário](inventario.md).

### `GET /api/v1/characters/{character_id}/inventory`: itens do personagem

Função: `get_inventory`. Status: **200** ou **404** (`Character not found`).

Resposta: lista de `InventoryEntrySchema`, um por item, na bolsa ou equipado:
```json
[ { "id": 1, "slot": "bag_0", "amount": 8,
    "item": { "id": "jellopy", "name": "Jellopy", "type": "Misc", "description": "…", "drop_rate": 70.0,
              "icon": "items/jellopy/icon.png", "collection": "items/jellopy/collection.png" } },
  { "id": 3, "slot": "bag_1", "amount": 2,
    "item": { "id": "apple", "name": "Apple", "type": "Misc", "description": "…", "drop_rate": 2.0,
              "icon": "items/apple/icon.png", "collection": "items/apple/collection.png" } } ]
```

Slots vazios não aparecem. `slot` é `bag_0`…`bag_39` ou um slot de equipamento (`head`, `armor`, `right_hand`, `left_hand`, `garment`, `shoes`, `accessory_1`, `accessory_2`).

### `POST /api/v1/characters/{character_id}/inventory/move`: mover um item

Função: `move_item`. Status: **200**, **404** (`Character not found` / `No item in that slot`) ou **422** (`Invalid slot` / `Item does not fit that slot`).

Corpo (`InventoryMoveSchema`): `{ "from_slot": "bag_0", "to_slot": "right_hand" }`. O item de `from_slot` vai para `to_slot`; se `to_slot` já tiver um item, os dois trocam. Um slot de equipamento só aceita o `type` certo (hoje, nenhum: só existem itens Misc), e isso vale para os dois lados da troca. Resposta: o inventário inteiro, já salvo (mesmo formato do `GET`).

### `DELETE /api/v1/characters/{character_id}/inventory/{entry_id}`: destruir um item

Função: `destroy_item`. Status: **200** ou **404** (`Character not found` / `Item not found`, inclusive quando a entrada é de outro personagem).

`entry_id` é o `id` da entrada do inventário (não o id do item). Apaga a entrada inteira, ou seja, a pilha toda, esteja ela na bolsa ou num slot de equipamento. Não há como desfazer. Resposta: o inventário inteiro, já salvo (mesmo formato do `GET`). O frontend chama esta rota pelo botão Destroy do inventário, depois do pop up de confirmação.

---

## Mapas: `api/v1/endpoints/maps.py`

### `GET /api/v1/maps/`: listar mapas

Função: `get_maps`. Status: **200**. Resposta: lista de `MapSchemaSummary`.

```json
[ { "id": "novice_academy", "name": "Novice Island" },
  { "id": "training_field_1", "name": "Training Field 1" } ]
```

O frontend usa esta rota na inicialização (`MapService.get_map_ids_sync`) para registrar uma rota por mapa.

### `GET /api/v1/maps/{map_id}`: detalhes de um mapa

Função: `get_map_by_id`. Status: **200**, ou **404** `{"detail": "Map not found"}`.

A consulta carrega de forma antecipada (`selectinload`) os NPCs, os lugares (com o mapa de destino das saídas), os spawns de monstros (com o monstro) e as conexões (com o mapa de destino). `to_response()` transforma isso num dict achatado (`MapSchemaResponse`):

```json
{
  "id": "training_field_1",
  "name": "Training Field 1",
  "level_range": "1 - 10",
  "parent_map": null,   // prédios: { "map_id": "novice_academy", "name": "Novice Island" }
  "town_image": "maps/training_field_1.jpg",
  "background_image": "maps/backgrounds/forest.jpg",
  "about": "...",
  "zone": "hostile_passive",
  "places": [
    { "id": 18, "name": "Training Grounds", "kind": "area", "icon": "training",
      "x": 0.3, "y": 0.66, "direction": null, "target": null },
    { "id": 19, "name": "Novice Island", "kind": "exit", "icon": "exit",
      "x": 0.63, "y": 0.9, "direction": "Southeast",
      "target": { "map_id": "novice_academy", "name": "Novice Island",
                  "level_range": "1 - 10", "zone": "safe" } }
  ],
  "npcs": [ { "name": "Trainer", "image": "npcs/trainer.gif", "place_id": 18,
              "greeting": "Ready to train? Monsters roam these woods." } ],
  "monsters": [
    { "name": "Poring",  "sheet": "poring",  "spawn_rate": 40 },
    { "name": "Lunatic", "sheet": "lunatic", "spawn_rate": 40 },
    { "name": "Wilow",   "sheet": "wilow",   "spawn_rate": 20 }
  ],
  "navigation": [
    { "name": "Novice Island", "map_id": "novice_academy", "level_range": "1 - 10" }
  ]
}
```

`monsters` lista **todos** os monstros do mapa. `MonsterSchema` expõe só `name`, `sheet`, `level`, `base_exp` e `spawn_rate`.

`places` vem de `place_to_dict`: `x`/`y` são o centro do marcador em fração da imagem, e `target` só existe nas saídas (`kind: "exit"`). Os `id` dos lugares mudam a cada seed (eles são regravados); `npcs[].place_id` aponta para eles na mesma resposta.

---

## Batalhas: `api/v1/endpoints/battles.py`

### `POST /api/v1/battles/`: iniciar uma caçada

Função: `start_battle`. Status de sucesso: **201**.

Corpo (`BattleSchemaCreate`):
```json
{ "character_id": 1, "map_id": "training_field_1" }
```

O que acontece:

1. Busca o personagem (`CharacterModel`); se não existir, **404** `Character not found`.
2. Busca o job do personagem (`JobModel`, pela chave `character.job`); se não existir, **404** `Job '<nome>' not found`.
3. Busca o mapa (`MapModel`); se não existir, **404** `Map not found`.
4. Lista os monstros do mapa (`MapMonsterModel`, ordenados por `monster_id`) com `spawn_rate > 0`. Se não houver nenhum, **400** `No monsters to hunt on this map`. Isso acontece, por exemplo, na Novice Island.
5. Monta a resposta: `units` só com o `hero` (`hero_unit(character, job)`), e `monsters`: de `MIN_MONSTERS` a `MAX_MONSTERS` (3 a 6, `core/battle_rules.py`) monstros sorteados com `random.choices` entre os do mapa, tendo `MapMonsterModel.spawn_rate` como peso (o mesmo monstro pode se repetir), cada um montado por `monster_unit(monster, nível do herói)`. A caçada termina quando o herói mata todos (vitória) ou morre (derrota): não há mais ondas.
6. Junta as skills do herói e de todos os monstros do pool com `skill_to_dict`.

Resposta (`BattleSchemaResponse`):

```json
{
  "units": {
    "hero": {
      "name": "Midrway", "job": "Novice", "team": "player", "level": 1,
      "sheet": "novice", "avatar": "characters_badges/0_novice_badge.png", "ai": null,
      "offset_x": 0, "offset_y": 0,
      "hp": 50, "max_hp": 50, "ap": 5, "max_ap": 5,
      "skills": ["Basic Attack"]
    }
  },
  "skills": {
    "Basic Attack": { "ap_cost": 1, "damage": 10, "range": 1, "icon": "skills/Basic Attack.png" }
  },
  "monsters": [
    {
      "name": "Poring", "job": null, "team": "enemy", "level": 1, "exp_reward": 6,
      "sheet": "poring", "avatar": null, "ai": "approach_and_attack",
      "offset_x": 0, "offset_y": 0,
      "hp": 50, "max_hp": 50, "ap": 2, "max_ap": 2,
      "skills": ["Basic Attack"]
    }
  ]
}
```

(`monsters` traz de 3 a 6 entradas, uma por monstro da caçada; o exemplo mostra só o primeiro.)

Origem de cada campo:

| Campo | Herói (`hero`) | Monstro (`monsters[]`) |
|---|---|---|
| `name` | `CharacterModel.name` | `MonsterModel.name` |
| `job` | `JobModel.name` | `null` |
| `sheet`, `offset_x`, `offset_y` | `JobModel` | `MonsterModel` |
| `level` | `CharacterModel.level` | `MonsterModel.level` |
| `exp_reward` | — | EXP que o herói ganha por este monstro se vencer (`exp_gain` com o nível dele); só para o log, a EXP real é calculada em `battle-result` |
| `avatar` | `JobModel.avatar` | `null` (o card mostra o idle da `sheet`) |
| `hp` / `max_hp` | `CharacterModel.hp` / `max_hp` | `MonsterModel.max_hp` (nos dois) |
| `ap` / `max_ap` | `JobModel.max_ap` (nos dois) | `MonsterModel.max_ap` (nos dois) |
| `skills` | `JobModel.skill_links`, em ordem de `slot` | `MonsterModel.skill_links`, em ordem de `slot` |
| `ai` | `null` | `MonsterModel.ai` |

As unidades **não têm posição**: `col`/`row` são definidos pelo frontend quando a batalha começa (ver [Sistema de combate](sistema-de-combate.md#posições-iniciais)).

Esta rota **não grava nada no banco**. Não existe registro de batalha, nem rota para enviar o resultado de volta.

---

## Resumo

| Método | Rota | Função | Sucesso | Erros |
|---|---|---|---|---|
| POST | `/api/v1/characters/` | `post_character` | 201 | 422 |
| GET | `/api/v1/characters/` | `get_characters` | 200 | n/a |
| GET | `/api/v1/characters/{character_id}` | `get_character_by_id` | 200 | 404 |
| DELETE | `/api/v1/characters/{character_id}` | `delete_character` | 204 | 404 |
| POST | `/api/v1/characters/{character_id}/battle-result` | `post_battle_result` | 200 | 404, 422 |
| PATCH | `/api/v1/characters/{character_id}/place` | `patch_character_place` | 200 | 404, 422 |
| GET | `/api/v1/characters/{character_id}/inventory` | `get_inventory` | 200 | 404 |
| POST | `/api/v1/characters/{character_id}/inventory/move` | `move_item` | 200 | 404, 422 |
| DELETE | `/api/v1/characters/{character_id}/inventory/{entry_id}` | `destroy_item` | 200 | 404 |
| GET | `/api/v1/maps/` | `get_maps` | 200 | n/a |
| GET | `/api/v1/maps/{map_id}` | `get_map_by_id` | 200 | 404 |
| POST | `/api/v1/battles/` | `start_battle` | 201 | 400, 404, 422 |

A única rota de atualização de um personagem é `PATCH /api/v1/characters/{character_id}/place` (a EXP muda só pelo `battle-result`); a única de exclusão é `DELETE /api/v1/characters/{character_id}` (204, sem corpo; apaga também os itens do personagem). Os itens mudam de lugar só por `inventory/move` e são destruídos só por `DELETE /api/v1/characters/{character_id}/inventory/{entry_id}`. Não existem outras.

## Como adicionar um endpoint

1. Crie ou edite um arquivo em `backend/api/v1/endpoints/` com `router = APIRouter()`.
2. Defina schemas em `backend/schemas/` para a entrada e a saída.
3. Use `db: AsyncSession = Depends(get_session)` para acessar o banco.
4. Se for um domínio novo, registre o roteador em `backend/api/v1/api.py` com `include_router(..., prefix="/<dominio>")`.
5. No frontend, crie um método no service do domínio (ou um service novo) usando o `api` de `services/api_client.py`.
