# AkaiGoBRRR - Akai Midi Mix Custom MIDI Interface

## Overview:
This Python script, based on Mido, enhances the functionality of your Akai Midi Mix MIDI controller by providing custom mappings. It offers features like fully lit, stateful buttons for both rows, shiftable rows using the SOLO button, and bank functionality. The script organizes MIDI inputs and outputs into separate banks (A, B, C, D), each with its own stored toggle states and control change (CC) outputs. Additionally, it includes a pickup mode to prevent abrupt jumps when switching banks.

## Features:
- **Fully Lit, Stateful Buttons:** Buttons reflect their states through lighting, providing intuitive feedback.
- **Shiftable Rows:** Rows can be shifted using the SOLO button, providing access to additional buttons for enhanced control.
- **Bank Functionality:** Utilizes the Bank Left and Bank Right buttons to switch between four separate banks (A, B, C, D), each with its own set of toggle states and CC outputs.
- **Channel Segregation:** Each bank outputs MIDI messages on a different MIDI channel, enhancing organization and control.
- **Binary Dial Indicator:** The bank buttons visually indicate the active bank, making it easy to track.
- **Wraparound Feature:** Switching between banks wraps around the bank list, allowing seamless navigation.
- **Pickup Mode:** Prevents sudden jumps in control positions when switching banks by comparing new inputs with the last stored CC outputs.

## Requirements:
- Mido and Rtp_midi
- Python version > 3.7
- Text Editor
- Loopback MIDI device (e.g., loopbe30)

## Setup:
1. Install Mido, Rtp_midi, and ensure Python version > 3.7.
2. Connect your Akai Midi Mix MIDI controller and set up a loopback MIDI device.
3. Update the script with your MIDI ports. (Refer to comments in the script)
4. Run the script by running MidiMasterator.py in terminal.
5. On the run, it will list all available MIDI ports (input and output) should you have trouble finding the proper ports.
6. Enjoy enhanced control and customization with your Akai Midi Mix!

## To Do:
- Implement user input for MIDI ports to make setup more convenient.
- Refine the pickup mode to allow for smoother control adjustments.

## Known Bugs:
- Occasional loss of control due to slow updates from the MIDI Mix when outputting CC moving the cc out of the pickup range controls. This will be addressed in future updates by refining the pickup mode.

Feel free to modify and improve the code according to your needs. If you have any questions, don't hesitate to ask ChatGPT!

**Note:** The provided information is directly from the creator's documentation.

