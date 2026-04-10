import tkinter as tk
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
with open(os.path.join(data_directory, "SyntaxHighlighterColors.json"), "r", encoding="utf-8") as f:
    TAG_COLORS = json.load(f)
    
with open(os.path.join(data_directory, "AutoCompleterNames.json"), "r", encoding="utf-8") as f:
    names = json.load(f)
    
for key in TAG_COLORS:
    color, font = TAG_COLORS[key]
    TAG_COLORS[key] = (color, tuple(font))

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

def md2html_dialog(parent, language="türkçe"):
    global TAG_COLORS, names
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
    elif language == "русский":
        w.title("Из Markdown в HTML")
        
    md_frame = tk.LabelFrame(w, text="Markdown", bd=1, relief="raised", padx=5, pady=5)
    md_frame.pack(padx=10, pady=(10, 0))
    
    md_text = tk.Text(md_frame, bd=1, padx=5, pady=5, font=("Consolas", 9), width=70, height=15, wrap="none")
    
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
    
    html_text = tk.Text(html_frame, bd=1, padx=5, pady=5, font=("Consolas", 9), width=70, height=15, wrap="none")
    
    for tag, style in TAG_COLORS.items():
        html_text.tag_config(
            tag,
            foreground=style[0],
            selectforeground="white",
            font=style[1]
        )
        
    hscroll = tk.Scrollbar(html_frame)
    hscroll.pack(side="right", pady=5, fill="y")
    hscroll.config(command=html_text.yview)

    hscroll_h = tk.Scrollbar(html_frame, orient="horizontal")
    hscroll_h.pack(side="bottom", fill="x")
    hscroll_h.config(command=html_text.xview)
    
    html_text.config(xscrollcommand=hscroll_h.set, yscrollcommand=hscroll.set)
    html_text.pack()
    
    def update_from_md(event=None):

        md = md_text.get("1.0", "end-1c")
        html = md_to_html(md_text=md)

        html_text.delete("1.0", tk.END)
        html_text.insert("1.0", html)

        highlighter(html_text, TAG_COLORS)
        
    def update_from_html(event=None):

        html = html_text.get("1.0", "end-1c")
        md = html_to_md(html)

        md_text.delete("1.0", tk.END)
        md_text.insert("1.0", md)
        
        highlighter(html_text, TAG_COLORS)

    md_text.bind("<KeyRelease>", update_from_md)
    html_text.bind("<KeyRelease>", update_from_html)
    
    AutoCompleter(html_text, names)