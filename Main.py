import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import tempfile
import re
import ctypes
import os, sys
import webbrowser
import json, traceback
from ToolTip import ToolTip
from ToolWindow import toolwindow
from MarkdownToHTML import md2html_dialog
from SyntaxHighlighter import highlighter
from ErrorHandler import error_handler

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

changed = False
current_file = None
filepath = None
font_size = 10
TAG_COLORS = {
    "tag": ["#0000bf", ("Consolas", font_size)],
    "attribute": ["#bf0000", ("Consolas", font_size)],
    "value": ["#00bf00", ("Consolas", font_size)],
    "comment": ["#808080", ("Consolas", 10, "italic")],
}

win = tk.Tk()
win.geometry("800x600")
win.minsize(700, 500)
win.grid_rowconfigure(1, weight=1)
win.grid_columnconfigure(0, weight=1)
win.grid_columnconfigure(1, weight=1)

def report_callback_exception(exc_type, exc_value, exc_traceback):
    error_handler(exc_type, exc_value, exc_traceback, parent=win, language=language.get())

win.report_callback_exception = report_callback_exception

configuration_file = "Configuration.json"

if os.path.exists(configuration_file):
    with open(configuration_file, "r", encoding="utf-8") as f:
        configuration = json.load(f)
else:
    configuration = {
        "show_tooltip": True,
        "language": "english",
        "auto_save": False
        }
          
show_tooltip = tk.BooleanVar(value=configuration["show_tooltip"])
language = tk.StringVar(value=configuration["language"])
auto_save = tk.BooleanVar(value=configuration["auto_save"])
fullscreen = tk.BooleanVar(value=False)
cover = tk.BooleanVar(value=False)

menu_labels = {}

editor = tk.Frame(win, bd=1, relief="raised", width=800, height=600)
editor.grid(padx=10, pady=10, row=1, column=0, columnspan=2, sticky="nsew")

status_bar = tk.Label(win, bd=1, relief="raised", text="", padx=5, pady=5, anchor="w")
status_bar.grid(padx=10, pady=(0, 10), row=2, column=0, columnspan=2, sticky="ew")

text = tk.Text(editor, wrap="none", width=60, height=20, font=("Consolas", 10), bd=1, undo=True, padx=5, pady=5)

for tag, style in TAG_COLORS.items():
    text.tag_config(
        tag,
        foreground=style[0],
        selectforeground="white",
        font=style[1]
    )

def highlight(widget):
    highlighter(widget)

def save_file(force=False):
    global current_file, changed

    if current_file is None:
        save_as()
        return

    if changed or force:
        with open(current_file, "w", encoding="utf-8") as f:
            f.write(text.get("1.0", "end-1c"))

        win.title(f'BukiHTML - {current_file}')
        changed = False
        save.config(state="disabled")
        update_status()

def save_as():
    global current_file, filepath

    if language.get() == "türkçe":
        filepath = filedialog.asksaveasfilename(
            defaultextension='.html',
            filetypes=[('HTML Dosyası', '*.html'), ('Tüm Dosyalar', '*.*')],
            title='Kaydet'
        )
    elif language.get() == "english":
        filepath = filedialog.asksaveasfilename(
            defaultextension='.html',
            filetypes=[('HTML Files', '*.html'), ('All Files', '*.*')],
            title='Save'
        )
    elif language.get() == "deutsch":
        filepath = filedialog.asksaveasfilename(
            defaultextension='.html',
            filetypes=[('HTML Dateien', '*.html'), ('Alle Dateien', '*.*')],
            title='Speichern'
        )

    if filepath:
        current_file = filepath
        win.title(f'BukiHTML - {filepath}')
        save_file(force=True)
        
def open_file():
    global filepath, current_file, changed
    
    if language.get() == "türkçe":
        filepath = filedialog.askopenfilename(title='Aç', filetypes=[('HTML Dosyası', '*.html'), ('Tüm dosyalar', '*.*')])
    elif language.get() == "english":
        filepath = filedialog.askopenfilename(title='Open', filetypes=[('HTML Files', '*.html'), ('All Files', '*.*')])
    elif language.get() == "deutsch":
        filepath = filedialog.askopenfilename(title='Öffnen', filetypes=[('HTML Dateien', '*.html'), ('Alle Dateien', '*.*')])
    
    if filepath:
        with open(filepath, 'r', encoding='utf-8') as file:
            opened_file = file.read()
        text.delete(1.0, tk.END)
        text.insert(1.0, opened_file)
        current_file = filepath
        win.title(f'BukiHTML - {current_file}')
        changed = False
        text.edit_modified(False)
        update()
        highlight(text)
        save.config(state="disabled")
        update_status()

