import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import tempfile
import re
import ctypes
import os, sys
import webbrowser
import json
from collections import defaultdict
from ToolTip import ToolTip
from MarkdownToHTML import md2html_dialog
from SyntaxHighlighter import highlighter
from ErrorHandler import error_handler
from AutoCompleter import AutoCompleter
from SyntaxColorPicker import pick_syntax_color, pick_background_color, pick_foreground_color

myappid = 'com.usbugraus.bukihtml'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

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
configuration_file = "Configuration.json"
data_directory = os.path.join(os.path.dirname(__file__), "Data")
menu_labels = {}
tooltip_labels = {}
dialogs = {}
labels = {}
default_configuration = {
    "show_tooltip": True,
    "language": "english",
    "auto_save": False,
    "highlighting": True,
    "line_numbers": True,
    "window_size": "800x600",
    "window_state": "normal",
    "font_size": 9,
    "auto_complete": True,
    "indent_level": 4,
    "background": "#ffffff",
    "foreground": "#000000",
    "smart_tag_completing": True,
    "syntax_highlighting": {
        "tag": [
            "#0040bf",
            [
                "Consolas",
                9
            ]
        ],
        "attribute": [
            "#bf0000",
            [
                "Consolas",
                9
            ]
        ],
        "value": [
            "#00bf00",
            [
                "Consolas",
                9
            ]
        ],
        "comment": [
            "#808080",
            [
                "Consolas",
                9,
                "italic"
            ]
        ]
    }
}
self_closing_tags = {
    "br", "img", "hr", "input", "meta", "link"
}

win = tk.Tk()
win.minsize(500, 400)
win.grid_rowconfigure(1, weight=1)
win.grid_columnconfigure(0, weight=1)
win.grid_columnconfigure(1, weight=1)

style = ttk.Style()
style.theme_use("default")

style.configure("TFrame", background="SystemButtonFace")

style.configure("TButton", background="SystemButtonFace")
style.map("TButton", background=[("pressed", "#ffff00"), ("active", "SystemButtonFace"), ("disabled", "SystemButtonFace"), ("!active", "SystemButtonFace")])

style.configure("TProgressbar", background="#0040bf", troughcolor="#bfbfbf")

style.configure("TScrollbar", background="SystemButtonFace", troughcolor="#bfbfbf", arrowsize=14)
style.map("TScrollbar", background=[("active", "SystemButtonFace"), ("!active", "SystemButtonFace")], relief=[("pressed", "sunken")])

style.configure("Out.TFrame", background="SystemButtonFace", borderwidth=1, relief=tk.RAISED)

style.configure("In.TFrame", background="SystemButtonFace", borderwidth=1, relief=tk.SUNKEN)

style.configure("ToolbarButton.TButton", background="SystemButtonFace", relief=tk.FLAT, width=5, padding=(0, 5), font=("Segoe Fluent Icons", 10))
style.map("ToolbarButton.TButton", background=[("pressed", "#ffff00"), ("active", "SystemButtonFace")])

style.configure("MarkedToolbarButton.TButton", background="SystemButtonFace", foreground="#0040bf", relief=tk.FLAT, width=5, padding=(0, 5), font=("Segoe Fluent Icons", 10))
style.map("MarkedToolbarButton.TButton", background=[("pressed", "#0040bf"), ("active", "SystemButtonFace")], foreground=[("pressed", "#ffffff"), ("active", "#0040bf")])

style.configure("DangerToolbarButton.TButton", background="SystemButtonFace", foreground="#bf0000", relief=tk.FLAT, width=5, padding=(0, 5), font=("Segoe Fluent Icons", 10))
style.map("DangerToolbarButton.TButton", background=[("pressed", "#bf0000"), ("active", "SystemButtonFace")], foreground=[("pressed", "#ffffff"), ("active", "#bf0000")])

def report_callback_exception(exc_type, exc_value, exc_traceback):
    error_handler(exc_type, exc_value, exc_traceback, language=language.get())

sys.excepthook = lambda t, v, tb: error_handler(t, v, tb, language=language.get())
win.report_callback_exception = report_callback_exception

