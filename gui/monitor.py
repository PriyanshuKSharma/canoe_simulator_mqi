import threading
import customtkinter as ctk
import can
from core.bus import bus_manager
from core.dbc import dbc_manager
from core.simulator import bms_simulator
from database.sqlite import get_db
from datetime import datetime

MAX_ROWS = 200


class MonitorPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._running = False
        self._thread = None
        self._row_count = 0
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(12, 4))
        ctk.CTkLabel(top, text="CAN Monitor", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        ctk.CTkButton(top, text="Clear", width=80, command=self._clear).pack(side="right", padx=4)
        self._stop_btn = ctk.CTkButton(top, text="Stop", width=80, command=self._stop, state="disabled")
        self._stop_btn.pack(side="right", padx=4)
        self._start_btn = ctk.CTkButton(top, text="Start", width=80, command=self._start)
        self._start_btn.pack(side="right", padx=4)

        # Simulator row
        sim_row = ctk.CTkFrame(self, fg_color="transparent")
        sim_row.pack(fill="x", padx=16, pady=(0, 4))
        self._sim_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            sim_row, text="Run BMS Simulator (virtual bus)",
            variable=self._sim_var, command=self._toggle_simulator,
        ).pack(side="left")
        self._sim_label = ctk.CTkLabel(sim_row, text="● Simulator OFF", text_color=("gray40", "gray60"))
        self._sim_label.pack(side="left", padx=12)

        # Status bar
        self._status = ctk.CTkLabel(
            self, text="Connect the bus in Settings, then press Start.",
            text_color=("gray40", "gray60"),
        )
        self._status.pack(anchor="w", padx=16)

        # Column header
        header = ctk.CTkFrame(self, fg_color=("gray80", "gray25"))
        header.pack(fill="x", padx=16, pady=(6, 0))
        for col, w in [("Time", 110), ("CAN ID", 80), ("DLC", 40), ("Data (hex)", 210), ("Decoded Signals", 0)]:
            ctk.CTkLabel(
                header, text=col, width=w, anchor="w",
                font=ctk.CTkFont(weight="bold"),
            ).pack(side="left", padx=6, pady=4)

        self._scroll = ctk.CTkScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True, padx=16, pady=(0, 8))

    # ------------------------------------------------------------------ #
    #  Start / Stop                                                        #
    # ------------------------------------------------------------------ #
    def _start(self):
        if not bus_manager.connected:
            self._status.configure(
                text="⚠  Bus not connected — go to Settings → Connect Bus first.",
                text_color="orange",
            )
            return
        self._running = True
        self._start_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")
        self._status.configure(text="● Receiving…", text_color="green")
        self._thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._thread.start()

    def _stop(self):
        self._running = False
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")
        self._status.configure(text="Stopped.", text_color=("gray40", "gray60"))

    def _clear(self):
        for w in self._scroll.winfo_children():
            w.destroy()
        self._row_count = 0

    # ------------------------------------------------------------------ #
    #  Simulator                                                           #
    # ------------------------------------------------------------------ #
    def _toggle_simulator(self):
        if self._sim_var.get():
            if not bus_manager.connected:
                self._status.configure(
                    text="⚠  Connect the bus before starting the simulator.",
                    text_color="orange",
                )
                self._sim_var.set(False)
                return
            bms_simulator.start()
            self._sim_label.configure(text="● Simulator ON", text_color="green")
        else:
            bms_simulator.stop()
            self._sim_label.configure(text="● Simulator OFF", text_color=("gray40", "gray60"))

    # ------------------------------------------------------------------ #
    #  Receive loop                                                        #
    # ------------------------------------------------------------------ #
    def _recv_loop(self):
        while self._running:
            msg = bus_manager.recv(timeout=0.5)
            if msg:
                self._log_to_db(msg)
                self.after(0, self._add_row, msg)

    def _log_to_db(self, msg: can.Message):
        db = get_db()
        db.execute(
            "INSERT INTO can_log (timestamp, can_id, dlc, data, channel) VALUES (?,?,?,?,?)",
            (
                datetime.utcnow().isoformat(),
                hex(msg.arbitration_id),
                msg.dlc,
                msg.data.hex(" ").upper(),
                bus_manager.channel,
            ),
        )
        db.commit()

    def _add_row(self, msg: can.Message):
        # Drop oldest row when cap reached
        if self._row_count >= MAX_ROWS:
            children = self._scroll.winfo_children()
            if children:
                children[0].destroy()

        decoded = dbc_manager.decode(msg.arbitration_id, bytes(msg.data))
        decoded_str = (
            "  ".join(
                f"{k}={v:.2f}" if isinstance(v, float) else f"{k}={v}"
                for k, v in decoded.items()
            )
            if decoded else ""
        )

        bg = ("gray86", "gray22") if self._row_count % 2 == 0 else ("gray92", "gray17")
        row = ctk.CTkFrame(self._scroll, fg_color=bg)
        row.pack(fill="x", pady=1)

        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        for text, width in [
            (ts, 110),
            (f"0x{msg.arbitration_id:03X}", 80),
            (str(msg.dlc), 40),
            (msg.data.hex(" ").upper(), 210),
            (decoded_str, 0),
        ]:
            ctk.CTkLabel(row, text=text, width=width, anchor="w").pack(side="left", padx=6, pady=2)

        self._row_count += 1
