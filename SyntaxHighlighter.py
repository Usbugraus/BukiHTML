import tkinter as tk
import re, keyword
import builtins

SYNTAX_COLORS = {
    "keyword": ["#bf0000", ("Consolas", 10, "bold")],
    "string": ["#00bf00", ("Consolas", 10)],
    "comment": ["#808080", ("Consolas", 10, "italic")],
    "number": ["#0000bf", ("Consolas", 10)],
    "builtin": ["#bf8000", ("Consolas", 10)],
    "operator": ["#404040", ("Consolas", 10)],
}

def highlight(widget, event=None):
    content = widget.get("1.0", "end-1c")

    for tag in SYNTAX_COLORS:
        widget.tag_remove(tag, "1.0", "end")
        
    def has_tag_range(start, end, tag):
        index = start
        while widget.compare(index, "<", end):
            if tag in widget.tag_names(index):
                return True
            index = widget.index(f"{index}+1c")
        return False
    
    triple_pattern = r'("""|\'\'\')'
    matches = list(re.finditer(triple_pattern, content))
    i = 0
    while i < len(matches):
        start_idx = matches[i].start()
        t = matches[i].group(1)
        # Bir sonraki eşleşme varsa kapama olarak kullan
        if i+1 < len(matches) and matches[i+1].group(1) == t:
            end_idx = matches[i+1].end()
            start = f"1.0+{start_idx}c"
            end   = f"1.0+{end_idx}c"
            widget.tag_add("string", start, end)
            i += 2
        else:
            start = f"1.0+{start_idx}c"
            widget.tag_add("string", start, "end-1c")
            i += 1

    lines = content.split("\n")
    pos = 0
    for line in lines:
        single_open = False
        open_idx = None
        i = 0
        while i < len(line):
            if line[i] in ('"', "'"):
                # Üçlü tırnakları atla
                if i+2 < len(line) and line[i:i+3] in ('"""',"'''"):
                    i += 2
                else:
                    if not single_open:
                        open_idx = i
                    single_open = not single_open
            i += 1
        if single_open and open_idx is not None:
            start = f"1.0+{pos + open_idx}c"
            end   = f"1.0+{pos + len(line)}c"
            widget.tag_add("string", start, end)
        pos += len(line)+1

    for m in re.finditer(r"(\".*?\"|\'.*?\')", content):
        start = f"1.0+{m.start()}c"
        end   = f"1.0+{m.end()}c"
        widget.tag_add("string", start, end)

    for m in re.finditer(r"#.*", content):
        start = f"1.0+{m.start()}c"
        end   = f"1.0+{m.end()}c"
        if has_tag_range(start, end, "string"): 
            continue
        widget.tag_add("comment", start, end)

    for m in re.finditer(r"\b\d+(\.\d+)?\b", content):
        start = f"1.0+{m.start()}c"
        end   = f"1.0+{m.end()}c"
        if has_tag_range(start, end, "string") or has_tag_range(start, end, "comment"):
            continue
        widget.tag_add("number", start, end)
    
    for kw in keyword.kwlist:
        for m in re.finditer(rf"\b{kw}\b", content):
            start = f"1.0+{m.start()}c"
            end   = f"1.0+{m.end()}c"
            if has_tag_range(start, end, "string") or has_tag_range(start, end, "comment"):
                continue
            widget.tag_add("keyword", start, end)

    builtins_list = [b for b in dir(builtins)
                     if callable(getattr(builtins, b)) and b.isidentifier()]
    for b in builtins_list:
        for m in re.finditer(rf"\b{re.escape(b)}\b", content):
            start = f"1.0+{m.start()}c"
            end   = f"1.0+{m.end()}c"
            if has_tag_range(start, end, "string") or has_tag_range(start, end, "comment") or has_tag_range(start, end, "keyword"):
                continue
            widget.tag_add("builtin", start, end)

    operator_pattern = r"""
        (\+=|-=|\*=|/=|%=|//=|\*\*|
         ==|!=|<=|>=|
         =|<|>|
         \+|-|\*|/|%|
         \b(and|or|not)\b)
    """
    for m in re.finditer(operator_pattern, content, re.VERBOSE):
        start = f"1.0+{m.start()}c"
        end   = f"1.0+{m.end()}c"
        if has_tag_range(start, end, "string") or has_tag_range(start, end, "comment"):
            continue
        widget.tag_add("operator", start, end)
