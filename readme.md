![alternate_text](https://i.imgur.com/EXfOFM3.png)

# SpawnCycler
by Tamari

#### Current Version
1.3

#### Contact
- Discord: Tamari#6292
- Email: nate92@gmail.com
- Steam: https://steamcommunity.com/id/tamaritm

## Description
SpawnCycler is a SpawnCycle editor for Killing Floor 2's Controlled Difficulty mod (https://github.com/notblackout/kf2-controlled-difficulty)

The main purpose of this utility is to allow for swift and intuitive creation, generation, analysis, and editing of SpawnCycles for CD.
SpawnCycler attempts to simplify and completely replace the (rather tedious) process of creating a SpawnCycle by hand using a Text Editor.
Quality-of-life features such as a built-in parser and "drag-and-drop" UI elements ensure maximum ease-of-use and make iterations quick and simple, with minimal errors.

![alternate_text](https://i.imgur.com/jyyg0WC.png)

**Figure 1** - Text-based (left) vs SpawnCycler (right)

## Features
- Minimalistic and easily-navigable UI
- Simplistic SpawnCycle creation achieved through intuitive "drag-and-drop" operations and other features such as the ability to change the ordering of the waves
- A built-in parser that syntax-checks SpawnCycles, ensuring that created Cycles are fully-compatible with CD by eliminating errors and enforcing formatting standards
- The ability to Generate a SpawnCycle from scratch based on pre-determined criteria
- The ability to Simulate and Analyze a SpawnCycle based on pre-determined criteria, in order to obtain summary info such as Number of ZEDs Spawned and Difficulty Estimates on a per-wave basis
- The ability to perform Batch operations on a SpawnCycle, such as reversing the wave order or replacing all of one ZED type

## Planned Features
- Allow for directly dragging a file into the main window to load it
- Batch Converter to quickly convert multiple SpawnCycles between the available filetypes and also run a string of commands on a series of cycles
- Scrollable Wave bars
- The ability to compare two SpawnCycles using the Analysis Tool
- Individual tabs for each Wave of the SpawnCycle
- The ability to reorganize ZEDs within Squads via dragging
- The ability to drag entire Squads to move them around and/or reorder them
- The ability to drag Waves to reorder them instead of using buttons
- The ability to drag a ZED out of a Squad and insert it between two other Squads
- The ability to clone Squads and ZEDs onto the cursor and drag them elsewhere
- The ability to collapse a Squad for easier viewing

## Binaries
#### Windows
v1.3: https://github.com/tamari92/spawncycler/releases/tag/13

## Credits
- UI Design + General Programming: **Tamari**
- ZED Icons: **Louice Adler** (https://www.artstation.com/artwork/VdgnVP)
- Controlled Difficulty: **blackout** (https://github.com/notblackout/kf2-controlled-difficulty)
- Controlled Difficulty - Eternal Edition: **H U N ナ E R** (https://steamcommunity.com/sharedfiles/filedetails/?id=1554427429)

## Legal / License
SpawnCycler is written in Python and uses PyQt GUI Library

This software is licensed under GNU General Public License v3.0 (GPLv3):
```
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
```

© Tamari 2020-2022

All rights reserved.

## Reference Documentation
- [SpawnCycle Creation](https://github.com/tamari92/spawncycler/blob/main/creation.md)
- [SpawnCycle Generation](https://github.com/tamari92/spawncycler/blob/main/generation.md)
- [SpawnCycle Analysis](https://github.com/tamari92/spawncycler/blob/main/analysis.md)
- [SpawnCycle Conversion](https://github.com/tamari92/spawncycler/blob/main/conversion.md)
- [Program Settings](https://github.com/tamari92/spawncycler/blob/main/settings.md)