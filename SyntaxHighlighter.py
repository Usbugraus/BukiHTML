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

    for tag, style in TAG_COLORS.items():
        widget.tag_remove(tag, "1.0", "end")

    for m in re.finditer(r"<!--.*?-->", content, re.S):
        widget.tag_add(
            "comment",
            f"1.0+{m.start()}c",
            f"1.0+{m.end()}c"
        )

    for m in re.finditer(r"<([^>]+)>", content):
        start = m.start(1)
        end = m.end(1)

        widget.tag_add(
            "tag",
            f"1.0+{start}c",
            f"1.0+{end}c"
        )

        tag_content = m.group(1)

        for am in re.finditer(r'(\w+)=(".*?"|\'.*?\')', tag_content):
            a_start = start + am.start(1)
            a_end = start + am.end(1)
            v_start = start + am.start(2)
            v_end = start + am.end(2)

            widget.tag_add(
                "attribute",
                f"1.0+{a_start}c",
                f"1.0+{a_end}c"
            )
            widget.tag_add(
                "value",
                f"1.0+{v_start}c",
                f"1.0+{v_end}c"
            )