with open(os.path.join(data_directory, "MenuLabels.json"), "r", encoding="utf-8") as f:
    menu_labels_dict = json.load(f)
    
with open(os.path.join(data_directory, "ToolTipLabels.json"), "r", encoding="utf-8") as f:
    tooltip_dict = json.load(f)
    
with open(os.path.join(data_directory, "AutoCompleterNames.json"), "r", encoding="utf-8") as f:
    names = json.load(f)

with open(os.path.join(data_directory, "Dialogs.json"), "r", encoding="utf-8") as f:
    dialog_dict = json.load(f)

with open(os.path.join(data_directory, "Labels.json"), "r", encoding="utf-8") as f:
    label_dict = json.load(f)

if os.path.exists(configuration_file):
    try:
        with open(configuration_file, "r", encoding="utf-8") as f:
            configuration = json.load(f)

        for key, value in default_configuration.items():
            configuration.setdefault(key, value)

    except json.JSONDecodeError:
        messagebox.showwarning("Warning", "The configuration file is corrupt. Therefore, the settings have been reset.")
        configuration = default_configuration.copy()
else:
    messagebox.showwarning("Warning", "The configuration file has been moved to another location or deleted. Therefore, the settings have been reset.")
    configuration = default_configuration.copy()
    
size = configuration.get("window_size", "800x600")

try:
    win.geometry(size)
except:
    win.geometry("800x600")

state = configuration.get("window_state", "normal")

if state == "zoomed":
    win.state("zoomed")
elif state == "iconic":
    win.iconify()
          
show_tooltip = tk.BooleanVar(value=configuration["show_tooltip"])
language = tk.StringVar(value=configuration["language"])
auto_save = tk.BooleanVar(value=configuration["auto_save"])
fullscreen = tk.BooleanVar(value=False)
cover = tk.BooleanVar(value=False)
hghlgtning = tk.BooleanVar(value=configuration["highlighting"])
lnnumbers = tk.BooleanVar(value=configuration["line_numbers"])
font_size = configuration["font_size"]
auto_complete = tk.BooleanVar(value=configuration["auto_complete"])
indent_level = tk.IntVar(value=configuration["indent_level"])
smart_tag_completing = tk.BooleanVar(value=configuration["smart_tag_completing"])
TAG_COLORS = configuration["syntax_highlighting"]

for key in TAG_COLORS:
    color, font = TAG_COLORS[key]
    TAG_COLORS[key] = [color, tuple(font)]

editor = ttk.Frame(win, width=800, height=600, style="Out.TFrame")
editor.grid(padx=10, pady=10, row=1, column=0, columnspan=2, sticky="nsew")

status_bar = ttk.Label(win, text="", anchor="w")
status_bar.grid(padx=10, pady=(0, 10), row=2, column=0, columnspan=2, sticky="ew")

line_numbers = tk.Canvas(editor, width=45, background="#f0f0f0", highlightthickness=0)

text = tk.Text(editor, wrap="none", width=60, height=20, font=("Consolas", font_size), bd=1, undo=True, padx=5, pady=5, selectbackground="#0040bf")

def highlight(widget):
    if hghlgtning.get():
        highlighter(widget, tag_colors=TAG_COLORS)
        update_fonts()
    else:
        for tag in TAG_COLORS.keys():
            widget.tag_remove(tag, "1.0", "end")

        widget.config(fg="#000000")

def save_file(force=False):
    global current_file, changed

    if current_file is None:
        save_as()
        return

    if changed or force:
        try:
            with open(current_file, "w", encoding="utf-8") as f:
                f.write(text.get("1.0", "end-1c"))

            win.title(f'BukiHTML - {current_file}')
            changed = False
            save.config(state="disabled")
            update_status()
        except Exception:
            error_handler(*sys.exc_info(), language.get())

def save_as():
    global current_file, filepath, dialogs

    filepath = filedialog.asksaveasfilename(defaultextension='.html', filetypes=[(dialogs["save"][0], '*.html'), (dialogs["save"][1], '*.*')], title=dialogs["save"][2])

    if filepath:
        current_file = filepath
        win.title(f'BukiHTML - {filepath}')
        save_file(force=True)
        
