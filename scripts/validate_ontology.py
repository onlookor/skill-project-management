#!/usr/bin/env python3
"""Validate the self-authored ontology and its negative fixtures with pyshacl.

This script is optional tooling.  It is not a runtime prerequisite of the
project: missing dependencies are reported as "无法评估" (exit 2) rather than
silently passing.

Exit codes: 0 all expected results, 1 unexpected result, 2 cannot evaluate.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ONTO = ROOT / "ontology"
SHAPES_FILE = ONTO / "pmbok8-shapes.ttl"
DATA_FILES = sorted(p for p in ONTO.glob("*.ttl") if p.name != SHAPES_FILE.name)
BASE = "https://example.org/pm#"


def _load_deps():
    try:
        from rdflib import Graph
        from pyshacl import validate
    except ImportError as exc:
        print(f"无法评估：缺少依赖（{exc.name}）。安装后可运行：python3 -m pip install rdflib pyshacl",
              file=sys.stderr)
        raise SystemExit(2)
    return Graph, validate


def build_graph(Graph):
    g = Graph()
    for path in DATA_FILES:
        g.parse(path, format="turtle")
    return g


def run(validate, data_graph, shapes_file=SHAPES_FILE):
    return validate(
        data_graph,
        shacl_graph=str(shapes_file),
        inference="none",
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
    )


def summary(conforms, text):
    lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join(lines[:20])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", action="store_true",
                        help="run each negative fixture and check the expected shape fires")
    parser.add_argument("--graph", help="validate an extra Turtle graph instead of the ontology files")
    args = parser.parse_args()

    Graph, validate = _load_deps()
    shapes_graph_conforms = True
    failures = 0

    if args.graph:
        target = Graph()
        target.parse(args.graph, format="turtle")
    else:
        target = build_graph(Graph)

    conforms, _, text = run(validate, target)
    print(f"ontology: {'conforms' if conforms else 'violations'} "
          f"({len(target)} triples, {len(DATA_FILES)} data files)")
    if not conforms:
        print(summary(conforms, text))
        failures += 1

    if args.matrix:
        manifest = json.loads((ONTO / "fixtures" / "manifest.json").read_text())
        valid = ONTO / "fixtures" / "valid.ttl"
        vg = Graph()
        vg.parse(valid, format="turtle")
        vconf, _, vtext = run(validate, vg)
        print(f"fixture valid.ttl: {'conforms' if vconf else 'violations'}")
        if not vconf:
            print(summary(vconf, vtext))
            failures += 1

        print(f"{'shape':38} {'fixture':44} result")
        for shape, entry in sorted(manifest.items()):
            fname = entry["fixture"]
            message = entry["message"]
            fg = Graph()
            fg.parse(ONTO / "fixtures" / fname, format="turtle")
            conf, _, rtext = run(validate, fg)
            detected = (not conf) and (message in rtext)
            result = "detected" if detected else ("conforms" if conf else "wrong-shape")
            if not detected:
                failures += 1
            print(f"{shape:38} {fname:44} {result}")
        print(f"matrix: {len(manifest)} shapes, {failures} unexpected")

    raise SystemExit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()
