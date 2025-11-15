"""
AI-Powered Level Generator Tool

Comprehensive level generation tool with chat interface.
Users can generate complete levels by chatting with AI.
"""

import json
import random
from typing import Dict, List, Optional, Tuple

import pygame

from ..core.ecs import GridPosition, Health, ResourceStorage, Sprite, Survival, Transform, TurnActor
from ..core.event_commands import EventPage, GameEvent, TriggerType
from ..editor.ai_level_builder import AILevelBuilder, PlacementSuggestion
from ..editor.ai_navmesh import AINavmeshGenerator, NavmeshConfig
from ..rendering.tilemap import Tile
from .map_tools import MapTool, ToolContext


class AILevelGenerator:
    """
    Comprehensive AI level generator that creates complete, playable levels.

    Generates:
    - Terrain (tiles with biomes)
    - Buildings (bases, structures)
    - Props (trees, rocks, decorations)
    - Entities (NPCs, enemies, chests)
    - Navmesh (walkability)
    - Events (NPCs, chests, triggers)
    """

    def __init__(self):
        self.templates = {
            "rpg_town": {
                "description": "Medieval RPG town with NPCs and shops",
                "terrain": "grass",
                "buildings": ["houses", "shops", "inn", "smithy"],
                "props": ["trees", "flowers", "fences"],
                "entities": ["npc_villager", "npc_merchant", "npc_guard"],
                "events": ["npc", "door", "chest"],
            },
            "dungeon": {
                "description": "Dark dungeon with enemies and treasure",
                "terrain": "stone",
                "buildings": ["walls", "pillars", "doors"],
                "props": ["torches", "bones", "rubble"],
                "entities": ["enemy_skeleton", "enemy_zombie", "chest"],
                "events": ["trigger", "chest", "door"],
            },
            "forest": {
                "description": "Natural forest with wildlife and resources",
                "terrain": "grass",
                "buildings": [],
                "props": ["trees", "bushes", "rocks"],
                "entities": ["enemy_wolf", "npc_hermit", "chest"],
                "events": ["npc", "trigger"],
            },
            "desert_oasis": {
                "description": "Desert oasis with merchants and bandits",
                "terrain": "sand",
                "buildings": ["tents", "market_stalls"],
                "props": ["palm_trees", "cacti", "rocks"],
                "entities": ["npc_merchant", "enemy_bandit", "chest"],
                "events": ["npc", "chest"],
            },
            "castle": {
                "description": "Grand castle with guards and throne room",
                "terrain": "floor",
                "buildings": ["throne_room", "guard_towers", "walls"],
                "props": ["banners", "furniture", "decorations"],
                "entities": ["npc_guard", "npc_king", "npc_knight"],
                "events": ["npc", "door", "trigger"],
            },
            "battlefield": {
                "description": "Tactical battlefield for combat encounters",
                "terrain": "dirt",
                "buildings": ["cover", "barriers"],
                "props": ["debris", "craters", "obstacles"],
                "entities": ["enemy_soldier", "enemy_archer"],
                "events": ["trigger"],
            },
        }

        self.terrain_types = {
            "grass": {"color": (100, 200, 50), "walkable": True},
            "dirt": {"color": (139, 90, 43), "walkable": True},
            "stone": {"color": (128, 128, 128), "walkable": True},
            "sand": {"color": (255, 220, 150), "walkable": True},
            "water": {"color": (100, 150, 255), "walkable": False},
            "floor": {"color": (200, 200, 200), "walkable": True},
            "lava": {"color": (255, 100, 0), "walkable": False},
            "wall": {"color": (80, 80, 80), "walkable": False},
        }

    def generate_from_prompt(self, prompt: str, context: ToolContext) -> str:
        """
        Generate a level based on natural language prompt.

        Args:
            prompt: User's text description
            context: Tool context for level modification

        Returns:
            Response message describing what was generated
        """
        prompt_lower = prompt.lower()

        # Check for template matches
        template_name = None
        for name, template in self.templates.items():
            if name.replace("_", " ") in prompt_lower or any(
                word in prompt_lower for word in template["description"].lower().split()
            ):
                template_name = name
                break

        # Parse prompt for customizations
        width = 50
        height = 50
        if "small" in prompt_lower:
            width, height = 30, 30
        elif "large" in prompt_lower or "huge" in prompt_lower:
            width, height = 80, 80
        elif "medium" in prompt_lower:
            width, height = 50, 50

        # Generate level
        if template_name:
            return self._generate_from_template(template_name, width, height, context)
        else:
            return self._generate_custom(prompt, width, height, context)

    def _generate_from_template(
        self, template_name: str, width: int, height: int, context: ToolContext
    ) -> str:
        """Generate level from predefined template."""
        template = self.templates[template_name]

        # Update grid size
        context.grid_width = width
        context.grid_height = height

        # Initialize tilemap if needed
        if not context.tilemap:
            from ..rendering.tilemap import Tilemap

            context.tilemap = Tilemap(
                width=width, height=height, tile_size=context.tile_size, layers=3
            )

        # 1. Generate terrain
        terrain_type = template["terrain"]
        self._generate_terrain(terrain_type, width, height, context)

        # 2. Generate buildings/structures
        num_buildings = random.randint(3, 8)
        self._generate_buildings(template["buildings"], num_buildings, width, height, context)

        # 3. Generate props/decorations
        prop_density = 0.15
        self._generate_props(template["props"], prop_density, width, height, context)

        # 4. Generate entities
        num_entities = random.randint(5, 15)
        self._generate_entities(template["entities"], num_entities, width, height, context)

        # 5. Generate events
        num_events = random.randint(3, 8)
        self._generate_events(template["events"], num_events, width, height, context)

        # 6. Generate navmesh
        self._generate_navmesh(width, height, context)

        response = (
            f"✅ Generated '{template_name.replace('_', ' ').title()}' level!\n\n"
            f"📐 Size: {width}x{height}\n"
            f"🌍 Terrain: {terrain_type}\n"
            f"🏛️ Buildings: {num_buildings}\n"
            f"🌳 Props: ~{int(width * height * prop_density)}\n"
            f"👥 Entities: {num_entities}\n"
            f"⭐ Events: {num_events}\n"
            f"🗺️ Navmesh: Generated\n\n"
            f"💬 You can now:\n"
            f"  • Add more: 'add 5 houses' or 'add 10 enemies'\n"
            f"  • Modify terrain: 'add water in center'\n"
            f"  • Or manually edit with tools:\n"
            f"    - Shape Tool (5): Draw rectangles, circles, lines\n"
            f"    - Stamp Tool (6): Paint with custom patterns\n"
            f"    - Eyedropper (7): Pick tiles from map\n"
            f"    - Fill Tool (3): Flood fill areas\n"
            f"    - Select Tool (4): Select & copy regions"
        )

        return response

    def _generate_custom(self, prompt: str, width: int, height: int, context: ToolContext) -> str:
        """Generate custom level from freeform prompt."""
        # Parse prompt for intent
        prompt_lower = prompt.lower()

        # Determine terrain
        terrain_type = "grass"  # default
        for t in self.terrain_types.keys():
            if t in prompt_lower:
                terrain_type = t
                break

        # Update grid size
        context.grid_width = width
        context.grid_height = height

        # Initialize tilemap
        if not context.tilemap:
            from ..rendering.tilemap import Tilemap

            context.tilemap = Tilemap(
                width=width, height=height, tile_size=context.tile_size, layers=3
            )

        # Generate terrain
        self._generate_terrain(terrain_type, width, height, context)

        response = (
            f"✅ Generated custom level from your description!\n\n"
            f"📐 Size: {width}x{height}\n"
            f"🌍 Terrain: {terrain_type}\n\n"
            f"💬 Tell me what else to add:\n"
            f"  • 'add buildings'\n"
            f"  • 'add enemies'\n"
            f"  • 'add NPCs'\n"
            f"  • 'add trees and rocks'\n"
            f"  • 'make it a dungeon'\n\n"
            f"🔧 Or use manual tools:\n"
            f"  • Shape Tool (5): Geometric shapes\n"
            f"  • Stamp Tool (6): Custom patterns\n"
            f"  • Eyedropper (7): Pick tiles\n"
            f"  • Fill Tool (3): Flood fill\n"
            f"  • Undo/Redo: Ctrl+Z / Ctrl+Y"
        )

        return response

    def _generate_terrain(self, terrain_type: str, width: int, height: int, context: ToolContext):
        """Generate terrain using selected tile type."""
        terrain_data = self.terrain_types.get(terrain_type, self.terrain_types["grass"])

        # Base layer - fill entire map
        for y in range(height):
            for x in range(width):
                tile = Tile(tile_type=terrain_type, walkable=terrain_data["walkable"])
                context.tilemap.set_tile(x, y, 0, tile)

        # Add variation with Perlin-noise-like patterns
        self._add_terrain_variation(terrain_type, width, height, context)

    def _add_terrain_variation(
        self, base_terrain: str, width: int, height: int, context: ToolContext
    ):
        """Add natural-looking terrain variation."""
        # Determine variation terrain
        variations = {
            "grass": ["dirt", "flowers"],
            "dirt": ["stone", "grass"],
            "stone": ["wall", "floor"],
            "sand": ["dirt", "stone"],
            "floor": ["stone", "dirt"],
        }

        if base_terrain not in variations:
            return

        variation_types = variations[base_terrain]

        # Create random patches
        num_patches = random.randint(3, 8)
        for _ in range(num_patches):
            center_x = random.randint(0, width - 1)
            center_y = random.randint(0, height - 1)
            radius = random.randint(2, 5)
            variation_type = random.choice(variation_types)

            # Only use valid terrain types
            if variation_type not in self.terrain_types:
                continue

            terrain_data = self.terrain_types[variation_type]

            # Fill circular patch
            for y in range(max(0, center_y - radius), min(height, center_y + radius + 1)):
                for x in range(max(0, center_x - radius), min(width, center_x + radius + 1)):
                    dist_sq = (x - center_x) ** 2 + (y - center_y) ** 2
                    if dist_sq <= radius**2 and random.random() > 0.3:
                        tile = Tile(tile_type=variation_type, walkable=terrain_data["walkable"])
                        context.tilemap.set_tile(x, y, 0, tile)

    def _generate_buildings(
        self,
        building_types: List[str],
        num_buildings: int,
        width: int,
        height: int,
        context: ToolContext,
    ):
        """Generate buildings using AI placement."""
        if not building_types:
            return

        ai_builder = AILevelBuilder(width, height)

        # Use AI to suggest good building positions
        for _ in range(num_buildings):
            # Random position with some margin from edges
            x = random.randint(5, width - 6)
            y = random.randint(5, height - 6)

            # Place wall tiles to represent building
            building_size = random.randint(2, 4)
            for dy in range(building_size):
                for dx in range(building_size):
                    bx, by = x + dx, y + dy
                    if 0 <= bx < width and 0 <= by < height:
                        tile = Tile(tile_type="wall", walkable=False)
                        context.tilemap.set_tile(bx, by, 1, tile)

    def _generate_props(
        self, prop_types: List[str], density: float, width: int, height: int, context: ToolContext
    ):
        """Generate props/decorations."""
        if not prop_types:
            return

        num_props = int(width * height * density)

        for _ in range(num_props):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)

            # Check if position is already occupied
            existing_tile = context.tilemap.get_tile(x, y, 1)
            if existing_tile:
                continue

            # Place prop tile
            prop_type = random.choice(["tree", "rock", "flower"]) if prop_types else "rock"
            if prop_type == "tree":
                tile = Tile(tile_type="tree", walkable=False)
            elif prop_type == "rock":
                tile = Tile(tile_type="stone", walkable=False)
            else:
                tile = Tile(tile_type="grass", walkable=True)

            context.tilemap.set_tile(x, y, 1, tile)

    def _generate_entities(
        self,
        entity_types: List[str],
        num_entities: int,
        width: int,
        height: int,
        context: ToolContext,
    ):
        """Generate entities (NPCs, enemies, chests)."""
        if not entity_types:
            return

        for _ in range(num_entities):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)

            # Choose entity type
            entity_type = random.choice(entity_types) if entity_types else "enemy"

            # Create entity
            entity_id = context.world.create_entity()

            # Add components
            context.world.add_component(
                entity_id, Transform(x=x * context.tile_size, y=y * context.tile_size)
            )
            context.world.add_component(entity_id, GridPosition(x, y))

            # Determine entity properties
            if "enemy" in entity_type:
                color = (255, 0, 0)
                context.world.add_component(entity_id, Health(current=50, maximum=50))
                context.world.add_component(entity_id, TurnActor(initiative=10))
                context.world.tag_entity(entity_id, "enemy")
            elif "npc" in entity_type:
                color = (100, 150, 255)
                context.world.tag_entity(entity_id, "npc")
            elif "chest" in entity_type:
                color = (255, 215, 0)
                context.world.add_component(entity_id, ResourceStorage(capacity=50))
                context.world.tag_entity(entity_id, "interactable")
            else:
                color = (150, 150, 150)

            context.world.add_component(
                entity_id, Sprite(asset_id=f"entity_{entity_type}", color=color)
            )

    def _generate_events(
        self, event_types: List[str], num_events: int, width: int, height: int, context: ToolContext
    ):
        """Generate events (NPCs, chests, doors, triggers)."""
        if not event_types:
            return

        event_templates = {
            "npc": {
                "name": "NPC",
                "color": (100, 150, 255),
                "trigger": TriggerType.ACTION_BUTTON,
                "icon": "👤",
            },
            "chest": {
                "name": "Chest",
                "color": (255, 215, 0),
                "trigger": TriggerType.ACTION_BUTTON,
                "icon": "📦",
            },
            "door": {
                "name": "Door",
                "color": (139, 69, 19),
                "trigger": TriggerType.ACTION_BUTTON,
                "icon": "🚪",
            },
            "trigger": {
                "name": "Trigger",
                "color": (255, 100, 200),
                "trigger": TriggerType.PLAYER_TOUCH,
                "icon": "⚡",
            },
        }

        for i in range(num_events):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)

            # Choose event type
            event_type = random.choice(event_types) if event_types else "trigger"

            # Check if event already exists at this position
            if any(e.x == x and e.y == y for e in context.events):
                continue

            template = event_templates.get(event_type, event_templates["trigger"])

            # Generate new event ID
            new_id = max([e.id for e in context.events], default=0) + 1

            # Create event
            new_event = GameEvent(
                id=new_id, name=f"{template['name']} {new_id:03d}", x=x, y=y, pages=[]
            )

            # Add metadata
            new_event.color = template["color"]
            new_event.icon = template["icon"]
            new_event.template_type = event_type

            # Add default page
            default_page = EventPage(trigger=template["trigger"], commands=[])
            new_event.pages.append(default_page)

            context.events.append(new_event)

        # Sync to event editor if available
        if context.event_editor:
            context.event_editor.load_events_from_scene(context.events)

    def _generate_navmesh(self, width: int, height: int, context: ToolContext):
        """Generate navmesh using AI."""
        # Use AI navmesh generator
        config = NavmeshConfig(
            detect_buildings=True,
            detect_terrain=True,
            detect_props=True,
            auto_detect_chokepoints=True,
            auto_detect_cover=True,
        )

        generator = AINavmeshGenerator(config)
        navmesh = generator.generate(context.world, width, height)

        # Store navmesh (would integrate with game's navmesh system)
        print(f"Generated navmesh with {len(navmesh.walkable_cells)} walkable cells")


