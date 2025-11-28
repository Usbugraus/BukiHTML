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
TAG_COLORS = {
    "tag": "#0000bf",
    "attribute": "#bf0000",
    "value": "#00bf00",
    "comment": "#008000",
}

win = tk.Tk()
win.geometry("800x600")
win.minsize(700, 500)
win.grid_rowconfigure(1, weight=1)
win.grid_columnconfigure(0, weight=1)
win.grid_columnconfigure(1, weight=1)

def report_callback_exception(exc_type, exc_value, exc_traceback):
    tk_error_handler(exc_type, exc_value, exc_traceback)

win.report_callback_exception = report_callback_exception

configuration_file = "Configuration.json"

with open(configuration_file, "r", encoding="utf-8") as f:
    configuration = json.load(f)
          
show_tooltip = tk.BooleanVar(value=configuration["show_tooltip"])
language = tk.StringVar(value=configuration["language"])
auto_save = tk.BooleanVar(value=configuration["auto_save"])

menu_labels = {}

editor = tk.Frame(win, bd=1, relief="raised", width=800, height=600)
editor.grid(padx=10, pady=(0, 10), row=1, column=0, columnspan=2, sticky="nsew")

text = tk.Text(editor, wrap="none", width=60, height=20, font=("Consolas", 10), bd=1, undo=True, padx=5, pady=5)

for tag, color in TAG_COLORS.items():
    text.tag_config(
        tag,
        foreground=color,
        selectforeground="white",
    )
    
def toolwindow(window):
    window.update_idletasks()
    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    
    GWL_STYLE = -16
    WS_MINIMIZEBOX = 0x00020000
    WS_MAXIMIZEBOX = 0x00010000
    
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
    
    style = style & ~WS_MINIMIZEBOX & ~WS_MAXIMIZEBOX
    
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
    
    ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 
                                      0x0002 | 0x0001 | 0x0004 | 0x0020 | 0x0010)
    
def tk_error_handler(exc_type, exc_value, exc_traceback):
    tb_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    errorwin = tk.Toplevel(win)
    errorwin.title("Hata")
    errorwin.resizable(False, False)
    errorwin.transient(win)
    errorwin.lift()
    errorwin.focus_force()
    toolwindow(errorwin)
    errorwin.grab_set()
    
    frame = tk.Frame(errorwin, bd=1, relief="raised")
    frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    if language.get() == "türkçe":
        tk.Label(frame, text="Bir sorun oluştu: ").pack(anchor="nw", padx=5, pady=(5, 0))
    elif language.get() == "english":
        tk.Label(frame, text="An error occured: ").pack(anchor="nw", padx=5, pady=(5, 0))
    
    error = tk.Text(frame, bd=1, font=("Consolas", 10), width=50, height=20, wrap="none", padx=5, pady=5)
    error.insert(1.0, traceback.format_exc())
    error.config(state="disabled")
    
    scroll = tk.Scrollbar(frame, orient="vertical")
    scroll.pack(padx=(0, 5), pady=5, fill="y", side='right')
    scroll.config(command=error.yview)
    
    scroll2 = tk.Scrollbar(frame, orient="horizontal")
    scroll2.pack(padx=5, pady=(0, 5), fill="x", side='bottom')
    scroll2.config(command=error.xview)
    
    error.config(yscrollcommand=scroll.set)
    error.config(xscrollcommand=scroll2.set)
    error.pack(padx=(5, 0), pady=(5, 0), fill="both", expand=True)
    
    frame2 = tk.Frame(errorwin, bd=1, relief="raised")
    frame2.pack(padx=20, pady=(0, 20))
    
    def copy_error():
         error_content = error.get("1.0", "end-1c")
         error.clipboard_clear()
         error.clipboard_append(error_content)
         cp.config(state="disabled")
    
    ok = tk.Button(frame2, text="Tamam", bd=1, command=lambda: errorwin.destroy(), width=30)
    ok.pack(padx=5, pady=5, side="right")
    cp = tk.Button(frame2, text="Kopyala", bd=1, command=copy_error, width=30)
    cp.pack(padx=(5, 0), pady=5, side="left")
    
    if language.get() == "türkçe":
        ok.config(text="Tamam")
        cp.config(text="Kopyala")
    elif language.get() == "english":
        ok.config(text="Ok")
        cp.config(text="Copy")

def highlighter(event=None):
    content = text.get("1.0", "end-1c")
    
    for tag in TAG_COLORS:
        text.tag_remove(tag, "1.0", "end")
    
    for match in re.finditer(r"<!--.*?-->", content, re.DOTALL):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text.tag_add("comment", start, end)
    
    for match in re.finditer(r"<([^>]+)>", content):
        tag_content = match.group(1)
        start_index = match.start(1)
        end_index = match.end(1)
        text.tag_add("tag", f"1.0 + {start_index} chars", f"1.0 + {end_index} chars")
        
        for attr_match in re.finditer(r'(\w+)=(".*?"|\'.*?\')', tag_content):
            attr_start = f"1.0 + {start_index + attr_match.start(1)} chars"
            attr_end = f"1.0 + {start_index + attr_match.end(1)} chars"
            val_start = f"1.0 + {start_index + attr_match.start(2)} chars"
            val_end = f"1.0 + {start_index + attr_match.end(2)} chars"
            
            text.tag_add("attribute", attr_start, attr_end)
            text.tag_add("value", val_start, val_end)

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


