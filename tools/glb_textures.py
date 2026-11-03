#!/usr/bin/env python3
"""
Swap or clone the textures baked into .glb models.

    # replace every embedded image called <name> (in all models) with assets/textures/<name>.png
    python tools/glb_textures.py swap mossy_cobble forest_grass ...      (no names = all of assets/textures)

    # make a copy of a model with one texture swapped for another (new floor/wall/roof pieces)
    python tools/glb_textures.py clone assets/models/env/floor_cobble.glb assets/models/env/floor_dirt_road.glb mossy_cobble=dirt_road

Images are matched by their glTF image name (which is the texture file name without .png). The binary chunk is
rebuilt so offsets stay valid; geometry, materials and UVs are untouched.
"""
import glob
import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_glb(path):
    b = open(path, "rb").read()
    assert b[:4] == b"glTF", path
    jlen = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + jlen])
    off = 20 + jlen
    bin_ = b""
    if off < len(b):
        blen = struct.unpack("<I", b[off:off + 4])[0]
        bin_ = b[off + 8:off + 8 + blen]
    return j, bin_


def write_glb(path, j, views):
    """views: list of bytes, one per bufferView (in order)."""
    out = bytearray()
    for i, data in enumerate(views):
        while len(out) % 4:
            out.append(0)
        j["bufferViews"][i]["byteOffset"] = len(out)
        j["bufferViews"][i]["byteLength"] = len(data)
        out += data
    while len(out) % 4:
        out.append(0)
    j["buffers"] = [{"byteLength": len(out)}]
    js = json.dumps(j, separators=(",", ":")).encode()
    while len(js) % 4:
        js += b" "
    total = 12 + 8 + len(js) + 8 + len(out)
    with open(path, "wb") as f:
        f.write(b"glTF" + struct.pack("<II", 2, total))
        f.write(struct.pack("<I", len(js)) + b"JSON" + js)
        f.write(struct.pack("<I", len(out)) + b"BIN\x00" + bytes(out))


def split_views(j, bin_):
    return [bin_[v.get("byteOffset", 0):v.get("byteOffset", 0) + v["byteLength"]] for v in j.get("bufferViews", [])]


def replace_images(j, views, mapping):
    """mapping: image name -> (new name, png bytes). Returns number replaced."""
    n = 0
    for img in j.get("images", []):
        name = img.get("name", "")
        if name in mapping and "bufferView" in img:
            new_name, data = mapping[name]
            views[img["bufferView"]] = data
            img["name"] = new_name
            img["mimeType"] = "image/png"
            n += 1
    return n


def png(name):
    p = os.path.join(ROOT, "assets/textures", name + ".png")
    return open(p, "rb").read()


def swap(names):
    if not names:
        names = [os.path.basename(p)[:-4] for p in glob.glob(os.path.join(ROOT, "assets/textures/*.png"))]
    mapping = {n: (n, png(n)) for n in names if n != "diag_missing"}
    total = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "assets/models/**/*.glb"), recursive=True)):
        j, bin_ = read_glb(path)
        views = split_views(j, bin_)
        k = replace_images(j, views, mapping)
        if k:
            write_glb(path, j, views)
            total += k
    print(f"swapped {total} embedded image(s) for {len(mapping)} texture(s)")


def clone(src, dst, pairs):
    j, bin_ = read_glb(os.path.join(ROOT, src))
    views = split_views(j, bin_)
    mapping = {}
    for p in pairs:
        old, new = p.split("=")
        mapping[old] = (new, png(new))
    k = replace_images(j, views, mapping)
    if not k:
        sys.exit(f"{src}: no image named {list(mapping)}")
    write_glb(os.path.join(ROOT, dst), j, views)
    print(f"wrote {dst}")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "swap":
        swap(sys.argv[2:])
    elif len(sys.argv) >= 5 and sys.argv[1] == "clone":
        clone(sys.argv[2], sys.argv[3], sys.argv[4:])
    else:
        print(__doc__)
