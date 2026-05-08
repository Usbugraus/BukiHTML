from tkinter import colorchooser
import os, json

data_directory = os.path.join(os.path.dirname(__file__), "Data")

with open(os.path.join(data_directory, "Dialogs.json"), "r", encoding="utf-8") as f:
    dialog_dict = json.load(f)

def pick_syntax_color(parent, tag_colors, syntax="tag", language="english"):
    try:
        dialogs = dialog_dict[language]
    except:
        dialogs = dialog_dict["english"]

    title = dialogs["syntax"]

    color = colorchooser.askcolor(
        parent=parent,
        title=title
    )

    if not color or not color[1]:
        return

    tag_colors[syntax][0] = color[1]
    return color[1]

def pick_background_color(parent, language="english"):
    global dialogs

    try:
        dialogs = dialog_dict[language]
    except:
        dialogs = dialog_dict["english"]

    title = dialogs["back"]

    color = colorchooser.askcolor(
        parent=parent,
        title=title
    )

    if not color or not color[1]:
        return

    return color[1]

def pick_foreground_color(parent, language="english"):
    global dialogs

    try:
        dialogs = dialog_dict[language]
    except:
        dialogs = dialog_dict["english"]

    title = dialogs["fore"]

    color = colorchooser.askcolor(
        parent=parent,
        title=title
    )

    if not color or not color[1]:
        return

    return color[1]