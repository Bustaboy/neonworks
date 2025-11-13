"""
Puzzle System for Dungeon Mechanics

Handles switches, pressure plates, pushable blocks, and puzzle logic.
"""

from typing import List, Optional

from neonworks.gameplay.movement import Collider2D, Direction, Movement
from neonworks.gameplay.puzzle_objects import (
    Chest,
    CrackableWall,
    Door,
    IceTile,
    PressurePlate,
    PushableBlock,
    PuzzleController,
    Switch,
    TeleportPad,
)
from neonworks.core.ecs import Entity, GridPosition, System, World
from neonworks.core.events import Event, EventManager, EventType


class PuzzleSystem(System):
    """
    System for handling dungeon puzzle mechanics.

    Features:
    - Switch activation/deactivation
    - Pressure plate detection
    - Pushable block movement
    - Door opening/closing
    - Teleportation
    - Puzzle state persistence
    """

    def __init__(self, event_manager: EventManager):
        super().__init__()
        self.priority = 25
        self.event_manager = event_manager

        # Puzzle state (persisted per zone)
        self.puzzle_states = {}  # zone_id -> {puzzle_id -> state}

        # Subscribe to interaction events
        self.event_manager.subscribe(EventType.CUSTOM, self._handle_custom_event)

    def update(self, world: World, delta_time: float):
        """Update puzzle system"""
        # Update pressure plates
        self._update_pressure_plates(world)

        # Update auto-close doors
        self._update_auto_close_doors(world, delta_time)

        # Update puzzle controllers
        self._update_puzzle_controllers(world)

    def activate_switch(self, world: World, switch_entity: Entity):
        """Activate a switch"""
        switch = switch_entity.get_component(Switch)
        if not switch or switch.is_locked:
            return

        # Toggle switch state
        if switch.switch_type == "toggle":
            switch.is_active = not switch.is_active
        elif switch.switch_type == "momentary" or switch.switch_type == "one-time":
            if switch.is_one_time and switch.is_active:
                return  # Already activated once
            switch.is_active = True

        # Update visual
        # (Would update sprite component here)

        # Activate targets
        for target_id in switch.target_ids:
            target = world.get_entity(target_id)
            if target:
                self._activate_puzzle_element(world, target, switch.is_active)

        # Emit event
        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "switch_toggled",
                    "switch_id": switch_entity.id,
                    "is_active": switch.is_active,
                },
            )
        )

        # Trigger callback
        if switch.is_active and switch.on_activate:
            switch.on_activate()
        elif not switch.is_active and switch.on_deactivate:
            switch.on_deactivate()

    def push_block(
        self, world: World, block_entity: Entity, direction: Direction
    ) -> bool:
        """
        Push a block in a direction.

        Returns:
            True if block was pushed successfully
        """
        block = block_entity.get_component(PushableBlock)
        grid_pos = block_entity.get_component(GridPosition)

        if not block or not grid_pos or block.is_being_pushed:
            return False

        # Calculate target position
        dx, dy = direction.to_vector()
        target_x = grid_pos.grid_x + dx
        target_y = grid_pos.grid_y + dy

        # Check if target is walkable
        if not self._is_position_walkable(world, target_x, target_y, block_entity):
            return False

        # Start push
        block.is_being_pushed = True

        # Move block
        movement = block_entity.get_component(Movement)
        if movement:
            movement.is_moving = True
            movement.target_grid_x = target_x
            movement.target_grid_y = target_y
            movement.move_progress = 0.0

        # Update grid position (immediate for simplicity)
        grid_pos.grid_x = target_x
        grid_pos.grid_y = target_y

        block.is_being_pushed = False

        # Emit event
        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "block_pushed",
                    "block_id": block_entity.id,
                    "new_x": target_x,
                    "new_y": target_y,
                },
            )
        )

        # Check if block is now on a pressure plate
        self._check_pressure_plate_at_position(world, target_x, target_y, block_entity)

        return True

    def open_door(self, world: World, door_entity: Entity):
        """Open a door"""
        door = door_entity.get_component(Door)
        if not door or door.is_open or door.is_locked:
            return

        door.is_open = True

        # Update collider to allow passage
        collider = door_entity.get_component(Collider2D)
        if collider:
            collider.is_solid = False

        # Emit event
        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "door_opened",
                    "door_id": door_entity.id,
                },
            )
        )

        # Trigger callback
        if door.on_open:
            door.on_open()

    def close_door(self, world: World, door_entity: Entity):
        """Close a door"""
        door = door_entity.get_component(Door)
        if not door or not door.is_open:
            return

        door.is_open = False

        # Update collider to block passage
        collider = door_entity.get_component(Collider2D)
        if collider:
            collider.is_solid = True

        # Emit event
        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "door_closed",
                    "door_id": door_entity.id,
                },
            )
        )

        # Trigger callback
        if door.on_close:
            door.on_close()

    def teleport_entity(self, world: World, entity: Entity, teleport_pad: Entity):
        """Teleport an entity to destination"""
        teleport = teleport_pad.get_component(TeleportPad)
        grid_pos = entity.get_component(GridPosition)

        if not teleport or not grid_pos or not teleport.is_active:
            return

        # Store old position
        old_x, old_y = grid_pos.grid_x, grid_pos.grid_y

        # Teleport to destination
        grid_pos.grid_x = teleport.target_x
        grid_pos.grid_y = teleport.target_y

        # Update transform if exists
        from neonworks.core.ecs import Transform

        transform = entity.get_component(Transform)
        if transform:
            # Assuming 32x32 tile size (should be configurable)
            transform.x = teleport.target_x * 32
            transform.y = teleport.target_y * 32

        # Emit event
        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "entity_teleported",
                    "entity_id": entity.id,
                    "from_x": old_x,
                    "from_y": old_y,
                    "to_x": teleport.target_x,
                    "to_y": teleport.target_y,
                },
            )
        )

        # Trigger callback
        if teleport.on_teleport:
            teleport.on_teleport(old_x, old_y)

    def open_chest(self, world: World, chest_entity: Entity, opener: Entity) -> bool:
        """
        Open a chest and give contents to opener.

        Returns:
            True if chest was opened successfully
        """
        chest = chest_entity.get_component(Chest)
        if not chest or chest.is_open:
            return False

        # Check if locked
        if chest.is_locked:
            # Would check for key in inventory here
            return False

        # Open chest
        chest.is_open = True

        # Give contents (emit event for inventory system to handle)
        self.event_manager.emit(
            Event(
                EventType.CUSTOM,
                {
                    "type": "chest_opened",
                    "chest_id": chest_entity.id,
                    "opener_id": opener.id,
                    "gold": chest.gold,
                    "items": chest.items,
                },
            )
        )

        # Trigger callback
        if chest.on_open:
            chest.on_open()

        return True

    def _update_pressure_plates(self, world: World):
        """Update all pressure plates"""
        plates = world.get_entities_with_components(PressurePlate, GridPosition)

        for plate_entity in plates:
            plate = plate_entity.get_component(PressurePlate)
            grid_pos = plate_entity.get_component(GridPosition)

            if plate.is_locked:
                continue

            # Find entities at this position
            entities_here = self._get_entities_at_position(
                world, grid_pos.grid_x, grid_pos.grid_y, plate_entity
            )

            # Filter by what can activate plate
            valid_entities = []
            for entity in entities_here:
                if entity.has_tag("player") and plate.can_activate_by_player:
                    valid_entities.append(entity)
                elif (
                    entity.has_component(PushableBlock)
                    and plate.can_activate_by_objects
                ):
                    valid_entities.append(entity)
                elif entity.has_tag("enemy") and plate.can_activate_by_enemies:
                    valid_entities.append(entity)

            # Update weight
            plate.current_weight = len(valid_entities)
            plate.entities_on_plate = [e.id for e in valid_entities]

            # Check if should be pressed
            should_be_pressed = plate.current_weight >= plate.required_weight

            # State change
            if should_be_pressed and not plate.is_pressed:
                # Plate pressed
                plate.is_pressed = True
                if plate.on_press:
                    plate.on_press()

                # Activate targets
                for target_id in plate.target_ids:
                    target = world.get_entity(target_id)
                    if target:
                        self._activate_puzzle_element(world, target, True)

                self.event_manager.emit(
                    Event(
                        EventType.CUSTOM,
                        {"type": "pressure_plate_pressed", "plate_id": plate_entity.id},
                    )
                )

            elif not should_be_pressed and plate.is_pressed:
                # Plate released (unless stays_pressed)
                if not plate.stays_pressed:
                    plate.is_pressed = False
                    if plate.on_release:
                        plate.on_release()

                    # Deactivate targets
                    for target_id in plate.target_ids:
                        target = world.get_entity(target_id)
                        if target:
                            self._activate_puzzle_element(world, target, False)

                    self.event_manager.emit(
                        Event(
                            EventType.CUSTOM,
                            {
                                "type": "pressure_plate_released",
                                "plate_id": plate_entity.id,
                            },
                        )
                    )

    def _update_auto_close_doors(self, world: World, delta_time: float):
        """Update doors with auto-close"""
        # This would track door timers and close them
        # Simplified for now
        pass

    def _update_puzzle_controllers(self, world: World):
        """Update puzzle controllers"""
        controllers = world.get_entities_with_component(PuzzleController)

        for controller_entity in controllers:
            controller = controller_entity.get_component(PuzzleController)

            if controller.is_solved:
                continue

            # Check if puzzle is solved
            if controller.check_solution():
                # Puzzle solved!
                controller.is_solved = True

                # Activate rewards
                for target_id in controller.reward_target_ids:
                    target = world.get_entity(target_id)
                    if target:
                        self._activate_puzzle_element(world, target, True)

                # Emit event
                self.event_manager.emit(
                    Event(
                        EventType.CUSTOM,
                        {
                            "type": "puzzle_solved",
                            "puzzle_id": controller.puzzle_id,
                            "controller_id": controller_entity.id,
                        },
                    )
                )

    def _activate_puzzle_element(self, world: World, target: Entity, activate: bool):
        """Activate/deactivate a puzzle element"""
        # Door
        if target.has_component(Door):
            if activate:
                self.open_door(world, target)
            else:
                self.close_door(world, target)

        # TeleportPad
        elif target.has_component(TeleportPad):
            teleport = target.get_component(TeleportPad)
            teleport.is_active = activate

    def _is_position_walkable(
        self, world: World, x: int, y: int, ignore_entity: Optional[Entity] = None
    ) -> bool:
        """Check if position is walkable"""
        # Check for solid entities at position
        entities = self._get_entities_at_position(world, x, y, ignore_entity)

        for entity in entities:
            collider = entity.get_component(Collider2D)
            if collider and collider.is_solid:
                return False

        return True

    def _get_entities_at_position(
        self, world: World, x: int, y: int, ignore_entity: Optional[Entity] = None
    ) -> List[Entity]:
        """Get all entities at a grid position"""
        entities_here = []
        all_entities = world.get_entities_with_component(GridPosition)

        for entity in all_entities:
            if ignore_entity and entity.id == ignore_entity.id:
                continue

            grid_pos = entity.get_component(GridPosition)
            if grid_pos.grid_x == x and grid_pos.grid_y == y:
                entities_here.append(entity)

        return entities_here

    def _check_pressure_plate_at_position(
        self, world: World, x: int, y: int, entity: Entity
    ):
        """Check if there's a pressure plate at position"""
        plates = world.get_entities_with_components(PressurePlate, GridPosition)

        for plate_entity in plates:
            grid_pos = plate_entity.get_component(GridPosition)
            if grid_pos.grid_x == x and grid_pos.grid_y == y:
                # Pressure plate found, it will be updated in next update cycle
                pass

    def _handle_custom_event(self, event: Event):
        """Handle custom events"""
        if not event.data:
            return

        event_type = event.data.get("type")

        # Handle interactions
        if event_type == "interaction":
            # Would handle chest opening, switch activation, etc.
            pass

    def save_puzzle_state(self, zone_id: str, puzzle_id: str, state: dict):
        """Save puzzle state for persistence"""
        if zone_id not in self.puzzle_states:
            self.puzzle_states[zone_id] = {}
        self.puzzle_states[zone_id][puzzle_id] = state

    def load_puzzle_state(self, zone_id: str, puzzle_id: str) -> Optional[dict]:
        """Load puzzle state"""
        if zone_id in self.puzzle_states:
            return self.puzzle_states[zone_id].get(puzzle_id)
        return None
