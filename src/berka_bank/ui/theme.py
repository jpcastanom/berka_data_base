"""Visual theme: one <style> block injected into the page (Voilà or notebook)."""

import ipywidgets as w

CSS = """
:root {
  --bk-bg: #ffffff;
  --bk-card: #ffffff;
  --bk-ink: #16215e;          /* deep navy text */
  --bk-muted: #5b6694;
  --bk-line: #dde6f6;
  --bk-soft: #f4f8fe;         /* pale blue */
  --bk-cream: #fff6dc;
  --bk-navy: #1d2f8f;
  --bk-primary: #1d2f8f;
  --bk-primary-2: #2a45c4;
  --bk-teal: #7fa9e8;
  --bk-gold: #f2b632;
  --bk-ok: #3f9a52;
  --bk-danger: #d1584f;
  --bk-info: #1d2f8f;
  --bk-radius: 16px;
  --bk-font: 'Segoe UI', 'Segoe UI Variable', system-ui, -apple-system, Roboto, 'Helvetica Neue', Arial, sans-serif;
  --bk-shadow: 0 1px 2px rgba(22, 33, 94, .05), 0 10px 28px rgba(22, 33, 94, .08);
  --bk-shadow-sm: 0 1px 2px rgba(22, 33, 94, .05), 0 3px 10px rgba(22, 33, 94, .07);
}

body {
  background-color: #fff !important;
  background-image:
    linear-gradient(var(--bk-cream), var(--bk-cream)),
    linear-gradient(103deg, transparent 52%, var(--bk-soft) 52%) !important;
  background-repeat: no-repeat !important;
  background-position: left bottom, right top !important;
  background-size: 100% 24vh, 100% 76vh !important;
  background-attachment: fixed !important;
  min-height: 100vh;
}
#main, .jp-OutputArea, .jp-OutputArea-output, #rendered_cells, .jp-Cell { background: transparent !important; }
.jp-OutputArea-prompt, .jp-InputPrompt { display: none !important; }

/* ---------- root + widget variables ---------- */
.bk-root {
  width: 100%;
  min-height: 100vh;
  box-sizing: border-box;
  margin: 0 auto;
  padding: clamp(12px, 2.5vw, 56px) clamp(12px, 2.5vw, 56px) 36px;
  color: var(--bk-ink);
  font-family: var(--bk-font);
  font-size: 16px;
  --jp-widgets-color: var(--bk-ink);
  --jp-widgets-label-color: var(--bk-ink);
  --jp-widgets-font-size: 16px;
  --jp-widgets-inline-height: 46px;
  --jp-widgets-inline-label-width: 0px;
  --jp-widgets-input-color: var(--bk-ink);
  --jp-widgets-input-background-color: #ffffff;
  --jp-widgets-input-border-color: #cfd9ee;
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
.bk-root .widget-html, .bk-root .widget-html-content { height: auto; line-height: 1.45; }

/* ---------- header ---------- */
.bk-header {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;
  padding: 4px 2px; color: var(--bk-ink);
}
.bk-brand { display: flex; align-items: center; gap: 16px; }
.bk-logo {
  width: 52px; height: 52px; border-radius: 14px; display: grid; place-items: center;
  background: var(--bk-soft); border: 1px solid var(--bk-line); box-shadow: var(--bk-shadow-sm);
}
.bk-logo svg { width: 38px; height: 38px; }
.bk-title { font-size: 27px; font-weight: 800; color: var(--bk-navy); letter-spacing: -.02em; line-height: 1.1; }
.bk-subtitle { font-size: 15px; color: var(--bk-muted); margin-top: 3px; }
.bk-conn {
  display: flex; align-items: center; gap: 10px; padding: 9px 16px; border-radius: 999px;
  background: var(--bk-soft); border: 1px solid var(--bk-line); font-size: 14px; font-weight: 600;
}
.bk-conn small { font-weight: 400; color: var(--bk-muted); font-size: 13px; }
.bk-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--bk-primary); box-shadow: 0 0 0 4px rgba(29,47,143,.2); }

/* ---------- tabs: top navigation ---------- */
.bk-root .widget-tab > .widget-tab-contents {
  background: transparent; border: none; padding: 22px 0 0; overflow: visible;
}
.bk-root .widget-tab > .p-TabBar, .bk-root .widget-tab > .lm-TabBar {
  min-height: 0; border: none; background: transparent; margin-top: 14px;
}
.bk-root .widget-tab > .p-TabBar .p-TabBar-content, .bk-root .widget-tab > .lm-TabBar .lm-TabBar-content {
  gap: 6px 26px; flex-wrap: wrap; border-bottom: 1px solid var(--bk-line);
}
.bk-root .widget-tab > .p-TabBar .p-TabBar-tab, .bk-root .widget-tab > .lm-TabBar .lm-TabBar-tab {
  flex: 0 0 auto; min-width: 0; height: auto; line-height: 22px; margin: 0;
  padding: 10px 2px 11px; border: none !important; border-radius: 0; background: transparent;
  color: var(--bk-muted); font-weight: 600; font-size: 17px; box-shadow: none; transition: color .15s ease;
}
.bk-root .widget-tab > .p-TabBar .p-TabBar-tab:hover, .bk-root .widget-tab > .lm-TabBar .lm-TabBar-tab:hover { color: var(--bk-navy); background: transparent; }
.bk-root .widget-tab > .p-TabBar .p-TabBar-tab.p-mod-current, .bk-root .widget-tab > .lm-TabBar .lm-TabBar-tab.lm-mod-current {
  background: transparent; color: var(--bk-navy); font-weight: 800; transform: none;
  box-shadow: inset 0 -4px 0 var(--bk-gold);
}
.bk-root .widget-tab > .p-TabBar .p-TabBar-tab.p-mod-current::before,
.bk-root .widget-tab > .lm-TabBar .lm-TabBar-tab.lm-mod-current::before { display: none; }

/* secondary (nested) tabs: underline style */
.bk-root .bk-subtabs > .p-TabBar, .bk-root .bk-subtabs > .lm-TabBar { margin-top: 0; border-bottom: 1px solid var(--bk-line); }
.bk-root .bk-subtabs > .p-TabBar .p-TabBar-tab, .bk-root .bk-subtabs > .lm-TabBar .lm-TabBar-tab {
  padding: 11px 18px; border-radius: 10px 10px 0 0; border: none !important; background: transparent;
  box-shadow: none; color: var(--bk-muted); font-size: 15.5px;
}
.bk-root .bk-subtabs > .p-TabBar .p-TabBar-tab.p-mod-current, .bk-root .bk-subtabs > .lm-TabBar .lm-TabBar-tab.lm-mod-current {
  background: transparent; color: var(--bk-ink); box-shadow: inset 0 -3px 0 var(--bk-primary);
}
.bk-root .bk-subtabs > .widget-tab-contents { padding-top: 18px; }

/* ---------- cards / sections ---------- */
.bk-card {
  background: var(--bk-card); border: 1px solid var(--bk-line); border-radius: var(--bk-radius);
  box-shadow: var(--bk-shadow); padding: 30px 34px;
}
.bk-root .bk-card > * + * { margin-top: 16px; }
.bk-card .bk-card { box-shadow: var(--bk-shadow-sm); background: #fff; padding: 20px 22px; }
.bk-card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.bk-card-title { margin: 0; font-size: 22px; font-weight: 700; letter-spacing: -.01em; color: var(--bk-ink); }
.bk-card-help { margin: 6px 0 0; color: var(--bk-muted); font-size: 15.5px; line-height: 1.5; max-width: 760px; }
.bk-card-help code, .bk-callout code {
  background: var(--bk-soft); border: 1px solid var(--bk-line); padding: 1px 6px; border-radius: 6px; font-size: 14px;
}
.bk-badge {
  flex: 0 0 auto; padding: 4px 11px; line-height: 1.5; border-radius: 999px; font-size: 12px; font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; background: #e3ebfb; color: #1d2f8f;
}
.bk-badge.bk-teal { background: #e3ebfb; color: #1d2f8f; }
.bk-badge.bk-gold { background: #fff0c4; color: #7a5a0a; }
.bk-root .bk-h4 { margin: 4px 0 0; font-size: 16.5px; font-weight: 700; color: var(--bk-ink); }

/* ---------- forms ---------- */
.bk-root .bk-grid { display: grid; gap: 22px 28px; width: 100%; overflow: visible; }
.bk-field { width: 100%; }
.bk-label { display: block; margin: 0 0 8px; font-size: 14px; font-weight: 600; color: var(--bk-muted); letter-spacing: .01em; }
.bk-root .widget-text input, .bk-root .widget-text textarea, .bk-root .widget-dropdown select,
.bk-root .widget-datepicker input, .bk-root .widget-numeric-text input {
  height: 46px; border-radius: 10px; padding: 0 14px; background-color: #ffffff; box-shadow: inset 0 1px 2px rgba(22,33,94,.04);
  box-sizing: border-box; width: 100%; min-width: 0; margin: 0; transition: border-color .15s, box-shadow .15s;
}
.bk-root .widget-dropdown select {
  appearance: none; -webkit-appearance: none; padding-right: 36px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1.5l5 5 5-5' fill='none' stroke='%236f7468' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 14px center;
}
.bk-root .widget-text, .bk-root .widget-dropdown, .bk-root .widget-datepicker, .bk-root .widget-numeric-text,
.bk-root .widget-bounded-int-text, .bk-root .widget-bounded-float-text { width: 100% !important; min-width: 0; box-sizing: border-box; }
.bk-root .widget-datepicker input[type=date] { padding-right: 10px; }
.bk-root .widget-text input:focus, .bk-root .widget-dropdown select:focus, .bk-root .widget-datepicker input:focus {
  border-color: var(--bk-primary); box-shadow: 0 0 0 3px rgba(29,47,143,.2); outline: none;
}
.bk-root input:disabled, .bk-root select:disabled { background: var(--bk-soft); color: #9aa5c8; }
.bk-root .widget-checkbox { margin-top: 4px; }
.bk-row { display: flex; align-items: flex-end; gap: 14px; flex-wrap: wrap; }
.bk-row > .bk-field { flex: 0 1 340px; }
.bk-actions { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 4px; }

/* ---------- buttons ---------- */
.bk-root .jupyter-button {
  width: auto; min-width: 170px; height: 46px; line-height: 46px; padding: 0 24px; border: none; border-radius: 10px;
  color: #fff; font-weight: 700; font-size: 16px; letter-spacing: .005em; cursor: pointer;
  box-shadow: 0 1px 2px rgba(22,33,94,.10), 0 4px 12px rgba(22,33,94,.12); transition: transform .12s ease, filter .12s ease, box-shadow .12s ease;
}
.bk-root .jupyter-button:hover:not(:disabled) { filter: brightness(1.05); transform: translateY(-1px); box-shadow: 0 2px 4px rgba(22,33,94,.10), 0 8px 18px rgba(22,33,94,.16); }
.bk-root .jupyter-button:active:not(:disabled) { transform: translateY(0); }
.bk-root .jupyter-button:disabled { opacity: .4; box-shadow: none; cursor: not-allowed; }
.bk-root .jupyter-button.mod-primary { background: var(--bk-primary); }
.bk-root .jupyter-button.mod-success { background: var(--bk-primary); }
.bk-root .jupyter-button.mod-info    { background: var(--bk-primary); }
.bk-root .jupyter-button.mod-warning { background: var(--bk-gold); }
.bk-root .jupyter-button.mod-danger  { background: var(--bk-danger); }
.bk-root .jupyter-button i.fa { margin-right: 4px; }

/* ---------- callouts ---------- */
.bk-callout {
  display: flex; gap: 12px; align-items: flex-start; padding: 12px 16px; border-radius: 12px;
  border: 1px solid; font-size: 15.5px; line-height: 1.5;
}
.bk-callout-icon {
  flex: 0 0 22px; height: 22px; border-radius: 50%; display: grid; place-items: center;
  color: #fff; font-size: 12px; font-weight: 800; margin-top: 1px;
}
.bk-callout.bk-ok    { background: #eef4ff; border-color: #cddcf7; color: #1d2f8f; }
.bk-callout.bk-error { background: #f8eeee; border-color: #ead2d2; color: #8a4545; }
.bk-callout.bk-info  { background: var(--bk-soft); border-color: var(--bk-line); color: var(--bk-ink); }
.bk-ok .bk-callout-icon { background: var(--bk-ok); }
.bk-error .bk-callout-icon { background: var(--bk-danger); }
.bk-info .bk-callout-icon { background: var(--bk-info); }

/* ---------- output area ---------- */
.bk-out { margin-top: 6px; }
.bk-out .jp-OutputArea-child, .bk-out .output_area { padding: 0; }
.bk-out > * + * , .bk-out .jp-OutputArea-child + .jp-OutputArea-child { margin-top: 14px; }

/* ---------- tables ---------- */
.bk-table-wrap { max-height: clamp(300px, 65vh, 720px); overflow: auto; border: 1px solid var(--bk-line); border-radius: 12px; background: #fff; box-shadow: var(--bk-shadow-sm); }
.bk-root .bk-table { table-layout: auto; width: max-content; min-width: 100%; border-collapse: separate; border-spacing: 0; font-size: 15px; font-variant-numeric: tabular-nums; }
.bk-root .bk-table th {
  max-width: none; overflow: visible; text-overflow: clip;
  position: sticky; top: 0; z-index: 1; text-align: left; white-space: nowrap; padding: 13px 16px;
  background: var(--bk-soft); color: var(--bk-muted); font-size: 12.5px; font-weight: 600; letter-spacing: .05em;
  text-transform: uppercase; border-bottom: 1px solid var(--bk-line);
}
.bk-root .bk-table td { text-align: left; max-width: none; overflow: visible; text-overflow: clip; padding: 12px 16px; border-bottom: 1px solid #edf1fa; white-space: nowrap; color: var(--bk-ink); }
.bk-table tbody tr:nth-child(even) td { background: #f8faff; }
.bk-table tbody tr:hover td { background: #eef4ff; }
.bk-table tbody tr:last-child td { border-bottom: none; }
.bk-root .bk-table td.bk-num, .bk-root .bk-table th.bk-num { text-align: right; }
.bk-null { color: #b6bfd8; }
.bk-table-note { padding: 8px 14px; font-size: 12px; color: var(--bk-muted); background: var(--bk-soft); border-top: 1px solid var(--bk-line); }
.bk-empty { padding: 26px; text-align: center; color: var(--bk-muted); border: 1px dashed #c9d6ef; border-radius: 12px; background: var(--bk-soft); }

/* ---------- KPIs ---------- */
.bk-kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 250px), 1fr)); gap: 14px; }
.bk-root .bk-kpi {
  position: relative; overflow: hidden; padding: 16px 18px 15px; border-radius: 12px; background: #fff;
  border: 1px solid var(--bk-line); box-shadow: var(--bk-shadow-sm);
}
.bk-kpi.bk-strong { background: var(--bk-primary); border-color: var(--bk-primary); box-shadow: 0 4px 14px rgba(29,47,143,.35); }
.bk-kpi-label { font-size: 12.5px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--bk-muted); }
.bk-kpi-value { margin-top: 6px; white-space: nowrap; font-size: clamp(24px, 2.3vw, 32px); font-weight: 700; letter-spacing: -.01em; line-height: 1.15; font-variant-numeric: tabular-nums; }
.bk-unit { font-size: 13px; font-weight: 600; opacity: .65; margin-left: 2px; }
.bk-kpi-sub { margin-top: 4px; font-size: 13.5px; color: var(--bk-muted); }
.bk-kpi.bk-strong .bk-kpi-label, .bk-kpi.bk-strong .bk-kpi-sub { color: rgba(255,255,255,.8); }
.bk-kpi.bk-strong .bk-kpi-value { color: #fff; }
.bk-kpi.bk-ok .bk-kpi-value { color: var(--bk-ok); }
.bk-kpi.bk-danger .bk-kpi-value { color: var(--bk-danger); }

/* ---------- bars ---------- */
.bk-bars { display: grid; gap: 13px; }
.bk-bar-top { display: flex; justify-content: space-between; gap: 12px; font-size: 15px; margin-bottom: 5px; }
.bk-bar-top b { font-weight: 700; }
.bk-bar-top span { color: var(--bk-muted); font-variant-numeric: tabular-nums; }
.bk-bar-track { height: 10px; border-radius: 999px; background: #e6edf9; overflow: hidden; }
.bk-bar-fill { height: 100%; border-radius: 999px; background: #7fa9e8; }
.bk-bar-fill.bk-ok { background: var(--bk-primary); }
.bk-bar-fill.bk-danger { background: var(--bk-danger); }
.bk-bar-fill.bk-gold { background: var(--bk-gold); }
.bk-bar-fill.bk-teal { background: var(--bk-teal); }

.bk-two { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.bk-steps { margin: 0; padding-left: 20px; color: var(--bk-muted); line-height: 1.9; font-size: 15.5px; }
.bk-steps b { color: var(--bk-ink); }
.bk-footer { margin-top: 26px; text-align: center; color: var(--bk-muted); font-size: 13.5px; }

/* ---------- hero (Inicio) ---------- */
.bk-hero { display: grid; grid-template-columns: minmax(0, 1.05fr) minmax(0, .95fr); align-items: center; gap: clamp(16px, 3vw, 56px); min-height: clamp(300px, 46vh, 560px); }
.bk-hero h1 { margin: 0; font-size: clamp(30px, 4.2vw, 76px); line-height: 1.08; font-weight: 800; letter-spacing: -.03em; color: var(--bk-navy); }
.bk-hero p { margin: 18px 0 0; max-width: 34ch; font-size: clamp(15px, 1.5vw, 26px); line-height: 1.4; color: var(--bk-ink); }
.bk-hero svg { width: 100%; height: auto; max-height: 56vh; display: block; }
.bk-hero-tags { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 22px; }
.bk-hero-tags span { padding: 6px 14px; border-radius: 999px; background: #fff; border: 1px solid var(--bk-line); font-size: 13px; font-weight: 700; color: var(--bk-navy); box-shadow: var(--bk-shadow-sm); }

/* ---------- cards fill the screen height (no half-empty page) ---------- */
.bk-root .bk-tabs > .widget-tab-contents > .bk-card { min-height: calc(100vh - 310px); }
.bk-root .bk-subtabs > .widget-tab-contents > .bk-card { min-height: calc(100vh - 400px); }

/* ---------- wide screens (16:9 monitors, ultrawide, second display) ---------- */
@media (min-width: 1400px) {
  /* forms: fixed-size fields packed from the left instead of a few giant stretched inputs */
  .bk-root .bk-grid { grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)) !important; }
  .bk-table-wrap { max-height: clamp(360px, 62vh, 900px); }
}
/* 2K / 4K: scale the whole interface so text and controls keep a comfortable size */
@media (min-width: 2200px) { .bk-root { zoom: 1.2; } }
@media (min-width: 3000px) { .bk-root { zoom: 1.5; } }

/* ---------- responsive ---------- */
@media (max-width: 960px) {
  /* forms: as many columns as fit, whatever the Python side asked for */
  .bk-root .bk-grid { grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr)) !important; }
  .bk-two { grid-template-columns: 1fr; }
  .bk-hero { grid-template-columns: 1fr; min-height: 0; }
}
@media (max-width: 640px) {
  .bk-header { padding: 16px; }
  .bk-conn { width: 100%; box-sizing: border-box; border-radius: 12px; flex-wrap: wrap; gap: 4px 10px; }
  .bk-card { padding: 16px; }
  .bk-card-head { flex-wrap: wrap; }
  .bk-title { font-size: 20px; }
  .bk-root .jupyter-button { width: 100%; }
  .bk-actions { width: 100%; }
  .bk-row > .bk-field { flex: 1 1 100%; }
  /* main tabs: one scrollable line instead of three wrapped rows */
  .bk-root .bk-tabs > .p-TabBar .p-TabBar-content, .bk-root .bk-tabs > .lm-TabBar .lm-TabBar-content {
    flex-wrap: nowrap; overflow-x: auto; padding-bottom: 8px; scrollbar-width: thin;
  }
}
"""


def theme() -> w.HTML:
    """Widget that injects the stylesheet."""
    return w.HTML(f"<style>{CSS}</style>")