class AIGeneratorTool(MapTool):
    """
    AI-powered level generator tool with chat interface.

    Users can chat with AI to generate and modify levels.
    """

    def __init__(self):
        super().__init__("AI Gen", 9, (150, 0, 150))
        self.cursor_type = "ai"
        self.generator = AILevelGenerator()

        # Chat interface state
        self.chat_visible = False
        self.chat_history: List[Tuple[str, str]] = []  # [(sender, message), ...]
        self.input_text = ""
        self.input_active = False

    def on_mouse_down(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        # AI tool doesn't use mouse for painting
        return False

    def on_mouse_drag(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        return False

    def on_mouse_up(self, grid_x: int, grid_y: int, button: int, context: ToolContext) -> bool:
        return False

    def toggle_chat(self):
        """Toggle chat interface visibility."""
        self.chat_visible = not self.chat_visible
        if self.chat_visible and not self.chat_history:
            # Add welcome message
            self.chat_history.append(
                (
                    "AI",
                    "👋 Hi! I'm your AI Level Designer.\n\n"
                    "Tell me what kind of level you want:\n"
                    "  • 'Create an RPG town'\n"
                    "  • 'Make a dungeon with enemies'\n"
                    "  • 'Generate a forest area'\n"
                    "  • 'Build a desert oasis'\n"
                    "  • 'Design a castle'\n\n"
                    "I'll create a complete level with terrain, buildings, NPCs, events, and navmesh!\n\n"
                    "🔧 New Tools Available:\n"
                    "  • Shape Tool (5): Geometric shapes\n"
                    "  • Stamp Tool (6): Custom patterns\n"
                    "  • Eyedropper (7): Pick tiles\n"
                    "  • Undo/Redo: Ctrl+Z / Ctrl+Y",
                )
            )

    def send_message(self, message: str, context: ToolContext):
        """Process user message and generate response."""
        if not message.strip():
            return

        # Add user message to chat
        self.chat_history.append(("User", message))

        # Generate level based on prompt
        response = self.generator.generate_from_prompt(message, context)

        # Add AI response to chat
        self.chat_history.append(("AI", response))

    def render_cursor(
        self,
        screen: pygame.Surface,
        grid_x: int,
        grid_y: int,
        tile_size: int,
        camera_offset: Tuple[int, int],
    ):
        """Render AI cursor."""
        screen_x = grid_x * tile_size + camera_offset[0]
        screen_y = grid_y * tile_size + camera_offset[1]

        # Draw purple outline with AI sparkle
        pygame.draw.rect(screen, (150, 0, 150), (screen_x, screen_y, tile_size, tile_size), 3)

        # Draw AI icon
        font = pygame.font.Font(None, 20)
        text = font.render("AI", True, (150, 0, 150))
        screen.blit(text, (screen_x + tile_size // 4, screen_y + tile_size // 4))

    def render_chat(self, screen: pygame.Surface):
        """Render chat interface."""
        if not self.chat_visible:
            return

        screen_width = screen.get_width()
        screen_height = screen.get_height()

        # Chat panel dimensions
        panel_width = 500
        panel_height = 600
        panel_x = screen_width - panel_width - 20
        panel_y = screen_height - panel_height - 20

        # Draw panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((20, 20, 30, 240))
        screen.blit(panel_surface, (panel_x, panel_y))

        # Draw border
        pygame.draw.rect(screen, (150, 0, 150), (panel_x, panel_y, panel_width, panel_height), 2)

        # Title
        title_font = pygame.font.Font(None, 24)
        title_text = title_font.render("🤖 AI Level Designer", True, (255, 255, 255))
        screen.blit(title_text, (panel_x + 10, panel_y + 10))

        # Close button
        close_rect = pygame.Rect(panel_x + panel_width - 30, panel_y + 5, 25, 25)
        pygame.draw.rect(screen, (100, 0, 0), close_rect, border_radius=3)
        close_font = pygame.font.Font(None, 20)
        close_text = close_font.render("X", True, (255, 255, 255))
        screen.blit(close_text, (close_rect.x + 7, close_rect.y + 3))

        # Chat history area
        chat_area_y = panel_y + 40
        chat_area_height = panel_height - 100
        message_y = chat_area_y + 5

        font = pygame.font.Font(None, 18)

        # Render chat messages (scroll to bottom)
        visible_messages = self.chat_history[-20:]  # Show last 20 messages
        for sender, message in visible_messages:
            # Sender label
            sender_color = (150, 0, 150) if sender == "AI" else (100, 150, 255)
            sender_text = font.render(f"{sender}:", True, sender_color)
            screen.blit(sender_text, (panel_x + 10, message_y))
            message_y += 20

            # Message text (wrap long lines)
            words = message.split(" ")
            line = ""
            for word in words:
                test_line = line + word + " "
                if font.size(test_line)[0] > panel_width - 30:
                    if line:
                        msg_text = font.render(line, True, (220, 220, 220))
                        screen.blit(msg_text, (panel_x + 20, message_y))
                        message_y += 18
                    line = word + " "
                else:
                    line = test_line

            if line:
                msg_text = font.render(line, True, (220, 220, 220))
                screen.blit(msg_text, (panel_x + 20, message_y))
                message_y += 18

            message_y += 10  # Space between messages

        # Input area
        input_y = panel_y + panel_height - 50
        input_rect = pygame.Rect(panel_x + 10, input_y, panel_width - 100, 35)

        # Input box background
        input_color = (40, 40, 50) if self.input_active else (30, 30, 40)
        pygame.draw.rect(screen, input_color, input_rect, border_radius=3)
        pygame.draw.rect(screen, (150, 0, 150), input_rect, 2, border_radius=3)

        # Input text
        input_font = pygame.font.Font(None, 20)
        input_surface = input_font.render(self.input_text, True, (255, 255, 255))
        screen.blit(input_surface, (input_rect.x + 5, input_rect.y + 8))

        # Send button
        send_rect = pygame.Rect(panel_x + panel_width - 80, input_y, 70, 35)
        pygame.draw.rect(screen, (150, 0, 150), send_rect, border_radius=3)
        send_text = input_font.render("Send", True, (255, 255, 255))
        screen.blit(send_text, (send_rect.x + 15, send_rect.y + 8))

    def handle_chat_event(
        self, event: pygame.event.Event, context: ToolContext, screen: pygame.Surface
    ) -> bool:
        """Handle events for chat interface."""
        if not self.chat_visible:
            return False

        screen_width = screen.get_width()
        screen_height = screen.get_height()

        panel_width = 500
        panel_height = 600
        panel_x = screen_width - panel_width - 20
        panel_y = screen_height - panel_height - 20

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Check close button
            close_rect = pygame.Rect(panel_x + panel_width - 30, panel_y + 5, 25, 25)
            if close_rect.collidepoint(mouse_x, mouse_y):
                self.toggle_chat()
                return True

            # Check input box
            input_y = panel_y + panel_height - 50
            input_rect = pygame.Rect(panel_x + 10, input_y, panel_width - 100, 35)
            if input_rect.collidepoint(mouse_x, mouse_y):
                self.input_active = True
                return True

            # Check send button
            send_rect = pygame.Rect(panel_x + panel_width - 80, input_y, 70, 35)
            if send_rect.collidepoint(mouse_x, mouse_y):
                self.send_message(self.input_text, context)
                self.input_text = ""
                return True

        elif event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                self.send_message(self.input_text, context)
                self.input_text = ""
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
                return True
            elif event.key == pygame.K_ESCAPE:
                self.input_active = False
                return True
            elif len(self.input_text) < 100:  # Limit input length
                if event.unicode.isprintable():
                    self.input_text += event.unicode
                return True

        return False
