import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import tempfile
import re
import ctypes
import os, sys
import webbrowser

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
win.title("BukiHTML - Yeni")
win.geometry("800x600")
win.minsize(700, 500)
win.grid_rowconfigure(1, weight=1)
win.grid_columnconfigure(0, weight=1)
win.grid_columnconfigure(1, weight=1)

editor = tk.Frame(win, bd=1, relief="raised", width=800, height=600)
editor.grid(padx=10, pady=(0, 10), row=1, column=0, columnspan=2, sticky="nsew")

text = tk.Text(editor, wrap="word", width=60, height=20, font=("Consolas", 10), bd=1, undo=True)
text.pack(side="left", fill="both", padx=(5, 0), pady=5, expand=True)

for tag, color in TAG_COLORS.items():
    text.tag_config(
        tag,
        foreground=color,
        selectforeground="white",
    )

def highlighter(event=None):
    content = text.get("1.0", "end-1c")
    
    # Önce tüm tagleri kaldır
    for tag in TAG_COLORS:
        text.tag_remove(tag, "1.0", "end")
    
    # HTML yorumlarını renklendir
    for match in re.finditer(r"<!--.*?-->", content, re.DOTALL):
        start = f"1.0 + {match.start()} chars"
        end = f"1.0 + {match.end()} chars"
        text.tag_add("comment", start, end)
    
    # HTML taglerini renklendir (sadece tag içeriğini)
    for match in re.finditer(r"<([^>]+)>", content):
        tag_content = match.group(1)  # < ve > karakterleri hariç
        start_index = match.start(1)
        end_index = match.end(1)
        text.tag_add("tag", f"1.0 + {start_index} chars", f"1.0 + {end_index} chars")
        
        # Tag içindeki attributeleri renklendir
        for attr_match in re.finditer(r'(\w+)=(".*?"|\'.*?\')', tag_content):
            attr_start = f"1.0 + {start_index + attr_match.start(1)} chars"
            attr_end = f"1.0 + {start_index + attr_match.end(1)} chars"
            val_start = f"1.0 + {start_index + attr_match.start(2)} chars"
            val_end = f"1.0 + {start_index + attr_match.end(2)} chars"
            
            text.tag_add("attribute", attr_start, attr_end)
            text.tag_add("value", val_start, val_end)

def save_file(force=False):
    global current_file, changed
    if changed or force:
        if current_file:
            try:
                with open(current_file, "w", encoding="utf-8") as f:
                    f.write(text.get("1.0", "end-1c"))
                    win.title(f'BukiHTML - {current_file}')
                    changed = False
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya kaydedilemedi:\n{str(e)}")
        else:
            save_as()

def save_as():
    global current_file, filepath
    filepath = filedialog.asksaveasfilename(defaultextension='.md',
                                            filetypes=[('HTML Dosyası', '*.html'), ('Tüm Dosyalar', '*.*')],
                                            title='Kaydet')
    if filepath:
        current_file = filepath
        win.title(f'BukiHTML - {filepath}')
        save_file(force=True)
        
def open_file():
    global filepath, current_file, changed
    try:
        filepath = filedialog.askopenfilename(title='Aç', filetypes=[('HTML Dosyası', '*.html'), ('Tüm dosyalar', '*.*')])
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
    except Exception as e:
        messagebox.showerror('Hata', f"Dosya açılamadı:\n{str(e)}")

def new_file():
    global current_file, filepath, changed
    if changed:
        confirm = messagebox.askyesnocancel("Kaydet", "Bu belgeyi kaydetmek istiyor musunuz?")
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

def update_title():
    title = "BukiHTML - Yeni" if current_file is None else f"BukiHTML - {current_file}"
    if changed:
        title += " *"
    win.title(title)
        
def save_on_exit():
    global changed
    if changed:
        confirm = messagebox.askyesnocancel("Kaydet", "Bu belgeyi kaydetmek istiyor musunuz?")
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
        
def run_():
    try:
        code = text.get("1.0", "end")
        tmp_html = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8')
        tmp_html.write(code)
        tmp_html.close()
        webbrowser.open(tmp_html.name)
    except Exception as e:
        messagebox.showerror("Hata" f"Dosya tarayıcıda açılamadı:\n{str(e)}")

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

new = tk.Button(file_toolbar, text="📄", width=4, bd=0, command=new_file, activebackground="yellow", font=("Segoe UI Emoji", 9))
new.grid(row=0, column=0, padx=(3, 0), pady=3)

open_ = tk.Button(file_toolbar, text="📂", width=4, bd=0, command=open_file, activebackground="yellow", font=("Segoe UI Emoji", 9))
open_.grid(row=0, column=1, pady=3)