def save_as():
    global current_file, filepath

    if language.get() == "turkish":
        filepath = filedialog.asksaveasfilename(
            defaultextension='.html',
            filetypes=[('HTML Dosyası', '*.html'), ('Tüm Dosyalar', '*.*')],
            title='Kaydet'
        )
    else:
        filepath = filedialog.asksaveasfilename(
            defaultextension='.html',
            filetypes=[('HTML Files', '*.html'), ('All Files', '*.*')],
            title='Save'
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
        highlighter()
        save.config(state="disabled")

def new_file():
    global current_file, filepath, changed
    if changed:
        if language.get() == "türkçe":
            confirm = messagebox.askyesnocancel("Kaydet", "Bu belgeyi kaydetmek istiyor musunuz?")
        elif language.get() == "english":
            confirm = messagebox.askyesnocancel("Save", "Do you want to save this document?")
            
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
    win.update_idletasks()

def update_title():
    if language.get() == "türkçe":
        title = "BukiHTML - Yeni" if current_file is None else f"BukiHTML - {current_file}"
    elif language.get() == "english":
        title = "BukiHTML - New" if current_file is None else f"BukiHTML - {current_file}"
        
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
            
        if confirm:
            save_file()
            win.destroy()
        if confirm == False: 
            win.destroy()
    else:
        win.destroy()
    
    config = {
        "show_tooltip": show_tooltip.get(),
        "language": language.get(),
        "auto_save": auto_save.get()
        }
        
    with open(configuration_file, "w", encoding="utf-8") as f:
        cfile = json.dump(config, f, ensure_ascii=False, indent=4)
              
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
        messagebox.showinfo("Hakkında", "BukiHTML v1.1.0\n© Telif Hakkı 2025 Buğra US")
    elif language.get() == "english":
        messagebox.showinfo("About", "BukiHTML v1.1.0\n© Copyright 2025 Buğra US")
    
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

file_toolbar = tk.Frame(toolbar_frame, bd=1, relief="raised")
file_toolbar.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="w")

text_toolbar = tk.Frame(toolbar_frame, bd=1, relief="raised")
text_toolbar.grid(row=0, column=1, padx=10, pady=10, sticky="w")

do_toolbar = tk.Frame(toolbar_frame, bd=1, relief="raised")
do_toolbar.grid(row=0, column=2, padx=(0, 10), pady=10, sticky="w")

other_toolbar_frame = tk.Frame(win)
other_toolbar_frame.grid(row=0, column=1, sticky="e")

other_toolbar = tk.Frame(other_toolbar_frame, bd=1, relief="raised")
other_toolbar.grid(row=0, column=0, padx=10, pady=10, sticky="e")

new = tk.Button(file_toolbar, text="", width=5, pady=4, bd=0, command=new_file, activebackground="yellow", font=("Segoe Fluent Icons", 10))
new.grid(row=0, column=0, padx=(3, 0), pady=3)

open_ = tk.Button(file_toolbar, text="", width=5, pady=4, bd=0, command=open_file, activebackground="yellow", font=("Segoe Fluent Icons", 10))
open_.grid(row=0, column=1, pady=3)

save = tk.Button(file_toolbar, text="", width=5, pady=4, bd=0, command=save_file, activebackground="yellow", font=("Segoe Fluent Icons", 10), state=("normal" if not filepath else "disabled"))
save.grid(row=0, column=2, pady=3)

run = tk.Button(file_toolbar, text="", width=5, pady=4, bd=0, command=run_, activebackground="#0040bf", font=("Segoe Fluent Icons", 10), activeforeground="white")
run.grid(row=0, column=3, padx=(0, 3), pady=3)

cut = tk.Button(text_toolbar, text="", width=5, pady=4, bd=0, command=lambda: text.event_generate("<<Cut>>"), font=("Segoe Fluent Icons", 10), activebackground="yellow")
cut.grid(row=0, column=0, padx=(3, 0), pady=3)

copy = tk.Button(text_toolbar, text="", width=5, pady=4, bd=0, command=lambda: text.event_generate("<<Copy>>"), activebackground="yellow", font=("Segoe Fluent Icons", 10))
copy.grid(row=0, column=1, pady=3)

paste = tk.Button(text_toolbar, text="", width=5, pady=4, bd=0, command=lambda: text.event_generate("<<Paste>>"), activebackground="yellow", font=("Segoe Fluent Icons", 10))
paste.grid(row=0, column=2, padx=(0, 3), pady=3)

