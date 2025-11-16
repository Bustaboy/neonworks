"""
Crash Recovery and Auto-Save System

Provides automatic saving and crash recovery for the engine.
"""

import json
import os
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional


class AutoSaveManager:
    """Manages automatic saving of project state"""

    def __init__(self, save_dir: str = "autosaves", interval: float = 300.0):
        """
        Initialize auto-save manager.

        Args:
            save_dir: Directory to store auto-saves
            interval: Auto-save interval in seconds (default: 5 minutes)
        """
        self.save_dir = Path(save_dir)
        self.interval = interval
        self.last_save_time: float = 0.0
        self.enabled: bool = True
        self.save_callback: Optional[Callable[[], Dict[str, Any]]] = None
        self.max_autosaves: int = 10  # Keep last 10 autosaves

        # Create autosave directory
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def register_save_callback(self, callback: Callable[[], Dict[str, Any]]):
        """
        Register callback that returns data to save.

        Args:
            callback: Function that returns dict of data to save
        """
        self.save_callback = callback

    def update(self, dt: float):
        """
        Update auto-save timer.

        Args:
            dt: Delta time since last update
        """
        if not self.enabled or not self.save_callback:
            return

        self.last_save_time += dt

        if self.last_save_time >= self.interval:
            self.save()
            self.last_save_time = 0.0

    def save(self) -> bool:
        """
        Perform auto-save.

        Returns:
            True if save was successful
        """
        if not self.save_callback:
            print("Warning: No save callback registered for auto-save")
            return False

        try:
            # Get save data
            data = self.save_callback()

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"autosave_{timestamp}.json"
            filepath = self.save_dir / filename

            # Save to file
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)

            print(f"Auto-save successful: {filename}")

            # Clean up old autosaves
            self._cleanup_old_saves()

            return True

        except Exception as e:
            print(f"Error during auto-save: {e}")
            traceback.print_exc()
            return False

    def _cleanup_old_saves(self):
        """Remove old auto-saves, keeping only the most recent ones"""
        try:
            # Get all autosave files
            autosaves = sorted(
                self.save_dir.glob("autosave_*.json"), key=os.path.getmtime, reverse=True
            )

            # Remove old ones
            for old_save in autosaves[self.max_autosaves :]:
                old_save.unlink()
                print(f"Removed old auto-save: {old_save.name}")

        except Exception as e:
            print(f"Error cleaning up old auto-saves: {e}")

    def get_latest_autosave(self) -> Optional[Path]:
        """
        Get the most recent auto-save file.

        Returns:
            Path to latest autosave, or None if no autosaves exist
        """
        try:
            autosaves = sorted(
                self.save_dir.glob("autosave_*.json"), key=os.path.getmtime, reverse=True
            )

            return autosaves[0] if autosaves else None

        except Exception as e:
            print(f"Error getting latest auto-save: {e}")
            return None

    def load_autosave(self, filepath: Optional[Path] = None) -> Optional[Dict[str, Any]]:
        """
        Load data from auto-save file.

        Args:
            filepath: Path to autosave file (uses latest if None)

        Returns:
            Loaded data dict, or None if failed
        """
        try:
            if filepath is None:
                filepath = self.get_latest_autosave()

            if filepath is None or not filepath.exists():
                print("No auto-save file found")
                return None

            with open(filepath, "r") as f:
                data = json.load(f)

            print(f"Loaded auto-save: {filepath.name}")
            return data

        except Exception as e:
            print(f"Error loading auto-save: {e}")
            traceback.print_exc()
            return None


