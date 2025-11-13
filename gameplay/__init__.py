"""Gameplay systems"""

# Lazy imports to avoid loading heavy dependencies during test collection

__all__ = [
    # Character Controller
    "CharacterController",
    "CharacterControllerSystem",
    "AIController",
    "AIControllerSystem",
    "MovementState",
    # Combat
    "Health",
    "CombatStats",
    "Weapon",
    "ActionPoints",
    "TeamComponent",
    "Team",
    "DamageType",
    "DamageInstance",
    "HealthSystem",
    "CombatSystem",
]


def __getattr__(name):
    """Lazy load gameplay modules"""
    if name in __all__:
        if name in [
            "CharacterController",
            "CharacterControllerSystem",
            "AIController",
            "AIControllerSystem",
            "MovementState",
        ]:
            from neonworks.gameplay.character_controller import (
                AIController,
                AIControllerSystem,
                CharacterController,
                CharacterControllerSystem,
                MovementState,
            )

            globals().update(
                {
                    "CharacterController": CharacterController,
                    "CharacterControllerSystem": CharacterControllerSystem,
                    "AIController": AIController,
                    "AIControllerSystem": AIControllerSystem,
                    "MovementState": MovementState,
                }
            )
        else:
            from neonworks.gameplay.combat import (
                ActionPoints,
                CombatStats,
                CombatSystem,
                DamageInstance,
                DamageType,
                Health,
                HealthSystem,
                Team,
                TeamComponent,
                Weapon,
            )

            globals().update(
                {
                    "Health": Health,
                    "CombatStats": CombatStats,
                    "Weapon": Weapon,
                    "ActionPoints": ActionPoints,
                    "TeamComponent": TeamComponent,
                    "Team": Team,
                    "DamageType": DamageType,
                    "DamageInstance": DamageInstance,
                    "HealthSystem": HealthSystem,
                    "CombatSystem": CombatSystem,
                }
            )
        return globals()[name]
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
