"""Minimal KiCad .kicad_pcb parser: footprints, pads and Edge.Cuts outline."""
import re

_TOKEN = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+')


def parse(text):
    stack = [[]]
    for t in _TOKEN.findall(text):
        if t == "(":
            stack.append([])
        elif t == ")":
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(t[1:-1] if t.startswith('"') else t)
    return stack[0][0]


def find(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def first(node, key):
    r = find(node, key)
    return r[0] if r else None


def load(path):
    with open(path, encoding="utf-8") as f:
        return parse(f.read())


def footprints(board):
    out = []
    for fp in find(board, "footprint"):
        at = first(fp, "at")
        ref = next((p[2] for p in find(fp, "property") if p[1] == "Reference"), "")
        out.append(dict(lib=fp[1], ref=ref, x=float(at[1]), y=float(at[2]),
                        rot=float(at[3]) if len(at) > 3 else 0.0,
                        layer=first(fp, "layer")[1], node=fp))
    return out


def pads(fp):
    """Pads of a footprint in footprint-local coordinates."""
    out = []
    for p in find(fp["node"], "pad"):
        at, size = first(p, "at"), first(p, "size")
        drill = first(p, "drill")
        out.append(dict(name=p[1], kind=p[2], shape=p[3],
                        x=float(at[1]), y=float(at[2]),
                        w=float(size[1]), h=float(size[2]),
                        drill=float(drill[1]) if drill and len(drill) > 1 and drill[1] != "oval" else None))
    return out


def edge_lines(board):
    out = []
    for g in find(board, "gr_line"):
        if first(g, "layer")[1] == "Edge.Cuts":
            s, e = first(g, "start"), first(g, "end")
            out.append(((float(s[1]), float(s[2])), (float(e[1]), float(e[2]))))
    return out