def open_file():
    global filepath, current_file, changed

    filepath = filedialog.askopenfilename(title=dialogs["open"][2], filetypes=[(dialogs["open"][0], '*.html'), (dialogs["open"][1], '*.*')])
    
    if filepath:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                opened_file = f.read()
                
            text.delete(1.0, tk.END)
            text.insert(1.0, opened_file)
            current_file = filepath
            win.title(f'BukiHTML - {current_file}')
            changed = False
            text.edit_modified(False)
            update()
            highlight(text)
            save.config(state="disabled")
            text.edit_reset()
            update_status()
        except Exception:
            error_handler(*sys.exc_info(), language=language.get())

def new_file():
    global current_file, filepath, changed
    if changed:
        confirm = messagebox.askyesnocancel(dialogs["svwarn"][0], dialogs["svwarn"][1])
            
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
    text.edit_reset()
    win.update_idletasks()

def update_title():
    title = labels[1] if current_file is None else f"BukiHTML - {current_file}"
        
    if changed:
        title += " *"
    win.title(title)
        
def save_on_exit():
    global changed

    win.attributes("-fullscreen", False)
    cover.set(False)

    win.update_idletasks()
    configuration["window_size"] = win.geometry().split("+")[0]
    configuration["window_state"] = str(win.state())

    update_settings()

    if changed:
        confirm = messagebox.askyesnocancel(dialogs["svwarn"][0], dialogs["svwarn"][1])

        if confirm:
            save_file()
            win.destroy()
        elif confirm == False:
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
    messagebox.showinfo(dialogs["about"][0], dialogs["about"][1])
    
def autosv(event):
    global current_file
    if current_file and auto_save.get():
        save_file()
        
def redraw_line_numbers(event=None):
    global font_size
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
            font=("Consolas", font_size)
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
    
def check_easter_egg(event=None):
    if text.get("1.0", "end-1c").strip().lower() == "bad apple":
        webbrowser.open("https://www.youtube.com/watch?v=FtutLA63Cp8")

if hasattr(sys, "_MEIPASS"):
    icon_path = os.path.join(sys._MEIPASS, "Icon.ico")
else:
    icon_path = os.path.join(os.path.dirname(__file__), "Icon.ico")

if os.path.exists(icon_path):
    win.iconbitmap(icon_path)

toolbar_frame = ttk.Frame(win)
toolbar_frame.grid(row=0, column=0, sticky="ew")

file_toolbar = ttk.Frame(toolbar_frame, padding=5, style="Out.TFrame")
file_toolbar.grid(row=0, column=0, padx=(10, 0), pady=(10, 0), sticky="w")

html_toolbar = ttk.Frame(toolbar_frame, padding=5, style="Out.TFrame")
html_toolbar.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="w")

about_toolbar_frame = ttk.Frame(win)
about_toolbar_frame.grid(row=0, column=1, sticky="e")

about_toolbar = ttk.Frame(about_toolbar_frame, padding=5, style="Out.TFrame")
about_toolbar.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="e")

new = ttk.Button(file_toolbar, text="\uE130", command=new_file, style="ToolbarButton.TButton")
new.grid(row=0, column=0)

open_ = ttk.Button(file_toolbar, text="\uE197", command=open_file, style="ToolbarButton.TButton")
open_.grid(row=0, column=1)

save = ttk.Button(file_toolbar, text="\uE105", command=save_file, style="ToolbarButton.TButton", state=("normal" if not filepath else "disabled"))
save.grid(row=0, column=2)

run = ttk.Button(html_toolbar, text="\uE163", command=run_, style="MarkedToolbarButton.TButton")
run.grid(row=0, column=3)

about = ttk.Button(about_toolbar, text="\uE946", command=show_about, style="ToolbarButton.TButton")
about.grid(row=0, column=0, sticky="e")

scroll = ttk.Scrollbar(editor)
scroll.pack(side="right", padx=(0, 5), pady=5, fill="y")
scroll.config(command=on_scrollbar)

scroll_h = ttk.Scrollbar(editor, orient="horizontal")
scroll_h.pack(side="bottom", padx=(5, 0), pady=(0, 5), fill="x")
scroll_h.config(command=text.xview)
text.config(
    xscrollcommand=scroll_h.set,
    yscrollcommand=on_text_scroll
)

