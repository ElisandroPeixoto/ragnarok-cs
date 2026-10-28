# Sprites e animação

Os personagens e monstros são desenhados a partir de **sprite sheets**: uma imagem PNG com todos os frames em grade, mais um JSON que diz onde está cada animação. As sheets são geradas a partir dos arquivos originais do Ragnarok Online pelos scripts em `tools/`.

## Pipeline de conversão

```
art_source/<nome>.spr + .act   ──tools/ro_to_sheet.py──►   assets/sprites/<nome>/<nome>_sheet.png
(corpo, cabeça, arma)                                       assets/sprites/<nome>/<nome>.json
```

`art_source/` é ignorado pelo git; os arquivos originais ficam só na máquina de quem gera as sheets. Os scripts precisam de **Pillow** e **numpy**.

### `tools/spr_to_frames.py`: leitura dos formatos do RO

- `read_spr(path)`: lê o `.spr` (versões até 2.1, com frames indexados com paleta e RGBA, e RLE de zeros na v2.1).
- `read_act(path)`: lê o `.act`, cuja estrutura é ações → motions → layers (posição, sprite, espelhamento, escala, cor) mais os anchors.
- `STAND_FRONT_ACTION`: índice da pose parada de frente (tipo 0, direção 0/sul).
- Também funciona como script, para salvar os frames crus em PNG (`--stand` salva só a pose parada):

```bash
python tools/spr_to_frames.py art_source/novice.spr art_source/novice/stand --stand
```

### `tools/ro_to_sheet.py`: montagem da sheet

No RO, corpo, cabeça e arma são arquivos separados, juntados em tempo real pelo cliente. O script faz o mesmo: posiciona cada peça usando os anchors do `.act` (posição = anchor do corpo − anchor da peça) e monta cada frame num canvas único, com os pés sempre no mesmo ponto.

```bash
python tools/ro_to_sheet.py art_source/novice novice --head art_source/novice_head --weapon art_source/weapon --preview preview.png
```

```bash
python tools/ro_to_sheet.py art_source/poring/poring poring --kind monster
```

Constantes que controlam o resultado:

| Constante | Papel |
|---|---|
| `CLIP_TYPES` | qual tipo de ação do RO vira cada clip (`idle`, `walk`, `attack`, `hurt`, `dead`, `stand`); jogadores e monstros têm layouts diferentes |
| `ARMED_TYPES` | para jogador armado, usa standby (4) e attack2 (10), as únicas ações que desenham a arma |
| `DIRECTIONS` | quais direções do RO viram `se`, `sw`, `nw`, `ne` |
| `CLIP_DIRECTIONS` | `stand` só existe de frente (`s`) |
| `CLIP_RULES` | `loop`, `hold_last` e `fps` de cada clip (`dead` segura o último frame; `stand` roda a 0,5 fps) |
| `DRAW_ORDER` | ordem de pintura das peças (corpo, cabeça, arma) |
| `SNAP_GAP`, `SNAP_MAX_SHIFT` | encaixe automático da arma na mão (desligável com `--no-snap`) |
| `MIN_ALPHA` | ignora layers com alpha abaixo de 0,5 (ajustável com `--min-alpha`) |

Outras opções úteis: `--kind auto|player|monster` (o padrão `auto` trata como monstro um `.act` com até 48 ações), `--idle`/`--attack` para forçar o tipo de ação de um clip, `--out` para mudar a pasta de saída.

## Formato do JSON

Exemplo (`assets/sprites/novice/novice.json`, resumido):

```json
{
  "src": "sprites/novice/novice_sheet.png",
  "frame_w": 110, "frame_h": 106,
  "cols": 9, "rows": 21,
  "anchor_x": 55, "anchor_y": 81,
  "clips": {
    "idle_se": { "row": 0, "frames": 6, "fps": 10.0, "loop": true, "box": [22, 2, 59, 89] },
    "dead_se": { "row": 16, "frames": 1, "fps": 10.0, "loop": false, "hold_last": true, "box": [17, 47, 65, 53] },
    "stand_s": { "row": 20, "frames": 3, "fps": 0.5, "loop": true, "box": [37, 1, 36, 91] }
  }
}
```

