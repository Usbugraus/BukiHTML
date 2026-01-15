import subprocess
import sys
import tempfile
import os
import tkinter as tk
from tkinter import messagebox, filedialog
import ctypes
import json
import builtins, keyword
from ToolTip import ToolTip
from ErrorHandler import error_handler
from SyntaxHighlighter import highlight
from AutoCompleter import AutoCompleter

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass
   
win = tk.Tk()
win.geometry("800x600")
win.minsize(700, 500)
win.grid_rowconfigure(1, weight=1)
win.grid_columnconfigure(0, weight=1)
win.grid_columnconfigure(1, weight=1)

def report_callback_exception(exc_type, exc_value, exc_traceback):
    error_handler(exc_type, exc_value, exc_traceback, parent=win, language=language.get())

win.report_callback_exception = report_callback_exception

changed = False
current_file = None
filepath = None
font_size = 10
names = dir(builtins) + keyword.kwlist
SYNTAX_COLORS = {
    "keyword": ["#bf0000", ("Consolas", font_size, "bold")],
    "string": ["#00bf00", ("Consolas", font_size)],
    "comment": ["#808080", ("Consolas", font_size, "italic")],
    "number": ["#0000bf", ("Consolas", font_size)],
    "builtin": ["#bf8000", ("Consolas", font_size)],
    "operator": ["#404040", ("Consolas", font_size)],
}

configuration_file = "Configuration.json"
python_config_file = "Interpreter.json"

if os.path.exists(configuration_file):
    with open(configuration_file, "r", encoding="utf-8") as f:
        configuration = json.load(f)
else:
    configuration = {
        "show_tooltip": True,
        "language": "english",
        "auto_save": False
        }
    
if os.path.exists(python_config_file):
    with open(python_config_file, "r", encoding="utf-8") as f:
        pyconfig = json.load(f)
    python_path = pyconfig["python_path"]
else:
    python_path = None
          
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

line_numbers = tk.Canvas(
    editor,
    width=45,
    background="#f0f0f0",
    highlightthickness=0
)

text = tk.Text(editor, wrap="none", width=60, height=20, font=("Consolas", font_size), bd=1, undo=True, padx=5, pady=5)

for tag, style in SYNTAX_COLORS.items():
    text.tag_configure(tag, foreground=style[0], font=style[1], selectforeground="#ffffff")

def resource_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, filename)

def save_file(force=False):
    global current_file, changed

    if current_file is None:
        save_as()
        return

    if changed or force:
        with open(current_file, "w", encoding="utf-8") as f:
            f.write(text.get("1.0", "end-1c"))

        win.title(f'BukiPython - {current_file}')
        changed = False
        update_status()
        save.config(state="disabled")

def save_as():
    global current_file, filepath

    if language.get() == "türkçe":
        filepath = filedialog.asksaveasfilename(
            defaultextension='.html',
            filetypes=[('Python Dosyası', '*.py'), ('Tüm Dosyalar', '*.*')],
            title='Kaydet'
        )
    elif language.get() == "english":
        filepath = filedialog.asksaveasfilename(
            defaultextension='.html',
            filetypes=[('Python Files', '*.py'), ('All Files', '*.*')],
            title='Save'
        )
    elif language.get() == "deutsch":
        filepath = filedialog.asksaveasfilename(
            defaultextension='.html',
            filetypes=[('Python Dateien', '*.py'), ('Alle Dateien', '*.*')],
            title='Speichern'
        )

    if filepath:
        current_file = filepath
        win.title(f'BukiPython - {filepath}')
        save_file(force=True)
        
