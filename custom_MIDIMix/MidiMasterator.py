import mido
from MidiHandler import MidiHandler as Bank
import time


def print_available_midi_connections():
    """
    Print out all available MIDI connections.
    """
    print("Available MIDI Input Ports:")
    for port in mido.get_input_names():
        print(port)

    print("\nAvailable MIDI Output Ports:")
    for port in mido.get_output_names():
        print(port)


class MidiMasterator:
    def __init__(self, input_port_name, output_port_name, output_port_name_2):
        self.input_port_name = input_port_name
        self.output_port_name = output_port_name
        self.output_port_name_2 = output_port_name_2
        self.input_port = None
        self.output_port = None
        self.output_port_2 = None
        self.bank_A = None
        self.bank_B = None
        self.bank_C = None
        self.bank_D = None
        self.bankstate = 0


    def receive_from_bank_1(self, message):
        print("To Output", message)
        # Process the message as needed
        self.output_port.send(message)

    def receive_from_bank_2(self, message):
        print("Lightswitch for:", message.note)
        # Process the message as needed
        self.output_port_2.send(message)

    def open_ports(self):
        try:
            self.input_port = mido.open_input(self.input_port_name)
            self.output_port = mido.open_output(self.output_port_name)
            self.output_port_2 = mido.open_output(self.output_port_name_2)

            # Initialize banks with appropriate input callbacks
            self.bank_A = Bank(self.receive_from_bank_1, self.receive_from_bank_2, mchannel=1, name="Bank A")
            self.bank_B = Bank(self.receive_from_bank_1, self.receive_from_bank_2, mchannel=2, name="Bank B")
            self.bank_C = Bank(self.receive_from_bank_1, self.receive_from_bank_2, mchannel=3, name="Bank C")
            self.bank_D = Bank(self.receive_from_bank_1, self.receive_from_bank_2, mchannel=4, name="Bank D")

        except OSError as e:
            print(f"Error: {e}")
            return False
        return True

    def close_ports(self):
        if self.input_port:
            self.input_port.close()
        if self.output_port:
            self.output_port.close()
        if self.output_port_2:
            self.output_port_2.close()

    def process_messages(self):
        try:
            print("Processing MIDI messages. Press Ctrl+C to exit.")

            while True:
                # Check for any pending messages
                for message in self.input_port.iter_pending():
                    print("Pending:", message)
                    # Process the pending message if needed

                # Process incoming messages
                for message in self.input_port:
                    print("Received:", message)
                    # Process the received message

                    if message.type in ['note_on', 'note_off'] and message.note in [25, 26]:
                        self.toggle_state(message.note, message.type)

                    elif self.bankstate == 0:
                        self.bank_A.process_messages(message)
                    elif self.bankstate == 1:
                        self.bank_B.process_messages(message)
                    elif self.bankstate == 2:
                        self.bank_C.process_messages(message)
                    elif self.bankstate == 3:
                        self.bank_D.process_messages(message)
                    else:
                        # Send all other message types to the output port
                        pass

        except KeyboardInterrupt:
            print("Exiting...")
        except Exception as e:
            print(f"Error processing messages: {e}")

    def toggle_state(self, note, type):
        if note == 26 and type == 'note_on':
            if self.bankstate > 0:
                self.bankstate -= 1
                self.send_state_messages()
                print(f"Bank state: {self.bankstate}")
            else:
                self.bankstate = 3
                self.send_state_messages()
                print(f"Bank state: {self.bankstate}")
        elif note == 25 and type == 'note_on':
            if self.bankstate < 3:
                self.bankstate += 1
                self.send_state_messages()
                print(f"Bank state: {self.bankstate}")
            else:
                self.bankstate = 0
                self.send_state_messages()
                print(f"Bank state: {self.bankstate}")
        else:
            self.send_state_messages()
            print(f"Bank state: {self.bankstate}")

    def send_state_messages(self):
        if self.bankstate == 0:
            self.output_port_2.send(mido.Message('note_on', note=25, velocity=0, channel=0))
            self.output_port_2.send(mido.Message('note_on', note=26, velocity=0, channel=0))
            self.bank_A.update_lights()
        if self.bankstate == 1:
            self.output_port_2.send(mido.Message('note_on', note=25, velocity=0, channel=0))
            self.output_port_2.send(mido.Message('note_on', note=26, velocity=127, channel=0))
            self.bank_B.update_lights()
        if self.bankstate == 2:
            self.output_port_2.send(mido.Message('note_on', note=25, velocity=127, channel=0))
            self.output_port_2.send(mido.Message('note_on', note=26, velocity=0, channel=0))
            self.bank_C.update_lights()
        if self.bankstate == 3:
            self.output_port_2.send(mido.Message('note_on', note=25, velocity=127, channel=0))
            self.output_port_2.send(mido.Message('note_on', note=26, velocity=127, channel=0))
            self.bank_D.update_lights()


if __name__ == "__main__":
    print_available_midi_connections()

    input_port_name = "MIDI Mix 5" # This should be the Output Port of your MIDI Mix
    output_port_name = "05. Internal MIDI 0" # This should be a Virtual Midi Loopback device i.e. Loop Be 30 or similar
    output_port_name_2 = "MIDI Mix 6" # This should be the Input Port of your MIDI Mix

    midi_masterator = MidiMasterator(input_port_name, output_port_name, output_port_name_2)
    print(midi_masterator.output_port)
    print(midi_masterator.output_port_2)
    if midi_masterator.open_ports():
        midi_masterator.process_messages()

    midi_masterator.close_ports()
