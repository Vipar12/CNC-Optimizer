"""Modal state tracking helpers for G-code parsing."""

from __future__ import annotations

from cnc_optimizer.models.machine_state import MachinePosition, ModalState


class ModalStateTracker:
    """Maintains the active machine-modal state while the parser walks a program."""

    def __init__(self) -> None:
        self.state = ModalState()

    def apply_value(self, letter: str, value: float | int | str | None) -> None:
        if value is None:
            return

        code = float(value)
        letter_upper = letter.upper()

        if letter_upper == "F":
            self.state.feed_rate = code
        elif letter_upper == "S":
            self.state.spindle_speed = code
        elif letter_upper == "T":
            self.state.tool = int(code)
        elif letter_upper == "G":
            g_code = int(code)
            if g_code == 17:
                self.state.plane = "XY"
            elif g_code == 18:
                self.state.plane = "XZ"
            elif g_code == 19:
                self.state.plane = "YZ"
            elif g_code == 20:
                self.state.units = "in"
            elif g_code == 21:
                self.state.units = "mm"
            elif g_code == 90:
                self.state.absolute_positioning = True
            elif g_code == 91:
                self.state.absolute_positioning = False
            elif g_code in {0, 1, 2, 3}:
                self.state.motion_mode = f"G{g_code}"
            elif g_code == 40:
                self.state.motion_mode = "G40"
            elif g_code in {41, 42}:
                self.state.motion_mode = f"G{g_code}"
            elif g_code in {43, 49}:
                self.state.motion_mode = f"G{g_code}"
            elif g_code in {54, 55, 56, 57, 58, 59}:
                self.state.work_offset = f"G{g_code}"
            elif g_code == 94:
                self.state.feed_mode = "G94"
            elif g_code == 95:
                self.state.feed_mode = "G95"
        elif letter_upper == "M":
            m_code = int(code)
            if m_code == 3:
                self.state.spindle_state = "CW"
            elif m_code == 4:
                self.state.spindle_state = "CCW"
            elif m_code == 5:
                self.state.spindle_state = "OFF"
            elif m_code == 8:
                self.state.coolant_on = True
            elif m_code == 9:
                self.state.coolant_on = False
            elif m_code == 6:
                self.state.tool_change_pending = True

    def update_position(self, values: dict[str, float | int | str | None]) -> MachinePosition:
        x_value = values.get("X")
        y_value = values.get("Y")
        z_value = values.get("Z")

        current = self.state.current_position
        next_x = current.x if x_value is None else float(x_value)
        next_y = current.y if y_value is None else float(y_value)
        next_z = current.z if z_value is None else float(z_value)

        if not self.state.absolute_positioning:
            next_x = current.x + (0.0 if x_value is None else float(x_value))
            next_y = current.y + (0.0 if y_value is None else float(y_value))
            next_z = current.z + (0.0 if z_value is None else float(z_value))

        updated = MachinePosition(x=next_x, y=next_y, z=next_z)
        self.state.current_position = updated
        return updated

    def current_motion_code(self) -> int:
        mode = self.state.motion_mode
        if mode in {"G0", "G1", "G2", "G3"}:
            return int(mode[1:])
        return 1
