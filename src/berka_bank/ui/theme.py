"""Visual theme: one <style> block injected into the page (Voilà or notebook)."""

import ipywidgets as w

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bk-bg: #f2f5fb;
  --bk-card: #ffffff;
  --bk-ink: #14223a;
  --bk-muted: #6b7a92;
  --bk-line: #e3e9f3;
  --bk-soft: #f6f8fc;
  --bk-navy: #0a2342;
  --bk-primary: #1f56a8;
  --bk-primary-2: #3b82d6;
  --bk-teal: #12a594;
  --bk-gold: #e4a82d;
  --bk-ok: #17996a;
  --bk-danger: #d4444f;
  --bk-info: #2f78d1;
  --bk-radius: 16px;
  --bk-font: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  --bk-shadow: 0 1px 2px rgba(16, 36, 59, .05), 0 10px 30px rgba(16, 36, 59, .07);
}

body, .jp-Notebook, .jp-OutputArea, .jp-OutputArea-output, #rendered_cells, .jp-Cell {
  background: var(--bk-bg) !important;
}
.jp-OutputArea-prompt, .jp-InputPrompt { display: none !important; }

/* ---------- root + widget variables ---------- */
.bk-root {
  max-width: 1120px;
  margin: 0 auto;
  padding: 20px 18px 36px;
  color: var(--bk-ink);
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  font-size: 14px;
  --jp-widgets-color: var(--bk-ink);
  --jp-widgets-label-color: var(--bk-ink);
  --jp-widgets-font-size: 14px;
  --jp-widgets-inline-height: 40px;
  --jp-widgets-inline-label-width: 0px;
  --jp-widgets-input-color: var(--bk-ink);
  --jp-widgets-input-background-color: #fff;
  --jp-widgets-input-border-color: #d3dcea;
  --jp-widgets-input-focus-border-color: var(--bk-primary-2);
  --jp-widgets-input-border-width: 1px;
  --jp-widgets-border-width: 1px;
  --jp-widgets-disabled-opacity: .55;
}
.bk-root input, .bk-root select, .bk-root button { font-family: inherit; }

/* force one font everywhere (except icons and code) and clear Jupyter's output backgrounds inside the app */
.bk-root *:not(i):not(code):not(.fa) { font-family: var(--bk-font) !important; }
.bk-root .jp-OutputArea, .bk-root .jp-OutputArea-output, .bk-root .jp-OutputArea-child, .bk-root .jp-RenderedHTMLCommon { background: transparent !important; }
.bk-root .widget-html, .bk-root .widget-html-content, .bk-root .widget-hbox, .bk-root .widget-vbox { overflow: visible; }
.bk-root .jp-RenderedHTMLCommon h4 { font-weight: 700; margin: 4px 0 0; }
.bk-root .jp-RenderedHTMLCommon { padding: 0; }

