from tkinter import colorchooser

def pick_syntax_color(parent, tag_colors, syntax="tag", language="english"):
    titles = {
        "türkçe": "Sözdizimi Rengi Seç",
        "english": "Select Syntax Color",
        "deutsch": "Syntaxfarbe auswählen",
        "русский": "Выбрать цвет синтаксиса"
    }

    title = titles.get(language, "Select Syntax Color")

    current_color = tag_colors.get(syntax, "#ffffff")

    color = colorchooser.askcolor(
        parent=parent,
        title=title
    )

    if not color or not color[1]:
        return

    tag_colors[syntax][0] = color[1]