def open_file():
    global filepath, current_file, changed
    if language.get() == "türkçe":
        filepath = filedialog.askopenfilename(title='Aç', filetypes=[('Python Dosyası', '*.py'), ('Tüm dosyalar', '*.*')])
    elif language.get() == "english":
        filepath = filedialog.askopenfilename(title='Open', filetypes=[('Python Files', '*.py'), ('All Files', '*.*')])
    elif language.get() == "deutsch":
        filepath = filedialog.askopenfilename(title='Öffnen', filetypes=[('Python Dateien', '*.py'), ('Alle Dateien', '*.*')])
    
    if filepath:
        with open(filepath, 'r', encoding='utf-8') as file:
            opened_file = file.read()
        text.delete(1.0, tk.END)
        text.insert(1.0, opened_file)
        current_file = filepath
        win.title(f'BukiPython - {current_file}')
        changed = False
        text.edit_modified(False)
        update()
        save.config(state="disabled")
        update_status()
        redraw_line_numbers()
        text.edit_reset()

def new_file():
    global current_file, filepath, changed
    if changed:
        if language.get() == "türkçe":
            confirm = messagebox.askyesnocancel("Kaydet", "Bu kodu kaydetmek istiyor musunuz?")
        elif language.get() == "english":
            confirm = messagebox.askyesnocancel("Save", "Do you want to save this code?")
        elif language.get() == "deutsch":
            confirm = messagebox.askyesnocancel("Speichern", "Möchten Sie diesen Code speichern?")
            
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
    redraw_line_numbers()
    text.edit_reset()
    win.update_idletasks()

def update_title():
    if language.get() == "türkçe":
        title = "BukiPython - Yeni" if current_file is None else f"BukiPython - {current_file}"
    elif language.get() == "english":
        title = "BukiPython - New" if current_file is None else f"BukiPython - {current_file}"
    elif language.get() == "deutsch":
        title = "BukiPython - Neu" if current_file is None else f"BukiPython - {current_file}"
        
    if changed:
        title += " *"
    win.title(title)
        
def save_on_exit():
    global changed
    if changed:
        if language.get() == "türkçe":
            confirm = messagebox.askyesnocancel("Kaydet", "Bu kodu kaydetmek istiyor musunuz?")
        elif language.get() == "english":
            confirm = messagebox.askyesnocancel("Save", "Do you want to save this code?")
        elif language.get() == "deutsch":
            confirm = messagebox.askyesnocancel("Speichern", "Möchten Sie diesen Code speichern?")
            
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
    highlight(text)

