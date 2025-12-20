# Developer Guide — DeskTidy (local workspace)

This document explains how the source files in this workspace are linked,
how the main methods call into each other, and provides quick run
commands. It complements the project's `README.md` with an implementation
map for developers exploring the code.

## High-level startup sequence

1. `main.py` is the entry point. It:
   - loads settings using `core.settings_manager.SettingsManager`,
   - instantiates `core.logger.Logger`,
   - creates `ui.main_window.MainWindow(settings, logger)` and shows it.

2. `MainWindow` constructs the tab UI and injects `settings` and `logger`
   into the tabs that need them: `FileCleanerTab`, `SettingsTab`,
   and `LogsTab`. `Logger.log_added` is connected to `LogsTab.on_new_log` so
   logs update live in the UI.

## Core package and responsibilities

- `core/settings_manager.py`
  - Load and persist the `settings.json` file.
  - Called by: `main.py`, `ui/tabs/settings_tab.py`.

- `core/logger.py`
  - Centralized logging (in-memory + persistent JSON). Exposes `log_added` signal.
  - Called by: UI components and core modules to record events.

- `core/file_ops.py`
  - Safe deletion, hashing, duplicate-finding helpers.
  - Called by: `core/cleaner.py`, `core/batch_processor.py`.

- `core/disk_analyzer.py`
  - Compute folder statistics and recommendations.
  - Called by: `ui/tabs/analysis_tab.py` (in a background thread).

- `core/cleaner.py`
  - Scans and filters files, performs deletions (uses `rules_engine`).
  - Called by: `FileCleanerTab` via background `CleanerThread`.

- `core/rules_engine.py`
  - Evaluate files against configured rules and return scores/decisions.
  - Called by: `core/cleaner.py` and batch processors.

- `core/batch_processor.py`
  - Concurrent per-file operations using `ThreadPoolExecutor`.
  - Called by: any component that needs to process many files in parallel.

- `core/scheduler.py`
  - Schedule periodic cleanups and emit triggers.

## UI package and responsibilities

- `ui/main_window.py`
  - Builds `QMainWindow`, creates tabs, applies themes, handles shutdown.
  - Instantiates tabs and wires the `logger.log_added` signal.

- `ui/tabs/file_cleaner_tab.py`
  - UI to preview files and run cleans. Creates `CleanerThread` which
    delegates to `core.cleaner.FileCleaner` for scanning and deletion.

- `ui/tabs/analysis_tab.py`
  - Runs `core.disk_analyzer.analyze_folder()` in a worker thread and
    displays results.

- `ui/tabs/settings_tab.py`
  - Edit and persist settings via `SettingsManager`.

- `ui/tabs/logs_tab.py`
  - Show logs (calls `Logger.get_logs`, `Logger.save_logs`). Reacts to `log_added`.

- `ui/tabs/dashboard_tab.py`
  - Lightweight overview and quick actions. Periodically polls `psutil`.

- `ui/components/folder_chooser.py`, `ui/components/preview_panel.py`
  - Small widgets used by tabs.

## Example call flows (concise)

- Startup: `python main.py` → `SettingsManager.load()` → `Logger()` → `MainWindow()`
- Run cleanup: `FileCleanerTab.run_cleanup()` → `CleanerThread.run()` →
  `FileCleaner.scan_files()` → `RulesEngine.evaluate_file()` →
  `FileCleaner.clean_files()` → `FileOperations.safe_delete()` → `Logger.log_action()`
- Analysis: `AnalysisTab.start()` → `AnalysisThread.run()` → `disk_analyzer.analyze_folder()` → UI update

## Files modified/annotated in this session

- `main.py`
- `core/settings_manager.py`
- `core/logger.py`
- `core/file_ops.py`
- `core/disk_analyzer.py`
- `core/cleaner.py`
- `core/rules_engine.py`
- `core/scheduler.py`
- `core/batch_processor.py`
- `core/__init__.py`
- `ui/__init__.py`
- `ui/components/folder_chooser.py`
- `ui/components/preview_panel.py`
- `ui/tabs/file_cleaner_tab.py`
- `ui/tabs/logs_tab.py`
- `ui/tabs/settings_tab.py`
- `ui/tabs/analysis_tab.py`
- `ui/tabs/dashboard_tab.py`
- `ui/main_window.py`

## Quick commands (PowerShell)

```powershell
# Syntax check (compile-only)
C:/MHANSTEVOSTUFF/DeskTidy/.venv/Scripts/python.exe -m compileall -q .

# Run the application
C:/MHANSTEVOSTUFF/DeskTidy/.venv/Scripts/python.exe main.py

# (Optional) Run tests
C:/MHANSTEVOSTUFF/DeskTidy/.venv/Scripts/python.exe -m pytest -v
```

## Next steps you might want

- Finish adding comments where you want more detail (I can continue).
- Run the app to test changes in the UI.
- Ask me to generate a Graphviz `.dot` file if you want a visual call graph.

---

If you want a visual call graph or per-file sequence diagrams next, tell me which format you prefer and I will generate them.
