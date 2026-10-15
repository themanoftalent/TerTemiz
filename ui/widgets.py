"""Localized widgets and responsive table layout without changing callback keys."""
import customtkinter as _ctk
import textwrap
import tkinter
from ui.theme import CCleanerTheme
from ui.i18n import tr


def __getattr__(name):
    return getattr(_ctk, name)


class _Localized:
    def __init__(self, *args, **kwargs):
        self._source_text = kwargs.get("text")
        self._source_placeholder = kwargs.get("placeholder_text")
        if "text" in kwargs:
            kwargs["text"] = self._display_text(kwargs["text"])
        if "placeholder_text" in kwargs:
            kwargs["placeholder_text"] = tr(kwargs["placeholder_text"])
        super().__init__(*args, **kwargs)
        self._text_wrap_binding = None
        if isinstance(self, (_ctk.CTkCheckBox, _ctk.CTkSwitch)):
            self._text_wrap_binding = tkinter.Misc.bind(self.master, "<Configure>", lambda event: self.configure(text=self._source_text), add="+")

    def destroy(self):
        if getattr(self, "_text_wrap_binding", None):
            try:
                tkinter.Misc.unbind(self.master, "<Configure>", self._text_wrap_binding)
            except tkinter.TclError:
                pass
            self._text_wrap_binding = None
        super().destroy()

    def configure(self, require_redraw=False, **kwargs):
        if "text" in kwargs:
            self._source_text = kwargs["text"]
            kwargs["text"] = self._display_text(kwargs["text"])
        if "placeholder_text" in kwargs:
            self._source_placeholder = kwargs["placeholder_text"]
            kwargs["placeholder_text"] = tr(kwargs["placeholder_text"])
        return super().configure(require_redraw=require_redraw, **kwargs)

    def _display_text(self, text):
        translated = tr(text)
        if isinstance(self, (_ctk.CTkCheckBox, _ctk.CTkSwitch)) and isinstance(translated, str):
            parent = getattr(self, "master", None)
            width = parent.winfo_width() if parent is not None else 0
            characters = max(12, int((self._reverse_widget_scaling(width) - 52) / 7)) if width > 60 else 30
            return "\n".join(textwrap.fill(line, width=characters) for line in translated.split("\n"))
        return translated

    def refresh_language(self):
        options = {}
        if self._source_text is not None:
            options["text"] = self._source_text
        if self._source_placeholder is not None:
            options["placeholder_text"] = self._source_placeholder
        if options:
            self.configure(**options)


class CTkLabel(_Localized, _ctk.CTkLabel):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("wraplength", 520)
        if getattr(master, "_table_constrained", False):
            kwargs.setdefault("width", 1)
            kwargs["wraplength"] = 100
        super().__init__(master, **kwargs)
        self._wrap_binding = tkinter.Misc.bind(master, "<Configure>", self._wrap_to_parent, add="+")
        tkinter.Misc.bind(self, "<Configure>", self._wrap_grid_cell, add="+")

    def pack(self, **kwargs):
        if getattr(self.master, "_table_constrained", False):
            kwargs.setdefault("fill", "x")
        return super().pack(**kwargs)

    def destroy(self):
        if getattr(self, "_wrap_binding", None):
            try:
                tkinter.Misc.unbind(self.master, "<Configure>", self._wrap_binding)
            except tkinter.TclError:
                pass
            self._wrap_binding = None
        super().destroy()

    def _wrap_grid_cell(self, event):
        if self.winfo_manager() == "grid":
            self._set_wrap_width(event.width, 16)

    def _set_wrap_width(self, width, padding):
        width = max(40, self._reverse_widget_scaling(width) - padding)
        if self.cget("wraplength") != width:
            self.configure(wraplength=width)

    def _wrap_to_parent(self, event):
        # A grid cell has its own allocated column width. Packed labels use the
        # parent's width so paragraphs can grow vertically instead of clipping.
        if self.winfo_manager() == "grid":
            self._set_wrap_width(self.winfo_width(), 16)
        else:
            self._set_wrap_width(event.width, 32)


class CTkButton(_Localized, _ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        if kwargs.get("fg_color") in (CCleanerTheme.BG_INPUT, CCleanerTheme.BG_CARD, CCleanerTheme.BG_CARD_HOVER):
            kwargs.setdefault("text_color", CCleanerTheme.TEXT_PRIMARY)
        super().__init__(*args, **kwargs)

    def configure(self, require_redraw=False, **kwargs):
        if "fg_color" in kwargs:
            kwargs.setdefault("text_color", CCleanerTheme.TEXT_PRIMARY if kwargs["fg_color"] in (CCleanerTheme.BG_INPUT, CCleanerTheme.BG_CARD, CCleanerTheme.BG_CARD_HOVER) else "#ffffff")
        return super().configure(require_redraw=require_redraw, **kwargs)
class CTkCheckBox(_Localized, _ctk.CTkCheckBox):
    pass
class CTkSwitch(_Localized, _ctk.CTkSwitch):
    pass
class CTkEntry(_Localized, _ctk.CTkEntry):
    pass


class CTkTabview(_ctk.CTkTabview):
    def __init__(self, *args, **kwargs):
        self._tab_names = {}
        super().__init__(*args, **kwargs)

    def add(self, name, **kwargs):
        visible = tr(name)
        self._tab_names[name] = visible
        return super().add(visible, **kwargs)

    def get(self):
        visible = super().get()
        return next((key for key, value in self._tab_names.items() if value == visible), visible)

    def set(self, name):
        return super().set(self._tab_names.get(name, name))

    def tab(self, name):
        return super().tab(self._tab_names.get(name, name))

    def refresh_language(self):
        selected = self.get()
        for source, old in list(self._tab_names.items()):
            new = tr(source)
            if new != old:
                self.rename(old, new)
                self._tab_names[source] = new
        if selected:
            self.set(selected)


def refresh_language(root):
    if hasattr(root, "refresh_language"):
        root.refresh_language()
    for child in root.winfo_children():
        refresh_language(child)


def table_cell(widget, position):
    """Replace overlapping absolute table positions with weighted grid cells."""
    parent = widget.master
    positions = getattr(parent, "_table_positions", set())
    column = round(position * 100)
    positions.add(column)
    parent._table_positions = positions
    ordered = sorted(positions)
    for index, current in enumerate(ordered):
        end = ordered[index + 1] if index + 1 < len(ordered) else 100
        parent.grid_columnconfigure(current, weight=end - current, uniform="table")
    parent.grid_rowconfigure(0, weight=1)
    if isinstance(widget, _ctk.CTkFrame):
        widget.configure(width=1)
        widget._table_constrained = True
    if isinstance(widget, _ctk.CTkLabel):
        widget.configure(width=1, justify="left", anchor="w")
    widget.grid(row=0, column=column, sticky="nsew", padx=8, pady=6)
