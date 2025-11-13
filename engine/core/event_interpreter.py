"""
Event Command Interpreter

Sophisticated interpreter for executing event commands with flow control,
conditional branching, loops, and parallel execution support.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from neonworks.core.event_commands import (
    CommandType,
    EventCommand,
    EventContext,
    EventPage,
    GameEvent,
    GameState,
)
from neonworks.core.events import Event, EventManager, EventType

logger = logging.getLogger(__name__)


class InterpreterState(Enum):
    """State of the interpreter"""

    IDLE = 0
    RUNNING = 1
    WAITING = 2
    PAUSED = 3
    FINISHED = 4
    ERROR = 5


class CommandExecutionError(Exception):
    """Exception raised when command execution fails"""

    pass


@dataclass
class LoopFrame:
    """Stack frame for loop execution"""

    loop_start: int  # Command index where loop starts
    loop_end: int  # Command index where loop ends (closing bracket)
    current_indent: int  # Indentation level of loop


@dataclass
class BranchFrame:
    """Stack frame for branch execution"""

    branch_command_index: int  # Index of conditional branch command
    branch_result: bool  # Result of condition evaluation
    else_index: Optional[int] = None  # Index of else clause if exists
    end_index: Optional[int] = None  # Index where branch ends


@dataclass
class InterpreterInstance:
    """
    Individual interpreter instance for a running event.

    Manages execution state, flow control, and command processing
    for a single event context.
    """

    context: EventContext
    state: InterpreterState = InterpreterState.IDLE
    game_state: GameState = None

    # Flow control stacks
    loop_stack: List[LoopFrame] = field(default_factory=list)
    branch_stack: List[BranchFrame] = field(default_factory=list)

    # Wait management
    wait_frames: int = 0
    wait_for_message: bool = False
    wait_for_choice: bool = False
    wait_for_movement: bool = False

    # Label map for jumps (built on initialization)
    label_map: Dict[str, int] = field(default_factory=dict)

    # Error tracking
    last_error: Optional[str] = None
    error_command_index: Optional[int] = None

    # Callbacks
    on_show_text: Optional[Callable[[str, Dict[str, Any]], None]] = None
    on_show_choices: Optional[Callable[[List[str], int], int]] = None
    on_wait_complete: Optional[Callable[[], None]] = None

    def __post_init__(self):
        """Initialize label map after instance creation"""
        self._build_label_map()

    def _build_label_map(self):
        """Build map of labels to command indices"""
        self.label_map.clear()
        for i, cmd in enumerate(self.context.page.commands):
            if cmd.command_type == CommandType.LABEL:
                label_name = cmd.parameters.get("name", "")
                if label_name:
                    self.label_map[label_name] = i

    def is_finished(self) -> bool:
        """Check if interpreter has finished execution"""
        return (
            self.state == InterpreterState.FINISHED
            or self.state == InterpreterState.ERROR
            or self.context.is_finished()
        )

    def is_waiting(self) -> bool:
        """Check if interpreter is waiting"""
        return (
            self.state == InterpreterState.WAITING
            or self.wait_frames > 0
            or self.wait_for_message
            or self.wait_for_choice
            or self.wait_for_movement
        )


class EventInterpreter:
    """
    Main event interpreter that manages execution of event commands.

    Features:
    - Sequential command execution
    - Flow control (conditionals, loops, jumps)
    - Wait state management
    - Parallel event execution
    - Error handling and recovery
    """

    def __init__(
        self, game_state: GameState, event_manager: Optional[EventManager] = None
    ):
        """
        Initialize the event interpreter.

        Args:
            game_state: Reference to game state for variable/switch access
            event_manager: Optional event manager for emitting game events
        """
        self.game_state = game_state
        self.event_manager = event_manager

        # Active interpreters
        self.running_interpreters: Dict[int, InterpreterInstance] = {}
        self.parallel_interpreters: List[InterpreterInstance] = []

        # Statistics
        self.total_commands_executed = 0
        self.total_events_completed = 0

        # Callbacks
        self.on_event_start: Optional[Callable[[GameEvent, EventPage], None]] = None
        self.on_event_end: Optional[Callable[[GameEvent], None]] = None
        self.on_command_execute: Optional[
            Callable[[EventCommand, EventContext], None]
        ] = None
        self.on_error: Optional[Callable[[InterpreterInstance, str], None]] = None

    def start_event(
        self, event: GameEvent, page: EventPage, is_parallel: bool = False
    ) -> InterpreterInstance:
        """
        Start interpreting an event.

        Args:
            event: The game event to execute
            page: The active page to execute
            is_parallel: Whether this event runs in parallel

        Returns:
            InterpreterInstance managing the event execution
        """
        context = EventContext(event=event, page=page)
        instance = InterpreterInstance(
            context=context, state=InterpreterState.RUNNING, game_state=self.game_state
        )

        if is_parallel:
            self.parallel_interpreters.append(instance)
        else:
            self.running_interpreters[event.id] = instance

        logger.info(
            f"Started event {event.name} (ID: {event.id}, Parallel: {is_parallel})"
        )

        if self.on_event_start:
            self.on_event_start(event, page)

        return instance

    def stop_event(self, event_id: int):
        """
        Stop a running event.

        Args:
            event_id: ID of the event to stop
        """
        if event_id in self.running_interpreters:
            instance = self.running_interpreters[event_id]
            instance.state = InterpreterState.FINISHED
            del self.running_interpreters[event_id]

            if self.on_event_end:
                self.on_event_end(instance.context.event)

    def update(self, delta_time: float):
        """
        Update all running interpreters.

        Args:
            delta_time: Time elapsed since last update in seconds
        """
        # Update non-parallel events
        finished_ids = []
        for event_id, instance in self.running_interpreters.items():
            if self._update_instance(instance, delta_time):
                finished_ids.append(event_id)

        # Clean up finished events
        for event_id in finished_ids:
            self._finish_event(event_id)

        # Update parallel events
        finished_indices = []
        for i, instance in enumerate(self.parallel_interpreters):
            if self._update_instance(instance, delta_time):
                finished_indices.append(i)

        # Remove finished parallel events (reverse to maintain indices)
        for i in reversed(finished_indices):
            self.parallel_interpreters.pop(i)
            self.total_events_completed += 1

    def _update_instance(
        self, instance: InterpreterInstance, delta_time: float
    ) -> bool:
        """
        Update a single interpreter instance.

        Args:
            instance: The interpreter instance to update
            delta_time: Time elapsed since last update

        Returns:
            True if the instance has finished execution
        """
        # Handle wait states BEFORE checking if finished
        # (wait frames need to count down even if at end of command list)
        if instance.wait_frames > 0:
            instance.wait_frames -= 1
            if instance.wait_frames == 0:
                instance.state = InterpreterState.RUNNING
                if instance.on_wait_complete:
                    instance.on_wait_complete()
            return False

        if instance.is_finished():
            return True

        if (
            instance.wait_for_message
            or instance.wait_for_choice
            or instance.wait_for_movement
        ):
            # Waiting for external input/completion
            return False

        # Process commands (execute multiple per frame if not waiting)
        max_commands_per_frame = 100  # Prevent infinite loops
        commands_executed = 0

        while (
            commands_executed < max_commands_per_frame
            and instance.state == InterpreterState.RUNNING
            and not instance.is_finished()
            and not instance.is_waiting()
        ):
            try:
                if not self._execute_next_command(instance):
                    break
                commands_executed += 1
            except CommandExecutionError as e:
                self._handle_error(instance, str(e))
                return True  # Finish event on error

        # Don't mark as finished if we're waiting
        if instance.is_waiting():
            return False

        return instance.is_finished()

    def _execute_next_command(self, instance: InterpreterInstance) -> bool:
        """
        Execute the next command in the event.

        Args:
            instance: The interpreter instance

        Returns:
            True if a command was executed, False if should stop
        """
        command = instance.context.get_current_command()
        if not command:
            instance.state = InterpreterState.FINISHED
            return False

        # Check if we should skip this command due to branching
        if self._should_skip_command(instance, command):
            instance.context.advance()
            # Check for loop jump-back even when skipping commands
            self._check_loop_jump_back(instance)
            return True

        # Execute command based on type
        try:
            self._execute_command(instance, command)
            self.total_commands_executed += 1

            if self.on_command_execute:
                self.on_command_execute(command, instance.context)

            # Check if we've reached the end of a loop and need to jump back
            self._check_loop_jump_back(instance)

            return True
        except Exception as e:
            raise CommandExecutionError(
                f"Error executing command {command.command_type.name} "
                f"at index {instance.context.command_index}: {str(e)}"
            )

    def _check_loop_jump_back(self, instance: InterpreterInstance):
        """
        Check if we've reached the end of a loop and need to jump back.

        Args:
            instance: The interpreter instance
        """
        if instance.loop_stack:
            current_frame = instance.loop_stack[-1]
            # If we've moved past the loop end, jump back to the start
            if instance.context.command_index > current_frame.loop_end:
                instance.context.command_index = current_frame.loop_start + 1

    def _should_skip_command(
        self, instance: InterpreterInstance, command: EventCommand
    ) -> bool:
        """
        Determine if a command should be skipped based on branching logic.

        Args:
            instance: The interpreter instance
            command: The command to check

        Returns:
            True if command should be skipped
        """
        if not instance.branch_stack:
            return False

        current_frame = instance.branch_stack[-1]
        current_index = instance.context.command_index

        # If we're inside a branch
        if current_frame.branch_command_index < current_index:
            # Check if we should skip based on indent level
            if command.indent > 0:
                # We're in a nested section
                # Skip if we're in the wrong branch
                if not current_frame.branch_result and current_frame.else_index is None:
                    return True
                if (
                    not current_frame.branch_result
                    and current_frame.else_index is not None
                ):
                    # Skip if before else
                    if current_index < current_frame.else_index:
                        return True
                if current_frame.branch_result and current_frame.else_index is not None:
                    # Skip if after else
                    if current_index >= current_frame.else_index:
                        return True

        return False

    def _execute_command(self, instance: InterpreterInstance, command: EventCommand):
        """
        Execute a single command.

        Args:
            instance: The interpreter instance
            command: The command to execute
        """
        cmd_type = command.command_type

        # Flow control commands
        if cmd_type == CommandType.CONDITIONAL_BRANCH:
            self._execute_conditional_branch(instance, command)
        elif cmd_type == CommandType.LOOP:
            self._execute_loop_start(instance, command)
        elif cmd_type == CommandType.BREAK_LOOP:
            self._execute_break_loop(instance, command)
        elif cmd_type == CommandType.EXIT_EVENT:
            self._execute_exit_event(instance, command)
        elif cmd_type == CommandType.LABEL:
            self._execute_label(instance, command)
        elif cmd_type == CommandType.JUMP_TO_LABEL:
            self._execute_jump_to_label(instance, command)
        elif cmd_type == CommandType.COMMENT:
            instance.context.advance()

        # Wait commands
        elif cmd_type == CommandType.WAIT:
            self._execute_wait(instance, command)

        # Message commands
        elif cmd_type == CommandType.SHOW_TEXT:
            self._execute_show_text(instance, command)
        elif cmd_type == CommandType.SHOW_CHOICES:
            self._execute_show_choices(instance, command)

        # Game state commands
        elif cmd_type == CommandType.CONTROL_SWITCHES:
            self._execute_control_switches(instance, command)
        elif cmd_type == CommandType.CONTROL_VARIABLES:
            self._execute_control_variables(instance, command)
        elif cmd_type == CommandType.CONTROL_SELF_SWITCH:
            self._execute_control_self_switch(instance, command)

        # Audio commands
        elif cmd_type == CommandType.PLAY_BGM:
            self._execute_play_bgm(instance, command)
        elif cmd_type == CommandType.PLAY_SE:
            self._execute_play_se(instance, command)
        elif cmd_type == CommandType.FADEOUT_BGM:
            self._execute_fadeout_bgm(instance, command)

        # Transfer commands
        elif cmd_type == CommandType.TRANSFER_PLAYER:
            self._execute_transfer_player(instance, command)

        # Script commands
        elif cmd_type == CommandType.SCRIPT:
            self._execute_script(instance, command)

        # Default: just advance
        else:
            logger.warning(f"Unimplemented command type: {cmd_type.name}")
            instance.context.advance()

    # ========== Flow Control Implementation ==========

    def _execute_conditional_branch(
        self, instance: InterpreterInstance, command: EventCommand
    ):
        """Execute conditional branch command"""
        condition_type = command.parameters.get("condition_type")
        result = self._evaluate_condition(instance, command.parameters)

        # Find the else and end indices
        else_index, end_index = self._find_branch_indices(
            instance.context.page.commands,
            instance.context.command_index,
            command.indent,
        )

        # Create branch frame
        frame = BranchFrame(
            branch_command_index=instance.context.command_index,
            branch_result=result,
            else_index=else_index,
            end_index=end_index,
        )
        instance.branch_stack.append(frame)

        # Advance to appropriate section
        if result:
            # Execute if branch
            instance.context.advance()
        elif else_index is not None:
            # Jump to else branch
            instance.context.command_index = else_index + 1
        elif end_index is not None:
            # Skip entire branch
            instance.context.command_index = end_index + 1
        else:
            # No else, skip to next command at same or lower indent
            instance.context.advance()

    def _evaluate_condition(
        self, instance: InterpreterInstance, params: Dict[str, Any]
    ) -> bool:
        """
        Evaluate a condition from a conditional branch.

        Args:
            instance: The interpreter instance
            params: Condition parameters

        Returns:
            True if condition is met
        """
        condition_type = params.get("condition_type")

        if condition_type == "switch":
            switch_id = params.get("switch_id", 1)
            expected = params.get("value", True)
            actual = self.game_state.get_switch(switch_id)
            return actual == expected

        elif condition_type == "variable":
            var_id = params.get("variable_id", 1)
            operator = params.get("operator", "==")
            value = params.get("value", 0)
            var_value = self.game_state.get_variable(var_id)

            return self._compare_values(var_value, operator, value)

        elif condition_type == "self_switch":
            # Self switches are per-event
            switch_ch = params.get("switch_ch", "A")
            expected = params.get("value", True)
            # Would need to implement self-switch storage
            return expected

        elif condition_type == "script":
            # Evaluate custom script
            script = params.get("script", "True")
            try:
                return bool(eval(script, {"game_state": self.game_state}))
            except Exception as e:
                logger.error(f"Script evaluation error: {e}")
                return False

        return False

    def _compare_values(self, left: Any, operator: str, right: Any) -> bool:
        """Compare two values using an operator"""
        if operator == "==":
            return left == right
        elif operator == "!=":
            return left != right
        elif operator == ">":
            return left > right
        elif operator == ">=":
            return left >= right
        elif operator == "<":
            return left < right
        elif operator == "<=":
            return left <= right
        return False

    def _find_branch_indices(
        self, commands: List[EventCommand], branch_start: int, branch_indent: int
    ) -> tuple[Optional[int], Optional[int]]:
        """
        Find the else and end indices for a conditional branch.

        Args:
            commands: List of all commands
            branch_start: Index of the conditional branch command
            branch_indent: Indent level of the branch

        Returns:
            Tuple of (else_index, end_index)
        """
        else_index = None
        end_index = None

        # Scan forward to find else/end at same indent level
        for i in range(branch_start + 1, len(commands)):
            cmd = commands[i]

            # Found a command at same or lower indent level
            if cmd.indent <= branch_indent:
                # Check if it's an else
                if (
                    cmd.command_type == CommandType.COMMENT
                    and cmd.parameters.get("text", "").strip().lower() == "else"
                    and cmd.indent == branch_indent + 1
                ):
                    else_index = i
                    continue

                # End of branch
                if cmd.indent == branch_indent:
                    end_index = i - 1
                    break

        return else_index, end_index

    def _execute_loop_start(self, instance: InterpreterInstance, command: EventCommand):
        """Execute loop start command"""
        # Find loop end
        loop_end = self._find_loop_end(
            instance.context.page.commands,
            instance.context.command_index,
            command.indent,
        )

        frame = LoopFrame(
            loop_start=instance.context.command_index,
            loop_end=loop_end,
            current_indent=command.indent,
        )
        instance.loop_stack.append(frame)
        instance.context.advance()

    def _find_loop_end(
        self, commands: List[EventCommand], loop_start: int, loop_indent: int
    ) -> int:
        """Find the end index of a loop"""
        depth = 1
        for i in range(loop_start + 1, len(commands)):
            cmd = commands[i]
            if cmd.command_type == CommandType.LOOP and cmd.indent >= loop_indent:
                depth += 1
            elif cmd.indent <= loop_indent:
                depth -= 1
                if depth == 0:
                    return i
        return len(commands) - 1

    def _execute_break_loop(self, instance: InterpreterInstance, command: EventCommand):
        """Execute break loop command"""
        if not instance.loop_stack:
            logger.warning("Break loop called outside of loop")
            instance.context.advance()
            return

        frame = instance.loop_stack.pop()
        # Jump to after loop end
        instance.context.command_index = frame.loop_end + 1

    def _execute_exit_event(self, instance: InterpreterInstance, command: EventCommand):
        """Execute exit event command"""
        instance.state = InterpreterState.FINISHED
        instance.context.command_index = len(instance.context.page.commands)

    def _execute_label(self, instance: InterpreterInstance, command: EventCommand):
        """Execute label command (just advance)"""
        instance.context.advance()

    def _execute_jump_to_label(
        self, instance: InterpreterInstance, command: EventCommand
    ):
        """Execute jump to label command"""
        label_name = command.parameters.get("label", "")
        if label_name in instance.label_map:
            instance.context.command_index = instance.label_map[label_name]
        else:
            logger.error(f"Label not found: {label_name}")
            instance.context.advance()

    # ========== Wait Commands ==========

    def _execute_wait(self, instance: InterpreterInstance, command: EventCommand):
        """Execute wait command"""
        duration = command.parameters.get("duration", 60)
        instance.wait_frames = duration
        instance.state = InterpreterState.WAITING
        instance.context.advance()

    # ========== Message Commands ==========

    def _execute_show_text(self, instance: InterpreterInstance, command: EventCommand):
        """Execute show text command"""
        text = command.parameters.get("text", "")

        if instance.on_show_text:
            instance.on_show_text(text, command.parameters)

        # Wait for message to be dismissed
        instance.wait_for_message = True
        instance.context.advance()

        # Emit event if event manager available
        if self.event_manager:
            self.event_manager.emit(
                Event(
                    event_type=EventType.UI_TEXT_DISPLAYED,
                    data={"text": text, "event_id": instance.context.event.id},
                )
            )

    def _execute_show_choices(
        self, instance: InterpreterInstance, command: EventCommand
    ):
        """Execute show choices command"""
        choices = command.parameters.get("choices", [])
        default = command.parameters.get("default_choice", 0)

        if instance.on_show_choices:
            # Callback should return the selected choice index
            choice_index = instance.on_show_choices(choices, default)
            instance.context.branch_result = choice_index

        instance.wait_for_choice = True
        instance.context.advance()

    # ========== Game State Commands ==========

    def _execute_control_switches(
        self, instance: InterpreterInstance, command: EventCommand
    ):
        """Execute control switches command"""
        switch_id = command.parameters.get("switch_id", 1)
        value = command.parameters.get("value", True)
        end_id = command.parameters.get("end_id")

        if end_id:
            for sid in range(switch_id, end_id + 1):
                self.game_state.set_switch(sid, value)
        else:
            self.game_state.set_switch(switch_id, value)

        instance.context.advance()

    def _execute_control_variables(
        self, instance: InterpreterInstance, command: EventCommand
    ):
        """Execute control variables command"""
        var_id = command.parameters.get("variable_id", 1)
        operation = command.parameters.get("operation", "set")
        operand_type = command.parameters.get("operand_type", "constant")
        operand_value = command.parameters.get("operand_value", 0)
        end_id = command.parameters.get("end_id")

        # Get operand value
        if operand_type == "variable":
            operand_value = self.game_state.get_variable(operand_value)
        elif operand_type == "random":
            import random

            min_val, max_val = operand_value
            operand_value = random.randint(min_val, max_val)

        # Apply operation
        var_ids = range(var_id, end_id + 1) if end_id else [var_id]
        for vid in var_ids:
            current = self.game_state.get_variable(vid)

            if operation == "set":
                new_value = operand_value
            elif operation == "add":
                new_value = current + operand_value
            elif operation == "sub":
                new_value = current - operand_value
            elif operation == "mul":
                new_value = current * operand_value
            elif operation == "div":
                new_value = current // operand_value if operand_value != 0 else current
            elif operation == "mod":
                new_value = current % operand_value if operand_value != 0 else current
            else:
                new_value = operand_value

            self.game_state.set_variable(vid, new_value)

        instance.context.advance()

    def _execute_control_self_switch(
        self, instance: InterpreterInstance, command: EventCommand
    ):
        """Execute control self switch command"""
        # Self switches would be stored per-event
        # Implementation depends on game state structure
        instance.context.advance()

    # ========== Audio Commands ==========

    def _execute_play_bgm(self, instance: InterpreterInstance, command: EventCommand):
        """Execute play BGM command"""
        if self.event_manager:
            self.event_manager.emit(
                Event(event_type=EventType.AUDIO_BGM_PLAY, data=command.parameters)
            )
        instance.context.advance()

    def _execute_play_se(self, instance: InterpreterInstance, command: EventCommand):
        """Execute play SE command"""
        if self.event_manager:
            self.event_manager.emit(
                Event(event_type=EventType.AUDIO_SE_PLAY, data=command.parameters)
            )
        instance.context.advance()

    def _execute_fadeout_bgm(
        self, instance: InterpreterInstance, command: EventCommand
    ):
        """Execute fadeout BGM command"""
        if self.event_manager:
            self.event_manager.emit(
                Event(event_type=EventType.AUDIO_BGM_FADEOUT, data=command.parameters)
            )
        instance.context.advance()

    # ========== Transfer Commands ==========

    def _execute_transfer_player(
        self, instance: InterpreterInstance, command: EventCommand
    ):
        """Execute transfer player command"""
        if self.event_manager:
            self.event_manager.emit(
                Event(event_type=EventType.PLAYER_TRANSFER, data=command.parameters)
            )
        instance.context.advance()

    # ========== Script Commands ==========

    def _execute_script(self, instance: InterpreterInstance, command: EventCommand):
        """Execute custom script command"""
        script = command.parameters.get("script", "")
        try:
            # Provide safe execution context
            context = {
                "game_state": self.game_state,
                "event": instance.context.event,
                "context": instance.context,
            }
            exec(script, context)
            instance.context.advance()
        except Exception as e:
            logger.error(f"Script execution error: {e}")
            instance.context.advance()
            # Re-raise to trigger error handling
            raise

    # ========== Error Handling ==========

    def _handle_error(self, instance: InterpreterInstance, error_msg: str):
        """
        Handle an error during command execution.

        Args:
            instance: The interpreter instance with the error
            error_msg: Error message
        """
        instance.state = InterpreterState.ERROR
        instance.last_error = error_msg
        instance.error_command_index = instance.context.command_index

        logger.error(
            f"Event {instance.context.event.name} (ID: {instance.context.event.id}) "
            f"error at command {instance.context.command_index}: {error_msg}"
        )

        if self.on_error:
            self.on_error(instance, error_msg)

    def _finish_event(self, event_id: int):
        """Clean up a finished event"""
        if event_id in self.running_interpreters:
            instance = self.running_interpreters[event_id]
            del self.running_interpreters[event_id]

            self.total_events_completed += 1

            if self.on_event_end:
                self.on_event_end(instance.context.event)

    # ========== Public API ==========

    def is_event_running(self, event_id: int) -> bool:
        """Check if an event is currently running"""
        return event_id in self.running_interpreters

    def has_blocking_event(self) -> bool:
        """Check if there's a blocking (non-parallel) event running"""
        return len(self.running_interpreters) > 0

    def clear_all_events(self):
        """Stop all running events"""
        self.running_interpreters.clear()
        self.parallel_interpreters.clear()

    def resume_message(self, event_id: int):
        """Resume event after message display"""
        if event_id in self.running_interpreters:
            instance = self.running_interpreters[event_id]
            instance.wait_for_message = False
            instance.state = InterpreterState.RUNNING

    def resume_choice(self, event_id: int, choice_index: int):
        """Resume event after choice selection"""
        if event_id in self.running_interpreters:
            instance = self.running_interpreters[event_id]
            instance.wait_for_choice = False
            instance.context.branch_result = choice_index
            instance.state = InterpreterState.RUNNING

    def resume_movement(self, event_id: int):
        """Resume event after movement completion"""
        if event_id in self.running_interpreters:
            instance = self.running_interpreters[event_id]
            instance.wait_for_movement = False
            instance.state = InterpreterState.RUNNING

    def get_statistics(self) -> Dict[str, Any]:
        """Get interpreter statistics"""
        return {
            "running_events": len(self.running_interpreters),
            "parallel_events": len(self.parallel_interpreters),
            "total_commands_executed": self.total_commands_executed,
            "total_events_completed": self.total_events_completed,
        }
