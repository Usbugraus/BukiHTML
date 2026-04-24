import tkinter as tk
from tkinter import ttk
import markdown
import html2text
import ctypes, os, sys, json
from ToolWindow import toolwindow
from SyntaxHighlighter import highlighter
from AutoCompleter import AutoCompleter

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

data_directory = os.path.join(os.path.dirname(__file__), "Data")
    
with open(os.path.join(data_directory, "AutoCompleterNames.json"), "r", encoding="utf-8") as f:
    names = json.load(f)

def html_to_md(html_text=""):
    return html2text.html2text(html_text)

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

def md2html_dialog(parent, tag_colors, language="türkçe", font_size=9):
    global names
    w = tk.Toplevel(parent)
    w.resizable(False, False)
    w.lift()
    w.focus()
    w.transient(parent)
    w.focus_force()
    w.grab_set()
    toolwindow(w)

    style = ttk.Style()
    style.theme_use("default")

    style.configure("TFrame", background="SystemButtonFace")
    style.configure("TLabelFrame", background="SystemButtonFace")

    style.configure("TScrollbar", background="SystemButtonFace", troughcolor="#bfbfbf", arrowsize=14)
    style.map("TScrollbar", background=[("active", "SystemButtonFace"), ("!active", "SystemButtonFace")], relief=[("pressed", "sunken")])

    style.configure("Out.TFrame", background="SystemButtonFace", borderwidth=1, relief=tk.RAISED)

    style.configure("In.TFrame", background="SystemButtonFace", borderwidth=1, relief=tk.SUNKEN)

    style.configure("Out.TLabelframe", background="SystemButtonFace", borderwidth=1, relief=tk.RAISED)

    style.configure("In.TLabelframe", background="SystemButtonFace", borderwidth=1, relief=tk.SUNKEN)
    
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
    elif language == "русский":
        w.title("Из Markdown в HTML")
        
    md_frame = ttk.LabelFrame(w, text="Markdown", style="Out.TLabelframe", padding=5)
    md_frame.pack(padx=10, pady=(10, 0))
    
    md_text = tk.Text(md_frame, bd=1, padx=5, pady=5, font=("Consolas", font_size), width=60 if font_size < 12 else 30, height=12 if font_size < 12 else 8, wrap="none")
    
    mscroll = ttk.Scrollbar(md_frame)
    mscroll.pack(side="right", fill="y")
    mscroll.config(command=md_text.yview)

    mscroll_h = ttk.Scrollbar(md_frame, orient="horizontal")
    mscroll_h.pack(side="bottom", fill="x")
    mscroll_h.config(command=md_text.xview)
    
    md_text.config(xscrollcommand=mscroll_h.set, yscrollcommand=mscroll.set)
    md_text.pack()
    
    html_frame = ttk.LabelFrame(w, text="HTML", style="Out.TLabelframe", padding=5)
    html_frame.pack(padx=10, pady=10)
    
    html_text = tk.Text(html_frame, bd=1, padx=5, pady=5, font=("Consolas", font_size), width=60 if font_size < 12 else 30, height=12 if font_size < 12 else 8, wrap="none")
    
    for tag, style in tag_colors.items():
        html_text.tag_config(
            tag,
            foreground=style[0],
            selectforeground="white",
            font=style[1]
        )
        
    hscroll = ttk.Scrollbar(html_frame)
    hscroll.pack(side="right", fill="y")
    hscroll.config(command=html_text.yview)

    hscroll_h = ttk.Scrollbar(html_frame, orient="horizontal")
    hscroll_h.pack(side="bottom", fill="x")
    hscroll_h.config(command=html_text.xview)
    
    html_text.config(xscrollcommand=hscroll_h.set, yscrollcommand=hscroll.set)
    html_text.pack()
    
    def update_from_md(event=None):

        md = md_text.get("1.0", "end-1c")
        html = md_to_html(md_text=md)

        html_text.delete("1.0", tk.END)
        html_text.insert("1.0", html)

        highlighter(html_text, tag_colors)
        
    def update_from_html(event=None):

        html = html_text.get("1.0", "end-1c")
        md = html_to_md(html)

        md_text.delete("1.0", tk.END)
        md_text.insert("1.0", md)
        
        highlighter(html_text, tag_colors)

    md_text.bind("<KeyRelease>", update_from_md)
    html_text.bind("<KeyRelease>", update_from_html)
    
    AutoCompleter(html_text, names)