line_numbers.pack(side="left", fill="y", padx=(5, 0), pady=5)
text.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=(5, 0))

auto_completer = AutoCompleter(text, names, font_size=font_size)

def indent(event=None):
    spaces = " " * indent_level.get()

    try:
        selection = text.tag_ranges("sel")
        if selection:
            start, end = selection
            lines = text.get(start, end).splitlines()
            indented = "\n".join(spaces + line for line in lines)
            text.delete(start, end)
            text.insert(start, indented)
        else:
            text.insert("insert", spaces)
    except:
        text.insert("insert", spaces)

    return "break"

def unindent(event=None):
    spaces = indent_level.get()
    try:
        selection = text.tag_ranges("sel")
        if selection:
            start, end = selection
            lines = text.get(start, end).splitlines()
            unindented = "\n".join(
                line[spaces:] if line.startswith(" " * spaces) else line
                for line in lines
            )
            text.delete(start, end)
            text.insert(start, unindented)
        else:
            cur_line = text.get("insert linestart", "insert lineend")
            if cur_line.startswith(" " * spaces):
                text.delete("insert linestart", f"insert linestart+{spaces}c")
    except:
        pass
    return "break"

def update_settings(*args):
    global menu_labels, configuration_file, tooltip_labels, font_size, TAG_COLORS, dialogs, labels

    try:
        menu_labels = menu_labels_dict[language.get()]
        tooltip_labels = tooltip_dict[language.get()]
        dialogs = dialog_dict[language.get()]
        labels = label_dict[language.get()]
    except:
        menu_labels = menu_labels_dict["english"]
        tooltip_labels = tooltip_dict["english"]
        dialogs = dialog_dict["english"]
        labels = label_dict["english"]
    
    ToolTip(about, tooltip_labels[4], shown=show_tooltip.get())
    ToolTip(run, f"{tooltip_labels[3]} - Ctrl+P", shown=show_tooltip.get())
    ToolTip(save, f"{tooltip_labels[2]} - Ctrl+S", shown=show_tooltip.get())
    ToolTip(open_, f"{tooltip_labels[1]} - Ctrl+O", shown=show_tooltip.get())
    ToolTip(new, f"{tooltip_labels[0]} - Ctrl+N", shown=show_tooltip.get())
        
    if lnnumbers.get():
        line_numbers.config(width=45)
    else:
        line_numbers.config(width=0)

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
    edit_menu.entryconfig(10, label=menu_labels["edit"]["menus"][8])
    
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
    pre_menu.entryconfig(3, label=menu_labels["settings"]["menus"][3])
    pre_menu.entryconfig(4, label=menu_labels["settings"]["menus"][4])
    pre_menu.entryconfig(5, label=menu_labels["settings"]["menus"][5])
    pre_menu.entryconfig(6, label=menu_labels["settings"]["menus"][6])
    pre_menu.entryconfig(7, label=menu_labels["settings"]["menus"][7])
    pre_menu.entryconfig(8, label=menu_labels["settings"]["menus"][14])

    syntax_menu.entryconfig(0, label=f"{menu_labels['settings']['menus'][8]}: {TAG_COLORS['tag'][0]}")
    syntax_menu.entryconfig(1, label=f"{menu_labels['settings']['menus'][9]}: {TAG_COLORS['attribute'][0]}")
    syntax_menu.entryconfig(2, label=f"{menu_labels['settings']['menus'][10]}: {TAG_COLORS['value'][0]}")
    syntax_menu.entryconfig(3, label=f"{menu_labels['settings']['menus'][11]}: {TAG_COLORS['comment'][0]}")
    syntax_menu.entryconfig(4, label=f"{menu_labels['settings']['menus'][12]}: {configuration['background']}")
    syntax_menu.entryconfig(5, label=f"{menu_labels['settings']['menus'][13]}: {configuration['foreground']}")
    
    menu.entryconfig(5, label=menu_labels["tools"]["label"])
    tool_menu.entryconfig(0, label=menu_labels["tools"]["menus"][0])
    tool_menu.entryconfig(1, label=menu_labels["tools"]["menus"][1])

    auto_completer.shown = auto_complete.get()
    auto_completer.font_size = font_size

    text.config(bg=configuration['background'])
    text.config(fg=configuration['foreground'])

    update_title()
    update_status()
    
    config = {
        "show_tooltip": show_tooltip.get(),
        "language": language.get(),
        "auto_save": auto_save.get(),
        "highlighting": hghlgtning.get(),
        "line_numbers": lnnumbers.get(),
        "window_size": f"{win.winfo_width()}x{win.winfo_height()}",
        "window_state": str(win.state()),
        "font_size": font_size,
        "auto_complete": auto_complete.get(),
        "indent_level": indent_level.get(),
        "background": text.cget("bg"),
        "foreground": text.cget("fg"),
        "smart_tag_completing": smart_tag_completing.get(),
        "syntax_highlighting": TAG_COLORS
        }
        
    with open(configuration_file, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
        
def update_fonts():
    global TAG_COLORS

    text.config(font=("Consolas", font_size))

    for tag, style in TAG_COLORS.items():
        color = style[0]
        font_style = list(style[1])

        if len(font_style) >= 2:
            font_style[1] = font_size
        else:
            font_style.append(font_size)

        TAG_COLORS[tag] = [color, tuple(font_style)]

        text.tag_configure(
            tag,
            foreground=color,
            font=tuple(font_style),
            selectforeground="#ffffff"
        )
        
def increase_size():
    global font_size
    if font_size < 24:
        font_size += 1
        update_fonts()
        highlight(text)
        update_settings()
        redraw_line_numbers()

def decrease_size():
    global font_size
    if font_size > 6:
        font_size -= 1
        update_fonts()
        highlight(text)
        update_settings()
        redraw_line_numbers()
        
def reset_size():
    global font_size
    font_size = default_configuration["font_size"]
    update_fonts()
    highlight(text)
    update_settings()
    redraw_line_numbers()
    
def update_view(*args):
    if fullscreen.get():
        win.attributes("-fullscreen", True)
    else:
        win.attributes("-fullscreen", False)
        
    if cover.get():
        toolbar_frame.grid_forget()
        about_toolbar_frame.grid_forget()
        status_bar.grid_forget()
        editor.grid_configure(padx=0, pady=0, row=1, column=0, columnspan=2, sticky="nsew")
        editor.config(style="TFrame")
    else:
        toolbar_frame.grid(row=0, column=0, sticky="ew")
        about_toolbar_frame.grid(row=0, column=1, sticky="e")
        status_bar.grid(padx=10, pady=(0, 10), row=2, column=0, columnspan=2, sticky="ew")
        editor.grid_configure(padx=10, pady=10, row=1, column=0, columnspan=2, sticky="nsew")
        editor.config(style="Out.TFrame")
        
def update_status():
    global current_file
    newfile_status = labels[0]
        
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
    
def enter_key(event=None):
    if event and (event.state & 0x0001):
        return

    line = text.get("insert linestart", "insert lineend")
    base_indent = len(line) - len(line.lstrip(" "))
    text.insert("insert", "\n" + " " * base_indent)
    return "break"

def shift_enter_key(event=None):
    line = text.get("insert linestart", "insert lineend")
    base_indent = len(line) - len(line.lstrip(" "))
    text.insert("insert", "\n" + " " * (base_indent + indent_level.get()))
    return "break"

def on_modified(event=None):
    update()
    highlight(text)
    redraw_line_numbers()
    check_easter_egg()
    text.edit_modified(False)

def smart_backspace(event=None):
    spaces = indent_level.get()
    cur = text.get("insert linestart", "insert")

    if cur.endswith(" " * spaces):
        text.delete(f"insert-{spaces}c", "insert")
        return "break"

def auto_close_tag(event=None):
    if smart_tag_completing.get():
        if event.char != ">":
            return

        cursor = text.index("insert")
        line_start = text.get("insert linestart", "insert")

        match = re.search(r"<([a-zA-Z0-9]+)$", line_start)
        if not match:
            return

        tag = match.group(1)

        if tag.startswith("/"):
            return

        if tag in self_closing_tags:
            return

        text.insert(cursor, f"</{tag}>")
        text.mark_set("insert", cursor)

        return

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_text_color_hex(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    luminance = 0.299*r + 0.587*g + 0.114*b
    return "#000000" if luminance > 150 else "#FFFFFF"

def set_syntax_color(syntax, menuconfig=0):
    global TAG_COLORS
    color = pick_syntax_color(win, TAG_COLORS, syntax=syntax, language=language.get())
    highlight(text)
    if color:
        syntax_menu.entryconfig(menuconfig, background=color, foreground=get_text_color_hex(color))
    update_settings()

def set_background_color():
    color = pick_background_color(win, language=language.get())
    highlight(text)
    if color:
        configuration["background"] = color
        text.config(bg=color)
        syntax_menu.entryconfig(4, background=color, foreground=get_text_color_hex(color))
    update_settings()

def set_foreground_color():
    color = pick_foreground_color(win, language=language.get())
    highlight(text)
    if color:
        configuration["foreground"] = color
        text.config(fg=color)
        syntax_menu.entryconfig(5, background=color, foreground=get_text_color_hex(color))
    update_settings()
    
show_tooltip.trace_add("write", update_settings)
language.trace_add("write", update_settings)
auto_save.trace_add("write", update_settings)
hghlgtning.trace_add("write", update_settings)
lnnumbers.trace_add("write", update_settings)
fullscreen.trace_add("write", update_view)
cover.trace_add("write", update_view)
auto_complete.trace_add("write", update_settings)
indent_level.trace_add("write", update_settings)

text.bind("<Shift-Tab>", unindent)
text.bind("<Tab>", indent)
text.bind("<BackSpace>", smart_backspace)
text.bind(">", auto_close_tag)

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
win.bind("<F11>", toggle_fullscreen)
win.bind("<Escape>", exit_fullscreen)

menu = tk.Menu(win)
win.config(menu=menu)

file_menu = tk.Menu(menu, tearoff=0, activebackground="#0040bf", activeforeground="#ffffff")
file_menu.add_command(label="", command=new_file, accelerator="Ctrl+N")
file_menu.add_command(label="", command=lambda: subprocess.Popen([sys.executable, __file__]), accelerator="Ctrl+Shift+N")
file_menu.add_separator()
file_menu.add_command(label="", command=open_file, accelerator="Ctrl+O")
file_menu.add_command(label="", command=save_file, accelerator="Ctrl+S")
file_menu.add_command(label="", command=save_as, accelerator="Ctrl+Shift+S")
file_menu.add_separator()
file_menu.add_command(label="", command=lambda: win.destroy(), accelerator="Alt+F4")
menu.add_cascade(menu=file_menu, label="")

edit_menu = tk.Menu(menu, tearoff=0, activebackground="#0040bf", activeforeground="#ffffff")
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
edit_menu.add_command(label="", command=lambda: text.event_generate('<Shift-Return>'), accelerator="Shift+Enter")
menu.add_cascade(menu=edit_menu, label="")

view_menu = tk.Menu(menu, tearoff=0, activebackground="#0040bf", activeforeground="#ffffff")
view_menu.add_command(label="", command=increase_size, accelerator="Ctrl++")
view_menu.add_command(label="", command=decrease_size, accelerator="Ctrl+-")
view_menu.add_command(label="", command=reset_size, accelerator="Ctrl+Shift+R")
view_menu.add_separator()
view_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=fullscreen, accelerator="F11")
view_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=cover)
menu.add_cascade(menu=view_menu, label="")

