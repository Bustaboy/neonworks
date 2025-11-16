"""
Workspace System for NeonWorks Engine

Provides workspace organization for tools and editors with AI context tracking.
Inspired by Godot's workspace tabs and Unity's layout system.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set


class WorkspaceType(Enum):
    """Available workspace types"""

    PLAY = "play"
    LEVEL_EDITOR = "level_editor"
    CONTENT_CREATION = "content_creation"
    SETTINGS_DEBUG = "settings_debug"


@dataclass
class ToolDefinition:
    """Definition of a tool/editor in a workspace"""

    id: str
    name: str
    description: str
    icon: str  # Emoji or icon identifier
    hotkey: Optional[str] = None
    toggle_method: Optional[str] = None  # Method name on MasterUIManager


@dataclass
class Workspace:
    """
    A workspace groups related tools and editors together.

    Attributes:
        type: Workspace type enum
        name: Display name
        description: User-friendly description
        icon: Icon emoji
        tools: List of tool definitions in this workspace
        default_tool: Default tool to activate when entering workspace
    """

    type: WorkspaceType
    name: str
    description: str
    icon: str
    tools: List[ToolDefinition] = field(default_factory=list)
    default_tool: Optional[str] = None

    def add_tool(self, tool: ToolDefinition):
        """Add a tool to this workspace"""
        self.tools.append(tool)

    def get_tool(self, tool_id: str) -> Optional[ToolDefinition]:
        """Get tool by ID"""
        for tool in self.tools:
            if tool.id == tool_id:
                return tool
        return None

    def has_tool(self, tool_id: str) -> bool:
        """Check if workspace has a tool"""
        return any(tool.id == tool_id for tool in self.tools)


@dataclass
class WorkspaceContext:
    """
    Current workspace context for AI assistant.

    This is exported to .neonworks/ai_context.json for AI to read.
    """

    workspace: str
    mode: str
    active_tools: List[str] = field(default_factory=list)
    visible_uis: List[str] = field(default_factory=list)
    selected_entities: List[int] = field(default_factory=list)
    current_layer: int = 0
    selected_tile: Optional[int] = None
    project_path: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceContext":
        """Load from dictionary"""
        return cls(**data)


class WorkspaceManager:
    """
    Manages workspaces and tracks current state for AI context.

    Singleton pattern - use get_workspace_manager() to access.
    """

    _instance: Optional["WorkspaceManager"] = None

    def __init__(self):
        if WorkspaceManager._instance is not None:
            raise RuntimeError("WorkspaceManager is a singleton. Use get_workspace_manager()")

        self.workspaces: Dict[WorkspaceType, Workspace] = {}
        self.current_workspace: Optional[WorkspaceType] = None
        self.context = WorkspaceContext(workspace="play", mode="game")

        # Initialize default workspaces
        self._initialize_workspaces()

        # Context export path
        self.context_file = Path.home() / ".neonworks" / "ai_context.json"
        self.context_file.parent.mkdir(parents=True, exist_ok=True)

        WorkspaceManager._instance = self

    def _initialize_workspaces(self):
        """Initialize default workspace definitions"""

        # 🎮 PLAY MODE Workspace
        play_workspace = Workspace(
            type=WorkspaceType.PLAY,
            name="Play",
            description="Play and test your game",
            icon="🎮",
        )
        play_workspace.add_tool(
            ToolDefinition(
                id="game_hud",
                name="Game HUD",
                description="In-game heads-up display",
                icon="📊",
                hotkey="F10",
                toggle_method="toggle_game_hud",
            )
        )
        play_workspace.add_tool(
            ToolDefinition(
                id="combat_ui",
                name="Combat",
                description="Combat interface",
                icon="⚔️",
                hotkey="F9",
                toggle_method="toggle_combat_ui",
            )
        )
        play_workspace.add_tool(
            ToolDefinition(
                id="building_ui",
                name="Building",
                description="Building placement",
                icon="🏗️",
                hotkey="F3",
                toggle_method="toggle_building_ui",
            )
        )
        self.workspaces[WorkspaceType.PLAY] = play_workspace

        # 🗺️ LEVEL EDITOR Workspace
        level_editor_workspace = Workspace(
            type=WorkspaceType.LEVEL_EDITOR,
            name="Level Editor",
            description="Create and edit game levels",
            icon="🗺️",
            default_tool="level_builder",
        )
        level_editor_workspace.add_tool(
            ToolDefinition(
                id="level_builder",
                name="Level Builder",
                description="Main tilemap editor",
                icon="🗺️",
                hotkey="F4",
                toggle_method="toggle_level_builder",
            )
        )
        level_editor_workspace.add_tool(
            ToolDefinition(
                id="autotile_editor",
                name="Autotile Editor",
                description="Configure autotiles",
                icon="🧩",
                hotkey="F11",
                toggle_method="toggle_autotile_editor",
            )
        )
        level_editor_workspace.add_tool(
            ToolDefinition(
                id="navmesh_editor",
                name="Navmesh Editor",
                description="Edit navigation mesh",
                icon="🧭",
                hotkey="F12",
                toggle_method="toggle_navmesh_editor",
            )
        )
        level_editor_workspace.add_tool(
            ToolDefinition(
                id="event_editor",
                name="Event Editor",
                description="Create map events",
                icon="⚡",
                hotkey="F5",
                toggle_method="toggle_event_editor",
            )
        )
        level_editor_workspace.add_tool(
            ToolDefinition(
                id="map_manager",
                name="Map Manager",
                description="Manage multiple maps",
                icon="🗺️",
                hotkey="Ctrl+M",
                toggle_method="toggle_map_manager",
            )
        )
        level_editor_workspace.add_tool(
            ToolDefinition(
                id="ai_assistant",
                name="AI Assistant",
                description="AI-powered level editing",
                icon="🤖",
                hotkey="Ctrl+Space",
                toggle_method="toggle_ai_assistant",
            )
        )
        self.workspaces[WorkspaceType.LEVEL_EDITOR] = level_editor_workspace

        # 🎨 CONTENT CREATION Workspace
        content_workspace = Workspace(
            type=WorkspaceType.CONTENT_CREATION,
            name="Content Creation",
            description="Create assets and content",
            icon="🎨",
        )
        content_workspace.add_tool(
            ToolDefinition(
                id="database_editor",
                name="Database Editor",
                description="Manage game database (actors, items, skills)",
                icon="💾",
                hotkey="F6",
                toggle_method="toggle_database_editor",
            )
        )
        content_workspace.add_tool(
            ToolDefinition(
                id="character_generator",
                name="Character Generator",
                description="Create custom character sprites",
                icon="👤",
                hotkey="F7",
                toggle_method="toggle_character_generator",
            )
        )
        content_workspace.add_tool(
            ToolDefinition(
                id="quest_editor",
                name="Quest Editor",
                description="Create quests and dialogue",
                icon="📜",
                hotkey="F8",
                toggle_method="toggle_quest_editor",
            )
        )
        content_workspace.add_tool(
            ToolDefinition(
                id="asset_browser",
                name="Asset Browser",
                description="Manage game assets",
                icon="📁",
                hotkey="Ctrl+Shift+A",
                toggle_method="toggle_asset_browser",
            )
        )
        content_workspace.add_tool(
            ToolDefinition(
                id="ai_animator",
                name="AI Animator",
                description="AI-powered sprite animation",
                icon="🤖",
                hotkey="Shift+F7",
                toggle_method="toggle_ai_animator",
            )
        )
        self.workspaces[WorkspaceType.CONTENT_CREATION] = content_workspace

        # ⚙️ SETTINGS & DEBUG Workspace
        settings_workspace = Workspace(
            type=WorkspaceType.SETTINGS_DEBUG,
            name="Settings & Debug",
            description="Configure and debug",
            icon="⚙️",
        )
        settings_workspace.add_tool(
            ToolDefinition(
                id="settings",
                name="Settings",
                description="Game and editor settings",
                icon="⚙️",
                hotkey="F2",
                toggle_method="toggle_settings",
            )
        )
        settings_workspace.add_tool(
            ToolDefinition(
                id="debug_console",
                name="Debug Console",
                description="Debug commands and logs",
                icon="🐛",
                hotkey="F1",
                toggle_method="toggle_debug_console",
            )
        )
        settings_workspace.add_tool(
            ToolDefinition(
                id="project_manager",
                name="Project Manager",
                description="Manage projects",
                icon="📦",
                hotkey="Ctrl+Shift+P",
                toggle_method="toggle_project_manager",
            )
        )
        self.workspaces[WorkspaceType.SETTINGS_DEBUG] = settings_workspace

    def set_workspace(self, workspace_type: WorkspaceType):
        """
        Switch to a different workspace.

        Args:
            workspace_type: Workspace to switch to
        """
        if workspace_type not in self.workspaces:
            raise ValueError(f"Unknown workspace: {workspace_type}")

        self.current_workspace = workspace_type

        # Update context
        self.context.workspace = workspace_type.value

        # Set mode based on workspace
        if workspace_type == WorkspaceType.PLAY:
            self.context.mode = "game"
        elif workspace_type in (WorkspaceType.LEVEL_EDITOR, WorkspaceType.CONTENT_CREATION):
            self.context.mode = "editor"
        else:
            self.context.mode = "menu"

        # Export context for AI
        self.export_context()

    def get_current_workspace(self) -> Optional[Workspace]:
        """Get the current workspace"""
        if self.current_workspace is None:
            return None
        return self.workspaces.get(self.current_workspace)

    def get_workspace(self, workspace_type: WorkspaceType) -> Optional[Workspace]:
        """Get workspace by type"""
        return self.workspaces.get(workspace_type)

    def get_all_workspaces(self) -> List[Workspace]:
        """Get all workspaces in order"""
        return [
            self.workspaces[WorkspaceType.PLAY],
            self.workspaces[WorkspaceType.LEVEL_EDITOR],
            self.workspaces[WorkspaceType.CONTENT_CREATION],
            self.workspaces[WorkspaceType.SETTINGS_DEBUG],
        ]

    def update_context(
        self,
        active_tools: Optional[List[str]] = None,
        visible_uis: Optional[List[str]] = None,
        selected_entities: Optional[List[int]] = None,
        current_layer: Optional[int] = None,
        selected_tile: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Update workspace context for AI assistant.

        Args:
            active_tools: List of currently active tool IDs
            visible_uis: List of visible UI names
            selected_entities: List of selected entity IDs
            current_layer: Current editing layer
            selected_tile: Currently selected tile ID
            metadata: Additional metadata
        """
        if active_tools is not None:
            self.context.active_tools = active_tools
        if visible_uis is not None:
            self.context.visible_uis = visible_uis
        if selected_entities is not None:
            self.context.selected_entities = selected_entities
        if current_layer is not None:
            self.context.current_layer = current_layer
        if selected_tile is not None:
            self.context.selected_tile = selected_tile
        if metadata is not None:
            self.context.metadata.update(metadata)

        self.context.timestamp = datetime.now().isoformat()
        self.export_context()

    def export_context(self):
        """
        Export current workspace context to JSON file for AI assistant.

        The AI assistant can read this file to understand:
        - What workspace the user is in
        - What tools are active
        - What entities/tiles are selected
        - Current editing state
        """
        try:
            with open(self.context_file, "w") as f:
                json.dump(self.context.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to export AI context: {e}")

    def load_context(self) -> Optional[WorkspaceContext]:
        """Load workspace context from file"""
        if not self.context_file.exists():
            return None

        try:
            with open(self.context_file, "r") as f:
                data = json.load(f)
                return WorkspaceContext.from_dict(data)
        except Exception as e:
            print(f"Warning: Failed to load AI context: {e}")
            return None

    def find_tool(self, tool_id: str) -> Optional[tuple[WorkspaceType, ToolDefinition]]:
        """
        Find a tool by ID across all workspaces.

        Returns:
            Tuple of (workspace_type, tool_definition) or None
        """
        for workspace_type, workspace in self.workspaces.items():
            tool = workspace.get_tool(tool_id)
            if tool:
                return (workspace_type, tool)
        return None


# Singleton accessor
_workspace_manager_instance: Optional[WorkspaceManager] = None


def get_workspace_manager() -> WorkspaceManager:
    """Get the global WorkspaceManager instance (singleton)"""
    global _workspace_manager_instance
    if _workspace_manager_instance is None:
        _workspace_manager_instance = WorkspaceManager()
    return _workspace_manager_instance
