import tkinter as tk
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

class AutoCompleter:
    def __init__(self, text_widget, words):
        self.text = text_widget
        self.words = words

        self.popup = None
        self.listbox = None

        self.text.bind("<KeyRelease>", self._on_keyrelease, add="+")
        self.text.bind("<Down>", self._down)
        self.text.bind("<Up>", self._up)
        self.text.bind("<Tab>", self._complete_if_popup, add="+")
        self.text.bind("<FocusOut>", self._hide, add="+")

    def _complete_if_popup(self, event):
        if self.popup:
            return self._complete(event)
        return None

    def _get_current_word(self):
        insert = self.text.index("insert")
        start = insert

        while True:
            prev = self.text.index(f"{start} -1c")
            if prev == start:
                break

            c = self.text.get(prev)
            if not (c.isalnum() or c in "_<"):
                break

            start = prev

        word = self.text.get(start, insert)
        return start, word

    def _on_keyrelease(self, event):
        if event.keysym in ("Up", "Down", "Tab", "Escape"):
            return

        start, word = self._get_current_word()

        if word.startswith("<"):
            word = word[1:]

        if not word:
            self._hide()
            return

        matches = [w for w in self.words if w.lstrip("<").startswith(word)]
        if matches:
            self._show(matches)
        else:
            self._hide()

    def _down(self, event):
        if self.listbox and self.listbox.curselection():
            i = self.listbox.curselection()[0]
            self.listbox.selection_clear(i)
            self.listbox.selection_set(min(i + 1, self.listbox.size() - 1))
        return "break"

    def _up(self, event):
        if self.listbox and self.listbox.curselection():
            i = self.listbox.curselection()[0]
            self.listbox.selection_clear(i)
            self.listbox.selection_set(max(i - 1, 0))
        return "break"

    def _complete(self, event):
        if not self.listbox:
            return "break"

        value = self.listbox.get(tk.ACTIVE)
        start, _ = self._get_current_word()

        self.text.delete(start, "insert")
        self.text.insert(start, value)

        self._hide()
        return "break"

    def _show(self, matches):
        if not self.popup:
            self.popup = tk.Toplevel(self.text, bd=1, relief="raised")
            self.popup.transient(self.text.winfo_toplevel())
            self.popup.overrideredirect(True)
            self.popup.lift(self.text.winfo_toplevel())

            self.listbox = tk.Listbox(
                self.popup,
                height=10,
                width=20,
                font=("Consolas", 10),
                bd=1,
                highlightthickness=0
            )
            self.listbox.pack(padx=(5, 0), pady=5, side="left")
            self.listbox.bind("<Double-Button-1>", self._mouse_select)
            
            self.scrollbar = tk.Scrollbar(self.popup, orient="vertical")
            self.scrollbar.pack(padx=(0, 5), pady=5, side="right", fill="y")
            
            self.scrollbar.config(command=self.listbox.yview)
            self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.listbox.delete(0, tk.END)
        for m in matches:
            self.listbox.insert(tk.END, m)

        self.listbox.selection_set(0)

        bbox = self.text.bbox("insert")
        if not bbox:
            return

        x, y, w, h = bbox
        x += self.text.winfo_rootx()
        y += self.text.winfo_rooty() + h

        self.popup.geometry(f"+{x}+{y}")
        
    def _mouse_select(self, event):
        if not self.listbox:
            return

        index = self.listbox.nearest(event.y)
        value = self.listbox.get(index)
        start, _ = self._get_current_word()

        self.text.delete(start, "insert")
        self.text.insert(start, value)

        self._hide()

    def _hide(self, event=None):
        if not self.popup:
            return

        current_focus = self.text.focus_get()

        if current_focus and str(current_focus).startswith(str(self.popup)):
            return

        self.popup.destroy()
        self.popup = None
        self.listbox = None
            
    def _check_focus(self):
        if not self.text.focus_get():
            self._hide()

