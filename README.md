# MIDI **Masterator** for Akai MIDImix
_because Akai could’ve shipped this as “Banks & Brains.” they didn’t. so here you go._

Turns a stock **MIDImix** into a **4‑bank**, **LED‑truthy**, **state‑persisting** controller with a live GUI — **entirely DAW‑agnostic**.
No scripts, no remote API, no Ableton weirdness. The host only ever sees **plain MIDI notes/CCs** from a loopback port.

---

## What this rig *actually* is

- **Four banks (A–D)** on the physical **BANK LEFT / BANK RIGHT** buttons.
  - The two bank‑button LEDs are a **binary dial**:  
    **A = off/off**, **B = on/off**, **C = off/on**, **D = on/on**.
- **All buttons are stateful toggles** (on/off) **per bank**. Tap = switch. States persist to disk.
- **Shift semantics the panel should’ve had:**  
  - The hardware’s native **Mute shift** stays as‑is.  
  - The **Rec‑Arm row now has a proper shift layer too**: **shifted Rec‑Arm = base note + 32**.  
  - LEDs are mapped so the panel shows the truth of whatever layer you’re using.
- **Host sees only the notes you send.** There is **no DAW state feedback** by design. Bind your toggles to whatever in your DAW (mutes, arms, FX on/off, macros…) and forget about fragile integrations.
- **Hysteresis per CC per Bank.** CC “hysteresis” is used to stabilize **bank state recall** so flipping banks doesn’t spew jitter. It’s **not** about DAW preset pickup. Looking at you, broken Midi Pickup Modes in Ableton -.- (since Ableton 8 btw, took me 15 minutes to fix this.)
- **GUI**: detailed current‑bank view + 4‑bank micro overview so you can have the entire mixer at a glance when performing ;)

Use‑case: **live set / DJ mix companion**. Turn one MIDImix into four disciplined mini‑surfaces and make local DJs blush.

---

## Why this exists

Because “a lot of buttons” without **banks**, **LED truth**, and **state memory** is unfinished UX. This project wires the obvious:
real banks on the bank buttons, a binary LED dial, and dead‑simple **toggle notes via loopback** so you can bind anything in any DAW without ever writing a control script.
This is intended for Live use to make your DJ Pseudo Musician peer blush in anguish as they watch you pull of shit they couldn't even dream of on their scrawny little CDJs. (2k a pop for what? blinky MP3 Players? HELL NAW!)
Like, why are they even called that still, CDJ? 
![hayaaaaa](https://github.com/user-attachments/assets/112ff11b-3a47-4381-910e-b446f4cb1346)

---

## Repo layout

- `MidiMasterator.py` — orchestration: ports, 4 banks, bank‑LED dial, snapshots to GUI.
- `MidiHandler.py` — a single bank’s brain: note/CC routing, shift handling, LED updates, bank‑recall hysteresis, per‑bank state.
- `StateHandler.py` — JSON persistence (`Bank A.json` …).
- `MasteratorGui.py` — GUI (detail + micro views).
- `SoloMidiHandler.py` — minimal one‑bank runner (good for port sanity checks / headless use).

---

## REQUIRED: Program your MIDImix like this (in the Akai MIDImix Editor)

Yes, this mapping is **assumed** by the script. Change it in code *only* if you’re stubborn.

### CC map (incoming from device)
- **Knob Row 1**: `16, 20, 24, 28, 46, 50, 54, 58`  
- **Knob Row 2**: `17, 21, 25, 29, 47, 51, 55, 59`  
- **Knob Row 3**: `18, 22, 26, 30, 48, 52, 56, 60`  
- **Faders**: `19, 23, 27, 31, 49, 53, 57, 61`  
- **Master**: `127`

### Button notes (incoming from device)
- **Mute row (base layer)**: `1, 4, 7, 10, 13, 16, 19, 22`  
- **Solo row**: `2, 5, 8, 11, 14, 17, 20, 23`  
- **Rec‑Arm row (base layer)**: `3, 6, 9, 12, 15, 18, 21, 24`  
- **Rec‑Arm (shift layer)**: **base + 32** → `35, 38, 41, 44, 47, 50, 53, 56`  

### Bank buttons (use the physical “arrows”)
- **BANK RIGHT**: note `25`  
- **BANK LEFT**: note `26`  

### LED control
- Set **LEDs = External** in the editor.  
- The script sends **Note On vel=127 = LED on**, **vel=0 = off** on the MIDImix output port.

> Already have a personal map? Mirror your numbers into the constants in code or — radical idea — program the device once and go make music.

---

## Host / DAW routing (DAW‑agnostic by design)

- Create a **virtual loopback MIDI port** and point `output_port_name` to it. Examples:
  - **Windows:** loopMIDI → “Masterator OUT”
  - **macOS:** IAC Bus → “Masterator OUT”
  - **Linux:** ALSA virmidi → `VirMIDI 1-0`
- In your DAW, **MIDI‑learn** those **toggle notes** (from the loopback) to: track mutes, track arms, FX on/off, crossfader kills, macro punch‑ins… whatever.
- The DAW never sends state back. That’s intentional. Your surface is **the source of truth** during performance.

---

## Behavior, precisely

- **Banks** — Four handlers (A–D). Switch with **BANK LEFT/RIGHT**. LED pair = **2‑bit index**:
  - A: **off/off**, B: **on/off**, C: **off/on**, D: **on/on**.
- **Buttons = toggles** — Every button (Mute/Solo/Rec‑Arm) is **stateful** per bank and **persists** across sessions.
- **Shift** — Hardware’s Mute shift remains; **Rec‑Arm shift is added** as **base+32**. LEDs are remapped to display the active layer’s truth.
- **CCs & hysteresis** — CC values are stored per bank; **hysteresis stabilizes bank switching** so entering a bank won’t spew jitter. It’s **not** a DAW “preset pickup.”
- **Persistence** — `Bank X.json` stores `toggle_states` + `cc_values`. Delete to reset. Bad JSON? Auto‑defaults.

---

## Install

```bash
# Python 3.10+
pip install mido python-rtmidi
# Linux users may need:
# sudo apt-get install python3-tk
```

---

## Run

1) Plug in the MIDImix.  
2) In `MidiMasterator.py`, set your three port names:
   - `input_port_name`   → MIDImix input
   - `output_port_name`  → your **loopback** (“Masterator OUT”)
   - `output_port_name_2` → MIDImix **output** (for LEDs)
3) Go:
```bash
python MidiMasterator.py
```
GUI pops; bank A active; LED dial reads **off/off**.

---

## Live tips (actual stage workflow)

- **Banks with intent**: A = tracks, B = sends/returns, C = FX toggles, D = scene / emergency kills.  
- **Rec‑Arm shift layer**: use as “alt‑arm” or **momentary punch‑record** mapping.  
- **Loopback discipline**: reserve one loopback bus per rig to avoid cross‑project confusion.




## Troubleshooting

- **No LEDs** → `output_port_name_2` isn’t the MIDImix output or LEDs not set to External.  
- **DAW learns nothing** → You mapped to the device port instead of the **loopback**. Bind the DAW to the loopback.  
- **Buttons feel laggy** → Kill any DAW MIDI feedback/remote scripts you forgot about; this rig expects **one‑way** traffic.  
- **Bank LEDs wrong** → You remapped bank buttons in the editor; restore 25/26 notes.

---

## License

MIT. Ship sets, not proprietary pain.

---

If this spared you from buying three more controllers to fake banks, toss a ⭐.  
If you’re Akai and reading this: add banks + persistence in firmware and we’ll happily archive this with a thank‑you.
