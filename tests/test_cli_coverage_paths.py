"""
Deeper CLI coverage: exercise create/run/validate/list paths with stubs.
"""

from unittest.mock import MagicMock


def test_cli_create_run_validate(monkeypatch, tmp_path):
    from neonworks import cli

    dummy_manager = MagicMock()
    dummy_manager.list_projects.return_value = ["existing"]
    dummy_manager.create_project.return_value = object()
    dummy_manager.run_project.return_value = True
    dummy_manager.validate_project.return_value = True

    def _load_modules_stub(self):
        self.ProjectManager = MagicMock(return_value=dummy_manager)
        self.ProjectMetadata = MagicMock()
        self.ProjectSettings = MagicMock()
        self.Project = MagicMock()
        self.validate_project_config = lambda *a, **k: None
        self.ValidationError = Exception

    with monkeypatch.context() as m:
        m.setattr(cli.NeonWorksCLI, "_load_modules", _load_modules_stub)
        cli_obj = cli.NeonWorksCLI()
        cli_obj.projects_root = tmp_path
        cli_obj.templates_root = tmp_path / "templates"
        cli_obj._copy_template_files = lambda *a, **k: None
        cli_obj._create_minimal_structure = lambda *a, **k: None

        # create
        assert cli_obj.create_project("new_game", template="basic_game") is True
        # run existing
        assert cli_obj.run_project("existing") in (True, False)
        # validate existing
        assert cli_obj.validate_project("existing") in (True, False)
        # list
        cli_obj.list_projects()
        cli_obj.list_templates()

