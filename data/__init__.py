"""Data management systems"""

from engine.data.serialization import GameSerializer, SaveGameManager, AutoSaveManager

# Config loader (requires PyYAML for YAML support)
try:
    from engine.data.config_loader import ConfigLoader, GameDataLoader

    CONFIG_LOADER_AVAILABLE = True
except ImportError:
    CONFIG_LOADER_AVAILABLE = False

__all__ = [
    "GameSerializer",
    "SaveGameManager",
    "AutoSaveManager",
]

if CONFIG_LOADER_AVAILABLE:
    __all__.extend(["ConfigLoader", "GameDataLoader"])