class CrashRecovery:
    """Handles crash recovery and error logging"""

    def __init__(self, log_dir: str = "crash_logs"):
        """
        Initialize crash recovery system.

        Args:
            log_dir: Directory to store crash logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.crash_callback: Optional[Callable[[], Dict[str, Any]]] = None

    def register_crash_callback(self, callback: Callable[[], Dict[str, Any]]):
        """
        Register callback to save state on crash.

        Args:
            callback: Function that returns state to save on crash
        """
        self.crash_callback = callback

    def log_crash(self, exception: Exception, additional_info: Optional[Dict[str, Any]] = None):
        """
        Log crash information.

        Args:
            exception: Exception that caused the crash
            additional_info: Additional info to include in crash log
        """
        try:
            # Generate crash log filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"crash_{timestamp}.log"
            filepath = self.log_dir / filename

            # Collect crash info
            crash_info = {
                "timestamp": timestamp,
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
                "traceback": traceback.format_exc(),
            }

            # Add additional info
            if additional_info:
                crash_info["additional_info"] = additional_info

            # Save crash callback data if available
            if self.crash_callback:
                try:
                    crash_info["state_snapshot"] = self.crash_callback()
                except Exception as e:
                    crash_info["state_snapshot_error"] = str(e)

            # Write crash log
            with open(filepath, "w") as f:
                json.dump(crash_info, f, indent=2)

            print(f"\nCrash logged to: {filepath}")
            print(f"Exception: {crash_info['exception_type']}: {crash_info['exception_message']}")

            return filepath

        except Exception as e:
            print(f"Error logging crash: {e}")
            traceback.print_exc()
            return None

    def has_recent_crash(self, hours: int = 24) -> bool:
        """
        Check if there was a recent crash.

        Args:
            hours: Number of hours to look back

        Returns:
            True if recent crash found
        """
        try:
            cutoff_time = time.time() - (hours * 3600)

            crash_logs = self.log_dir.glob("crash_*.log")
            for log in crash_logs:
                if log.stat().st_mtime > cutoff_time:
                    return True

            return False

        except Exception as e:
            print(f"Error checking for recent crashes: {e}")
            return False

    def get_latest_crash_log(self) -> Optional[Path]:
        """
        Get the most recent crash log.

        Returns:
            Path to latest crash log, or None if no crashes
        """
        try:
            crash_logs = sorted(
                self.log_dir.glob("crash_*.log"), key=os.path.getmtime, reverse=True
            )

            return crash_logs[0] if crash_logs else None

        except Exception as e:
            print(f"Error getting latest crash log: {e}")
            return None


class SafeExecutor:
    """Executes functions with crash recovery"""

    def __init__(self, crash_recovery: CrashRecovery):
        """
        Initialize safe executor.

        Args:
            crash_recovery: CrashRecovery instance
        """
        self.crash_recovery = crash_recovery

    def execute(
        self,
        func: Callable,
        *args,
        error_message: str = "Operation failed",
        reraise: bool = False,
        **kwargs,
    ) -> Optional[Any]:
        """
        Execute function safely with crash logging.

        Args:
            func: Function to execute
            *args: Function arguments
            error_message: Error message to display on failure
            reraise: Whether to re-raise the exception
            **kwargs: Function keyword arguments

        Returns:
            Function result, or None if failed
        """
        try:
            return func(*args, **kwargs)

        except Exception as e:
            print(f"\n{error_message}")
            self.crash_recovery.log_crash(e)

            if reraise:
                raise

            return None


# Singleton instances
_autosave_manager: Optional[AutoSaveManager] = None
_crash_recovery: Optional[CrashRecovery] = None


def get_autosave_manager() -> AutoSaveManager:
    """Get global auto-save manager instance"""
    global _autosave_manager
    if _autosave_manager is None:
        _autosave_manager = AutoSaveManager()
    return _autosave_manager


def get_crash_recovery() -> CrashRecovery:
    """Get global crash recovery instance"""
    global _crash_recovery
    if _crash_recovery is None:
        _crash_recovery = CrashRecovery()
    return _crash_recovery


def setup_crash_recovery(
    autosave_interval: float = 300.0, save_callback: Optional[Callable] = None
):
    """
    Setup crash recovery and auto-save.

    Args:
        autosave_interval: Auto-save interval in seconds
        save_callback: Callback to get save data
    """
    autosave = get_autosave_manager()
    autosave.interval = autosave_interval

    if save_callback:
        autosave.register_save_callback(save_callback)
        get_crash_recovery().register_crash_callback(save_callback)

    print(f"Crash recovery initialized (auto-save every {autosave_interval}s)")