save = tk.Button(file_toolbar, text="💾", width=4, bd=0, command=save_file, activebackground="yellow", font=("Segoe UI Emoji", 9))
save.grid(row=0, column=2, pady=3)

run = tk.Button(file_toolbar, text="📰", width=4, bd=0, command=run_, activebackground="#0040bf", font=("Segoe UI Emoji", 9), activeforeground="white")
run.grid(row=0, column=3, padx=(0, 3), pady=3)

cut = tk.Button(text_toolbar, text="✂", width=4, bd=0, command=lambda: text.event_generate("<<Cut>>"), font=("Segoe UI Emoji", 9), activebackground="yellow")
cut.grid(row=0, column=0, padx=(3, 0), pady=3)

copy = tk.Button(text_toolbar, text="📑", width=4, bd=0, command=lambda: text.event_generate("<<Copy>>"), activebackground="yellow", font=("Segoe UI Emoji", 9))
copy.grid(row=0, column=1, pady=3)

paste = tk.Button(text_toolbar, text="📋", width=4, bd=0, command=lambda: text.event_generate("<<Paste>>"), activebackground="yellow", font=("Segoe UI Emoji", 9))
paste.grid(row=0, column=2, padx=(0, 3), pady=3)

undo = tk.Button(do_toolbar, text="↶", width=4, bd=0, command=undo_, font=("Segoe UI Emoji", 9), activebackground="yellow")
undo.grid(row=0, column=0, padx=(3, 0), pady=3)

redo = tk.Button(do_toolbar, text="↷", width=4, bd=0, command=redo_, font=("Segoe UI Emoji", 9), activebackground="yellow")
redo.grid(row=0, column=1, padx=(0, 3), pady=3)

about = tk.Button(other_toolbar, text="⁝", width=4, bd=0, command=lambda: messagebox.showinfo("Hakkında", "BukiHTML v1.0.5\n2025 Buğra US"), activebackground="yellow", font=("Segoe UI Emoji", 9))
about.grid(row=0, column=0, padx=3, pady=3, sticky="e")

scroll = tk.Scrollbar(editor)
scroll.pack(side="left", padx=(0, 5), pady=(0, 5), fill="y")
scroll.config(command=text.yview)
text.config(yscrollcommand=scroll.set)

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
win.bind("<Control-Shift-P>", lambda e: run_on_browser())


menu = tk.Menu(win)
win.config(menu=menu)

file_menu = tk.Menu(menu, tearoff=0)
file_menu.add_command(label='Yeni', command=new_file, accelerator="Ctrl+N")
file_menu.add_command(label='Yeni Pencere', command=lambda: subprocess.Popen([sys.executable, __file__]), accelerator="Ctrl+Shift+N")
file_menu.add_separator()
file_menu.add_command(label='Aç', command=open_file, accelerator="Ctrl+O")
file_menu.add_command(label='Kaydet', command=save_file, accelerator="Ctrl+S")
file_menu.add_command(label='Farklı Kaydet', command=save_as, accelerator="Ctrl+Shift+S")
file_menu.add_separator()
file_menu.add_command(label='Çık', command=lambda: win.destroy(), accelerator="Alt+F4")
menu.add_cascade(menu=file_menu, label="Dosya")

edit_menu = tk.Menu(menu, tearoff=0)
edit_menu.add_command(label='Geri al', command=undo_, accelerator="Ctrl+Z")
edit_menu.add_command(label='Yinele', command=redo_, accelerator="Ctrl+Y")
edit_menu.add_separator()
edit_menu.add_command(label='Kes', command=lambda: text.event_generate('<<Cut>>'), accelerator="Ctrl+X")
edit_menu.add_command(label='Kopyala', command=lambda: text.event_generate('<<Copy>>'), accelerator="Ctrl+C")
edit_menu.add_command(label='Yapıştır', command=lambda: text.event_generate('<<Paste>>'), accelerator="Ctrl+V")
edit_menu.add_command(label='Tümünü Seç', command=lambda: text.tag_add('sel', '1.0', 'end'), accelerator="Ctrl+A")
edit_menu.add_separator()
edit_menu.add_command(label="Satırı Girintile", command=indent, accelerator="Tab")
edit_menu.add_command(label="Satırın Girintisini Azalt", command=unindent, accelerator="Shift+Tab")
menu.add_cascade(menu=edit_menu, label="Düzen")

text.bind('<Button-3>', lambda event: edit_menu.tk_popup(event.x_root, event.y_root))
text.bind("<KeyRelease>", highlighter)
win.protocol("WM_DELETE_WINDOW", save_on_exit)                    
win.mainloop()

