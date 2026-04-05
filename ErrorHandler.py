import tkinter as tk
import traceback
from ToolWindow import toolwindow

def error_handler(exc_type, exc_value, exc_traceback, parent, language="türkçe"):
    tb_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    errorwin = tk.Toplevel(parent)     
    errorwin.resizable(False, False)
    errorwin.transient(parent)
    errorwin.lift()
    errorwin.focus_force()
    toolwindow(errorwin)
    errorwin.grab_set()
    
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
    
    frame2 = tk.Frame(errorwin, bd=1, relief="raised")
    frame2.pack(padx=20, pady=(0, 20))
    
    def copy_error():
         error_content = error.get("1.0", "end-1c")
         error.clipboard_clear()
         error.clipboard_append(error_content)
         cp.config(state="disabled")
    
    ok = tk.Button(frame2, text="", bd=0, command=lambda: errorwin.destroy(), width=10, activebackground="#ffff00")
    ok.grid(padx=3, pady=3, row=0, column=0)
    cp = tk.Button(frame2, text="", bd=0, command=copy_error, width=10, activebackground="#ffff00")
    cp.grid(padx=(0, 3), pady=3, row=0, column=1)
    
    if language == "türkçe":
        errorwin.title("Hata")
        ok.config(text="Tamam")
        cp.config(text="Kopyala")
    elif language == "english":
        errorwin.title("Error")
        ok.config(text="Ok")
        cp.config(text="Copy")
    elif language == "deutsch":
        errorwin.title("Fehler")
        ok.config(text="Okay")
        cp.config(text="Kopieren")
    elif language == "русский":
        errorwin.title("Ошибка")
        ok.config(text="Окей")
        cp.config(text="Копировать")