| Campo | Significado |
|---|---|
| `src` | caminho da imagem, relativo a `assets/` |
| `frame_w`, `frame_h` | tamanho de cada frame (todos iguais) |
| `cols`, `rows` | tamanho da grade da sheet |
| `anchor_x`, `anchor_y` | posição dos **pés** dentro do frame; é o ponto colocado no centro do tile |
| `clips` | chave `<anim>_<direção>`. Cada clip ocupa uma **linha** (`row`) e tem `frames`, `fps`, `loop`, `hold_last` opcional e `box` opcional (`[x, y, w, h]` da área efetivamente desenhada, usada para recortar e ampliar) |

Clips gerados:
- **Combate** (jogadores e monstros): `idle`, `walk`, `attack`, `hurt`, `dead` × `se`, `sw`, `nw`, `ne`.
- **Fora de combate** (só jogadores): `stand_s`, parado de frente com a cabeça virando, como no GIF da seleção de personagem do RO.

Sheets existentes: `novice` (21 clips, inclui `stand_s`) e `poring` (20 clips).

## Como o jogo usa as sheets

### Carregamento: `services/battle_animation.py`

- `Clip` e `SpriteSheet` são dataclasses imutáveis que espelham o JSON.
- `get_sheet(name)` lê `assets/sprites/<name>/<name>.json` e fica em cache (`lru_cache`), então cada sheet é lida do disco uma vez só.

### Animação na batalha

O frame atual é **calculado**, não guardado. A unidade só registra qual clip começou e quando:

- `play(unit, anim)` grava `unit["anim"]` e `unit["anim_started"] = time.monotonic()`. Unidade morta não troca mais de clip.
- `face_towards(unit, col, row)` ajusta `unit["facing"]` para o eixo dominante do movimento.
- `current_frame(unit, now=None)` é uma **função pura** que devolve `(linha, coluna)` do frame:
  1. Acha o clip com `_find_clip`: primeiro `<anim>_<facing>`; se não existir, `idle_<facing>`; por último, o primeiro clip da sheet.
  2. Calcula o índice a partir do tempo decorrido × `fps`.
  3. Clip em loop dá a volta; clip com `hold_last` para no último frame; os demais (ataque, dano) **voltam para `idle`** quando terminam.

Como o cálculo depende só do relógio, basta re-renderizar periodicamente, que é o que faz o `anim_loop` da `battle_page` (~12 fps).

### Desenho: `components/unit_sprite.py`

- `sheet_frame(sheet, row, col, box=None, scale=1.0)`: mostra um frame recortando a imagem inteira dentro de um `Container` com `clip_behavior=HARD_EDGE`. A imagem é deslocada para que só o frame (ou o `box`) fique visível. `filter_quality=NONE` mantém o pixel art nítido ao ampliar.
- `unit_sprite(unit, left, top)`: junta `get_sheet` e `current_frame` para desenhar a unidade no tabuleiro.

### Fora da batalha: `components/job_sprite.py`

`job_sprite(job, height)` mostra o clip `stand_s` recortado pelo `box` e ampliado até a altura pedida. Tem um loop próprio que avança o frame no ritmo do clip. Usado na seleção, criação e perfil. Se o job não tiver sheet (`sprite_selector.sheet_selector`), cai num GIF (`JOBS_SPRITES`) ou num espaço vazio.

## Adicionando um personagem ou monstro novo

1. Coloque os `.spr`/`.act` em `art_source/`.
2. Rode `tools/ro_to_sheet.py` (com `--preview` para conferir a grade).
3. Confira o resultado em `assets/sprites/<nome>/`.
4. Monstro: preencha `sheet` (e os dados de batalha) em `MONSTERS` no `backend/seed_data.py`. Job: preencha `JOBS` e também `JOBS_SHEETS`/`JOBS_BADGES` em `frontend/services/sprite_selector.py`.
5. Se o sprite parecer deslocado no tile, ajuste `offset_x`/`offset_y` no seed.
