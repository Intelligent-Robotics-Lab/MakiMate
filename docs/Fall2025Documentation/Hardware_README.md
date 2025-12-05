📦 Required Insert Quantities Per Part
Use the counts below when preparing 3D-printed pieces. All inserts are M3-0.5.
Part
Qty
Rear Head Mount 2 L
8
Eye 1 (x2)
2
Neck 2 + Neck Servo Mount
8
Eye Servo Mount, Eye UD Mount 1, Eye Pitch Arm
2
Rear Head Mount
18
Eye Servo Mount + Eyelid Servo Control Arm R
3
Neck Cover Front
4
Eyelid Servo Control Arm L
1
Camera Mount
1
Lower Mount Eyes
2
Top Eye Lid L + Eyelid Control Arm L
2
Top Eye Lid R + Eyelid Control Arm R
2
Torso Base Mount 2
15
AIY Microphone Mount 1
4
Face 1
4
Lower Head 1
8
Base Top 1 + Base Bttm 1
10
Ear 1 (x2)
8





General Notes
3D print tolerances vary between machines and materials. Expect to perform minor adjustments such as sanding, drilling, deburring, or heat-fitting to achieve smooth motion and proper alignment.


The Google AIY Voice Kit was not used, as it has been discontinued. Any related steps in the original tutorial were omitted or replaced with alternative components.


All assembly instructions are based on the original MAKI tutorial available at:
 https://www.hello-robo.com/tutorials


Several updates were made compared to the original tutorial to match the implemented robot:


A Raspberry Pi 5 is used instead of older Pi models.


No AIY kit or AIY microphone board is included.


A custom USB-powered speaker replaces the AIY audio hardware.


The SD card extension adapter is not used, as it did not function properly


🦴 NECK ASSEMBLY
General Tips:
Ensure all servos are centered/zeroed before installing.


Fit varies by printer; sanding may be required.


Deburring helps any rotating surfaces move smoothly.



Step 1 — Initial Neck Assembly
Parts:
 Neck Cover 1, Neck Servo Mount, 2× Neck Spacers, XL430 Servo (ID 1), X3P Cable, X3P Convertible Cable

Tips:
 Laser-cut or CNC neck spacers (Delrin/Acetal) give the best fit. 3D-printed spacers work but are less consistent.

Step 2 — Neck 1 and Servo ID 2
Install the XL430 Servo (ID 2) to Neck 1.
Tips:
 Remove the four back screws, insert the included servo spacers, then attach to Neck 1.


Step 3 — Combine Step 1 + Step 2
Add Neck 2 and route the Raspberry Pi ribbon cable.
Tips:
 Route servo wires to the sides. Keep the ribbon on the left side.


Step 4 — Add Neck Head Mount L
Attach to the previous assembly.
Tips:
 Depending on tolerances, you may need to tap the holes for smooth bolt insertion.


👀 EYE ASSEMBLY
All servos must be zeroed before assembly. Sand + deburr surfaces where rotation occurs.


Step 5 — Right Eyelid Mechanism
Parts: Top Eyelid R, Eyelid Horn 1 R, Lever Hub, Eyelid Control Arm R
Tips:
 M3 hardware must be used; larger screw heads interfere with eyelid movement.


Step 6 — Left Eyelid Mechanism
Repeat Step 5 for the left side.


Step 7 — Eyes Top Mount + Servo (ID 4)
Attach servo after inserting spacers.
Tips:
 If the servo pocket is tight, lightly sand or heat-soften the printed surfaces.


Step 8 — (Optional) Eyes LR Horn
This step can be skipped.

Step 9 — Eye Servo Mount + Servo (ID 5)
Attach Eyelid Servo Control Arm L, Eye UD Mount 1, and X3P Cable.
Tips:
 Insert servo spacers before mounting.


Step 10 — Add Eyes UD Lever + Lever Hub
Connect to assembly from Step 9.


Step 11 — Right Eyelid Servo System (ID 6)
Attach Eyelid Servo Control Arm R and 2× X3P cables.


Step 12 — Combine Step 7 + Step 8


Step 13 — Combine Step 10 + 11 + 12
Connect:
Servo ID 6 → Servo ID 4


Servo ID 6 → Servo ID 5


Step 14 — Eye Globes
Assemble Eyes 1, Iris 1, and Pupil 1 (x2).
Tips:
 Attach using screws or glue.


Step 15 — LR Lever Assembly
Attach Eyes LR Lever 1 and Lever Hubs.


Step 16 — Add Lower Mount Eyes


Step 17 — Add Eye Face Mount L + R


Step 18 — Combine Eyelids + Eyes
Integrate assemblies from Steps 5, 6, and 17.


🧠 HEAD ASSEMBLY
All servo positions must be zeroed before installation.

Step 19 — Attach Eyes to Lower Head
Add Eye Face Mount R and Lower Head 1; install the steel shaft.


Step 20 — Neck Front Cover + Rear Head Mounts + Camera Mount


Step 21 — Combine Steps 19 + 20


Step 22 — Add Neck Cover Servo Mount


Step 23 — Eyes UD Horn + Servo (ID 3)
Tips:
 Do not overtighten servo horn screws.


Step 24 — Combine Step 22 + Step 23
Insert servo spacers before fastening.


Step 25 — Combine Step 18 + Step 24
Add Eyelid Center Mount and aluminum spacer.


Step 26 — Add Rear Head Mount


Step 27 — Add Eye Face Mount 2 (x2)


Step 28 — Install Raspberry Pi Camera on Camera Mount 2


Step 29 — Combine Steps 27 + 28


Step 30 — Add Ears 1 + 2
Each ear is designed to fit a 66mm RGB LED ring.


Step 31 — Add Face 1
Ensure camera is perfectly centered with the mouth opening.


Step 32 — Final Head Closure
Verify all servo connections before closing.


🟦 BODY ASSEMBLY

Step 33 — Attach Head Assembly to Torso Base
Connect to Torso Base Mount 2, Neck Servo Mount 2, and the X3P cable.


Step 34 — Micro SD Extension
Align it correctly with Torso Base Mount 2.


Step 35 — Install Raspberry Pi
Add Micro USB cable and panel USB cable.


Step 36 — Add Base Top 1 + Power Cabling


Step 37 — Install OpenCM9.04
Plug in micro-USB before mounting.


Step 38 — Add Neck Back Mount 2


Step 39 — Microphone Assembly (Did not use AIY kit)

Step 40 — Combine Step 38 + Step 39


Step 41 — Install 5V PC Fan into Base Bttm 1 (Did not use 5V fan)

Step 42 — (Skipped)
Google AIY button not used.

Step 43 — Connect Main Power Harness Cables


Step 44 — Voice HAT Accessory Board (Optional)

Step 45 — Install 3" Speaker + HDMI Panel Mount


Step 46 — Combine Step 41 + Step 45


Step 47 — (Skipped) Speaker Cloth Assembly


Step 48 — Combine Step 46 + Step 47


Step 49 — Add Body B 1


Step 50 — Add HDMI Panel Mount


Step 51 — Final Body Assembly Completion


