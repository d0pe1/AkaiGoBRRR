import mido
from StateHandler import StateHandler


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


# def print_available_midi_connections():
#     """
#     Print out all available MIDI connections.
#     """
#     print("Available MIDI Input Ports:")
#     for port in mido.get_input_names():
#         print(port)
#
#     print("\nAvailable MIDI Output Ports:")
#     for port in mido.get_output_names():
#         print(port)
#

class MidiHandler:
    """Class for handling MIDI messages."""

    def __init__(self, cb1, cb2, name, mchannel):
        """
        Initialize MIDI handler.

        Args:
            name (str): Name of the input port.
            cb1 (function): Callback function for channel 1
            cb2 (function): Callback function for channel 2
        """
        self.ID = name
        self.cb1 = cb1
        self.cb2 = cb2
        self.channel = mchannel
        self.note_27_state = False  # Attribute to track the state of note 27
        self.sh = StateHandler()
        self.toggle_states = self.sh.default_toggle_states
        self.last_cc_values = self.sh.default_cc
        self.toggle_states, self.last_cc_values = self.sh.load_state(self.ID)

    def process_messages(self, message):
        """Process incoming MIDI messages."""
        try:
            print(self.ID, "Processing MIDI messages. Press Ctrl+C to exit.")
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
            print("BYE")

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
        self.sh.save_state(self.toggle_states, self.last_cc_values, self.ID)
        self.cb1(outbound)
        self.update_lights()

    def send_note_off_message(self, message):
        """Send note-off messages to the output port."""
        outbound = mido.Message('note_off', note=message.note, velocity=message.velocity, channel=self.channel)
        if message.note not in [25, 26, 27]:
            self.sh.save_state(self.toggle_states, self.last_cc_values, self.ID)
            print("Sent note:", outbound)
            self.cb1(outbound)

    def send_message(self, message):
        """Send other types of MIDI messages to the output port."""
        self.sh.save_state(self.toggle_states, self.last_cc_values, self.ID)
        self.cb1(message)

    def within_10(self, ccn, cco):
        """
        Check if two numbers are within 10 integers of each other.

        Args:
            ccn (int): New CC
            cco (int): Old CC

        Returns:
            bool: True if the numbers are within 10 integers of each other, False otherwise.
        """
        difference = abs(ccn - cco)
        if difference <= 10:
            print(f"{ccn} and {cco} are within 10 integers of each other.")
            return True
        else:
            print(f"{ccn} and {cco} are not within 10 integers of each other.")
            return False

    def send_control_change_message(self, message):
        """Send control change MIDI messages to the output port."""
        print("Sent control change:", message)
        if self.within_10(message.value, self.last_cc_values[message.control]):
            self.last_cc_values[message.control] = message.value
            self.sh.save_state(self.toggle_states, self.last_cc_values, self.ID)
            self.cb1(mido.Message('control_change', control=message.control, value=message.value, channel=self.channel))
        else:
            print("Not close enough to the Stored Value. Ignoring")

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
                    self.cb2(mido.Message('note_on', note=int(note_number), velocity=127))
                else:
                    self.cb2(mido.Message('note_on', note=int(note_number), velocity=127))
            else:
                if note_number in after_shift and self.note_27_state:
                    note_number -= 32
                    self.cb2(mido.Message('note_on', note=int(note_number), velocity=0))
                else:
                    self.cb2(mido.Message('note_on', note=int(note_number), velocity=0))

    def send_light_update(self, note_number):
        """Send light updates based on the toggle states."""
        if note_number in self.toggle_states:
            if self.toggle_states[note_number]:
                if note_number in after_shift:
                    note_number = note_number - 32
                    self.cb2(mido.Message('note_on', note=note_number, velocity=127))
                else:
                    self.cb2(mido.Message('note_on', note=note_number, velocity=127))

            elif not self.toggle_states[note_number]:
                if note_number in after_shift:
                    note_number = note_number - 32
                    self.cb2(mido.Message('note_on', note=note_number, velocity=0))
                else:
                    self.cb2(mido.Message('note_on', note=note_number, velocity=0))
