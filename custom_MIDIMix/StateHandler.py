import json


class StateHandler:
    def __init__(self):
        self.default_toggle_states = {
            1: False, 2: False, 3: False, 4: False,
            5: False, 6: False, 7: False, 8: False,
            9: False, 10: False, 11: False, 12: False,
            13: False, 14: False, 15: False, 16: False,
            17: False, 18: False, 19: False, 20: False,
            21: False, 22: False, 23: False, 24: False,
            35: False, 38: False, 41: False, 44: False,
            47: False, 53: False, 50: False, 56: False}
        self.default_cc = {
            16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0,
            26: 0, 27: 0, 28: 0, 29: 0, 30: 0, 31: 0, 46: 0, 47: 0, 48: 0, 49: 0,
            50: 0, 51: 0, 52: 0, 53: 0, 54: 0, 55: 0, 56: 0, 57: 0, 58: 0, 59: 0,
            60: 0, 61: 0, 127: 0
        }

    def save_state(self, toggle_states, cc_values, bid):
        # Create a dictionary to store the current state
        state = {
            # Convert toggle states to boolean values
            "toggle_states": {str(k): v for k, v in toggle_states.items()},
            # Convert CC values to integers
            "cc_values": {str(k): v for k, v in cc_values.items()}
        }

        # Save the state to a JSON file
        filename = bid + ".json"
        with open(filename, "w") as file:
            json.dump(state, file, indent=4)

        print(f"Debug: State saved to {filename}")

    def load_state(self, bid):
        filename = bid + ".json"
        try:
            # Attempt to load the state from the JSON file
            with open(filename, "r") as file:
                state = json.load(file)

            # Convert loaded data back to appropriate types
            toggle_states = {int(k): v for k, v in state["toggle_states"].items()}
            cc_values = {int(k): v for k, v in state["cc_values"].items()}

            print(f"Debug: State loaded from {filename}")
            print(f"Debug: Loaded toggle_states: {toggle_states}")
            print(f"Debug: Loaded cc_values: {cc_values}")
            print(self.default_toggle_states, self.default_cc)
            return toggle_states, cc_values

        except FileNotFoundError:
            print(f"Debug: State file {filename} not found. Initializing new state with default values.")
            self.save_state(self.default_toggle_states, self.default_cc, bid)
            print(f"Debug: Initialized toggle_states: {self.default_toggle_states}")
            print(f"Debug: Initialized cc_values: {self.default_cc}")
            return self.default_toggle_states.copy(), self.default_cc.copy()
        except json.JSONDecodeError:
            print(f"Debug: State file {filename} is corrupted. Initializing new state with default values.")
            self.save_state(self.default_toggle_states, self.default_cc, bid)
            print(f"Debug: Initialized toggle_states: {self.default_toggle_states}")
            print(f"Debug: Initialized cc_values: {self.default_cc}")
            return self.default_toggle_states.copy(), self.default_cc.copy()

