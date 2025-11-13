"""
Turn-Based Strategy System

Manages turn order, action points, and turn-based gameplay.
"""

from typing import List, Optional
from neonworks.core.ecs import System, World, Entity, TurnActor
from neonworks.core.events import EventManager, Event, EventType, get_event_manager


class TurnSystem(System):
    """Manages turn-based gameplay"""

    def __init__(self):
        super().__init__()
        self.priority = -100  # Run early

        self.turn_order: List[Entity] = []
        self.current_turn_index = 0
        self.turn_number = 1
        self.is_player_turn = False

        self.event_manager = get_event_manager()

    def update(self, world: World, delta_time: float):
        """Update turn system"""
        # Build turn order if empty
        if not self.turn_order:
            self._build_turn_order(world)

        # Check if current actor needs to end turn
        if self.turn_order:
            current_entity = self.turn_order[self.current_turn_index]
            turn_actor = current_entity.get_component(TurnActor)

            if turn_actor and turn_actor.has_acted:
                self.end_turn()

    def _build_turn_order(self, world: World):
        """Build turn order based on initiative"""
        entities = world.get_entities_with_component(TurnActor)

        # Sort by initiative (higher first)
        entities.sort(key=lambda e: e.get_component(TurnActor).initiative, reverse=True)

        self.turn_order = entities
        self.current_turn_index = 0

        if self.turn_order:
            self.start_turn()

    def start_turn(self):
        """Start a new turn"""
        if not self.turn_order:
            return

        current_entity = self.turn_order[self.current_turn_index]
        turn_actor = current_entity.get_component(TurnActor)

        if turn_actor:
            # Reset action points
            turn_actor.action_points = turn_actor.max_action_points
            turn_actor.has_acted = False

            # Check if player turn
            self.is_player_turn = current_entity.has_tag("player")

            # Emit turn start event
            self.event_manager.emit(Event(
                EventType.TURN_START,
                {
                    "entity_id": current_entity.id,
                    "turn_number": self.turn_number,
                    "is_player": self.is_player_turn
                }
            ))

    def end_turn(self):
        """End the current turn"""
        if not self.turn_order:
            return

        current_entity = self.turn_order[self.current_turn_index]

        # Emit turn end event
        self.event_manager.emit(Event(
            EventType.TURN_END,
            {
                "entity_id": current_entity.id,
                "turn_number": self.turn_number
            }
        ))

        # Move to next entity
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)

        # If we wrapped around, increment turn number
        if self.current_turn_index == 0:
            self.turn_number += 1

        # Start next turn
        self.start_turn()

    def use_action_points(self, entity: Entity, cost: int) -> bool:
        """Use action points for an action"""
        turn_actor = entity.get_component(TurnActor)

        if not turn_actor:
            return False

        if turn_actor.action_points >= cost:
            turn_actor.action_points -= cost
            return True

        return False

    def end_actor_turn(self, entity: Entity):
        """Mark an actor as having finished their turn"""
        turn_actor = entity.get_component(TurnActor)
        if turn_actor:
            turn_actor.has_acted = True

    def get_current_actor(self) -> Optional[Entity]:
        """Get the entity whose turn it is"""
        if self.turn_order:
            return self.turn_order[self.current_turn_index]
        return None

    def add_to_turn_order(self, entity: Entity):
        """Add an entity to turn order"""
        if entity not in self.turn_order:
            # Insert based on initiative
            turn_actor = entity.get_component(TurnActor)
            if turn_actor:
                inserted = False
                for i, e in enumerate(self.turn_order):
                    other_actor = e.get_component(TurnActor)
                    if other_actor and turn_actor.initiative > other_actor.initiative:
                        self.turn_order.insert(i, entity)
                        inserted = True
                        break

                if not inserted:
                    self.turn_order.append(entity)

    def remove_from_turn_order(self, entity: Entity):
        """Remove an entity from turn order"""
        if entity in self.turn_order:
            index = self.turn_order.index(entity)

            # Adjust current turn index if needed
            if index < self.current_turn_index:
                self.current_turn_index -= 1
            elif index == self.current_turn_index:
                # Current entity removed, end turn immediately
                self.current_turn_index -= 1
                self.end_turn()

            self.turn_order.remove(entity)

    def on_entity_added(self, entity: Entity):
        """Called when entity is added to world"""
        if entity.has_component(TurnActor):
            self.add_to_turn_order(entity)

    def on_entity_removed(self, entity: Entity):
        """Called when entity is removed from world"""
        if entity in self.turn_order:
            self.remove_from_turn_order(entity)
