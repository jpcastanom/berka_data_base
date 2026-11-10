"""Orchestrator: prepares the database end to end and opens the graphical interface.

    uv run berka                  # load/migrate only what is missing, then open the UI
    uv run berka --rebuild        # drop and rebuild banco_berka from staging
    uv run berka --setup-only     # prepare the database without opening the UI

Steps
    1. staging   : load berka.sql into the `berka` database (skipped if already loaded)
    2. model     : create banco_berka and migrate the data (skipped if already built)
    3. routines  : (re)create fn_saldo_cuenta, sp_extracto_cuenta and both triggers
    4. interface : serve the ipywidgets app with Voilà at http://localhost:<port>
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from berka_bank import migration, routines, schema, staging
from berka_bank.config import load_settings
from berka_bank.db import Database

UI_NOTEBOOK = Path(__file__).parent / "ui" / "interfaz.ipynb"


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="berka", description="Banco Berka: database setup + interface.")
    p.add_argument("--rebuild", action="store_true", help="drop and rebuild the model database")
    p.add_argument("--reload-staging", action="store_true", help="load berka.sql again")
    p.add_argument("--setup-only", action="store_true", help="prepare the database, do not open the UI")
    p.add_argument("--port", type=int, help="port for the interface (default: config [ui].port)")
    p.add_argument("--no-browser", action="store_true", help="do not open the browser automatically")
    return p.parse_args(argv)


def prepare_database(db: Database, rebuild: bool, reload_staging: bool) -> None:
    print(f"Connected to MySQL {db.version()} at {db.settings.host}:{db.settings.port}")

    staging.ensure(db, force=reload_staging)

    if rebuild or not schema.is_built(db):
        print(f"[model] Creating '{db.settings.model_db}' and migrating data...")
        schema.create(db)
        migration.migrate(db)
        result = migration.validate(db)
        print(result.to_string(index=False))
        if not result["OK"].all():
            print("[model] WARNING: some counts differ from the data dictionary.")
    else:
        print(f"[model] '{db.settings.model_db}' already built, skipping (use --rebuild to recreate it).")

    print("[routines] Creating function, procedure and triggers...")
    routines.create_all(db)


def launch_ui(db: Database, port: int, open_browser: bool) -> None:
    # The Voilà kernel is a separate process: hand it the password so it never has to prompt.
    env = os.environ | {"MYSQL_PASSWORD": db.settings.password}
    cmd = [sys.executable, "-m", "voila", str(UI_NOTEBOOK), f"--port={port}", "--show_tracebacks=True", "--theme=light"]
    if not open_browser:
        cmd.append("--no-browser")
    print(f"[ui] Interface at http://localhost:{port}  (Ctrl+C to stop)")
    try:
        subprocess.run(cmd, env=env, check=False)
    except KeyboardInterrupt:
        pass


def main(argv=None) -> None:
    args = parse_args(argv)
    settings = load_settings()
    db = Database(settings)
    prepare_database(
        db,
        rebuild=args.rebuild or settings.rebuild_model,
        reload_staging=args.reload_staging or settings.reload_staging,
    )
    if not args.setup_only:
        launch_ui(db, port=args.port or settings.ui_port, open_browser=settings.open_browser and not args.no_browser)


if __name__ == "__main__":
    main()
