#!/usr/bin/env python3
"""Script to detect and optionally insert placeholder docstrings into src/unyts.

Usage:
  python dev/add_docstrings.py         # just print report
  python dev/add_docstrings.py --apply # modify files in-place (backups created)
"""
from __future__ import annotations
import ast
import os
import argparse
from typing import List, Dict

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(WORKSPACE_ROOT, "src", "unyts")


def find_nodes_missing_docstrings(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    try:
        tree = ast.parse(src, filename=path)
    except Exception as e:
        return [{"file": path, "kind": "parse-error", "name": "", "lineno": 0, "docstring": str(e)}]

    results = []

    def record(kind, name, lineno, doc):
        results.append({"file": path, "kind": kind, "name": name, "lineno": lineno, "docstring": doc or ""})

    class Checker(ast.NodeVisitor):
        def __init__(self):
            self.current_class = None

        def visit_ClassDef(self, node: ast.ClassDef):
            doc = ast.get_docstring(node)
            if not doc or len(doc.strip()) < 20:
                record("class", node.name, node.lineno, doc)
            prev = self.current_class
            self.current_class = node.name
            self.generic_visit(node)
            self.current_class = prev

        def visit_FunctionDef(self, node: ast.FunctionDef):
            doc = ast.get_docstring(node)
            kind = "method" if self.current_class else "function"
            name = f"{self.current_class}.{node.name}" if self.current_class else node.name
            if not doc or len(doc.strip()) < 20:
                record(kind, name, node.lineno, doc)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
            self.visit_FunctionDef(node)

    # module docstring
    mdoc = ast.get_docstring(tree)
    if not mdoc or len(mdoc.strip()) < 20:
        record("module", os.path.basename(path), 1, mdoc)

    Checker().visit(tree)
    return results


def insert_placeholders(path: str, findings: List[Dict]) -> int:
    """Insert placeholder docstrings into file for the provided findings.
    Returns number of insertions made.
    """
    if not findings:
        return 0
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # sort findings by lineno descending so insertions don't affect later indices
    findings_sorted = sorted([f for f in findings if f.get("lineno")], key=lambda x: x["lineno"], reverse=True)
    insertions = 0

    for item in findings_sorted:
        kind = item["kind"]
        name = item["name"]
        lineno = item["lineno"]

        if kind == "module":
            # put module docstring at top (after shebang and encoding if present)
            insert_at = 0
            # skip shebang
            if lines and lines[0].startswith("#!"):
                insert_at = 1
            # skip encoding comment
            if len(lines) > insert_at and lines[insert_at].lstrip().startswith("#") and "coding" in lines[insert_at]:
                insert_at += 1
            placeholder = '"""TODO: Add module description for %s."""\n\n' % name
            lines.insert(insert_at, placeholder)
            insertions += 1
            continue

        # for class/function/method: find signature end line
        idx = lineno - 1
        if idx < 0 or idx >= len(lines):
            continue
        # find the line that ends with ':' which closes the def/class signature
        sig_end = idx
        while sig_end < len(lines) and not lines[sig_end].rstrip().endswith(":" ):
            sig_end += 1
        if sig_end >= len(lines):
            continue
        # compute indentation: take leading whitespace of signature line then add 4 spaces
        sig_line = lines[sig_end]
        leading = sig_line[:len(sig_line) - len(sig_line.lstrip(" \t"))]
        indent = leading + ("    " if "\t" not in leading else "\t")
        placeholder = indent + '"""TODO: Add description for %s %s."""\n' % (kind, name)
        insert_at = sig_end + 1
        lines.insert(insert_at, placeholder)
        insertions += 1

    if insertions:
        # make a backup
        bak = path + ".bak"
        if not os.path.exists(bak):
            with open(bak, "w", encoding="utf-8") as bf:
                bf.writelines(open(path, "r", encoding="utf-8").readlines())
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return insertions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Modify files in-place (creates .bak backups)")
    args = parser.parse_args()

    all_findings = []
    for dirpath, dirnames, filenames in os.walk(SRC_DIR):
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            findings = find_nodes_missing_docstrings(path)
            if findings:
                all_findings.extend(findings)
                if args.apply:
                    # filter to this file
                    count = insert_placeholders(path, findings)
                    print(f"Updated {path}: inserted {count} docstrings")

    print(f"Total missing/short docstrings found: {len(all_findings)}")
    # write a report next to the script for review
    import json
    report_path = os.path.join(os.path.dirname(__file__), "docstring_report.json")
    with open(report_path, "w", encoding="utf-8") as rf:
        json.dump(all_findings, rf, indent=2)
    print(f"Report written to {report_path}")


if __name__ == "__main__":
    main()