def new_file():
    global current_file, filepath, changed
    if changed:
        if language.get() == "türkçe":
            confirm = messagebox.askyesnocancel("Kaydet", "Bu belgeyi kaydetmek istiyor musunuz?")
        elif language.get() == "english":
            confirm = messagebox.askyesnocancel("Save", "Do you want to save this document?")
        elif language.get() == "deutsch":
            confirm = messagebox.askyesnocancel("Speichern", "Möchten Sie dieses Dokument speichern?")
            
        if confirm:
            save_file()
        if confirm == False: 
            pass
        if confirm is None:
            return
    changed = False
    current_file = None
    filepath = None
    text.delete(1.0, tk.END)
    update_title()
    text.edit_modified(False)
    text.xview_moveto(0)
    text.yview_moveto(0)
    text.config(xscrollcommand=scroll_h.set, yscrollcommand=scroll.set)
    save.config(state="disabled")
    update_status()
    win.update_idletasks()

def update_title():
    if language.get() == "türkçe":
        title = "BukiHTML - Yeni" if current_file is None else f"BukiHTML - {current_file}"
    elif language.get() == "english":
        title = "BukiHTML - New" if current_file is None else f"BukiHTML - {current_file}"
    elif language.get() == "deutsch":
        title = "BukiHTML - Neu" if current_file is None else f"BukiHTML - {current_file}"
        
    if changed:
        title += " *"
    win.title(title)
        
def save_on_exit():
    global changed
    if changed:
        if language.get() == "türkçe":
            confirm = messagebox.askyesnocancel("Kaydet", "Bu belgeyi kaydetmek istiyor musunuz?")
        elif language.get() == "english":
            confirm = messagebox.askyesnocancel("Save", "Do you want to save this document?")
        elif language.get() == "deutsch":
            confirm = messagebox.askyesnocancel("Speichern", "Möchten Sie dieses Dokument speichern?")
            
        if confirm:
            save_file()
            win.destroy()
        if confirm == False: 
            win.destroy()
    else:
        win.destroy()
              
def undo_():
    try:
        text.edit_undo()
        update()
    except: pass
    
def redo_():
    try:
        text.edit_redo()
        update()
    except: pass
    
def update(event=None):
    global changed
    if text.edit_modified():
        changed = True
        update_title()
        text.edit_modified(False)
        save.config(state="normal")
        
def run_():
    global current_file
    if not current_file:
        code = text.get("1.0", "end")
        tmp_html = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8')
        tmp_html.write(code)
        tmp_html.close()
        webbrowser.open(tmp_html.name)
    else:
        save_file()
        webbrowser.open(current_file)
        
def show_about():
    if language.get() == "türkçe":
        messagebox.showinfo("Hakkında", "BukiHTML v1.2.0\n© Telif Hakkı 2025 Buğra US")
    elif language.get() == "english":
        messagebox.showinfo("About", "BukiHTML v1.2.0\n© Copyright 2025 Buğra US")
    elif language.get() == "deutsch":
        messagebox.showinfo("Über", "BukiHTML v1.2.0\n© Urheberrecht 2025 Buğra US")
    
def autosv(event):
    global current_file
    if current_file and auto_save.get():
        save_file()

if hasattr(sys, "_MEIPASS"):
    icon_path = os.path.join(sys._MEIPASS, "Icon.ico")
else:
    icon_path = os.path.join(os.path.dirname(__file__), "Icon.ico")

if os.path.exists(icon_path):
    win.iconbitmap(icon_path)

toolbar_frame = tk.Frame(win)
toolbar_frame.grid(row=0, column=0, sticky="ew")

