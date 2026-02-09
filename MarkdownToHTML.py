import tkinter as tk
import markdown
import ctypes, os, sys
from ToolWindow import toolwindow
from SyntaxHighlighter import highlighter

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass
    
TAG_COLORS = {
    "tag": ["#0000bf", ("Consolas", 10)],
    "attribute": ["#bf0000", ("Consolas", 10)],
    "value": ["#00bf00", ("Consolas", 10)],
    "comment": ["#808080", ("Consolas", 10, "italic")],
}

def md_to_html(md_text=""):
    html = markdown.markdown(
        md_text,
        extensions = [
            "abbr",
            "admonition",
            "attr_list",
            "def_list",
            "fenced_code",
            "footnotes",
            "legacy_attrs",
            "legacy_em",
            "md_in_html",
            "meta",
            "nl2br",
            "sane_lists",
            "smarty",
            "tables",
            "wikilinks",
        ],
        output_format="html5",
    )
    return html

def md2html_dialog(parent, language="türkçe"):
    global TAG_COLORS
    w = tk.Toplevel(parent)
    w.resizable(False, False)
    w.lift()
    w.focus()
    w.transient(parent)
    w.focus_force()
    w.grab_set()
    toolwindow(w)
    
    if hasattr(sys, "_MEIPASS"):
        icon_path = os.path.join(sys._MEIPASS, "Icon.ico")
    else:
        icon_path = os.path.join(os.path.dirname(__file__), "Icon.ico")

    if os.path.exists(icon_path):
        w.iconbitmap(icon_path)
    
    if language == "türkçe":
        w.title("Markdown'dan HTML'e")
    elif language == "english":
        w.title("Markdown to HTML")
    elif language == "deutsch":
        w.title("Von Markdown zu HTML")
        
        
    md_frame = tk.LabelFrame(w, text="Markdown", bd=1, relief="raised", padx=5, pady=5)
    md_frame.pack(padx=10, pady=(10, 0))
    
    md_text = tk.Text(md_frame, bd=1, padx=5, pady=5, font=("Consolas", 10), width=70, height=15, wrap="none")
    
    mscroll = tk.Scrollbar(md_frame)
    mscroll.pack(side="right", pady=5, fill="y")
    mscroll.config(command=md_text.yview)

    mscroll_h = tk.Scrollbar(md_frame, orient="horizontal")
    mscroll_h.pack(side="bottom", fill="x")
    mscroll_h.config(command=md_text.xview)
    
    md_text.config(xscrollcommand=mscroll_h.set, yscrollcommand=mscroll.set)
    md_text.pack()
    
    html_frame = tk.LabelFrame(w, text="HTML", bd=1, relief="raised", padx=5, pady=5)
    html_frame.pack(padx=10, pady=10)
    
    toolbar = tk.Frame(html_frame, bd=1, relief="raised", padx=3, pady=3)
    toolbar.pack(pady=(0, 5), anchor="w")
    
    html_text = tk.Text(html_frame, bd=1, padx=5, pady=5, font=("Consolas", 10), width=70, height=15, wrap="none")
    
    for tag, style in TAG_COLORS.items():
        html_text.tag_config(
            tag,
            foreground=style[0],
            selectforeground="white",
            font=style[1]
        )
        
    html_text.config(state="disabled")
    
    def copy_html():
        html = html_text.get("1.0", "end-1c")
        html_text.clipboard_clear()
        html_text.clipboard_append(html)
        copy.config(state="disabled")
    
    copy = tk.Button(toolbar, width=5, pady=4, text="", bd=0, font=("Segoe Fluent Icons", 10), activebackground="#ffff00", command=copy_html)
    copy.pack(side="bottom", anchor="sw")
        
    hscroll = tk.Scrollbar(html_frame)
    hscroll.pack(side="right", pady=5, fill="y")
    hscroll.config(command=html_text.yview)

    hscroll_h = tk.Scrollbar(html_frame, orient="horizontal")
    hscroll_h.pack(side="bottom", fill="x")
    hscroll_h.config(command=html_text.xview)
    
    html_text.config(xscrollcommand=hscroll_h.set, yscrollcommand=hscroll.set)
    html_text.pack()
    
    def update(event=None):
        if not md_text.edit_modified():
            return

        md = md_text.get("1.0", "end-1c")
        html = md_to_html(md_text=md)

        html_text.config(state="normal")
        html_text.delete("1.0", tk.END)
        html_text.insert("1.0", html)

        highlighter(html_text)

        html_text.config(state="disabled")

        md_text.edit_modified(False)
    
    md_text.bind("<<Modified>>", update)