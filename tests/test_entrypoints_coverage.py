"""
Coverage-focused smoke tests for critical entrypoints:
- neonworks.cli (argument parsing + template listing)
- neonworks.main (help/version paths)
- neonworks.launcher (constructor)

These avoid disk/network side effects by patching heavy dependencies.
"""

import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

pygame = pytest.importorskip("pygame")


def _set_argv(monkeypatch, args):
    monkeypatch.setattr(sys, "argv", args)


def test_cli_parses_templates_and_list(monkeypatch):
    """
    Ensure cli.main can execute template/list commands without real FS work.
    """
    from neonworks import cli

    # Patch template loader and project manager to inert stubs
    dummy_manager = MagicMock()
    dummy_manager.list_projects.return_value = []
    dummy_project = MagicMock()

    def _load_modules_stub(self):
        # Emulate _load_modules attaching attributes
        self.ProjectManager = MagicMock(return_value=dummy_manager)
        self.Project = lambda *a, **k: dummy_project
        self.ProjectMetadata = MagicMock()
        self.ProjectSettings = MagicMock()
        self.ValidationError = Exception
        self.validate_project_config = lambda *a, **k: None

    with patch.object(cli.NeonWorksCLI, "_load_modules", _load_modules_stub), patch.object(
        cli, "print"
    ):
        _set_argv(monkeypatch, ["cli.py", "templates"])
        cli.main()
        _set_argv(monkeypatch, ["cli.py", "list"])
        cli.main()


def test_main_help_and_version(monkeypatch):
    """
    Exercise neonworks.main help/version paths without starting the engine.
    """
    from neonworks import main

    monkeypatch.setattr(main, "run_engine", lambda *a, **k: None, raising=False)
    # Preserve real sys but control argv and exit
    monkeypatch.setattr(main.sys, "exit", lambda code=0: None)
    _set_argv(monkeypatch, ["main.py", "--help"])
    main.main()
    _set_argv(monkeypatch, ["main.py", "--version"])
    main.main()


def test_launcher_constructs(monkeypatch):
    """
    Construct NeonWorksLauncher with heavy deps stubbed to cover __init__.
    """
    from neonworks import launcher

    # Stub pygame init/display to avoid creating real windows
    monkeypatch.setattr(
        launcher,
        "pygame",
        SimpleNamespace(
            init=lambda: None,
            display=SimpleNamespace(set_mode=lambda size: MagicMock(), set_caption=lambda title: None),
            event=SimpleNamespace(get=lambda: []),
            time=SimpleNamespace(Clock=lambda: MagicMock()),
        ),
    )
    monkeypatch.setattr(launcher, "APP_CONFIG", {}, raising=False)
    monkeypatch.setattr(launcher, "ProjectCatalog", MagicMock, raising=False)

    launcher.NeonWorksLauncher()