file_toolbar = tk.Frame(toolbar_frame, bd=1, relief="raised", padx=3, pady=3)
file_toolbar.grid(row=0, column=0, padx=(10, 0), pady=(10, 0), sticky="w")

html_toolbar = tk.Frame(toolbar_frame, bd=1, relief="raised", padx=3, pady=3)
html_toolbar.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="w")

other_toolbar_frame = tk.Frame(win)
other_toolbar_frame.grid(row=0, column=1, sticky="e")

other_toolbar = tk.Frame(other_toolbar_frame, bd=1, relief="raised", padx=3, pady=3)
other_toolbar.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="e")

new = tk.Button(file_toolbar, text="", width=5, pady=4, bd=0, command=new_file, activebackground="yellow", font=("Segoe Fluent Icons", 10))
new.grid(row=0, column=0)

open_ = tk.Button(file_toolbar, text="", width=5, pady=4, bd=0, command=open_file, activebackground="yellow", font=("Segoe Fluent Icons", 10))
open_.grid(row=0, column=1)

save = tk.Button(file_toolbar, text="", width=5, pady=4, bd=0, command=save_file, activebackground="yellow", font=("Segoe Fluent Icons", 10), state=("normal" if not filepath else "disabled"))
save.grid(row=0, column=2)

run = tk.Button(html_toolbar, text="", width=5, pady=4, bd=0, command=run_, activebackground="#0040bf", font=("Segoe Fluent Icons", 10), activeforeground="white", fg="#0040bf")
run.grid(row=0, column=3)

about = tk.Button(other_toolbar, text="", width=5, pady=4, bd=0, command=show_about, activebackground="yellow", font=("Segoe Fluent Icons", 10))
about.grid(row=0, column=0, sticky="e")

scroll = tk.Scrollbar(editor)
scroll.pack(side="right", padx=(0, 5), pady=5, fill="y")
scroll.config(command=text.yview)

scroll_h = tk.Scrollbar(editor, orient="horizontal")
scroll_h.pack(side="bottom", padx=(5, 0), pady=(0, 5), fill="x")
scroll_h.config(command=text.xview)
text.config(xscrollcommand=scroll_h.set, yscrollcommand=scroll.set)

text.pack(fill="both", padx=(5, 0), pady=(5, 0), expand=True)

def indent(event=None):
    try:
        selection = text.tag_ranges("sel")
        if selection:
            start, end = selection
            lines = text.get(start, end).splitlines()
            indented = "\n".join("    "+line for line in lines)
            text.delete(start, end)
            text.insert(start, indented)
        else:
            text.insert("insert", "    ")
    except:
        text.insert("insert", "    ")
    return "break"

def unindent(event=None):
    try:
        selection = text.tag_ranges("sel")
        if selection:
            start, end = selection
            lines = text.get(start, end).splitlines()
            unindented = "\n".join(line[4:] if line.startswith("    ") else line for line in lines)
            text.delete(start, end)
            text.insert(start, unindented)
        else:
            cur_line = text.get("insert linestart", "insert lineend")
            if cur_line.startswith("    "):
                text.delete("insert linestart", "insert linestart+4c")
    except:
        pass
    return "break" 

