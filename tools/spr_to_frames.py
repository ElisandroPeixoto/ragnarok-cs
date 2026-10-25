"""Lê .spr/.act do Ragnarok Online e salva os frames crus como PNG.

Todos os frames do .spr:

    python tools/spr_to_frames.py art_source/novice.spr art_source/novice/raw

Só os frames de uma ação do .act (índice = tipo * 8 + direção). --stand é o atalho para a
pose "Idle" do jogador: parado, de frente (ação 0 = tipo 0, direção 0/sul):

    python tools/spr_to_frames.py art_source/novice.spr art_source/novice/stand --stand
"""
import argparse
import struct
from pathlib import Path
from PIL import Image

# Ação do jogador parado de frente (pose "Idle" fora de combate): tipo 0 (stand), direção 0 (sul)
STAND_FRONT_ACTION = 0


def read_spr(path: str) -> list[Image.Image]:
    data = Path(path).read_bytes()
    if data[:2] != b"SP":
        raise ValueError("não é um arquivo SPR")

    minor, major = data[2], data[3]            # versão nos offsets 2-3 (2.1 => major=2, minor=1)
    version = major * 256 + minor
    pos = 4

    indexed_count = struct.unpack_from("<H", data, pos)[0]; pos += 2
    rgba_count = 0
    if version >= 0x0102:                      # >= v1.2 tem contagem de frames RGBA
        rgba_count = struct.unpack_from("<H", data, pos)[0]; pos += 2
    print(f"versão {major}.{minor} | indexados: {indexed_count} | rgba: {rgba_count}")

    indexed = []
    for _ in range(indexed_count):
        w, h = struct.unpack_from("<HH", data, pos); pos += 4
        if version >= 0x0201:                  # v2.1: RLE de zeros
            size = struct.unpack_from("<H", data, pos)[0]; pos += 2
            raw, out, i = data[pos:pos + size], bytearray(), 0
            while i < len(raw):
                b = raw[i]; i += 1
                if b == 0:
                    out += b"\x00" * raw[i]; i += 1
                else:
                    out.append(b)
            pos += size
        else:
            out = bytearray(data[pos:pos + w * h]); pos += w * h
        indexed.append((w, h, bytes(out)))

    rgba = []
    for _ in range(rgba_count):
        w, h = struct.unpack_from("<HH", data, pos); pos += 4
        px = data[pos:pos + w * h * 4]; pos += w * h * 4
        img = Image.frombytes("RGBA", (w, h), px, "raw", "ABGR")
        rgba.append(img.transpose(Image.FLIP_TOP_BOTTOM))

    palette = data[-1024:]                     # RGBA; índice 0 = transparente
    frames = []
    for w, h, idx in indexed:
        img = Image.new("RGBA", (w, h))
        img.putdata([(0, 0, 0, 0) if i == 0 else (*palette[i*4:i*4+3], 255) for i in idx])
        frames.append(img)
    return frames + rgba


def read_act(path: str) -> list[dict]:
    """Ações -> motions -> layers (x, y, sprite, espelhado, xs, ys) + anchors [(x, y)]."""
    d = Path(path).read_bytes()
    if d[:2] != b"AC":
        raise ValueError(f"{path}: não é um arquivo ACT")
    ver = d[3] * 256 + d[2]
    n_actions = struct.unpack_from("<H", d, 4)[0]
    pos = 16
    actions = []
    for _ in range(n_actions):
        n_motions = struct.unpack_from("<I", d, pos)[0]; pos += 4
        motions = []
        for _ in range(n_motions):
            pos += 32
            n_layers = struct.unpack_from("<I", d, pos)[0]; pos += 4
            layers = []
            for _ in range(n_layers):
                x, y, spr, flags = struct.unpack_from("<iiiI", d, pos); pos += 16
                xs = ys = 1.0
                color = (255, 255, 255, 255)
                if ver >= 0x0200:
                    color = tuple(d[pos:pos + 4]);
                    pos += 4  # R, G, B, A
                    xs = ys = struct.unpack_from("<f", d, pos)[0];
                    pos += 4
                    if ver >= 0x0204:
                        ys = struct.unpack_from("<f", d, pos)[0];
                        pos += 4
                    pos += 8  # rotação + tipo de sprite
                    if ver >= 0x0205:
                        pos += 8
                layers.append((x, y, spr, bool(flags & 1), xs, ys, color))
            anchors = []
            if ver >= 0x0200:
                pos += 4                                      # id de evento
            if ver >= 0x0203:
                n_anchors = struct.unpack_from("<i", d, pos)[0]; pos += 4
                for _ in range(n_anchors):
                    _, ax, ay, _ = struct.unpack_from("<iiii", d, pos); pos += 16
                    anchors.append((ax, ay))
            motions.append({"layers": layers, "anchors": anchors})
        actions.append({"motions": motions, "delay_ms": 150.0})
    if ver >= 0x0201:
        pos += 4 + 40 * struct.unpack_from("<I", d, pos)[0]
    if ver >= 0x0202:
        for a in actions:
            a["delay_ms"] = struct.unpack_from("<f", d, pos)[0] * 25; pos += 4
    return actions


def frames_of_action(actions: list[dict], action: int) -> list[int]:
    """Índices dos frames do .spr usados por uma ação, na ordem em que aparecem (sem repetir)."""
    used = []
    for motion in actions[action]["motions"]:
        for layer in motion["layers"]:
            if layer[2] >= 0 and layer[2] not in used:
                used.append(layer[2])
    return used


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Salva os frames de um .spr do RO como PNG")
    ap.add_argument("spr", nargs="?", default="novice.spr", help="arquivo .spr")
    ap.add_argument("out", nargs="?", default="art_source/novice/raw", help="pasta de saída")
    ap.add_argument("--act", help="arquivo .act (padrão: mesmo nome do .spr)")
    ap.add_argument("--action", type=int, help="salva só os frames desta ação do .act")
    ap.add_argument("--stand", action="store_true",
                    help=f"pose Idle do jogador, parado de frente (= --action {STAND_FRONT_ACTION})")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    frames = read_spr(a.spr)
    action = STAND_FRONT_ACTION if a.stand else a.action

    if action is None:
        for n, frame in enumerate(frames):
            frame.save(out / f"{n:03d}.png")
        print(f"{len(frames)} frames salvos em {out}")
    else:
        actions = read_act(a.act or str(Path(a.spr).with_suffix(".act")))
        used = frames_of_action(actions, action)
        for n in used:
            frames[n].save(out / f"{n:03d}.png")
        print(f"ação {action}: {len(used)} frames salvos em {out} ({', '.join(map(str, used))})")
