import tkinter as tk
import re

TAG_COLORS = {
    "tag": ["#0000bf", ("Consolas", 10)],
    "attribute": ["#bf0000", ("Consolas", 10)],
    "value": ["#00bf00", ("Consolas", 10)],
    "comment": ["#808080", ("Consolas", 10, "italic")],
}

def highlighter(widget):
    content = widget.get("1.0", "end-1c")

    for tag in TAG_COLORS:
        widget.tag_remove(tag, "1.0", "end")

    for m in re.finditer(r"<![^\n>]*>?", content):
        widget.tag_add(
            "comment",
            f"1.0+{m.start()}c",
            f"1.0+{m.end()}c"
        )

    for m in re.finditer(r"<!--.*?-->", content, re.S):
        widget.tag_add(
            "comment",
            f"1.0+{m.start()}c",
            f"1.0+{m.end()}c"
        )

    for m in re.finditer(r"<([^>]+)>", content):
        base = m.start(1)
        text = m.group(1)

        widget.tag_add("tag", f"1.0+{base}c", f"1.0+{m.end(1)}c")

        for am in re.finditer(r'(\w+)=', text):
            widget.tag_add(
                "attribute",
                f"1.0+{base + am.start(1)}c",
                f"1.0+{base + am.end(1)}c"
            )

        for vm in re.finditer(r'=(\"[^\"]*\"|\'[^\']*\')', text):
            widget.tag_add(
                "value",
                f"1.0+{base + vm.start(1)}c",
                f"1.0+{base + vm.end(1)}c"
            )

    for m in re.finditer(r"<[^\n>]*", content):
        base = m.start() + 1
        text = m.group()[1:]

        widget.tag_add(
            "tag",
            f"1.0+{base}c",
            f"1.0+{base + len(text)}c"
        )

        for am in re.finditer(r'(\w+)=', text):
            widget.tag_add(
                "attribute",
                f"1.0+{base + am.start(1)}c",
                f"1.0+{base + am.end(1)}c"
            )

        for vm in re.finditer(
            r'=(\"[^\"]*\"|\"[^\"]*$|\'[^\']*\'|\'[^\']*$)',
            text
        ):
            widget.tag_add(
                "value",
                f"1.0+{base + vm.start(1)}c",
                f"1.0+{base + vm.end(1)}c"
            )