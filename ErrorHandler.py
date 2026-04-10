import tkinter as tk
import traceback, datetime
from ToolWindow import toolwindow
from ToolTip import ToolTip
import os, sys, json

data_directory = os.path.join(os.path.dirname(__file__), "Data")
with open(os.path.join(data_directory, "ErrorToolTipLabels.json"), "r", encoding="utf-8") as f:
    error_tooltip_dict = json.load(f)

def error_handler(exc_type, exc_value, exc_traceback, parent, language="türkçe"):
    global error_tooltip_dict
    
    tb_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    errorwin = tk.Toplevel(parent)     
    errorwin.resizable(False, False)
    errorwin.transient(parent)
    errorwin.lift()
    errorwin.focus_force()
    toolwindow(errorwin)
    errorwin.grab_set()
    
    if language == "türkçe":
        errorwin.title("Hata")
        error_tooltips = error_tooltip_dict["türkçe"]
    elif language == "english":
        errorwin.title("Error")
        error_tooltips = error_tooltip_dict["english"]
    elif language == "deutsch":
        errorwin.title("Fehler")
        error_tooltips = error_tooltip_dict["deutsch"]
    elif language == "русский":
        errorwin.title("Ошибка")
        error_tooltips = error_tooltip_dict["русский"]
    
    if hasattr(sys, "_MEIPASS"):
        icon_path = os.path.join(sys._MEIPASS, "Icon.ico")
    else:
        icon_path = os.path.join(os.path.dirname(__file__), "Icon.ico")

    if os.path.exists(icon_path):
        errorwin.iconbitmap(icon_path)
    
    frame = tk.Frame(errorwin, bd=1, relief="raised")
    frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    if language == "türkçe":
        tk.Label(frame, text="Bir hata oluştu: ").pack(anchor="nw", padx=5, pady=(5, 0))
    elif language == "english":
        tk.Label(frame, text="An error occured: ").pack(anchor="nw", padx=5, pady=(5, 0))
    elif language == "deutsch":
        tk.Label(frame, text="Ein Fehler ist aufgetreten: ").pack(anchor="nw", padx=5, pady=(5, 0))
    elif language == "русский":
        tk.Label(frame, text="Произошла ошибка: ").pack(anchor="nw", padx=5, pady=(5, 0))
    
    error = tk.Text(frame, bd=1, font=("Consolas", 9), width=50, height=20, wrap="none", padx=5, pady=5)
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
    
    frame2 = tk.Frame(errorwin, bd=1, relief="raised", padx=3, pady=3)
    frame2.pack(padx=20, pady=(0, 20))
    
    def copy_error():
         error_content = error.get("1.0", "end-1c")
         error.clipboard_clear()
         error.clipboard_append(error_content)
         cp.config(state="disabled")
         
    def create_report():
        with open("ErrorLog.txt", "a", encoding="utf-8") as f:
            f.write(f"\nDate: {datetime.datetime.now()}\n\n{tb_text}")
        err.config(state="disabled")
    
    ok = tk.Button(frame2, text="\uE711", bd=0, command=lambda: errorwin.destroy(), width=5, pady=4, activebackground="#ffff00", font=("Segoe Fluent Icons", 10))
    ok.grid(row=0, column=0)
    cp = tk.Button(frame2, text="\uE8C8", bd=0, command=copy_error, width=5, pady=4, activebackground="#ffff00", font=("Segoe Fluent Icons", 10))
    cp.grid(row=0, column=1)
    err = tk.Button(frame2, text="\uE496", bd=0, command=create_report, width=5, pady=4, activebackground="#ffff00", font=("Segoe Fluent Icons", 10))
    err.grid(row=0, column=2)
    
    ToolTip(ok, error_tooltips[0])
    ToolTip(cp, error_tooltips[1])
    ToolTip(err, error_tooltips[2])
    