pre_menu = tk.Menu(menu, tearoff=0, activebackground="#0040bf", activeforeground="#ffffff")
pre_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=auto_save)
pre_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=show_tooltip)
pre_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=hghlgtning)
pre_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=lnnumbers)
pre_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=auto_complete)
pre_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=smart_tag_completing)

indent_menu = tk.Menu(pre_menu, tearoff=0, activebackground="#0040bf", activeforeground="#ffffff")
indent_menu.add_radiobutton(label="2", variable=indent_level, value=2)
indent_menu.add_radiobutton(label="3", variable=indent_level, value=3)
indent_menu.add_radiobutton(label="4", variable=indent_level, value=4)
indent_menu.add_radiobutton(label="5", variable=indent_level, value=5)
indent_menu.add_radiobutton(label="6", variable=indent_level, value=6)
pre_menu.add_cascade(menu=indent_menu, label="")

syntax_menu = tk.Menu(pre_menu, tearoff=0, activebackground="#0040bf", activeforeground="#ffffff")
syntax_menu.add_command(label="", command=lambda: set_syntax_color("tag", menuconfig=0), background=TAG_COLORS["tag"][0], foreground=get_text_color_hex(TAG_COLORS["tag"][0]))
syntax_menu.add_command(label="", command=lambda: set_syntax_color("attribute", menuconfig=1), background=TAG_COLORS["attribute"][0], foreground=get_text_color_hex(TAG_COLORS["attribute"][0]))
syntax_menu.add_command(label="", command=lambda: set_syntax_color("value", menuconfig=2), background=TAG_COLORS["value"][0], foreground=get_text_color_hex(TAG_COLORS["value"][0]))
syntax_menu.add_command(label="", command=lambda: set_syntax_color("comment", menuconfig=3), background=TAG_COLORS["comment"][0], foreground=get_text_color_hex(TAG_COLORS["comment"][0]))
syntax_menu.add_command(label="", command=lambda: set_background_color(), background=configuration["background"], foreground=get_text_color_hex(configuration["background"]))
syntax_menu.add_command(label="", command=lambda: set_foreground_color(), background=configuration["foreground"], foreground=get_text_color_hex(configuration["foreground"]))
pre_menu.add_cascade(menu=syntax_menu, label="")