def update_settings(*args):
    global menu_labels, configuration_file
    if language.get() == "türkçe":
        menu_labels = {
            "file":{"label": "Dosya",
                    "menus":[
                        "Yeni",
                        "Yeni Pencere",
                        "Aç",
                        "Kaydet",
                        "Farklı Kaydet",
                        "Çık"
                        ]
                    },
            "edit":{"label": "Düzen",
                    "menus":[
                        "Geri Al",
                        "Yinele",
                        "Kes",
                        "Kopyala",
                        "Yapıştır",
                        "Tümünü Seç",
                        "Satırı Girintile",
                        "Satırın Girintisini Azalt"
                        ]
                    },
            "view":{"label": "Görünüm",
                   "menus": [
                        "Yazı Tipi Boyutunu Arttır",
                        "Yazı Tipi Boyutunu Azalt",
                        "Varsayılan Yazı Tipi Boyutunu Ayarla",
                        "Tam Ekran",
                        "Ekranı Kapla"
                       ]
                   },
            "settings":{"label": "Ayarlar",
                        "menus":[
                            "Otomatik Kaydet",
                            "Araç İpuçlarını Göster",
                            "Dil"
                            ]
                        },
            "tools": {"label": "Araçlar",
                      "menus": [
                          "HTML Formları", ["Başlıklar", "Metin", "Diğer"], 
                          "Markdown'dan HTML'e",
                          ]
                      }
            }
    elif language.get() == "english":
        menu_labels = {
            "file":{"label": "File",
                    "menus":[
                        "New",
                        "New Window",
                        "Open",
                        "Save",
                        "Save As",
                        "Exit"
                        ]
                    },
            "edit":{"label": "Edit",
                    "menus":[
                        "Undo",
                        "Redo",
                        "Cut",
                        "Copy",
                        "Paste",
                        "Select All",
                        "Indent the line",
                        "Decrease the indent of the line"
                        ]
                    },
            "view":{"label": "View",
                   "menus": [
                        "Increase the Font Size",
                        "Decrease the Font Size",
                        "Set the Default Font Size",
                        "Fullscreen",
                        "Cover the Screen"
                       ]
                   },
            "settings":{"label": "Settings",
                        "menus":[
                            "Auto-Save",
                            "Show Tooltips",
                            "Language"
                            ]
                        },
            "tools": {"label": "Tools",
                      "menus": [
                          "HTML Forms", ["Headers", "Text", "Other"], 
                          "Markdown to HTML",
                          ]
                      }
            }
    elif language.get() == "deutsch":
        menu_labels = {
            "file":{"label": "Datei",
                    "menus":[
                        "Neu",
                        "Neues Fenster",
                        "Öffnen",
                        "Speichern",
                        "Speichern Unter",
                        "Ausgang"
                        ]
                    },
            "edit":{"label": "Ordnung",
                    "menus":[
                        "Rückgängig",
                        "Wiederholen",
                        "Schneiden",
                        "Kopieren",
                        "Einfügen",
                        "Alles Auswählen",
                        "Zeile Einrücken",
                        "Einzug Der Zeile Verringern"
                        ]
                    },
            "view":{"label": "Ansicht",
                   "menus": [
                        "Schriftgröße vergrößern",
                        "Schriftgröße verkleinern",
                        "Standard-Schriftgröße festlegen",
                        "Vollbild",
                        "Bildschirm abdecken"
                        ]
                   },
            "settings":{"label": "Einstellungen",
                        "menus":[
                            "Automatisch Speichern",
                            "Tooltipps Anzeigen",
                            "Sprache"
                            ]
                        },
            "tools": {"label": "Werkzeuge",
                      "menus": [
                          "HTML-Formulare", ["Titel", "Text", "Andere"], 
                          "Von Markdown zu HTML",
                          ]
                      }
            }
    
    if language.get() == "türkçe":
        ToolTip(about, "Hakkında", shown=show_tooltip.get())
        ToolTip(run, "Önizleme - Ctrl+P", shown=show_tooltip.get())
        ToolTip(save, "Kaydet - Ctrl+S", shown=show_tooltip.get())
        ToolTip(open_, "Aç - Ctrl+O", shown=show_tooltip.get())
        ToolTip(new, "Yeni - Ctrl+N", shown=show_tooltip.get())
        
    elif language.get() == "english":
        ToolTip(about, "About", shown=show_tooltip.get())
        ToolTip(run, "Preview - Ctrl+P", shown=show_tooltip.get())
        ToolTip(save, "Save - Ctrl+S", shown=show_tooltip.get())
        ToolTip(open_, "Open - Ctrl+O", shown=show_tooltip.get())
        ToolTip(new, "New - Ctrl+N", shown=show_tooltip.get())
        
    elif language.get() == "deutsch":
        ToolTip(about, "Über", shown=show_tooltip.get())
        ToolTip(run, "Vorschau - Ctrl+P", shown=show_tooltip.get())
        ToolTip(save, "Speichern - Ctrl+S", shown=show_tooltip.get())
        ToolTip(open_, "Öffnen - Ctrl+O", shown=show_tooltip.get())
        ToolTip(new, "Neu - Ctrl+N", shown=show_tooltip.get())
    
    menu.entryconfig(1, label=menu_labels["file"]["label"])
    file_menu.entryconfig(0, label=menu_labels["file"]["menus"][0])
    file_menu.entryconfig(1, label=menu_labels["file"]["menus"][1])
    file_menu.entryconfig(3, label=menu_labels["file"]["menus"][2])
    file_menu.entryconfig(4, label=menu_labels["file"]["menus"][3])
    file_menu.entryconfig(5, label=menu_labels["file"]["menus"][4])
    file_menu.entryconfig(7, label=menu_labels["file"]["menus"][5])
    
    menu.entryconfig(2, label=menu_labels["edit"]["label"])
    edit_menu.entryconfig(0, label=menu_labels["edit"]["menus"][0])
    edit_menu.entryconfig(1, label=menu_labels["edit"]["menus"][1])
    edit_menu.entryconfig(3, label=menu_labels["edit"]["menus"][2])
    edit_menu.entryconfig(4, label=menu_labels["edit"]["menus"][3])
    edit_menu.entryconfig(5, label=menu_labels["edit"]["menus"][4])
    edit_menu.entryconfig(6, label=menu_labels["edit"]["menus"][5])
    edit_menu.entryconfig(8, label=menu_labels["edit"]["menus"][6])
    edit_menu.entryconfig(9, label=menu_labels["edit"]["menus"][7])
    
    menu.entryconfig(3, label=menu_labels["view"]["label"])
    view_menu.entryconfig(0, label=menu_labels["view"]["menus"][0])
    view_menu.entryconfig(1, label=menu_labels["view"]["menus"][1])
    view_menu.entryconfig(2, label=menu_labels["view"]["menus"][2])
    view_menu.entryconfig(4, label=menu_labels["view"]["menus"][3])
    view_menu.entryconfig(5, label=menu_labels["view"]["menus"][4])
    
    menu.entryconfig(4, label=menu_labels["settings"]["label"])
    pre_menu.entryconfig(0, label=menu_labels["settings"]["menus"][0])
    pre_menu.entryconfig(1, label=menu_labels["settings"]["menus"][1])
    pre_menu.entryconfig(2, label=menu_labels["settings"]["menus"][2])
    
    menu.entryconfig(5, label=menu_labels["tools"]["label"])
    tool_menu.entryconfig(0, label=menu_labels["tools"]["menus"][0])
    tool_menu.entryconfig(1, label=menu_labels["tools"]["menus"][2])
    form_menu.entryconfig(0, label=menu_labels["tools"]["menus"][1][0])
    form_menu.entryconfig(1, label=menu_labels["tools"]["menus"][1][1])
    form_menu.entryconfig(2, label=menu_labels["tools"]["menus"][1][2])
    
    update_title()
    update_status()
    
    config = {
        "show_tooltip": show_tooltip.get(),
        "language": language.get(),
        "auto_save": auto_save.get()
        }
        
    with open(configuration_file, "w", encoding="utf-8") as f:
        cfile = json.dump(config, f, ensure_ascii=False, indent=4)
        
