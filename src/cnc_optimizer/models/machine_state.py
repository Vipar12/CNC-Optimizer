"""Machine state and position models used across the parser and analyzer."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class MachinePosition:
    """Represents the current machine position in the active coordinate system."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)


@dataclass(slots=True)
class ModalState:
    """Current modal machine state as it evolves through the program."""

    absolute_positioning: bool = True
    units: str = "mm"
    plane: str = "XY"
    motion_mode: str = "G0"
    feed_mode: str = "G94"
    feed_rate: float | None = None
    spindle_speed: float | None = None
    spindle_state: str | None = None
    tool: int | None = None
    coolant_on: bool = False
    current_position: MachinePosition = field(default_factory=MachinePosition)
    work_offset: str = "G54"
    tool_change_pending: bool = False

    def copy(self) -> "ModalState":
        return ModalState(
            absolute_positioning=self.absolute_positioning,
            units=self.units,
            plane=self.plane,
            motion_mode=self.motion_mode,
            feed_mode=self.feed_mode,
            feed_rate=self.feed_rate,
            spindle_speed=self.spindle_speed,
            spindle_state=self.spindle_state,
            tool=self.tool,
            coolant_on=self.coolant_on,
            current_position=MachinePosition(self.current_position.x, self.current_position.y, self.current_position.z),
            work_offset=self.work_offset,
            tool_change_pending=self.tool_change_pending,
        )