lang_menu = tk.Menu(pre_menu, tearoff=0, activebackground="#0040bf", activeforeground="#ffffff")
lang_menu.add_radiobutton(label='Türkçe', variable=language, value="turkish")
lang_menu.add_radiobutton(label='English', variable=language, value="english")
lang_menu.add_radiobutton(label='Deutsch', variable=language, value="german")
lang_menu.add_radiobutton(label='Pусский', variable=language, value="russian")
lang_menu.add_radiobutton(label='Español', variable=language, value="spanish")
lang_menu.add_radiobutton(label='Français', variable=language, value="french")
pre_menu.add_cascade(menu=lang_menu, label="")
menu.add_cascade(menu=pre_menu, label="")

tool_menu = tk.Menu(menu, tearoff=0, activebackground="#0040bf", activeforeground="#ffffff")
form_menu = tk.Menu(tool_menu, tearoff=0, activebackground="#0040bf", activeforeground="#ffffff")

def insert_tag(tag):
    text.insert(tk.INSERT, tag)
    highlight(text)

groups = defaultdict(list)
for tg in names:
    clean_tag = tg.strip("<>").lower()
    first_letter = clean_tag[0]
    groups[first_letter].append(tg)

for letter, tags in sorted(groups.items()):
    submenu = tk.Menu(form_menu, tearoff=0)
    for tg in tags:
        submenu.add_command(label=tg, command=lambda tg=tg: insert_tag(tg), activebackground="#0040bf", activeforeground="#ffffff")
    form_menu.add_cascade(label=letter.upper(), menu=submenu)

tool_menu.add_cascade(menu=form_menu, label="")
tool_menu.add_command(label="", command=lambda: md2html_dialog(win, TAG_COLORS, language=language.get(), font_size=font_size))
menu.add_cascade(menu=tool_menu, label="")

update_settings()

text.bind('<Button-3>', lambda event: edit_menu.tk_popup(event.x_root, event.y_root))
text.bind("<<Modified>>", on_modified)
text.bind("<KeyRelease>", autosv, add='+')
text.bind("<KeyRelease>", lambda e: update_status(), add='+')
text.bind("<ButtonRelease-1>", update_status_idle)
win.protocol("WM_DELETE_WINDOW", save_on_exit)
text.bind("<MouseWheel>", redraw_line_numbers)
text.bind("<Button-4>", redraw_line_numbers)
text.bind("<Button-5>", redraw_line_numbers)
text.bind("<Return>", enter_key)
text.bind("<Shift-Return>", shift_enter_key)

redraw_line_numbers()

win.mainloop()