# MidiMasterator.py
import mido
from MidiHandler import MidiHandler as Bank
import tkinter as tk
import threading
from MasteratorGui import MasteratorGUI, BankSnapshot

def print_available_midi_connections():
    print("Available MIDI Input Ports:")
    for port in mido.get_input_names(): print(port)
    print("\nAvailable MIDI Output Ports:")
    for port in mido.get_output_names(): print(port)

class MidiMasterator:
    def __init__(self, input_port_name, output_port_name, output_port_name_2, root):
        self.input_port_name = input_port_name
        self.output_port_name = output_port_name
        self.output_port_name_2 = output_port_name_2
        self.input_port = None; self.output_port = None; self.output_port_2 = None
        self.bank_A = self.bank_B = self.bank_C = self.bank_D = None
        self.bankstate = 0  # 0=A .. 3=D

        self.gui = MasteratorGUI(root)
        self.gui.start_render_loop(fps=3)

    # MIDI outs from banks
    def receive_from_bank_1(self, message):
        print("To Output", message); self.output_port.send(message)
    def receive_from_bank_2(self, message):
        print("Lightswitch for:", getattr(message, "note", None)); self.output_port_2.send(message)

    def open_ports(self):
        try:
            self.input_port  = mido.open_input(self.input_port_name)
            self.output_port = mido.open_output(self.output_port_name)
            self.output_port_2 = mido.open_output(self.output_port_name_2)
            self.bank_A = Bank(self.receive_from_bank_1, self.receive_from_bank_2, mchannel=1, name="Bank A")
            self.bank_B = Bank(self.receive_from_bank_1, self.receive_from_bank_2, mchannel=2, name="Bank B")
            self.bank_C = Bank(self.receive_from_bank_1, self.receive_from_bank_2, mchannel=3, name="Bank C")
            self.bank_D = Bank(self.receive_from_bank_1, self.receive_from_bank_2, mchannel=4, name="Bank D")
            for b in (self.bank_A, self.bank_B, self.bank_C, self.bank_D):
                self._bind_bank_to_gui(b)
            self.bank_A.update_lights()
            self._publish_all_banks()
            self._push_active_snapshot()
        except OSError as e:
            print(f"Error: {e}"); return False
        return True

    def close_ports(self):
        for p in (self.input_port, self.output_port, self.output_port_2):
            try:
                if p: p.close()
            except: pass

    def process_midi_messages(self):
        try:
            while True:
                for message in self.input_port.iter_pending(): print("Pending:", message)
                for message in self.input_port:
                    print("Received:", message)
                    if message.type in ('note_on','note_off') and message.note in (25,26):
                        self._handle_bank_nav(message.note, message.type); continue
                    (self.bank_A, self.bank_B, self.bank_C, self.bank_D)[self.bankstate].process_messages(message)
        except Exception as e:
            print(f"Error processing messages: {e}")

    # --- bank nav + LEDs
    def _handle_bank_nav(self, note, typ):
        if typ != 'note_on': return
        self.bankstate = (self.bankstate - 1) % 4 if note == 26 else (self.bankstate + 1) % 4
        print(f"Bank state: {self.bankstate}")
        self._apply_bank_leds_and_update()

    def _apply_bank_leds_and_update(self):
        if self.bankstate == 0:
            self.output_port_2.send(mido.Message('note_on', note=25, velocity=0,   channel=0))
            self.output_port_2.send(mido.Message('note_on', note=26, velocity=0,   channel=0))
            self.bank_A.update_lights()
        elif self.bankstate == 1:
            self.output_port_2.send(mido.Message('note_on', note=25, velocity=0,   channel=0))
            self.output_port_2.send(mido.Message('note_on', note=26, velocity=127, channel=0))
            self.bank_B.update_lights()
        elif self.bankstate == 2:
            self.output_port_2.send(mido.Message('note_on', note=25, velocity=127, channel=0))
            self.output_port_2.send(mido.Message('note_on', note=26, velocity=0,   channel=0))
            self.bank_C.update_lights()
        else:
            self.output_port_2.send(mido.Message('note_on', note=25, velocity=127, channel=0))
            self.output_port_2.send(mido.Message('note_on', note=26, velocity=127, channel=0))
            self.bank_D.update_lights()
        self._push_active_snapshot()

    # --- GUI publishing
    def _bind_bank_to_gui(self, bank_obj):
        def wrap(method_name):
            if not hasattr(bank_obj, method_name): return
            orig = getattr(bank_obj, method_name)
            def wrapped(*args, **kwargs):
                r = orig(*args, **kwargs)
                self._publish_bank(bank_obj)              # micro cache always fresh
                if self._is_active_bank(bank_obj):        # detail if active
                    self._push_active_snapshot()
                return r
            setattr(bank_obj, method_name, wrapped)
        for m in ("update_lights", "send_control_change_message", "send_note_message"):
            wrap(m)

    def _publish_bank(self, bank_obj):
        idx = (0 if bank_obj is self.bank_A else
               1 if bank_obj is self.bank_B else
               2 if bank_obj is self.bank_C else 3)
        # normalize keys: JSON persisted as strings -> cast to int
        ts = {int(k): v for k, v in bank_obj.toggle_states.items()}
        cc = {int(k): v for k, v in bank_obj.last_cc_values.items()}
        snap = BankSnapshot(
            name=("Bank A","Bank B","Bank C","Bank D")[idx],
            toggle_states=ts, cc_values=cc,
            note27_on=getattr(bank_obj, "note_27_state", False),
            active_bank=idx
        )
        self.gui.set_bank_snapshot(snap)

    def _publish_all_banks(self):
        for b in (self.bank_A, self.bank_B, self.bank_C, self.bank_D):
            self._publish_bank(b)

    def _is_active_bank(self, b):
        return (self.bankstate == 0 and b is self.bank_A) or \
               (self.bankstate == 1 and b is self.bank_B) or \
               (self.bankstate == 2 and b is self.bank_C) or \
               (self.bankstate == 3 and b is self.bank_D)

    def _push_active_snapshot(self):
        b, idx = ((self.bank_A,0),(self.bank_B,1),(self.bank_C,2),(self.bank_D,3))[self.bankstate]
        ts = {int(k): v for k, v in b.toggle_states.items()}
        cc = {int(k): v for k, v in b.last_cc_values.items()}
        snap = BankSnapshot(
            name=("Bank A","Bank B","Bank C","Bank D")[idx],
            toggle_states=ts, cc_values=cc,
            note27_on=getattr(b,"note_27_state",False),
            active_bank=idx
        )
        self.gui.set_snapshot(snap)

# ---- entrypoint
if __name__ == "__main__":
    print_available_midi_connections()
    input_port_name   = "MIDI Mix 14"
    output_port_name  = "01. Internal MIDI 3"
    output_port_name_2 = "MIDI Mix 15"

    root = tk.Tk()
    mm = MidiMasterator(input_port_name, output_port_name, output_port_name_2, root)
    if mm.open_ports():
        threading.Thread(target=mm.process_midi_messages, daemon=True).start()
        root.mainloop()
    mm.close_ports()
