# Mechanical_README.md

This document explains **all mechanical aspects of assembling MakiMate**, including:

* Required **3D-printed parts** and **M3 heat-set insert counts**
* How to properly **install brass threaded inserts** using a soldering iron
* Mechanical assembly of the **neck, eyes, head, and body**
* **Preparing all Dynamixel motors** (ID assignment, labeling, zeroing)
* **3D-printing troubleshooting** (PLA only)
* Reference to the full MAKI assembly guide (Hello-Robo)

For the full legacy MAKI assembly photos and tutorials:
➡️ [https://www.hello-robo.com/tutorials](https://www.hello-robo.com/tutorials)

---

# 1. Required Inserts Per 3D-Printed Part (All M3-0.5)

Install all heat-set inserts *before* mechanical assembly.

| Part                                           | Qty |
| ---------------------------------------------- | --- |
| Rear Head Mount 2 L                            | 8   |
| Eye 1 (x2)                                     | 2   |
| Neck 2 + Neck Servo Mount                      | 8   |
| Eye Servo Mount, Eye UD Mount 1, Eye Pitch Arm | 2   |
| Rear Head Mount                                | 18  |
| Eye Servo Mount + Eyelid Servo Control Arm R   | 3   |
| Neck Cover Front                               | 4   |
| Eyelid Servo Control Arm L                     | 1   |
| Camera Mount                                   | 1   |
| Lower Mount Eyes                               | 2   |
| Top Eye Lid L + Eyelid Control Arm L           | 2   |
| Top Eye Lid R + Eyelid Control Arm R           | 2   |
| Torso Base Mount 2                             | 15  |
| AIY Microphone Mount 1                         | 4   |
| Face 1                                         | 4   |
| Lower Head 1                                   | 8   |
| Base Top 1 + Base Bottom 1                     | 10  |
| Ear 1 (x2)                                     | 8   |

---

# 2. Installing Heat-Set Inserts

All threaded connections use **M3-0.5 brass heat-set inserts**.

## 2.1 Tools Needed

* Soldering iron (set to **180–220°C / 350–425°F**)
* Heat-set insert tip **or** flat chisel-style tip
* Tweezers or pliers
* Printed part with correctly sized insert holes

## 2.2 Installation Procedure

### **Step 1 — Heat the Insert**

* Use tweezers to hold the brass insert.
* Touch it to the soldering iron tip until the brass begins to warm (1–2 seconds).

### **Step 2 — Place Insert in Printed Hole**

* Align the insert over the 3D-printed recess.
* Press lightly with the soldering iron tip.

### **Step 3 — Melt Insert Into the PLA**

* Slowly press the insert down, allowing it to **sink evenly** into the print.
* Do NOT force it; the PLA should melt, not deform from pressure.

### **Step 4 — Stop When Flush**

* Remove heat and let the insert cool in place.
* The insert should be:

  * perfectly **flush with the top**, and
  * **perpendicular** to the surface.

### **Step 5 — Reinforce (Optional)**

If the fit is slightly loose:

* Add a tiny amount of melted PLA by lightly reheating the top edge.

### ✔️ A properly installed insert:

* Does not spin
* Is flush with the surface
* Accepts an M3 screw smoothly

### ❌ A bad insert installation:

* Sits crooked
* Melts through the print
* Spins when tightening a screw

If this happens, reheat the area and adjust or reprint the part.

---

# 3. General Mechanical Notes

### ✔️ Use **PLA only**

* MAKI tolerances are designed for PLA stiffness.
* PETG / ABS change dimensions and often cause binding.

### ✔️ Expect minor finishing

Every printer behaves differently. You may need:

* Sanding edges and mating surfaces
* Cleaning holes with a 3 mm drill bit
* Deburring pivot points
* Slight heat forming (hair dryer/heat gun) for tight fits

### ✔️ Motion parts must move freely

Any friction in:

* Eye pitch
* Eye yaw
* Eyelid levers
* Neck joints

…will result in **overworked motors**.

If something sticks:

* Sand lightly
* Ream the hole
* Remove stringing

---

# 4. Preparing Your Dynamixel Motors (Critical)

Before installing ANY motors mechanically, each motor must be:

1. **Assigned a correct ID**
2. **Set to Protocol 2.0**
3. **Set to Baud: 57,600 bps**
4. **Physically labeled**
5. **Zeroed (centered) before horn installation**

Use Dynamixel Wizard 2.0:

| ID | Function   |
| -- | ---------- |
| 1  | neck_yaw   |
| 2  | neck_pitch |
| 3  | eyes_pitch |
| 4  | eyes_yaw   |
| 5  | lid_left   |
| 6  | lid_right  |

### Centering Procedure

1. Disable torque
2. Rotate joint by hand to approximate center
3. Re-enable torque
4. Use Wizard to set goal position = center
5. Install servo horn while holding the output shaft centered

A poorly centered servo makes the entire assembly impossible to align later.

---

# 5. 3D Printing Guidelines & Troubleshooting (PLA Only)

### 5.1 Print Settings

* Nozzle: **0.4 mm**
* Layer height: **0.16–0.20 mm**
* Infill: **20–40%** (structural parts 40–50%)
* Bed: **60°C**
* Nozzle: **195–215°C**
* Cooling: **100% after first layers**

---

## 5.2 Troubleshooting Guide

### 🧵 **Problem: Spaghetti failure**

Cause: **Bed adhesion failure**
Two typical root causes:

1. **Print cannot grip the bed surface**

   * Clean bed with 90–99% IPA
   * Add glue stick or painter’s tape
   * Increase first-layer squish
   * Slow first layer to 20–25 mm/s

2. **Poor part orientation**

   * Re-orient so the largest flat surface touches the bed
   * Add **brim** (5–10 mm)
   * Avoid printing tall skinny parts without support

---

### ❌ Corners lifting or warping

* Increase bed temperature slightly
* Add a brim
* Reduce fan on first 5 layers
* Re-level the bed

---

### 🔩 Holes too tight / pegs don’t fit

* Clean with a 3 mm drill bit **by hand**
* Lightly sand
* Ream pivot holes carefully

---

### 🪡 Stringing

* Temperature too hot → lower by 5–10°C
* Increase retraction distance or speed

---

### 📏 Dimensional inaccuracies

* Slow print speed
* Ensure belts are tight
* Increase wall count to 3 perimeters

---

# 6. Neck Assembly

> Images and detailed diagrams can be found in the Hello-Robo tutorial.
> The following is MakiMate-specific (RPi 5 + OpenCM).

### Step 1 — Initial Neck Assembly

Parts: Neck Cover 1, Neck Servo Mount, 2× Neck Spacers, Servo **ID 1**, cables

* Use CNC/Delrin spacers if possible
* Ensure servo horn rotates freely

### Step 2 — Install Servo ID 2

* Remove servo back screws
* Add spacers
* Attach to Neck 1

### Step 3 — Combine Step 1 + 2

* Add Neck 2
* Route ribbon cable left
* Route servo cables along edges

### Step 4 — Add Neck Head Mount L

* Use M3 screws into previously installed inserts
* Sand holes if alignment is tight

---

# 7. Eye Assembly

### Step 5 — Right Eyelid

Assemble Top Eyelid R, Lever Hub, Control Arm.
Ensure friction-free motion.

### Step 6 — Left Eyelid

Mirror of Step 5.

### Step 7 — Eyes Yaw Servo (ID 4)

Install with spacers; lightly sand if tight.

### Step 8 — Eyes LR Horn (optional)

### Step 9 — Left Eyelid Servo (ID 5)

Attach servo & linkages.

### Step 10 — Eyes UD Lever

### Step 11 — Right Eyelid Servo (ID 6)

### Step 12 — Combine Step 7 + 8

### Step 13 — Combine Steps 10 + 11 + 12

### Step 14 — Eye Globes

Assemble eyes + iris + pupils.

### Step 15 — LR Lever

### Step 16 — Lower Mount Eyes

### Step 17 — Face Mounts L + R

### Step 18 — Combine Eyelids + Eyes

Ensure ALL eyelid motions are smooth before continuing.

---

# 8. Head Assembly

### Step 19 — Attach Eyes to Lower Head

### Step 20 — Neck Front Cover + Rear Head Mounts + Camera Mount

### Step 21 — Combine Steps 19 + 20

### Step 22 — Add Neck Cover Servo Mount

### Step 23 — Install Eyes Pitch Servo (ID 3)

### Step 24 — Combine Step 22 + 23

### Step 25 — Combine Eyelids + Eyes With Servo Assembly

### Step 26 — Add Rear Head Mount

### Step 27 — Add Eye Face Mount 2 (x2)

### Step 28 — Install Raspberry Pi Camera

### Step 29 — Combine Steps 27 + 28

### Step 30 — Add Ears (support 66 mm LED rings)

### Step 31 — Add Face 1

### Step 32 — Final Head Closure

Verify all:

* Servo IDs are correct
* Cables are free, not pinched
* Eyes and eyelids move freely

---

# 9. Body Assembly

### Step 33 — Attach Head to Torso Base

### Step 34 — SD Extension (optional; often skipped)

### Step 35 — Install Raspberry Pi 5 and USB/HDMI panel extensions

### Step 36 — Base Top + Power Cabling

### Step 37 — Install OpenCM9.04

Connect USB before mounting.

### Step 38 — Neck Back Mount

### Step 39 — Microphone Assembly (ReSpeaker, not AIY)

### Step 40 — Combine Step 38 + 39

### Step 41 — 5V Fan (not used)

### Step 42 — AIY Button (skipped)

### Step 43 — Connect Power Harness

### Step 44 — Optional boards (not included)

### Step 45 — Install 2" Speaker + HDMI Panel Mount

### Step 46 — Combine Step 41 + 45

### Step 47 — Speaker Cloth (optional)

### Step 48 — Lower Base Close-Out

### Step 49 — Add Body B

### Step 50 — Final HDMI Panel Mounting

### Step 51 — Final Assembly

Check:

* Head movement
* Cable routing
* Insert integrity
* Structural tightness

---

# 10. Full Tutorial Reference

For full photos, exploded diagrams, and additional context, use the original MAKI tutorial:

👉 **[https://www.hello-robo.com/tutorials](https://www.hello-robo.com/tutorials)**

The MakiMate build modifies some steps (new Pi, new speaker, no AIY kit), but mechanically follows the same layout.

---

# 🧭 Navigation

🔙 Back to Main Documentation
➡️ [`../../README.md`](Overall_README.md)