def update_fonts():
    global SYNTAX_COLORS
    text.config(font=("Consolas", font_size))

    for tag, style in TAG_COLORS.items():
        color = style[0]
        font_style = list(style[1])

        font_style[1] = font_size

        text.tag_configure(
            tag,
            foreground=color,
            font=tuple(font_style),
            selectforeground="#ffffff"
        )
        
def increase_size():
    global font_size
    if font_size < 48:
        font_size += 1
        update_fonts()
        highlight(text)

def decrease_size():
    global font_size
    if font_size > 6:
        font_size -= 1
        update_fonts()
        highlight(text)
        
def reset_size():
    global font_size
    font_size = 10
    update_fonts()
    highlight(text)
    
def update_view(*args):
    if fullscreen.get():
        win.attributes("-fullscreen", True)
    else:
        win.attributes("-fullscreen", False)
        
    if cover.get():
        toolbar_frame.grid_forget()
        other_toolbar_frame.grid_forget()
        status_bar.grid_forget()
    else:
        toolbar_frame.grid(row=0, column=0, sticky="ew")
        other_toolbar_frame.grid(row=0, column=1, sticky="e")
        status_bar.grid(padx=10, pady=(0, 10), row=2, column=0, columnspan=2, sticky="ew")
        
def update_status():
    global current_file
    if language.get() == "türkçe":
        newfile_status = "Yeni"
    if language.get() == "english":
        newfile_status = "New"
    if language.get() == "deutsch":
        newfile_status = "Neu"
    
    status_bar.config(text=f"{os.path.basename(current_file) if current_file else newfile_status} | {text.index('insert')}")