/* ---------- header ---------- */
.bk-header {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;
  padding: 22px 28px; border-radius: 20px; color: #fff;
  background: radial-gradient(1200px 300px at 85% -40%, rgba(59,130,214,.55), transparent 60%),
              linear-gradient(120deg, var(--bk-navy) 0%, #12365f 60%, #1a4a80 100%);
  box-shadow: 0 10px 22px -8px rgba(10, 35, 66, .45);
}
.bk-brand { display: flex; align-items: center; gap: 16px; }
.bk-logo {
  width: 52px; height: 52px; border-radius: 15px; display: grid; place-items: center;
  background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.22); color: #ffd36e;
}
.bk-title { font-size: 24px; font-weight: 800; letter-spacing: -.02em; line-height: 1.1; }
.bk-subtitle { font-size: 13.5px; opacity: .78; margin-top: 3px; }
.bk-conn {
  display: flex; align-items: center; gap: 10px; padding: 9px 16px; border-radius: 999px;
  background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.18); font-size: 13px; font-weight: 600;
}
.bk-conn small { font-weight: 400; opacity: .75; font-size: 12px; }
.bk-dot { width: 9px; height: 9px; border-radius: 50%; background: #42e0a5; box-shadow: 0 0 0 4px rgba(66,224,165,.25); }

/* ---------- tabs ---------- */
.bk-root .widget-tab > .widget-tab-contents {
  background: transparent; border: none; padding: 18px 0 0; overflow: visible;
}
.bk-root .widget-tab > .p-TabBar, .bk-root .widget-tab > .lm-TabBar {
  min-height: 0; border: none; background: transparent; margin-top: 18px;
}
.bk-root .widget-tab > .p-TabBar .p-TabBar-content, .bk-root .widget-tab > .lm-TabBar .lm-TabBar-content {
  gap: 8px; flex-wrap: wrap;
}
.bk-root .widget-tab > .p-TabBar .p-TabBar-tab, .bk-root .widget-tab > .lm-TabBar .lm-TabBar-tab {
  flex: 0 0 auto; min-width: 0; height: auto; line-height: 20px; margin: 0;
  padding: 10px 20px; border-radius: 999px; border: 1px solid var(--bk-line) !important;
  background: #fff; color: var(--bk-muted); font-weight: 600; font-size: 14px;
  box-shadow: 0 1px 2px rgba(16,36,59,.04); transition: all .15s ease;
}
.bk-root .widget-tab > .p-TabBar .p-TabBar-tab:hover, .bk-root .widget-tab > .lm-TabBar .lm-TabBar-tab:hover {
  color: var(--bk-primary); border-color: #c5d3ea !important; background: #fff;
}
.bk-root .widget-tab > .p-TabBar .p-TabBar-tab.p-mod-current, .bk-root .widget-tab > .lm-TabBar .lm-TabBar-tab.lm-mod-current {
  background: var(--bk-navy); color: #fff; border-color: var(--bk-navy) !important;
  box-shadow: 0 6px 16px rgba(10,35,66,.28);
}
.bk-root .widget-tab > .p-TabBar .p-TabBar-tab.p-mod-current::before,
.bk-root .widget-tab > .lm-TabBar .lm-TabBar-tab.lm-mod-current::before { display: none; }

/* secondary (nested) tabs: underline style */
.bk-root .bk-subtabs > .p-TabBar, .bk-root .bk-subtabs > .lm-TabBar { margin-top: 0; border-bottom: 1px solid var(--bk-line); }
.bk-root .bk-subtabs > .p-TabBar .p-TabBar-tab, .bk-root .bk-subtabs > .lm-TabBar .lm-TabBar-tab {
  padding: 9px 16px; border-radius: 10px 10px 0 0; border: none !important; background: transparent;
  box-shadow: none; color: var(--bk-muted); font-size: 13.5px;
}
.bk-root .bk-subtabs > .p-TabBar .p-TabBar-tab.p-mod-current, .bk-root .bk-subtabs > .lm-TabBar .lm-TabBar-tab.lm-mod-current {
  background: transparent; color: var(--bk-primary); box-shadow: inset 0 -3px 0 var(--bk-primary);
}
.bk-root .bk-subtabs > .widget-tab-contents { padding-top: 18px; }

/* ---------- cards / sections ---------- */
.bk-card {
  background: var(--bk-card); border: 1px solid var(--bk-line); border-radius: var(--bk-radius);
  box-shadow: var(--bk-shadow); padding: 24px 26px;
}
.bk-root .bk-card > * + * { margin-top: 16px; }
.bk-card .bk-card { box-shadow: none; background: #fbfcfe; padding: 20px 22px; }
.bk-card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.bk-card-title { margin: 0; font-size: 18px; font-weight: 700; letter-spacing: -.01em; color: var(--bk-ink); }
.bk-card-help { margin: 5px 0 0; color: var(--bk-muted); font-size: 13.5px; line-height: 1.5; max-width: 760px; }
.bk-card-help code, .bk-callout code {
  background: var(--bk-soft); border: 1px solid var(--bk-line); padding: 1px 6px; border-radius: 6px; font-size: 12.5px;
}
.bk-badge {
  flex: 0 0 auto; padding: 4px 11px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; background: #e8f0fc; color: var(--bk-primary);
}
.bk-badge.bk-teal { background: #dcf5f1; color: #0d7d70; }
.bk-badge.bk-gold { background: #fbefd2; color: #94650b; }
.bk-root .bk-h4 { margin: 4px 0 0; font-size: 14.5px; font-weight: 700; color: var(--bk-ink); }

/* ---------- forms ---------- */
.bk-root .bk-grid { display: grid; gap: 16px 24px; width: 100%; overflow: visible; }
.bk-field { width: 100%; }
.bk-label { display: block; margin: 0 0 6px; font-size: 12.5px; font-weight: 600; color: var(--bk-muted); letter-spacing: .01em; }
.bk-root .widget-text input, .bk-root .widget-text textarea, .bk-root .widget-dropdown select,
.bk-root .widget-datepicker input, .bk-root .widget-numeric-text input {
  height: 40px; border-radius: 10px; padding: 0 12px; background-color: #fff; box-shadow: none;
  box-sizing: border-box; width: 100%; min-width: 0; margin: 0; transition: border-color .15s, box-shadow .15s;
}
.bk-root .widget-dropdown select {
  appearance: none; -webkit-appearance: none; padding-right: 36px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1.5l5 5 5-5' fill='none' stroke='%236b7a92' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 14px center;
}
.bk-root .widget-text, .bk-root .widget-dropdown, .bk-root .widget-datepicker, .bk-root .widget-numeric-text,
.bk-root .widget-bounded-int-text, .bk-root .widget-bounded-float-text { width: 100% !important; min-width: 0; box-sizing: border-box; }
.bk-root .widget-datepicker input[type=date] { padding-right: 10px; }
.bk-root .widget-text input:focus, .bk-root .widget-dropdown select:focus, .bk-root .widget-datepicker input:focus {
  border-color: var(--bk-primary-2); box-shadow: 0 0 0 3px rgba(59,130,214,.18); outline: none;
}
.bk-root input:disabled, .bk-root select:disabled { background: var(--bk-soft); color: #93a0b5; }
.bk-root .widget-checkbox { margin-top: 4px; }
.bk-row { display: flex; align-items: flex-end; gap: 14px; flex-wrap: wrap; }
.bk-row > .bk-field { flex: 0 1 340px; }
.bk-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 4px; }

/* ---------- buttons ---------- */
.bk-root .jupyter-button {
  width: auto; min-width: 150px; height: 40px; line-height: 40px; padding: 0 20px; border: none; border-radius: 10px;
  color: #fff; font-weight: 600; font-size: 14px; letter-spacing: .005em; cursor: pointer;
  box-shadow: 0 2px 6px rgba(16,36,59,.18); transition: transform .12s ease, filter .12s ease, box-shadow .12s ease;
}
.bk-root .jupyter-button:hover:not(:disabled) { filter: brightness(1.07); transform: translateY(-1px); box-shadow: 0 6px 14px rgba(16,36,59,.22); }
.bk-root .jupyter-button:active:not(:disabled) { transform: translateY(0); }
.bk-root .jupyter-button:disabled { opacity: .4; box-shadow: none; cursor: not-allowed; }
.bk-root .jupyter-button.mod-primary { background: linear-gradient(135deg, var(--bk-primary), var(--bk-primary-2)); }
.bk-root .jupyter-button.mod-success { background: linear-gradient(135deg, #129060, #22b17f); }
.bk-root .jupyter-button.mod-info    { background: linear-gradient(135deg, #2565b9, #3f8ae0); }
.bk-root .jupyter-button.mod-warning { background: linear-gradient(135deg, #e0a024, #f0bc4b); color: #3b2800; }
.bk-root .jupyter-button.mod-danger  { background: linear-gradient(135deg, #c93a46, #e0555f); }
.bk-root .jupyter-button i.fa { margin-right: 4px; }

/* ---------- callouts ---------- */
.bk-callout {
  display: flex; gap: 12px; align-items: flex-start; padding: 12px 16px; border-radius: 12px;
  border: 1px solid; font-size: 13.5px; line-height: 1.5;
}
.bk-callout-icon {
  flex: 0 0 22px; height: 22px; border-radius: 50%; display: grid; place-items: center;
  color: #fff; font-size: 12px; font-weight: 800; margin-top: 1px;
}
.bk-callout.bk-ok    { background: #eaf8f2; border-color: #bfe8d6; color: #0f5c42; }
.bk-callout.bk-error { background: #fdeff0; border-color: #f4c6ca; color: #8a2430; }
.bk-callout.bk-info  { background: #ecf3fd; border-color: #c6dbf6; color: #1b4a85; }
.bk-ok .bk-callout-icon { background: var(--bk-ok); }
.bk-error .bk-callout-icon { background: var(--bk-danger); }
.bk-info .bk-callout-icon { background: var(--bk-info); }

/* ---------- output area ---------- */
.bk-out { margin-top: 6px; }
.bk-out .jp-OutputArea-child, .bk-out .output_area { padding: 0; }
.bk-out > * + * , .bk-out .jp-OutputArea-child + .jp-OutputArea-child { margin-top: 14px; }

/* ---------- tables ---------- */
.bk-table-wrap { max-height: 380px; overflow: auto; border: 1px solid var(--bk-line); border-radius: 12px; background: #fff; }
.bk-root .bk-table { table-layout: auto; width: max-content; min-width: 100%; border-collapse: separate; border-spacing: 0; font-size: 13px; font-variant-numeric: tabular-nums; }
.bk-root .bk-table th {
  max-width: none; overflow: visible; text-overflow: clip;
  position: sticky; top: 0; z-index: 1; text-align: left; white-space: nowrap; padding: 10px 14px;
  background: var(--bk-soft); color: var(--bk-muted); font-size: 11.5px; font-weight: 700; letter-spacing: .05em;
  text-transform: uppercase; border-bottom: 1px solid var(--bk-line);
}
.bk-root .bk-table td { text-align: left; max-width: none; overflow: visible; text-overflow: clip; padding: 9px 14px; border-bottom: 1px solid #eef2f8; white-space: nowrap; color: var(--bk-ink); }
.bk-table tbody tr:nth-child(even) td { background: #fafbfe; }
.bk-table tbody tr:hover td { background: #eef4fd; }
.bk-table tbody tr:last-child td { border-bottom: none; }
.bk-root .bk-table td.bk-num, .bk-root .bk-table th.bk-num { text-align: right; }
.bk-null { color: #b6c0d0; }
.bk-table-note { padding: 8px 14px; font-size: 12px; color: var(--bk-muted); background: var(--bk-soft); border-top: 1px solid var(--bk-line); }
.bk-empty { padding: 26px; text-align: center; color: var(--bk-muted); border: 1px dashed #cfd9e8; border-radius: 12px; background: var(--bk-soft); }

/* ---------- KPIs ---------- */
.bk-kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; }
.bk-root .bk-kpi {
  position: relative; overflow: hidden; padding: 16px 18px 15px; border-radius: 14px; background: #fff;
  border: 1px solid var(--bk-line); box-shadow: 0 1px 2px rgba(16,36,59,.04);
}
.bk-kpi::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 5px; background: var(--bk-primary-2); }
.bk-kpi.bk-ok::before { background: var(--bk-ok); }
.bk-kpi.bk-danger::before { background: var(--bk-danger); }
.bk-kpi.bk-gold::before { background: var(--bk-gold); }
.bk-kpi.bk-teal::before { background: var(--bk-teal); }
.bk-kpi.bk-strong { background: linear-gradient(135deg, var(--bk-navy), #17457a); border-color: var(--bk-navy); }
.bk-kpi.bk-strong::before { background: var(--bk-gold); }
.bk-kpi-label { font-size: 11.5px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--bk-muted); }
.bk-kpi-value { margin-top: 6px; white-space: nowrap; font-size: 23px; font-weight: 800; letter-spacing: -.02em; line-height: 1.15; font-variant-numeric: tabular-nums; }
.bk-unit { font-size: 13px; font-weight: 600; opacity: .65; margin-left: 2px; }
.bk-kpi-sub { margin-top: 4px; font-size: 12px; color: var(--bk-muted); }
.bk-kpi.bk-strong .bk-kpi-label, .bk-kpi.bk-strong .bk-kpi-sub { color: rgba(255,255,255,.7); }
.bk-kpi.bk-strong .bk-kpi-value { color: #fff; }
.bk-kpi.bk-ok .bk-kpi-value { color: var(--bk-ok); }
.bk-kpi.bk-danger .bk-kpi-value { color: var(--bk-danger); }

/* ---------- bars ---------- */
.bk-bars { display: grid; gap: 13px; }
.bk-bar-top { display: flex; justify-content: space-between; gap: 12px; font-size: 13px; margin-bottom: 5px; }
.bk-bar-top b { font-weight: 600; }
.bk-bar-top span { color: var(--bk-muted); font-variant-numeric: tabular-nums; }
.bk-bar-track { height: 10px; border-radius: 999px; background: #eaeff7; overflow: hidden; }
.bk-bar-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--bk-primary), var(--bk-primary-2)); }
.bk-bar-fill.bk-ok { background: linear-gradient(90deg, #129060, #2ec28f); }
.bk-bar-fill.bk-danger { background: linear-gradient(90deg, #c93a46, #ea6c75); }
.bk-bar-fill.bk-gold { background: linear-gradient(90deg, #d79a1f, #f3c35a); }
.bk-bar-fill.bk-teal { background: linear-gradient(90deg, #0f8e80, #36c9b8); }

.bk-two { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.bk-steps { margin: 0; padding-left: 18px; color: var(--bk-muted); line-height: 1.8; font-size: 13.5px; }
.bk-steps b { color: var(--bk-ink); }
.bk-footer { margin-top: 26px; text-align: center; color: var(--bk-muted); font-size: 12px; }

@media (max-width: 760px) {
  .bk-grid { grid-template-columns: 1fr !important; }
  .bk-two { grid-template-columns: 1fr; }
  .bk-header { padding: 18px; }
  .bk-card { padding: 18px; }
}
"""


def theme() -> w.HTML:
    """Widget that injects the stylesheet."""
    return w.HTML(f"<style>{CSS}</style>")
