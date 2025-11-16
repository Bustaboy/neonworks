"""
Tests for Crash Recovery and Auto-Save System

Tests automatic saving, crash logging, and safe execution.
"""

import json
import os
import time
from pathlib import Path

import pytest

from neonworks.core.crash_recovery import (
    AutoSaveManager,
    CrashRecovery,
    SafeExecutor,
    get_autosave_manager,
    get_crash_recovery,
    setup_crash_recovery,
)


class TestAutoSaveManager:
    """Test suite for AutoSaveManager"""

    def test_init_basic(self, tmp_path):
        """Test basic AutoSaveManager initialization"""
        save_dir = tmp_path / "autosaves"
        manager = AutoSaveManager(save_dir=str(save_dir), interval=60.0)

        assert manager.save_dir == save_dir
        assert manager.interval == 60.0
        assert manager.last_save_time == 0.0
        assert manager.enabled is True
        assert manager.save_callback is None
        assert manager.max_autosaves == 10
        assert save_dir.exists()

    def test_init_creates_directory(self, tmp_path):
        """Test initialization creates save directory"""
        save_dir = tmp_path / "new_dir" / "autosaves"
        manager = AutoSaveManager(save_dir=str(save_dir))

        assert save_dir.exists()
        assert save_dir.is_dir()

    def test_register_save_callback(self, tmp_path):
        """Test registering save callback"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"))

        def test_callback():
            return {"test": "data"}

        manager.register_save_callback(test_callback)

        assert manager.save_callback is test_callback

    def test_update_increments_timer(self, tmp_path):
        """Test update increments timer"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"), interval=100.0)
        manager.register_save_callback(lambda: {"data": "test"})

        initial_time = manager.last_save_time
        manager.update(10.0)

        assert manager.last_save_time == initial_time + 10.0

    def test_update_triggers_save_at_interval(self, tmp_path):
        """Test update triggers save when interval reached"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"), interval=5.0)
        manager.register_save_callback(lambda: {"test": "data"})

        # Update to reach interval
        manager.update(5.0)

        # Timer should reset
        assert manager.last_save_time == 0.0

        # File should be created
        autosaves = list(manager.save_dir.glob("autosave_*.json"))
        assert len(autosaves) == 1

    def test_update_disabled_does_nothing(self, tmp_path):
        """Test update when disabled doesn't save"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"), interval=1.0)
        manager.register_save_callback(lambda: {"test": "data"})
        manager.enabled = False

        manager.update(10.0)

        # No files should be created
        autosaves = list(manager.save_dir.glob("autosave_*.json"))
        assert len(autosaves) == 0

    def test_update_no_callback_does_nothing(self, tmp_path):
        """Test update without callback doesn't save"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"), interval=1.0)

        manager.update(10.0)

        # No files should be created
        autosaves = list(manager.save_dir.glob("autosave_*.json"))
        assert len(autosaves) == 0

    def test_save_successful(self, tmp_path):
        """Test successful save"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"))
        test_data = {"player": {"hp": 100, "level": 5}, "progress": "halfway"}
        manager.register_save_callback(lambda: test_data)

        result = manager.save()

        assert result is True

        # Check file was created
        autosaves = list(manager.save_dir.glob("autosave_*.json"))
        assert len(autosaves) == 1

        # Check file contents
        with open(autosaves[0], "r") as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data

    def test_save_without_callback_fails(self, tmp_path, capsys):
        """Test save without callback returns False"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"))

        result = manager.save()

        assert result is False
        captured = capsys.readouterr()
        assert "No save callback registered" in captured.out

    def test_save_with_callback_exception(self, tmp_path, capsys):
        """Test save handles callback exceptions"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"))

        def failing_callback():
            raise ValueError("Callback error")

        manager.register_save_callback(failing_callback)

        result = manager.save()

        assert result is False
        captured = capsys.readouterr()
        assert "Error during auto-save" in captured.out

    def test_cleanup_old_saves(self, tmp_path):
        """Test cleanup removes old autosaves"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"))
        manager.max_autosaves = 3

        # Manually create 5 autosave files with different timestamps
        base_time = time.time() - 100
        for i in range(5):
            filename = manager.save_dir / f"autosave_test_{i:02d}.json"
            with open(filename, "w") as f:
                json.dump({"test": f"data_{i}"}, f)
            # Set different modification times
            os.utime(filename, (base_time + i, base_time + i))

        # Trigger cleanup
        manager._cleanup_old_saves()

        # Only 3 most recent should remain
        autosaves = list(manager.save_dir.glob("autosave_*.json"))
        assert len(autosaves) == 3

    def test_cleanup_handles_errors(self, tmp_path):
        """Test cleanup handles errors gracefully"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"))
        manager.register_save_callback(lambda: {"test": "data"})

        # Create an autosave
        manager.save()

        # Manually trigger cleanup (should not crash)
        manager._cleanup_old_saves()

        # Should still have the file
        autosaves = list(manager.save_dir.glob("autosave_*.json"))
        assert len(autosaves) == 1

    def test_get_latest_autosave(self, tmp_path):
        """Test getting latest autosave"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"))
        manager.register_save_callback(lambda: {"test": "data"})

        # No autosaves initially
        assert manager.get_latest_autosave() is None

        # Create autosaves
        manager.save()
        time.sleep(0.01)
        manager.save()
        time.sleep(0.01)
        latest_time = time.time()
        manager.save()

        latest = manager.get_latest_autosave()

        assert latest is not None
        assert latest.exists()
        # Latest should be the most recent
        assert latest.stat().st_mtime >= latest_time - 1

    def test_get_latest_autosave_handles_errors(self, tmp_path):
        """Test get_latest_autosave handles errors"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"))

        # Should return None, not crash
        result = manager.get_latest_autosave()
        assert result is None

    def test_load_autosave_success(self, tmp_path):
        """Test loading autosave successfully"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"))
        test_data = {"player": {"hp": 100}, "world": {"level": 1}}
        manager.register_save_callback(lambda: test_data)

        # Save data
        manager.save()

        # Load it back
        loaded_data = manager.load_autosave()

        assert loaded_data is not None
        assert loaded_data == test_data

    def test_load_autosave_specific_file(self, tmp_path):
        """Test loading specific autosave file"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"))

        # Create first autosave manually to ensure different filename
        first_file = manager.save_dir / "autosave_20200101_120000.json"
        with open(first_file, "w") as f:
            json.dump({"version": 1}, f)

        # Create second autosave with manager
        manager.register_save_callback(lambda: {"version": 2})
        manager.save()

        # Load specific (first) file
        loaded_data = manager.load_autosave(first_file)

        assert loaded_data is not None
        assert loaded_data["version"] == 1

    def test_load_autosave_no_files(self, tmp_path, capsys):
        """Test loading when no autosaves exist"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"))

        loaded_data = manager.load_autosave()

        assert loaded_data is None
        captured = capsys.readouterr()
        assert "No auto-save file found" in captured.out

    def test_load_autosave_invalid_file(self, tmp_path, capsys):
        """Test loading invalid autosave file"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"))

        # Create invalid JSON file
        invalid_file = manager.save_dir / "autosave_invalid.json"
        with open(invalid_file, "w") as f:
            f.write("{ invalid json")

        loaded_data = manager.load_autosave(invalid_file)

        assert loaded_data is None
        captured = capsys.readouterr()
        assert "Error loading auto-save" in captured.out


