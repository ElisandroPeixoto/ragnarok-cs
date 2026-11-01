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

Só o nome é enviado. Todo o resto vem dos `default` de `CharacterModel`: job `Novice`, level 1, exp 0, hp/max_hp 50, max_sp 10, zeny 0, mapa atual `Novice Academy` (`novice_academy`).

Resposta (`CharacterSchemaResponse`):
```json
{
  "id": 1, "name": "Midrway", "job": "Novice", "level": 1, "exp": 0,
  "hp": 50, "max_hp": 50, "max_sp": 10, "zeny": "0.00",
  "current_map": "Novice Academy", "current_map_id": "novice_academy"
}
```

> `zeny` é `Numeric(10, 2)` no banco e `Decimal` no schema, então chega como texto (`"0.00"`).

Não há validação de nome vazio, tamanho ou duplicidade no backend. O frontend só impede nome em branco.

### `GET /api/v1/characters/`: listar personagens

Função: `get_characters`. Status: **200**. Devolve uma lista de `CharacterSchemaResponse` com todos os personagens do banco. Não há separação por conta ou usuário.

### `GET /api/v1/characters/{character_id}`: buscar um personagem

Função: `get_character_by_id`. Status: **200**, ou **404** `{"detail": "Character not found"}`.

O frontend ainda não usa esta rota.

---

## Mapas: `api/v1/endpoints/maps.py`

### `GET /api/v1/maps/`: listar mapas

Função: `get_maps`. Status: **200**. Resposta: lista de `MapSchemaSummary`.

```json
[ { "id": "novice_academy", "name": "Novice Academy" },
  { "id": "training_field_1", "name": "Training Field 1" } ]
```

O frontend usa esta rota na inicialização (`MapService.get_map_ids_sync`) para registrar uma rota por mapa.

### `GET /api/v1/maps/{map_id}`: detalhes de um mapa

Função: `get_map_by_id`. Status: **200**, ou **404** `{"detail": "Map not found"}`.

A consulta carrega de forma antecipada (`selectinload`) os NPCs, os spawns de monstros (com o monstro) e as conexões (com o mapa de destino). `to_response()` transforma isso num dict achatado (`MapSchemaResponse`):

```json
{
  "id": "training_field_1",
  "name": "Training Field 1",
  "level_range": "1 - 10",
  "image": "maps/training_field_1.jpg",
  "about": "...",
  "npcs": [ { "name": "Trainer", "image": "npcs/trainer.gif" } ],
  "monsters": [
    { "name": "Poring",  "sheet": "poring",  "spawn_rate": 40 },
    { "name": "Lunatic", "sheet": "lunatic", "spawn_rate": 40 },
    { "name": "Wilow",   "sheet": "wilow",   "spawn_rate": 20 }
  ],
  "navigation": [
    { "name": "Novice Academy", "image": "maps/novice_academy.jpg",
      "map_id": "novice_academy", "level_range": "1 - 10" }
  ]
}
```

`monsters` lista **todos** os monstros do mapa. `MonsterSchema` expõe só `name`, `sheet` e `spawn_rate`.

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
3. Lista os monstros do mapa (`MapMonsterModel`, ordenados por `monster_id`). Se não houver nenhum, **400** `No monsters to hunt on this map`. Isso acontece, por exemplo, na Novice Academy.
4. Monta as unidades: `hero` com `hero_unit(character, job)` e **um `monster_N` para cada monstro do mapa** (`monster_1`, `monster_2`…) com `monster_unit(monster)`. O `spawn_rate` não entra aqui; hoje ele só aparece no card do mapa.
5. Junta as skills usadas por todas as unidades com `skill_to_dict`.

Resposta (`BattleSchemaResponse`):

```json
{
  "units": {
    "hero": {
      "name": "Midrway", "job": "Novice", "team": "player",
      "sheet": "novice", "avatar": "characters_badges/0_novice_badge.png", "ai": null,
      "offset_x": 0, "offset_y": 0,
      "hp": 50, "max_hp": 50, "ap": 5, "max_ap": 5,
      "skills": ["Basic Attack"]
    },
    "monster_1": {
      "name": "Poring", "job": null, "team": "enemy",
      "sheet": "poring", "avatar": null, "ai": "approach_and_attack",
      "offset_x": 0, "offset_y": 0,
      "hp": 50, "max_hp": 50, "ap": 2, "max_ap": 2,
      "skills": ["Basic Attack"]
    }
  },
  "skills": {
    "Basic Attack": { "ap_cost": 1, "damage": 10, "range": 1, "icon": "skills/Basic Attack.png" }
  }
}
```

Origem de cada campo:

| Campo | Herói (`hero`) | Monstro (`monster_N`) |
|---|---|---|
| `name` | `CharacterModel.name` | `MonsterModel.name` |
| `job` | `JobModel.name` | `null` |
| `sheet`, `offset_x`, `offset_y` | `JobModel` | `MonsterModel` |
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
| GET | `/api/v1/maps/` | `get_maps` | 200 | n/a |
| GET | `/api/v1/maps/{map_id}` | `get_map_by_id` | 200 | 404 |
| POST | `/api/v1/battles/` | `start_battle` | 201 | 400, 404, 422 |

Não existem rotas de atualização ou exclusão (PUT/PATCH/DELETE) para nenhum recurso.

## Como adicionar um endpoint

1. Crie ou edite um arquivo em `backend/api/v1/endpoints/` com `router = APIRouter()`.
2. Defina schemas em `backend/schemas/` para a entrada e a saída.
3. Use `db: AsyncSession = Depends(get_session)` para acessar o banco.
4. Se for um domínio novo, registre o roteador em `backend/api/v1/api.py` com `include_router(..., prefix="/<dominio>")`.
5. No frontend, crie um método no service do domínio (ou um service novo) usando o `api` de `services/api_client.py`.
