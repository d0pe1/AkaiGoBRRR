import mido

# Notes
notes = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27]

# Control Changes
control_changes = [
    16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
    26, 27, 28, 29, 30, 31, 46, 47, 48, 49,
    50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
    60, 61, 127]

# Shifted Notes
shifted_notes = [3, 6, 9, 12, 15, 18, 21, 24]

# Notes after shift
after_shift = [35, 38, 41, 44, 47, 50, 53, 56]

# Notes with no light
no_light = [25, 26, 27]

# Add shifted notes after offset to the notes list
notes.extend([note + 32 for note in shifted_notes])


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


class MidiHandler:
    """Class for handling MIDI messages."""

    def __init__(self, input_port_name, output_port_name, output_port_name_2, mchannel):
        """
        Initialize MIDI handler.

        Args:
            input_port_name (str): Name of the input port.
            output_port_name (str): Name of the output port.
            output_port_name_2 (str): Name of the second output port.
            mchannel (int): MIDI channel.
        """
        self.midi_masterator = None
        self.input_port_name = input_port_name
        self.output_port_name = output_port_name
        self.output_port_name_2 = output_port_name_2
        self.channel = mchannel
        self.input_port = None
        self.output_port = None
        self.output_port_2 = None
        self.note_27_state = False  # Attribute to track the state of note 27
        self.toggle_states = {
            1: False, 2: False, 3: False, 4: False,
            5: False, 6: False, 7: False, 8: False,
            9: False, 10: False, 11: False, 12: False,
            13: False, 14: False, 15: False, 16: False,
            17: False, 18: False, 19: False, 20: False,
            21: False, 22: False, 23: False, 24: False,
            35: False, 38: False, 41: False, 44: False,
            47: False, 53: False, 50: False, 56: False
        }  # Dictionary to store toggle states
        self.last_cc_values = {}  # Dictionary to store last sent control change values

    def open_ports(self):
        """
        Open input and output MIDI ports.

        Returns:
            bool: True if ports are successfully opened, False otherwise.
        """
        try:
            self.input_port = mido.open_input(self.input_port_name)
            self.output_port = mido.open_output(self.output_port_name)
            self.output_port_2 = mido.open_output(self.output_port_name_2)
        except OSError as e:
            print(f"Error: {e}")
            return False
        return True

    def close_ports(self):
        """Close input and output MIDI ports."""
        if self.input_port:
            self.input_port.close()
        elif self.output_port:
            self.output_port.close()
        elif self.output_port_2:
            self.output_port_2.close()

    def process_messages(self):
        """Process incoming MIDI messages."""
        try:
            print("Processing MIDI messages. Press Ctrl+C to exit.")
            for message in self.input_port:
                # Print the received message for all message types
                print("Received:", message)
                if message.type == 'control_change':
                    self.process_control_change_message(message)
                # Check if the received message is a special message
                elif message.note == 25 and message.type in ['note_on', 'note_off']:
                    self.handle_bank_up()
                elif message.note == 26 and message.type in ['note_on', 'note_off']:
                    self.handle_bank_down()
                elif message.note == 27 and message.type in ['note_on', 'note_off']:
                    self.handle_switch_button(message)
                # Process regular MIDI messages
                elif message.type == 'note_on':
                    self.process_note_message(message)
                elif message.type == 'note_off':
                    self.process_note_off_message(message)
                else:
                    # Send all other message types to the output port
                    self.send_message(message)

        except KeyboardInterrupt:
            print("Exiting...")
        except Exception as e:
            print(f"Error processing messages: {e}")
        finally:
            self.close_ports()

    def process_note_off_message(self, message):
        """
        Process note-off MIDI messages.

        Args:
            message (mido.Message): The MIDI message.
        """

        # Check if the note should be shifted and note 27 is on
        if message.note in shifted_notes and self.note_27_state:
            message.note = message.note + 32
            self.send_note_off_message(message)
        else:
            # Send note-off messages to the output port
            self.send_note_off_message(message)

    def process_note_message(self, message):
        """
        Process note MIDI messages.

        Args:
            message (mido.Message): The MIDI message.
        """
        # Send note messages to the output port
        if message.note not in [25, 26, 27]:
            if message.note in shifted_notes and self.note_27_state:
                message.note = message.note + 32
                self.send_note_message(message)
            else:
                self.send_note_message(message)

    def process_control_change_message(self, message):
        """
        Process control change MIDI messages.

        Args:
            message (mido.Message): The MIDI message.
        """
        # Send control change messages to the output port
        self.send_control_change_message(message)

    def handle_bank_up(self):
        """Placeholder for handling Bank Up functionality."""
        print("Received special message: Bank Up")

    def handle_bank_down(self):
        """Placeholder for handling Bank Down functionality."""
        print("Received special message: Bank Down")

    def handle_switch_button(self, message):
        """
        Handle the switch button MIDI message.

        Args:
            message (mido.Message): The MIDI message.
        """
        print("Received special message: Switch Button")

        # Toggle the state of note 27 based on the message type
        if message.type == 'note_on':
            self.note_27_state = True
            print("Switch Button is on")
            self.update_lights()  # Update lights
        else:  # message.type == 'note_off'
            self.note_27_state = False
            print("Switch Button is off")
            self.update_lights()

    def send_note_message(self, message):
        """Send note messages to the output port."""
        outbound = mido.Message('note_on', note=message.note, velocity=message.velocity, channel=self.channel)
        print("Sent note:", outbound)
        self.toggle_note_state(message.note)
        self.output_port.send(outbound)
        self.update_lights()

    def send_note_off_message(self, message):
        """Send note-off messages to the output port."""
        outbound = mido.Message('note_off', note=message.note, velocity=message.velocity, channel=self.channel)
        if message.note not in [25, 26, 27]:
            print("Sent note:", outbound)
            self.output_port.send(outbound)

    def send_message(self, message):
        """Send other types of MIDI messages to the output port."""
        self.output_port.send(message)

    def send_control_change_message(self, message):
        """Send control change MIDI messages to the output port."""
        print("Sent control change:", message)
        self.output_port.send(message)

    def toggle_note_state(self, note_number):
        """Toggle the state of the note with the given note number."""
        if note_number in self.toggle_states:
            self.toggle_states[note_number] = not self.toggle_states[note_number]
            state_message = "turned" if self.toggle_states[note_number] else "turned off"
            print(f"Note {note_number} is now {state_message}.")
            self.send_light_update(note_number)
        else:
            self.toggle_states[note_number] = True  # Default to True if note not found
            print(f"Note {note_number} is now turned on.")
            self.send_light_update(note_number)

    def update_lights(self):
        """Update lights based on the toggle states."""
        for note_number, state in self.toggle_states.items():
            if state:
                if note_number in after_shift and self.note_27_state:
                    note_number -= 32
                    self.output_port_2.send(mido.Message('note_on', note=note_number, velocity=127))
                else:
                    self.output_port_2.send(mido.Message('note_on', note=note_number, velocity=127))
            else:
                if note_number in after_shift and self.note_27_state:
                    note_number -= 32
                    self.output_port_2.send(mido.Message('note_on', note=note_number, velocity=0))
                else:
                    self.output_port_2.send(mido.Message('note_on', note=note_number, velocity=0))

    def send_light_update(self, note_number):
        """Send light updates based on the toggle states."""
        if note_number in self.toggle_states:
            if self.toggle_states[note_number]:
                if note_number in after_shift:
                    note_number = note_number - 32
                    self.output_port_2.send(mido.Message('note_on', note=note_number, velocity=127))
                else:
                    self.output_port_2.send(mido.Message('note_on', note=note_number, velocity=127))

            elif not self.toggle_states[note_number]:
                if note_number in after_shift:
                    note_number = note_number - 32
                    self.output_port_2.send(mido.Message('note_on', note=note_number, velocity=0))
                else:
                    self.output_port_2.send(mido.Message('note_on', note=note_number, velocity=0))


if __name__ == "__main__":
    # Print available MIDI connections
    print_available_midi_connections()

    # Specify input and output port names
    input_port_name = "MIDI Mix 5"
    output_port_name = "05. Internal MIDI 0"
    output_port_name_2 = "MIDI Mix 6"
    mchannel = 0

    # Create MidiHandler instance
    midi_handler = MidiHandler(input_port_name, output_port_name, output_port_name_2, mchannel)

    # Open ports
    if midi_handler.open_ports():
        # Process messages
        midi_handler.process_messages()

    # Close ports
    midi_handler.close_ports()