class TestCrashRecovery:
    """Test suite for CrashRecovery"""

    def test_init_basic(self, tmp_path):
        """Test basic CrashRecovery initialization"""
        log_dir = tmp_path / "crash_logs"
        recovery = CrashRecovery(log_dir=str(log_dir))

        assert recovery.log_dir == log_dir
        assert recovery.crash_callback is None
        assert log_dir.exists()

    def test_init_creates_directory(self, tmp_path):
        """Test initialization creates log directory"""
        log_dir = tmp_path / "new_dir" / "logs"
        recovery = CrashRecovery(log_dir=str(log_dir))

        assert log_dir.exists()
        assert log_dir.is_dir()

    def test_register_crash_callback(self, tmp_path):
        """Test registering crash callback"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))

        def test_callback():
            return {"state": "data"}

        recovery.register_crash_callback(test_callback)

        assert recovery.crash_callback is test_callback

    def test_log_crash_basic(self, tmp_path):
        """Test basic crash logging"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))

        exception = ValueError("Test error")

        filepath = recovery.log_crash(exception)

        assert filepath is not None
        assert filepath.exists()

        # Check log contents
        with open(filepath, "r") as f:
            log_data = json.load(f)

        assert log_data["exception_type"] == "ValueError"
        assert log_data["exception_message"] == "Test error"
        assert "traceback" in log_data

    def test_log_crash_with_additional_info(self, tmp_path):
        """Test crash logging with additional info"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))

        exception = RuntimeError("Test crash")
        additional_info = {"user_action": "clicked button", "game_state": "menu"}

        filepath = recovery.log_crash(exception, additional_info)

        # Check additional info was saved
        with open(filepath, "r") as f:
            log_data = json.load(f)

        assert "additional_info" in log_data
        assert log_data["additional_info"] == additional_info

    def test_log_crash_with_callback(self, tmp_path):
        """Test crash logging saves callback state"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))

        state_data = {"player_hp": 50, "position": [10, 20]}
        recovery.register_crash_callback(lambda: state_data)

        exception = ValueError("Crash with state")

        filepath = recovery.log_crash(exception)

        # Check state was saved
        with open(filepath, "r") as f:
            log_data = json.load(f)

        assert "state_snapshot" in log_data
        assert log_data["state_snapshot"] == state_data

    def test_log_crash_with_failing_callback(self, tmp_path):
        """Test crash logging handles callback exceptions"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))

        def failing_callback():
            raise RuntimeError("Callback failed")

        recovery.register_crash_callback(failing_callback)

        exception = ValueError("Original error")

        filepath = recovery.log_crash(exception)

        # Should still create log
        assert filepath is not None

        # Check error was captured
        with open(filepath, "r") as f:
            log_data = json.load(f)

        assert "state_snapshot_error" in log_data
        assert "Callback failed" in log_data["state_snapshot_error"]

    def test_log_crash_handles_logging_errors(self, tmp_path, capsys):
        """Test log_crash handles errors gracefully"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))

        # Create exception with non-serializable data
        class NonSerializable:
            def __str__(self):
                raise ValueError("Cannot convert to string")

        exception = ValueError(NonSerializable())

        # Should not crash, but might return None
        result = recovery.log_crash(exception)

        # Should handle the error
        captured = capsys.readouterr()
        # Either logs successfully or reports error
        assert result is not None or "Error logging crash" in captured.out

    def test_has_recent_crash_no_crashes(self, tmp_path):
        """Test has_recent_crash with no crashes"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))

        assert recovery.has_recent_crash() is False
        assert recovery.has_recent_crash(hours=1) is False

    def test_has_recent_crash_within_timeframe(self, tmp_path):
        """Test has_recent_crash detects recent crash"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))

        # Log a crash
        recovery.log_crash(ValueError("Recent crash"))

        # Should detect it within 24 hours
        assert recovery.has_recent_crash(hours=24) is True

    def test_has_recent_crash_outside_timeframe(self, tmp_path):
        """Test has_recent_crash ignores old crashes"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))

        # Create old crash log with old modification time
        old_log = recovery.log_dir / "crash_20200101_120000.log"
        with open(old_log, "w") as f:
            json.dump({"old": "crash"}, f)

        # Set modification time to 2020 (very old)
        old_time = 1577836800.0  # 2020-01-01 00:00:00 UTC
        os.utime(old_log, (old_time, old_time))

        # Should not detect it (it's from 2020)
        assert recovery.has_recent_crash(hours=24) is False

    def test_has_recent_crash_handles_errors(self, tmp_path):
        """Test has_recent_crash handles errors"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))

        # Delete the directory to cause an error
        recovery.log_dir.rmdir()

        # Should return False, not crash
        assert recovery.has_recent_crash() is False

    def test_get_latest_crash_log(self, tmp_path):
        """Test getting latest crash log"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))

        # No crashes initially
        assert recovery.get_latest_crash_log() is None

        # Log multiple crashes
        recovery.log_crash(ValueError("First"))
        time.sleep(0.01)
        recovery.log_crash(ValueError("Second"))
        time.sleep(0.01)
        latest_time = time.time()
        recovery.log_crash(ValueError("Third"))

        latest = recovery.get_latest_crash_log()

        assert latest is not None
        assert latest.exists()
        # Latest should be the most recent
        assert latest.stat().st_mtime >= latest_time - 1

        # Check it's the third crash
        with open(latest, "r") as f:
            log_data = json.load(f)
        assert log_data["exception_message"] == "Third"

    def test_get_latest_crash_log_handles_errors(self, tmp_path):
        """Test get_latest_crash_log handles errors"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))

        # Delete directory
        recovery.log_dir.rmdir()

        # Should return None, not crash
        assert recovery.get_latest_crash_log() is None


