"""Converte .spr + .act do Ragnarok Online em sprite sheet PNG + JSON de clips.

No RO, corpo, cabeça e arma são arquivos separados que o cliente junta em tempo real.
Este script faz o mesmo: cabeça e arma são encaixadas no corpo pelos anchors do .act
(posição = anchor do corpo - anchor da peça). Cada clip é montado num canvas único,
com os pés fixos.

Corpo + cabeça + arma (caminhos com ou sem extensão):

    python tools/ro_to_sheet.py art_source/novice/novice novice \\
        --head art_source/novice/novice_head --weapon art_source/novice/weapon

Só corpo (jogador sem cabeça, ou monstro):

    python tools/ro_to_sheet.py art_source/poring/poring poring --kind monster

Para jogador, além dos clips de combate (idle/walk/attack/hurt/dead nas 4 diagonais), sai o
clip "stand_s": a pose Idle fora de combate, parado de frente, com a cabeça virando como no
GIF da seleção de personagem do RO. É o que as telas de personagem/perfil mostram.

Saída padrão: assets/sprites/<nome>/<nome>_sheet.png e <nome>.json
Use --preview prévia.png para gerar uma imagem com a grade dos frames para conferir.
"""
import argparse
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from spr_to_frames import read_spr, read_act, STAND_FRONT_ACTION

