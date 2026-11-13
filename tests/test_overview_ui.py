"""The 'Resumen' tab: it is wired into the app and its button runs the query without errors."""

from berka_bank.ui import app
from berka_bank.ui import routines as ui_routines


def find(widget, cls):
    """First descendant of the given widget class."""
    for child in getattr(widget, "children", ()):
        if isinstance(child, cls):
            return child
        if found := find(child, cls):
            return found
    return None


def test_tab_is_registered_in_the_app(loaded):
    import ipywidgets as w

    tabs = find(app.build(loaded), w.Tab)
    assert "Resumen" in tabs.titles


def test_button_renders_table_and_filters(loaded, monkeypatch):
    import ipywidgets as w

    shown = []  # outside a Jupyter kernel an Output widget captures nothing, so intercept the render calls
    monkeypatch.setattr(ui_routines, "render", lambda out, *html: shown.extend(html))
    monkeypatch.setattr(ui_routines, "message", lambda out, body, kind="ok", df=None: shown.append(f"{kind}:{body}"))

    panel = ui_routines.overview_panel(loaded)
    button = find(panel, w.Button)
    button.click()
    html = "".join(shown)
    assert "Cuentas" in html and "Saldo total" in html and "error:" not in html
    assert html.count("<tr>") == 1 + 3  # header + the 3 accounts with an owner
