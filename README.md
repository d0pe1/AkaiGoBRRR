# AkaiGoBRRR
Akai Midi Mix Custom Midi Interface

Pretty much what it says on the cover :D

Was kind of let down by the Akai Midi Mixes premade Ableton mapping. 
So I scratched it and built my own.

This is a Mido based Python Script that hooks your Akai Midi Mix, gives you some fancy functionality and outputs the MIDI based on the magic within.

Functions:

Fully Lit, Statefull Buttons for both rows, the MUTE aswell as the REC ARM buttons.
Both Rows now shiftable by the SOLO Button. So instead of 24, you now have 32 possible buttons to go beastmode. The lights get updated when you hit the SOLO buttons also,
so you are alway reflecting the states of the Buttons you are currently controlling.
This means you push and release once, boom, light goes on, you push again, boom light goes of. This is to reflect how mapping buttons in most use cases has worked for me.

Banks. BANKS. So, this was the part where I was let down by the MIDI Mix's standard Ableton Mapping.
Even though you could move within Ableton with them, apart from moving the "Hardmapped" Trackselection in Ableton, these Buttons gave little to no benefit in about any other application.
So I changed this. Now the Bank Left, Bank Right button have a use. A pretty awesome one if you ask me. I have split possible outputs from the script into banks. Bank A, B, C, D
Everytime you fire up the script, you will by default be on Bank A. Now all the Input coming from the MIDI Mix will be routed through Bank A, which will save button toggle states (+ lighting ;) )
and will save the Last CC you output for each CC-Output possible by the device. Now to the awesome sauce. Every Bank has it's own stored, segregated Outputs. I've accomplished this by changing the
Channel each bank outputs like so

Bank A will forward to MIDI Channel index 1 (Usually referred to as Channel 2, because it's index 1 and index 0 is Channel 1)
Bank B will forward to MIDI Channel index 2
Bank C will forward to MIDI Channel index 3
Bank D will forward to MIDI Channel index 4

On top of this, the lights on the bank buttons will reflect the currently active Bank in the script like a binary dial. You know, how with 2 bit you can show 4 different states, the buttons do too. :)
If you are at Bank D and go further up, a black whole will open and swallow you and your family. 


Just kidding it just wraps around the list, so from D => A is possible as well as A => D. With a little bit of practise (and maybe upping your midi-binding organization game, lol),
you should be able to get used to this multiplied Output capability.

I've also included a (right now) pretty simple pickup mode for each Bank.
So that you don't get awefull jumps should you change bank and the physical control position is too far away from the stored last CC output.
Right now, all it does is, is check the new input against the old one. If they are within ten values of each other, the new input gains back 1 : 1 control of the output CC, if not,
new input is ignore.

To run this, you need Mido and Rtp_midi + Python > 3.7 and a text Editor (unless you have 1 to 1 the same exact setup as me, which i highly doubt.)
You also need a loopback midi device to rout this scripts output to. (loop be 30 for instance)
I've commented the points in the Script where you need to insert your midi ports. To help you do this, the first time you run this, it will list all possible midi port (I & O).

Hope you have fun. Do whatever with the code.

To Do:

- Maybe take in the MIDI Ports as User Input at the start / as arguments to enable you to run this without needing to "edit" the code.
- Refine the Pickup, so we have a push / pull situash kinda thing going once we are within 25 values of the stored value

Bugs:
- Due to the nature of rather "slow" updates from the MIDI Mix when outputting CC, sometimes if you use the CC Controls moving them too fast,
  the pickup Method will loose track and you'll be out of the 10 Value Range and lose control. To counteract this in the future, i will refine the pickup Method.

  Have fun, if you have questions to my code, just ask ChatGPT, you bum. :D