undo = tk.Button(do_toolbar, text="", width=5, pady=4, bd=0, command=undo_, font=("Segoe Fluent Icons", 10), activebackground="yellow")
undo.grid(row=0, column=0, padx=(3, 0), pady=3)

redo = tk.Button(do_toolbar, text="", width=5, pady=4, bd=0, command=redo_, font=("Segoe Fluent Icons", 10), activebackground="yellow")
redo.grid(row=0, column=1, padx=(0, 3), pady=3)

about = tk.Button(other_toolbar, text="", width=5, pady=4, bd=0, command=show_about, activebackground="yellow", font=("Segoe Fluent Icons", 10))
about.grid(row=0, column=0, padx=3, pady=3, sticky="e")

scroll = tk.Scrollbar(editor)
scroll.pack(side="right", padx=(0, 5), pady=(0, 5), fill="y")
scroll.config(command=text.yview)

scroll_h = tk.Scrollbar(editor, orient="horizontal")
scroll_h.pack(side="bottom", padx=(5, 0), pady=(0, 5), fill="x")
scroll_h.config(command=text.xview)
text.config(xscrollcommand=scroll_h.set, yscrollcommand=scroll.set)

text.pack(fill="both", padx=(5, 0), pady=5, expand=True)

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
    global menu_labels
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
            "settings":{"label": "Settings",
                        "menus":[
                            "Auto Save",
                            "Show Tooltips",
                            "Language"
                            ]
                        }
            }
    
    if language.get() == "türkçe":
        ToolTip(about, "Hakkında", shown=show_tooltip.get())
        ToolTip(redo, "Yinele - Ctrl+Y", shown=show_tooltip.get())
        ToolTip(undo, "Geri Al - Ctrl+Z", shown=show_tooltip.get())
        ToolTip(paste, "Yapıştır - Ctrl+V", shown=show_tooltip.get())
        ToolTip(copy, "Kopyala - Ctrl+C", shown=show_tooltip.get())
        ToolTip(cut, "Kes - Ctrl+X", shown=show_tooltip.get())
        ToolTip(run, "Önizleme - Ctrl+P", shown=show_tooltip.get())
        ToolTip(save, "Kaydet - Ctrl+S", shown=show_tooltip.get())
        ToolTip(open_, "Aç - Ctrl+O", shown=show_tooltip.get())
        ToolTip(new, "Yeni - Ctrl+N", shown=show_tooltip.get())
        
    elif language.get() == "english":
        ToolTip(about, "About", shown=show_tooltip.get())
        ToolTip(redo, "Redo - Ctrl+Y", shown=show_tooltip.get())
        ToolTip(undo, "Undo - Ctrl+Z", shown=show_tooltip.get())
        ToolTip(paste, "Paste - Ctrl+V", shown=show_tooltip.get())
        ToolTip(copy, "Copy - Ctrl+C", shown=show_tooltip.get())
        ToolTip(cut, "Cut - Ctrl+X", shown=show_tooltip.get())
        ToolTip(run, "Preview - Ctrl+P", shown=show_tooltip.get())
        ToolTip(save, "Save - Ctrl+S", shown=show_tooltip.get())
        ToolTip(open_, "Open - Ctrl+O", shown=show_tooltip.get())
        ToolTip(new, "New - Ctrl+N", shown=show_tooltip.get())
    
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
    
    menu.entryconfig(3, label=menu_labels["settings"]["label"])
    pre_menu.entryconfig(0, label=menu_labels["settings"]["menus"][0])
    pre_menu.entryconfig(1, label=menu_labels["settings"]["menus"][1])
    pre_menu.entryconfig(2, label=menu_labels["settings"]["menus"][2])
    
    update_title()

show_tooltip.trace_add("write", update_settings)
language.trace_add("write", update_settings)
auto_save.trace_add("write", update_settings)

text.bind("<Shift-Tab>", unindent)
text.bind("<Tab>", indent)
text.bind("<<Modified>>", update)
win.bind("<Control-s>", lambda e: save_file())
win.bind("<Control-Shift-S>", lambda e: save_as())
win.bind("<Control-o>", lambda e: open_file())
win.bind("<Control-n>", lambda e: new_file())
win.bind("<Control-z>", lambda e: undo_())
win.bind("<Control-y>", lambda e: redo_())
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

pre_menu = tk.Menu(menu, tearoff=0)
pre_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=auto_save)
pre_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=show_tooltip)
lang_menu = tk.Menu(menu, tearoff=0)
lang_menu.add_radiobutton(label='Türkçe', variable=language, value="türkçe")
lang_menu.add_radiobutton(label='English', variable=language, value="english")
pre_menu.add_cascade(menu=lang_menu, label="")
menu.add_cascade(menu=pre_menu, label="")

update_settings()

text.bind('<Button-3>', lambda event: edit_menu.tk_popup(event.x_root, event.y_root))
text.bind("<KeyRelease>", highlighter)
text.bind("<KeyRelease>", autosv, add='+')
win.protocol("WM_DELETE_WINDOW", save_on_exit)                    
win.mainloop()
