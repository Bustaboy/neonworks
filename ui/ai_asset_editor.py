"""
AI Asset Editor

Natural language asset modification system.
Parses commands like "make it bigger" and applies transformations to entities/tiles.
"""

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

from ..core.ecs import Entity, GridPosition, Sprite, Transform


class EditActionType(Enum):
    """Types of editing actions"""

    SCALE = auto()  # Change size
    MOVE = auto()  # Change position
    ROTATE = auto()  # Change rotation
    COLOR = auto()  # Change color
    PROPERTY = auto()  # Change generic property
    DELETE = auto()  # Delete asset


@dataclass
class EditAction:
    """Represents an editing action to apply"""

    action_type: EditActionType
    target: str  # "entity", "tile", "component"
    property_name: Optional[str] = None
    old_value: Any = None
    new_value: Any = None
    metadata: Dict[str, Any] = None


class AIAssetEditor:
    """
    Natural language asset editor.

    Parses commands like:
    - "make it bigger" → scale up
    - "make it 2x size" → scale by 2
    - "change roof color to red" → change sprite color
    - "move it 5 tiles right" → offset position
    - "rotate 90 degrees" → rotate
    - "make it smaller" → scale down
    """

    def __init__(self):
        # Scale patterns
        self.scale_patterns = [
            (r"(?:make it |scale |resize )?(bigger|larger)", 1.5),
            (r"(?:make it |scale |resize )?(smaller|tiny)", 0.75),
            (r"(?:scale|resize) (?:by )?(\d+(?:\.\d+)?)x?", "multiply"),
            (r"(?:make it |scale |resize )?(\d+)x (?:size|scale)", "multiply"),
        ]

        # Move patterns
        self.move_patterns = [
            (r"move (?:it )?(\d+) (?:tiles? )?(?:to the )?(left|right|up|down)", "direction"),
            (r"move (?:it )?(?:to )?\(?(\d+),\s*(\d+)\)?", "absolute"),
            (r"shift (?:it )?(\d+),\s*(\d+)", "offset"),
        ]

        # Rotate patterns
        self.rotate_patterns = [
            (r"rotate (?:it )?(?:by )?(\d+) ?(?:degrees?)?", "degrees"),
            (r"(?:flip|mirror) (?:it )?(horizontally|vertically|h|v)", "flip"),
        ]

        # Color patterns
        self.color_patterns = [
            (r"(?:change|make|set) (?:the )?(\w+) (?:to |color to |)(\w+)", "component_color"),
            (r"(?:change|make|set) color (?:to )?(\w+)", "full_color"),
        ]

        # Delete patterns
        self.delete_patterns = [
            r"delete (?:it|this)",
            r"remove (?:it|this)",
        ]

        # Color name mapping
        self.color_map = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "orange": (255, 165, 0),
            "purple": (128, 0, 128),
            "pink": (255, 192, 203),
            "brown": (139, 69, 19),
            "black": (0, 0, 0),
            "white": (255, 255, 255),
            "gray": (128, 128, 128),
            "grey": (128, 128, 128),
        }

    def parse_command(self, command: str, selected_entity: Optional[Entity] = None) -> List[EditAction]:
        """
        Parse natural language command into edit actions.

        Args:
            command: User command (e.g., "make it bigger")
            selected_entity: Currently selected entity (for context)

        Returns:
            List of edit actions to apply
        """
        command_lower = command.lower().strip()
        actions = []

        # Try scale patterns
        action = self._parse_scale(command_lower)
        if action:
            actions.append(action)
            return actions

        # Try move patterns
        action = self._parse_move(command_lower)
        if action:
            actions.append(action)
            return actions

        # Try rotate patterns
        action = self._parse_rotate(command_lower)
        if action:
            actions.append(action)
            return actions

        # Try color patterns
        action = self._parse_color(command_lower)
        if action:
            actions.append(action)
            return actions

        # Try delete patterns
        if self._is_delete_command(command_lower):
            actions.append(
                EditAction(
                    action_type=EditActionType.DELETE,
                    target="entity",
                )
            )
            return actions

        # Unknown command
        return []

    def _parse_scale(self, command: str) -> Optional[EditAction]:
        """Parse scale command"""
        for pattern, scale_factor in self.scale_patterns:
            match = re.search(pattern, command)
            if match:
                if scale_factor == "multiply":
                    # Extract number from match
                    scale_value = float(match.group(1))
                else:
                    scale_value = scale_factor

                return EditAction(
                    action_type=EditActionType.SCALE,
                    target="entity",
                    property_name="scale",
                    new_value=scale_value,
                    metadata={"relative": True},
                )

        return None

    def _parse_move(self, command: str) -> Optional[EditAction]:
        """Parse move command"""
        for pattern, move_type in self.move_patterns:
            match = re.search(pattern, command)
            if match:
                if move_type == "direction":
                    distance = int(match.group(1))
                    direction = match.group(2)

                    # Convert to offset
                    offset = (0, 0)
                    if direction == "left":
                        offset = (-distance, 0)
                    elif direction == "right":
                        offset = (distance, 0)
                    elif direction == "up":
                        offset = (0, -distance)
                    elif direction == "down":
                        offset = (0, distance)

                    return EditAction(
                        action_type=EditActionType.MOVE,
                        target="entity",
                        property_name="position",
                        new_value=offset,
                        metadata={"relative": True},
                    )

                elif move_type == "absolute":
                    x = int(match.group(1))
                    y = int(match.group(2))

                    return EditAction(
                        action_type=EditActionType.MOVE,
                        target="entity",
                        property_name="position",
                        new_value=(x, y),
                        metadata={"relative": False},
                    )

                elif move_type == "offset":
                    dx = int(match.group(1))
                    dy = int(match.group(2))

                    return EditAction(
                        action_type=EditActionType.MOVE,
                        target="entity",
                        property_name="position",
                        new_value=(dx, dy),
                        metadata={"relative": True},
                    )

        return None

    def _parse_rotate(self, command: str) -> Optional[EditAction]:
        """Parse rotate command"""
        for pattern, rotate_type in self.rotate_patterns:
            match = re.search(pattern, command)
            if match:
                if rotate_type == "degrees":
                    degrees = int(match.group(1))

                    return EditAction(
                        action_type=EditActionType.ROTATE,
                        target="entity",
                        property_name="rotation",
                        new_value=degrees,
                        metadata={"relative": True},
                    )

                elif rotate_type == "flip":
                    flip_dir = match.group(1)
                    flip_h = flip_dir in ("horizontally", "h")
                    flip_v = flip_dir in ("vertically", "v")

                    return EditAction(
                        action_type=EditActionType.PROPERTY,
                        target="component",
                        property_name="Sprite",
                        new_value={"flip_h": flip_h, "flip_v": flip_v},
                    )

        return None

    def _parse_color(self, command: str) -> Optional[EditAction]:
        """Parse color command"""
        for pattern, color_type in self.color_patterns:
            match = re.search(pattern, command)
            if match:
                if color_type == "component_color":
                    component = match.group(1)  # e.g., "roof", "door"
                    color_name = match.group(2)

                    if color_name in self.color_map:
                        return EditAction(
                            action_type=EditActionType.COLOR,
                            target="component",
                            property_name=component,
                            new_value=self.color_map[color_name],
                        )

                elif color_type == "full_color":
                    color_name = match.group(1)

                    if color_name in self.color_map:
                        return EditAction(
                            action_type=EditActionType.COLOR,
                            target="entity",
                            property_name="color",
                            new_value=self.color_map[color_name],
                        )

        return None

    def _is_delete_command(self, command: str) -> bool:
        """Check if command is a delete command"""
        for pattern in self.delete_patterns:
            if re.search(pattern, command):
                return True
        return False

    def apply_action(self, action: EditAction, entity: Entity) -> bool:
        """
        Apply edit action to an entity.

        Args:
            action: Edit action to apply
            entity: Entity to modify

        Returns:
            True if action was applied successfully
        """
        try:
            if action.action_type == EditActionType.SCALE:
                return self._apply_scale(action, entity)

            elif action.action_type == EditActionType.MOVE:
                return self._apply_move(action, entity)

            elif action.action_type == EditActionType.ROTATE:
                return self._apply_rotate(action, entity)

            elif action.action_type == EditActionType.COLOR:
                return self._apply_color(action, entity)

            elif action.action_type == EditActionType.PROPERTY:
                return self._apply_property(action, entity)

            elif action.action_type == EditActionType.DELETE:
                # Deletion handled by caller (removes from world)
                return True

        except Exception as e:
            print(f"Error applying action: {e}")
            return False

        return False

    def _apply_scale(self, action: EditAction, entity: Entity) -> bool:
        """Apply scale transformation"""
        transform = entity.get_component(Transform)
        if not transform:
            return False

        scale_factor = action.new_value

        if action.metadata and action.metadata.get("relative"):
            # Relative scale (multiply current scale)
            transform.scale_x *= scale_factor
            transform.scale_y *= scale_factor
        else:
            # Absolute scale
            transform.scale_x = scale_factor
            transform.scale_y = scale_factor

        return True

    def _apply_move(self, action: EditAction, entity: Entity) -> bool:
        """Apply move transformation"""
        # Try GridPosition first
        grid_pos = entity.get_component(GridPosition)
        if grid_pos:
            new_value = action.new_value

            if action.metadata and action.metadata.get("relative"):
                # Relative move (offset)
                grid_pos.x += new_value[0]
                grid_pos.y += new_value[1]
            else:
                # Absolute position
                grid_pos.x = new_value[0]
                grid_pos.y = new_value[1]

            return True

        # Try Transform as fallback
        transform = entity.get_component(Transform)
        if transform:
            new_value = action.new_value

            if action.metadata and action.metadata.get("relative"):
                transform.x += new_value[0]
                transform.y += new_value[1]
            else:
                transform.x = new_value[0]
                transform.y = new_value[1]

            return True

        return False

    def _apply_rotate(self, action: EditAction, entity: Entity) -> bool:
        """Apply rotation transformation"""
        transform = entity.get_component(Transform)
        if not transform:
            return False

        degrees = action.new_value

        if action.metadata and action.metadata.get("relative"):
            # Relative rotation
            transform.rotation += degrees
        else:
            # Absolute rotation
            transform.rotation = degrees

        # Normalize to 0-360
        transform.rotation = transform.rotation % 360

        return True

    def _apply_color(self, action: EditAction, entity: Entity) -> bool:
        """Apply color change"""
        sprite = entity.get_component(Sprite)
        if not sprite:
            return False

        color = action.new_value

        # For now, we can add a color_tint property to Sprite
        # This would need to be supported by the rendering system
        if hasattr(sprite, "color_tint"):
            sprite.color_tint = color
        else:
            # Store in metadata for future implementation
            if not hasattr(sprite, "metadata"):
                sprite.metadata = {}
            sprite.metadata["color_tint"] = color

        return True

    def _apply_property(self, action: EditAction, entity: Entity) -> bool:
        """Apply generic property change"""
        if action.target == "component":
            # Change component property
            comp_name = action.property_name
            new_value = action.new_value

            # Find component by name
            for comp_type, component in entity.components.items():
                if comp_type.__name__ == comp_name:
                    # Apply property changes
                    if isinstance(new_value, dict):
                        for key, value in new_value.items():
                            if hasattr(component, key):
                                setattr(component, key, value)
                    return True

        return False

    def get_action_description(self, action: EditAction) -> str:
        """Get human-readable description of action"""
        if action.action_type == EditActionType.SCALE:
            return f"Scale by {action.new_value}x"

        elif action.action_type == EditActionType.MOVE:
            if action.metadata and action.metadata.get("relative"):
                return f"Move by {action.new_value}"
            else:
                return f"Move to {action.new_value}"

        elif action.action_type == EditActionType.ROTATE:
            return f"Rotate {action.new_value}°"

        elif action.action_type == EditActionType.COLOR:
            return f"Change color to {action.new_value}"

        elif action.action_type == EditActionType.DELETE:
            return "Delete entity"

        return "Unknown action"