class TestSafeExecutor:
    """Test suite for SafeExecutor"""

    def test_execute_successful_function(self, tmp_path):
        """Test executing successful function"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))
        executor = SafeExecutor(recovery)

        def successful_func(x, y):
            return x + y

        result = executor.execute(successful_func, 5, 10)

        assert result == 15

        # No crash logs should be created
        logs = list(recovery.log_dir.glob("crash_*.log"))
        assert len(logs) == 0

    def test_execute_with_kwargs(self, tmp_path):
        """Test executing function with keyword arguments"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))
        executor = SafeExecutor(recovery)

        def func_with_kwargs(a, b=10, c=20):
            return a + b + c

        result = executor.execute(func_with_kwargs, 5, b=15, c=25)

        assert result == 45

    def test_execute_failing_function(self, tmp_path, capsys):
        """Test executing failing function"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))
        executor = SafeExecutor(recovery)

        def failing_func():
            raise ValueError("Function failed")

        result = executor.execute(failing_func, error_message="Custom error message")

        assert result is None

        # Should create crash log
        logs = list(recovery.log_dir.glob("crash_*.log"))
        assert len(logs) == 1

        # Check custom error message was printed
        captured = capsys.readouterr()
        assert "Custom error message" in captured.out

    def test_execute_failing_function_with_reraise(self, tmp_path):
        """Test executing failing function with reraise"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))
        executor = SafeExecutor(recovery)

        def failing_func():
            raise RuntimeError("Reraise test")

        with pytest.raises(RuntimeError, match="Reraise test"):
            executor.execute(failing_func, reraise=True)

        # Should still create crash log
        logs = list(recovery.log_dir.glob("crash_*.log"))
        assert len(logs) == 1

    def test_execute_default_error_message(self, tmp_path, capsys):
        """Test execute uses default error message"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))
        executor = SafeExecutor(recovery)

        def failing_func():
            raise ValueError("Test")

        executor.execute(failing_func)

        captured = capsys.readouterr()
        assert "Operation failed" in captured.out


class TestGlobalFunctions:
    """Test suite for global singleton functions"""

    def test_get_autosave_manager_singleton(self):
        """Test get_autosave_manager returns singleton"""
        manager1 = get_autosave_manager()
        manager2 = get_autosave_manager()

        assert manager1 is manager2

    def test_get_autosave_manager_returns_instance(self):
        """Test get_autosave_manager returns AutoSaveManager"""
        manager = get_autosave_manager()

        assert isinstance(manager, AutoSaveManager)

    def test_get_crash_recovery_singleton(self):
        """Test get_crash_recovery returns singleton"""
        recovery1 = get_crash_recovery()
        recovery2 = get_crash_recovery()

        assert recovery1 is recovery2

    def test_get_crash_recovery_returns_instance(self):
        """Test get_crash_recovery returns CrashRecovery"""
        recovery = get_crash_recovery()

        assert isinstance(recovery, CrashRecovery)

    def test_setup_crash_recovery_basic(self, capsys):
        """Test setup_crash_recovery configures system"""
        setup_crash_recovery(autosave_interval=120.0)

        captured = capsys.readouterr()
        assert "Crash recovery initialized" in captured.out
        assert "120" in captured.out

    def test_setup_crash_recovery_with_callback(self):
        """Test setup_crash_recovery registers callback"""

        def test_callback():
            return {"test": "data"}

        setup_crash_recovery(autosave_interval=60.0, save_callback=test_callback)

        autosave = get_autosave_manager()
        recovery = get_crash_recovery()

        assert autosave.save_callback is test_callback
        assert recovery.crash_callback is test_callback


class TestIntegration:
    """Integration tests for crash recovery system"""

    def test_full_autosave_workflow(self, tmp_path):
        """Test complete autosave workflow"""
        manager = AutoSaveManager(save_dir=str(tmp_path / "autosaves"), interval=1.0)

        # Register callback
        game_state = {"player": {"hp": 100, "level": 5}, "world": {"time": 1000}}
        manager.register_save_callback(lambda: game_state)

        # Trigger autosave via update
        manager.update(1.0)

        # Verify save was created
        latest = manager.get_latest_autosave()
        assert latest is not None

        # Load and verify
        loaded_state = manager.load_autosave()
        assert loaded_state == game_state

    def test_full_crash_recovery_workflow(self, tmp_path):
        """Test complete crash recovery workflow"""
        recovery = CrashRecovery(log_dir=str(tmp_path / "logs"))
        executor = SafeExecutor(recovery)

        # Register state callback
        game_state = {"player_position": [100, 200], "inventory": ["sword", "shield"]}
        recovery.register_crash_callback(lambda: game_state)

        # Execute failing function
        def risky_operation():
            raise RuntimeError("Critical error")

        result = executor.execute(risky_operation, error_message="Game crashed")

        assert result is None

        # Verify crash log was created
        assert recovery.has_recent_crash() is True

        latest_log = recovery.get_latest_crash_log()
        assert latest_log is not None

        # Verify state was saved
        with open(latest_log, "r") as f:
            log_data = json.load(f)

        assert log_data["state_snapshot"] == game_state
        assert log_data["exception_type"] == "RuntimeError"

    def test_autosave_and_crash_integration(self, tmp_path):
        """Test autosave and crash recovery work together"""
        autosave_dir = tmp_path / "autosaves"
        log_dir = tmp_path / "logs"

        autosave = AutoSaveManager(save_dir=str(autosave_dir), interval=10.0)
        recovery = CrashRecovery(log_dir=str(log_dir))

        game_state = {"score": 1000, "level": 10}

        # Register same callback for both
        autosave.register_save_callback(lambda: game_state)
        recovery.register_crash_callback(lambda: game_state)

        # Normal autosave
        autosave.save()

        # Simulated crash
        recovery.log_crash(ValueError("Game error"))

        # Both should have saved the state
        loaded_autosave = autosave.load_autosave()
        assert loaded_autosave == game_state

        latest_crash = recovery.get_latest_crash_log()
        with open(latest_crash, "r") as f:
            crash_data = json.load(f)
        assert crash_data["state_snapshot"] == game_state