# clip -> tipo de ação do RO (índice // 8). Jogadores e monstros têm layouts diferentes.
CLIP_TYPES = {
    "player": {"idle": 0, "walk": 1, "attack": 5, "hurt": 6, "dead": 8, "stand": STAND_FRONT_ACTION // 8},
    "monster": {"idle": 0, "walk": 1, "attack": 2, "hurt": 3, "dead": 4},
}
# Jogador armado: o RO só desenha a arma em standby (4) e attack2 (10) neste arquivo de arma.
ARMED_TYPES = {"idle": 4, "attack": 10}
# No jogador, os 3 "frames" de stand(0)/sit(2) são variações da virada de cabeça, não animação.
STATIC_PLAYER_TYPES = {0, 2}

# Direção do RO (índice % 8). No tabuleiro isométrico: +col = SE, -col = NW, +row = SW, -row = NE
DIRECTIONS = {7: "se", 1: "sw", 3: "nw", 5: "ne"}
# Clips com direções próprias. "stand" (pose Idle fora de combate) só existe de frente (sul), e
# os seus 3 motions são a cabeça olhando para frente/lados, não um frame só como no "idle".
CLIP_DIRECTIONS = {"stand": {STAND_FRONT_ACTION % 8: "s"}}
STAND_FPS = 0.5                                               # 2 s em cada virada de cabeça, como no GIF
# Ordem de desenho das partes (da de trás para a da frente). Ajuste aqui se a arma
# ficar na frente/atrás errada em alguma direção.
DRAW_ORDER = {d: ("body", "head", "weapon")
              for dirs in (DIRECTIONS, *CLIP_DIRECTIONS.values()) for d in dirs.values()}

# Encaixe da arma na mão: se a arma ficar a SNAP_GAP px ou mais do corpo, ela é deslocada
# até o cabo encostar na mão (ponto do corpo mais extremo na direção da arma).
SNAP_GAP = 1.5
SNAP_MAX_SHIFT = 24

MIN_ALPHA = 0.5

CLIP_RULES = {
    "idle": {"loop": True},
    "walk": {"loop": True},
    "attack": {"loop": False},
    "hurt": {"loop": False},
    "dead": {"loop": False, "hold_last": True},
    "stand": {"loop": True, "fps": STAND_FPS},
}


def strip_ext(path: str) -> str:
    p = Path(path)
    return str(p.with_suffix("")) if p.suffix.lower() in (".spr", ".act") else str(p)


class Part:
    def __init__(self, path: str):
        base = strip_ext(path)
        self.frames = read_spr(base + ".spr")
        self.actions = read_act(base + ".act")


def tint(img, color):
    """Aplica a cor/alpha do layer (multiplica RGBA)."""
    arr = np.asarray(img).astype(np.float32) * (np.array(color, dtype=np.float32) / 255.0)
    return Image.fromarray(arr.round().astype(np.uint8), "RGBA")


def place(layer, frames):
    """(imagem já espelhada/escalada/tingida, x, y do canto sup. esq. relativo à origem) ou None."""
    x, y, spr, mirror, xs, ys, color = layer
    if not 0 <= spr < len(frames):
        return None                                           # layer vazio (índice -1)
    if color[3] / 255 < MIN_ALPHA:
        return None                                           # quase transparente
    img = frames[spr]
    if mirror:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if (xs, ys) != (1.0, 1.0):
        img = img.resize((max(1, round(img.width * xs)), max(1, round(img.height * ys))), Image.NEAREST)
    if color != (255, 255, 255, 255):
        img = tint(img, color)
    return img, x - img.width // 2, y - img.height // 2


def motion_of(part: Part, action: int, motion: int):
    if action >= len(part.actions) or not part.actions[action]["motions"]:
        return None
    motions = part.actions[action]["motions"]
    return motions[min(motion, len(motions) - 1)]


def first_anchor(motion):
    return motion["anchors"][0] if motion and motion["anchors"] else None


def _points(layers) -> np.ndarray:
    """Pixels opacos (x, y) de uma lista [(img, x, y)], relativos à origem."""
    pts = []
    for img, x, y in layers:
        ys, xs = np.nonzero(np.asarray(img)[:, :, 3] > 0)
        pts.append(np.stack([xs + x, ys + y], axis=1))
    return np.concatenate(pts) if pts else np.empty((0, 2))


def snap_to_hand(body_layers, weapon_layers) -> tuple[int, int]:
    """Deslocamento (dx, dy) que leva o cabo da arma até a mão, ou (0, 0) se ela já encosta no corpo."""
    body, weapon = _points(body_layers), _points(weapon_layers)
    if not len(body) or not len(weapon):
        return 0, 0
    if np.linalg.norm(weapon[:, None, :] - body[None, :, :], axis=2).min() < SNAP_GAP:
        return 0, 0
    direction = weapon.mean(axis=0) - body.mean(axis=0)
    direction = direction / (np.linalg.norm(direction) or 1.0)
    projection = body @ direction
    hand = body[projection >= projection.max() - 1.5].mean(axis=0)      # extremo do corpo rumo à arma
    grip = weapon[np.argmin(np.linalg.norm(weapon - hand, axis=1))]     # pixel da arma mais perto da mão
    shift = hand - grip
    if np.linalg.norm(shift) > SNAP_MAX_SHIFT:
        return 0, 0
    return int(round(shift[0])), int(round(shift[1]))


def render_parts(parts: dict, action: int, motion: int, order: tuple, snap: bool = True) -> list:
    """[(img, x, y)] relativos à origem (pés) do corpo, na ordem de desenho."""
    body_anchor = first_anchor(motion_of(parts["body"], action, motion))
    placed = {}
    for name in order:
        part = parts.get(name)
        m = motion_of(part, action, motion) if part else None
        if not m:
            continue
        dx = dy = 0
        if name != "body":                                    # cabeça/arma: anchor do corpo - anchor da peça
            part_anchor = first_anchor(m)
            if body_anchor and part_anchor:
                dx, dy = body_anchor[0] - part_anchor[0], body_anchor[1] - part_anchor[1]
        layers = []
        for layer in m["layers"]:
            result = place(layer, part.frames)
            if result:
                img, x, y = result
                layers.append((img, x + dx, y + dy))
        placed[name] = layers

    if snap and "weapon" in placed and "body" in placed:
        dx, dy = snap_to_hand(placed["body"], placed["weapon"])
        if dx or dy:
            placed["weapon"] = [(img, x + dx, y + dy) for img, x, y in placed["weapon"]]

    return [item for name in order for item in placed.get(name, [])]


def build(body, name, out_dir, head=None, weapon=None, kind="auto", idle=None, attack=None, preview=None, snap=True):
    parts = {"body": Part(body)}
    if head:
        parts["head"] = Part(head)
    if weapon:
        parts["weapon"] = Part(weapon)
    n_actions = len(parts["body"].actions)
    if kind == "auto":                                        # ACT de jogador tem ~100 ações; monstro ~40
        kind = "monster" if n_actions <= 48 else "player"
    print(f"{n_actions} ações no .act do corpo -> tratado como {kind} | partes: {', '.join(parts)}")

    clip_types = dict(CLIP_TYPES[kind])
    if kind == "player" and weapon:
        clip_types.update(ARMED_TYPES)
    if idle is not None:
        clip_types["idle"] = idle
    if attack is not None:
        clip_types["attack"] = attack
    print("tipos de ação:", clip_types)

    # 1) lista de (clip, ação) e extensão máxima do corpo em torno da origem
    wanted = []
    for clip, type_id in clip_types.items():
        for dir_id, dir_name in CLIP_DIRECTIONS.get(clip, DIRECTIONS).items():
            idx = type_id * 8 + dir_id
            if idx < n_actions and parts["body"].actions[idx]["motions"]:
                wanted.append((f"{clip}_{dir_name}", clip, type_id, dir_name, idx))

    def motions_for(clip, type_id, idx):
        count = len(parts["body"].actions[idx]["motions"])
        if kind == "player" and type_id in STATIC_PLAYER_TYPES and clip not in CLIP_DIRECTIONS:
            count = 1
        return range(count)

    left = right = top = bottom = 0
    for _, clip, type_id, dir_name, idx in wanted:
        for mi in motions_for(clip, type_id, idx):
            for img, ox, oy in render_parts(parts, idx, mi, DRAW_ORDER[dir_name], snap):
                left, right = min(left, ox), max(right, ox + img.width)
                top, bottom = min(top, oy), max(bottom, oy + img.height)
    half = max(-left, right)
    frame_w, frame_h = half * 2, bottom - top
    anchor_x, anchor_y = half, -top

    # 2) renderiza cada frame no canvas único
    rows, clips = [], {}
    for r, (clip_name, clip, type_id, dir_name, idx) in enumerate(wanted):
        row = []
        for mi in motions_for(clip, type_id, idx):
            canvas = Image.new("RGBA", (frame_w, frame_h))
            for img, ox, oy in render_parts(parts, idx, mi, DRAW_ORDER[dir_name], snap):
                canvas.alpha_composite(img, (anchor_x + ox, anchor_y + oy))
            row.append(canvas)
        rows.append(row)
        fps = round(1000 / parts["body"].actions[idx]["delay_ms"], 1)
        clips[clip_name] = {"row": r, "frames": len(row), "fps": fps, **CLIP_RULES[clip]}
        # caixa (x, y, w, h) com pixel opaco em algum frame do clip: permite exibir o clip
        # recortado e ampliado (ex.: stand na tela de perfil) sem a sobra do canvas único
        bboxes = [b for b in (frame.getbbox() for frame in row) if b]
        if bboxes:
            x0, y0 = min(b[0] for b in bboxes), min(b[1] for b in bboxes)
            x1, y1 = max(b[2] for b in bboxes), max(b[3] for b in bboxes)
            clips[clip_name]["box"] = [x0, y0, x1 - x0, y1 - y0]

    cols = max(len(r) for r in rows)
    sheet = Image.new("RGBA", (frame_w * cols, frame_h * len(rows)))
    for r, row in enumerate(rows):
        for c, frame in enumerate(row):
            sheet.paste(frame, (c * frame_w, r * frame_h))

    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    sheet.save(out / f"{name}_sheet.png")
    meta = {
        "src": f"sprites/{name}/{name}_sheet.png",
        "frame_w": frame_w, "frame_h": frame_h, "cols": cols, "rows": len(rows),
        "anchor_x": anchor_x, "anchor_y": anchor_y,           # pés do personagem dentro do frame
        "clips": clips,
    }
    (out / f"{name}.json").write_text(json.dumps(meta, indent=2))
    print(f"frame {frame_w}x{frame_h} | sheet {sheet.size} | {len(clips)} clips | âncora ({anchor_x},{anchor_y})")

    if preview:
        bg = Image.new("RGBA", sheet.size, (40, 40, 50, 255))
        bg.alpha_composite(sheet)
        draw = ImageDraw.Draw(bg)
        for x in range(0, sheet.width + 1, frame_w):
            draw.line([(x, 0), (x, sheet.height)], fill=(255, 0, 0, 120))
        for y in range(0, sheet.height + 1, frame_h):
            draw.line([(0, y), (sheet.width, y)], fill=(255, 0, 0, 120))
        bg.save(preview)
        print("prévia salva em", preview)
    return sheet, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Converte .spr + .act do RO em sprite sheet + JSON")
    ap.add_argument("body", help="corpo: caminho do .spr/.act, com ou sem extensão")
    ap.add_argument("name", help="nome da sheet (ex.: novice, poring)")
    ap.add_argument("--head", help="cabeça (.spr/.act, com ou sem extensão)")
    ap.add_argument("--weapon", help="arma (.spr/.act, com ou sem extensão)")
    ap.add_argument("--out", help="pasta de saída (padrão: assets/sprites/<name>)")
    ap.add_argument("--kind", choices=["auto", "player", "monster"], default="auto")
    ap.add_argument("--idle", type=int, help="força o tipo de ação do clip idle")
    ap.add_argument("--attack", type=int, help="força o tipo de ação do clip attack")
    ap.add_argument("--preview", help="salva uma prévia PNG com a grade dos frames")
    ap.add_argument("--no-snap", action="store_true", help="não encaixa a arma na mão (usa só os anchors)")
    ap.add_argument("--min-alpha", type=float, default=0.5,
                    help="ignora layers com alpha menor que isso (0 a 1; 0 mantém tudo)")
    a = ap.parse_args()
    MIN_ALPHA = a.min_alpha
    build(a.body, a.name, a.out or f"assets/sprites/{a.name}", a.head, a.weapon,
          a.kind, a.idle, a.attack, a.preview, not a.no_snap)