show_tooltip.trace_add("write", update_settings)
language.trace_add("write", update_settings)
auto_save.trace_add("write", update_settings)
fullscreen.trace_add("write", update_view)
cover.trace_add("write", update_view)

text.bind("<Shift-Tab>", unindent)
text.bind("<Tab>", indent)
text.bind("<<Modified>>", update)
win.bind("<Control-s>", lambda e: save_file())
win.bind("<Control-Shift-S>", lambda e: save_as())
win.bind("<Control-o>", lambda e: open_file())
win.bind("<Control-n>", lambda e: new_file())
win.bind("<Control-z>", lambda e: undo_())
win.bind("<Control-y>", lambda e: redo_())
win.bind("<Control-plus>", lambda e: increase_size())
win.bind("<Control-minus>", lambda e: decrease_size())
win.bind("<Control-Shift-R>", lambda e: reset_size())
win.bind("<Control-Shift-N>", lambda e: subprocess.Popen([sys.executable, __file__]))
win.bind("<Control-p>", lambda e: run_())

menu = tk.Menu(win)
win.config(menu=menu)

file_menu = tk.Menu(menu, tearoff=0)
file_menu.add_command(label="", command=new_file, accelerator="Ctrl+N")
file_menu.add_command(label="", command=lambda: subprocess.Popen([sys.executable, __file__]), accelerator="Ctrl+Shift+N")
file_menu.add_separator()
file_menu.add_command(label="", command=open_file, accelerator="Ctrl+O")
file_menu.add_command(label="", command=save_file, accelerator="Ctrl+S")
file_menu.add_command(label="", command=save_as, accelerator="Ctrl+Shift+S")
file_menu.add_separator()
file_menu.add_command(label="", command=lambda: win.destroy(), accelerator="Alt+F4")
menu.add_cascade(menu=file_menu, label="")

edit_menu = tk.Menu(menu, tearoff=0)
edit_menu.add_command(label="", command=undo_, accelerator="Ctrl+Z")
edit_menu.add_command(label="", command=redo_, accelerator="Ctrl+Y")
edit_menu.add_separator()
edit_menu.add_command(label="", command=lambda: text.event_generate('<<Cut>>'), accelerator="Ctrl+X")
edit_menu.add_command(label="", command=lambda: text.event_generate('<<Copy>>'), accelerator="Ctrl+C")
edit_menu.add_command(label="", command=lambda: text.event_generate('<<Paste>>'), accelerator="Ctrl+V")
edit_menu.add_command(label="", command=lambda: text.tag_add('sel', '1.0', 'end'), accelerator="Ctrl+A")
edit_menu.add_separator()
edit_menu.add_command(label="", command=indent, accelerator="Tab")
edit_menu.add_command(label="", command=unindent, accelerator="Shift+Tab")
menu.add_cascade(menu=edit_menu, label="")

view_menu = tk.Menu(menu, tearoff=0)
view_menu.add_command(label="", command=increase_size, accelerator="Ctrl++")
view_menu.add_command(label="", command=increase_size, accelerator="Ctrl+-")
view_menu.add_command(label="", command=reset_size, accelerator="Ctrl+Shift+R")
view_menu.add_separator()
view_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=fullscreen)
view_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=cover)
menu.add_cascade(menu=view_menu, label="")

pre_menu = tk.Menu(menu, tearoff=0)
pre_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=auto_save)
pre_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=show_tooltip)
lang_menu = tk.Menu(menu, tearoff=0)
lang_menu.add_radiobutton(label='Türkçe', variable=language, value="türkçe")
lang_menu.add_radiobutton(label='English', variable=language, value="english")
lang_menu.add_radiobutton(label='Deutsch', variable=language, value="deutsch")
pre_menu.add_cascade(menu=lang_menu, label="")
menu.add_cascade(menu=pre_menu, label="")

