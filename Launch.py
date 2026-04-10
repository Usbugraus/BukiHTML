from tkinter import messagebox
import traceback, datetime

try:
    import Main
except Exception:
    messagebox.showerror(
        "Error",
        f"An error occured while starting BukiHTML:\n{traceback.format_exc()}"
    )
    with open("ErrorLog.txt", "a", encoding="utf-8") as f:
        f.write(f"\nDate: {datetime.datetime.now()}\n\n{traceback.format_exc()}")
    