def run_():
    global current_file, python_path
    if python_path:
        code = text.get("1.0", tk.END)
        
        if language.get() == "türkçe":
            title = "Çıktı"
        elif language.get() == "english":
            title = "Output"
        elif language.get() == "deutsch":
            title = "Ausgabe"
        
        if not current_file:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(code)
                temp_path = f.name

            subprocess.Popen(
                f'cmd.exe /k title {title} && "{python_path}" "{temp_path}"',
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            if changed:
                save_file()
                
            subprocess.Popen(
                f'cmd.exe /k title {title} && "{python_path}" "{current_file}"',
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

    else:
        if language.get() == "türkçe":
            messagebox.showwarning("Seçili Değil", "Python yorumlayıcısı seçilmedi.")
        elif language.get() == "english":
            messagebox.showwarning("Not Selected", "Python interpreter is not selected.")
        elif language.get() == "deutsch":
            messagebox.showwarning("Nicht Ausgewählt", "Python-Interpreter ist nicht ausgewählt")
    
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

def auto_indent(event=None):
    line = text.get("insert linestart", "insert lineend")

    base_indent = len(line) - len(line.lstrip(" "))
    stripped = line.rstrip()

    indent_chars = (":", "{", "[", "(")
    extra = 4 if stripped.endswith(indent_chars) else 0

    text.insert("insert", "\n" + " " * (base_indent + extra))
    return "break"

def show_about():
    if language.get() == "türkçe":
        messagebox.showinfo("Hakkında", "BukiPython v1.1.2\n© Telif Hakkı 2025-2026 Buğra US")
    elif language.get() == "english":
        messagebox.showinfo("About", "BukiPython v1.1.2\n© Copyright 2025-2026 Buğra US")
    elif language.get() == "deutsch":
        messagebox.showinfo("Über", "BukiPython v1.1.2\n© Urheberrecht 2025-2026 Buğra US")
    
def run_terminal():
    global python_path
    subprocess.Popen(
        [
            "cmd.exe",
            "/k",
            "title Komut Satırı && "
            "echo == Python == && "
            "where python && "
            "echo == Pip == && "
            "where pip && "
            f"echo Python Path: {python_path}"
        ],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    
def autosv(event):
    global current_file
    if current_file and auto_save.get():
        save_file()
    
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
            "run":{"label": "Çalıştır",
                   "menus": [
                       "Çalıştır",
                       "Komut Satırını Aç",
                       "Python Yorumlayıcısı Seç"
                       ]
                   },
            "settings":{"label": "Ayarlar",
                        "menus":[
                            "Otomatik Kaydet",
                            "Araç İpuçlarını Göster",
                            "Dil"
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
            "run":{"label": "Run",
                   "menus": [
                       "Run",
                       "Open the Command Prompt",
                       "Select Python Interpreter"
                       ]
                   },
            "settings":{"label": "Settings",
                        "menus":[
                            "Auto-Save",
                            "Show Tooltips",
                            "Language"
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
            "run":{"label": "Laufen",
                   "menus": [
                        "Laufen",
                        "Öffne die Eingabeaufforderung",
                        "Python-Interpreter auswählen"
                       ]
                   },
            "settings":{"label": "Einstellungen",
                        "menus":[
                            "Automatisch Speichern",
                            "Tooltipps Anzeigen",
                            "Sprache"
                            ]
                        }
            }
    
    if language.get() == "türkçe":
        ToolTip(about, "Hakkında", shown=show_tooltip.get())
        ToolTip(term, "Komut Satırını Aç - Ctrl+T", shown=show_tooltip.get())
        ToolTip(run, "Çalıştır - F5", shown=show_tooltip.get())
        ToolTip(save, "Kaydet - Ctrl+S", shown=show_tooltip.get())
        ToolTip(open_, "Aç - Ctrl+O", shown=show_tooltip.get())
        ToolTip(new, "Yeni - Ctrl+N", shown=show_tooltip.get())
        
    elif language.get() == "english":
        ToolTip(about, "About", shown=show_tooltip.get())
        ToolTip(term, "Open the Command Prompt - Ctrl+T", shown=show_tooltip.get())
        ToolTip(run, "Run - F5", shown=show_tooltip.get())
        ToolTip(save, "Save - Ctrl+S", shown=show_tooltip.get())
        ToolTip(open_, "Open - Ctrl+O", shown=show_tooltip.get())
        ToolTip(new, "New - Ctrl+N", shown=show_tooltip.get())
        
    elif language.get() == "deutsch":
        ToolTip(about, "Über", shown=show_tooltip.get())
        ToolTip(term, "Öffne die Eingabeaufforderung - Ctrl+T", shown=show_tooltip.get())
        ToolTip(run, "Laufen - F5", shown=show_tooltip.get())
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
    
    menu.entryconfig(4, label=menu_labels["run"]["label"])
    run_menu.entryconfig(0, label=menu_labels["run"]["menus"][0])
    run_menu.entryconfig(1, label=menu_labels["run"]["menus"][1])
    run_menu.entryconfig(3, label=menu_labels["run"]["menus"][2])
    
    menu.entryconfig(5, label=menu_labels["settings"]["label"])
    pre_menu.entryconfig(0, label=menu_labels["settings"]["menus"][0])
    pre_menu.entryconfig(1, label=menu_labels["settings"]["menus"][1])
    pre_menu.entryconfig(2, label=menu_labels["settings"]["menus"][2])
    
    update_title()
    update_status()
    
    config = {
        "show_tooltip": show_tooltip.get(),
        "language": language.get(),
        "auto_save": auto_save.get()
        }
        
    with open(configuration_file, "w", encoding="utf-8") as f:
        cfile = json.dump(config, f, ensure_ascii=False, indent=4)
        
def select_python():
    global python_path
    if language.get() == "türkçe":
        pyfilepath = filedialog.askopenfilename(title='Python Yorumlayıcısı Seç', filetypes=[('Uygulama', '*.exe'), ('Tüm dosyalar', '*.*')])
    elif language.get() == "english":
        pyfilepath = filedialog.askopenfilename(title='Select Python Interpreter', filetypes=[('Application', '*.exe'), ('All Files', '*.*')])
    elif language.get() == "deutsch":
        pyfilepath = filedialog.askopenfilename(title='Python-Interpreter auswählen', filetypes=[('Anwendung', '*.exe'), ('Alle Dateien', '*.*')])
        
    if pyfilepath:
        if os.path.basename(pyfilepath).lower() in ("python.exe", "python3.exe"):
            python_path = pyfilepath
        else:
            if language.get() == "türkçe":
                messagebox.showerror("Geçersiz Dosya", "Bu dosya Python yorumlayıcısı değil.")
            elif language.get() == "english":
                messagebox.showerror("Invalid File", "This file is not a Python interpreter.")
            elif language.get() == "deutsch":
                messagebox.showerror("Ungültige Datei", "Diese Datei ist kein Python-Interpreter.")
            return
        
        pycf = {
            "python_path" : python_path
            }
            
        with open(python_config_file, "w", encoding="utf-8") as f:
            pyfile = json.dump(pycf, f, ensure_ascii=False, indent=4)
            
def update_fonts():
    global SYNTAX_COLORS
    text.config(font=("Consolas", font_size))

    for tag, style in SYNTAX_COLORS.items():
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
        
    def get_cursor_position():
        index = text.index(tk.INSERT)
        line, col = index.split(".")
        return int(line), int(col) + 1
    
    line, col = get_cursor_position()
    filename = os.path.basename(current_file) if current_file else newfile_status

    status_bar.config(
        text=f"{filename} | {line} : {col}"
    )
    
def update_status_idle(event=None):
    win.after_idle(update_status)
    
def redraw_line_numbers(event=None):
    line_numbers.delete("all")

    i = text.index("@0,0")
    while True:
        dline = text.dlineinfo(i)
        if dline is None:
            break

        y = dline[1]
        line_number = str(i).split(".")[0]
        line_numbers.create_text(
            40, y,
            anchor="ne",
            text=line_number,
            font=("Consolas", 10)
        )

        i = text.index(f"{i}+1line")
        
    text.edit_modified(False)
    
def on_text_scroll(*args):
    scroll.set(*args)
    redraw_line_numbers()

def on_scrollbar(*args):
    text.yview(*args)
    redraw_line_numbers()
    
def toggle_fullscreen(event=None):
    fullscreen.set(not fullscreen.get())
    win.attributes("-fullscreen", fullscreen.get())

def exit_fullscreen(event=None):
    fullscreen.set(False)
    win.attributes("-fullscreen", False)

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

run_toolbar = tk.Frame(toolbar_frame, bd=1, relief="raised", padx=3, pady=3)
run_toolbar.grid(row=0, column=1, padx=(10, 0), sticky="w", pady=(10, 0))

other_toolbar_frame = tk.Frame(win)
other_toolbar_frame.grid(row=0, column=1, sticky="e")

other_toolbar = tk.Frame(other_toolbar_frame, bd=1, relief="raised", padx=3, pady=3)
other_toolbar.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="e")

new = tk.Button(file_toolbar, text="", width=5, pady=4, bd=0, command=new_file, activebackground="yellow", font=("Segoe Fluent Icons", 10))
new.grid(row=0, column=0)

open_ = tk.Button(file_toolbar, text="", width=5, pady=4, bd=0, command=open_file, activebackground="yellow", font=("Segoe Fluent Icons", 10))
open_.grid(row=0, column=1)

save = tk.Button(file_toolbar, text="", width=5, pady=4, bd=0, command=save_file, activebackground="yellow", font=("Segoe Fluent Icons", 10))
save.grid(row=0, column=2)

run = tk.Button(run_toolbar, text="\uE102", width=5, pady=4, bd=0, command=run_, activebackground="#00bf00", font=("Segoe Fluent Icons", 10), activeforeground="white", fg="#00bf00")
run.grid(row=0, column=0)

term = tk.Button(run_toolbar, text="\uE756", width=5, pady=4, bd=0, command=run_terminal, activebackground="yellow", font=("Segoe Fluent Icons", 10))
term.grid(row=0, column=1)

about = tk.Button(other_toolbar, text="", width=5, pady=4, bd=0, command=show_about, activebackground="yellow", font=("Segoe Fluent Icons", 10))
about.grid(row=0, column=0, sticky="e")

scroll = tk.Scrollbar(editor)
scroll.pack(side="right", padx=(0, 5), pady=5, fill="y")
scroll.config(command=on_scrollbar)

scroll_h = tk.Scrollbar(editor, orient="horizontal")
scroll_h.pack(side="bottom", padx=(5, 0), pady=(0, 5), fill="x")
scroll_h.config(command=text.xview)
text.config(
    xscrollcommand=scroll_h.set,
    yscrollcommand=on_text_scroll
)

line_numbers.pack(side="left", fill="y", padx=(5, 0), pady=5)
text.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=(5, 0))

show_tooltip.trace_add("write", update_settings)
language.trace_add("write", update_settings)
auto_save.trace_add("write", update_settings)
fullscreen.trace_add("write", update_view)
cover.trace_add("write", update_view)

text.bind("<<Modified>>", update)
text.bind("<Return>", auto_indent, add="+")
text.bind("<KeyRelease>", autosv, add='+')
text.bind("<KeyRelease>", lambda e: update_status(), add='+')
text.bind("<ButtonRelease-1>", update_status_idle, add="+")
text.bind("<Shift-Tab>", unindent)
text.bind("<Tab>", indent)
win.bind("<Control-s>", lambda e: save_file())
win.bind("<Control-Shift-S>", lambda e: save_as())
win.bind("<Control-o>", lambda e: open_file())
win.bind("<Control-n>", lambda e: new_file())
win.bind("<Control-z>", lambda e: undo_())
win.bind("<Control-y>", lambda e: redo_())
win.bind("<Control-t>", lambda e: run_terminal())
win.bind("<Control-plus>", lambda e: increase_size())
win.bind("<Control-minus>", lambda e: decrease_size())
win.bind("<Control-Shift-R>", lambda e: reset_size())
win.bind("<Control-Shift-N>", lambda e: subprocess.Popen([sys.executable, __file__]))
win.bind("<F5>", lambda e: run_())
win.bind("<F11>", toggle_fullscreen)
win.bind("<Escape>", exit_fullscreen)
win.protocol("WM_DELETE_WINDOW", save_on_exit)

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
view_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=fullscreen, accelerator="F11")
view_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=cover)
menu.add_cascade(menu=view_menu, label="Görünüm")

run_menu = tk.Menu(menu, tearoff=0)
run_menu.add_command(label="", command=run_, accelerator="F5")
run_menu.add_command(label="", command=run_terminal, accelerator="Ctrl+T")
run_menu.add_separator()
run_menu.add_command(label="", command=select_python)
menu.add_cascade(menu=run_menu, label="")

pre_menu = tk.Menu(menu, tearoff=0)
pre_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=auto_save)
pre_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=show_tooltip)
lang_menu = tk.Menu(menu, tearoff=0)
lang_menu.add_radiobutton(label='Türkçe', variable=language, value="türkçe")
lang_menu.add_radiobutton(label='English', variable=language, value="english")
lang_menu.add_radiobutton(label='Deutsch', variable=language, value="deutsch")
pre_menu.add_cascade(menu=lang_menu, label="")
menu.add_cascade(menu=pre_menu, label="")

text.bind("<<Modified>>", redraw_line_numbers, add="+")
text.bind("<MouseWheel>", redraw_line_numbers)
text.bind("<Button-4>", redraw_line_numbers)
text.bind("<Button-5>", redraw_line_numbers)
text.bind("<Configure>", redraw_line_numbers)

redraw_line_numbers()

update_settings()

text.bind('<Button-3>', lambda event: edit_menu.tk_popup(event.x_root, event.y_root))

AutoCompleter(text, names)

win.mainloop()