tool_menu = tk.Menu(menu, tearoff=0)
form_menu = tk.Menu(tool_menu, tearoff=0)

title_menu = tk.Menu(form_menu, tearoff=0)
title_menu.add_command(label="<h1>", command=lambda: [text.insert(tk.INSERT, """<h1></h1>"""), highlight(text)])
title_menu.add_command(label="<h2>", command=lambda: [text.insert(tk.INSERT, """<h2></h2>"""), highlight(text)])
title_menu.add_command(label="<h3>", command=lambda: [text.insert(tk.INSERT, """<h3></h3>"""), highlight(text)])
title_menu.add_command(label="<h4>", command=lambda: [text.insert(tk.INSERT, """<h4></h4>"""), highlight(text)])
title_menu.add_command(label="<h5>", command=lambda: [text.insert(tk.INSERT, """<h5></h5>"""), highlight(text)])
title_menu.add_command(label="<h6>", command=lambda: [text.insert(tk.INSERT, """<h6></h6>"""), highlight(text)])
form_menu.add_cascade(menu=title_menu, label="")

text_menu = tk.Menu(form_menu, tearoff=0)
text_menu.add_command(label="<p>", command=lambda: [text.insert(tk.INSERT, """<p></p>"""), highlight(text)])
text_menu.add_command(label="<b>", command=lambda: [text.insert(tk.INSERT, """<b></b>"""), highlight(text)])
text_menu.add_command(label="<i>", command=lambda: [text.insert(tk.INSERT, """<i></i>"""), highlight(text)])
text_menu.add_command(label="<u>", command=lambda: [text.insert(tk.INSERT, """<u></u>"""), highlight(text)])
text_menu.add_command(label="<mark>", command=lambda: [text.insert(tk.INSERT, """<mark></mark>"""), highlight(text)])
text_menu.add_command(label="<sub>", command=lambda: [text.insert(tk.INSERT, """<sub></sub>"""), highlight(text)])
text_menu.add_command(label="<sup>", command=lambda: [text.insert(tk.INSERT, """<sup></sup>"""), highlight(text)])
form_menu.add_cascade(menu=text_menu, label="")

other_menu = tk.Menu(form_menu, tearoff=0)
other_menu.add_command(label="<span>", command=lambda: [text.insert(tk.INSERT, """<span></span>"""), highlight(text)])
other_menu.add_command(label="<div>", command=lambda: [text.insert(tk.INSERT, """<div></div>"""), highlight(text)])
other_menu.add_command(label="<br>", command=lambda: [text.insert(tk.INSERT, """<br>"""), highlight(text)])
other_menu.add_command(label="<hr>", command=lambda: [text.insert(tk.INSERT, """<hr>"""), highlight(text)])
other_menu.add_command(label="<pre>", command=lambda: [text.insert(tk.INSERT, """<pre></pre>"""), highlight(text)])
other_menu.add_command(label="<code>", command=lambda: [text.insert(tk.INSERT, """<code></code>"""), highlight(text)])
other_menu.add_command(label="<blockquote>", command=lambda: [text.insert(tk.INSERT, """<blockquote cite=""></blockquote>"""), highlight(text)])
other_menu.add_command(label="<q>", command=lambda: [text.insert(tk.INSERT, """<q cite=""></q>"""), highlight(text)])
other_menu.add_command(label="<link>", command=lambda: [text.insert(tk.INSERT, """<a href=""></a>"""), highlight(text)])
form_menu.add_cascade(menu=other_menu, label="")

tool_menu.add_cascade(menu=form_menu, label="")
tool_menu.add_command(label="", command=lambda: md2html_dialog(win, language=language.get()))
menu.add_cascade(menu=tool_menu, label="")

update_settings()

text.bind('<Button-3>', lambda event: edit_menu.tk_popup(event.x_root, event.y_root))
text.bind("<KeyRelease>", lambda event: highlight(text))
text.bind("<KeyRelease>", autosv, add='+')
text.bind("<KeyRelease>", lambda e: update_status(), add='+')
text.bind("<Button-1>", lambda e: update_status())
win.protocol("WM_DELETE_WINDOW", save_on_exit)                    
win.mainloop()
