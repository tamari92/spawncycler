# SpawnCycle Analysis

## Overview
The `SpawnCycle Analysis` tool allows you to analyze a SpawnCycle's contents and show meaningful information about its performance by simulating a full game.

The information shown includes:
- Total Number of ZEDs by Category (Trash, Medium, Large, Boss, etc.)
- Total Number of ZEDs by Type (Alpha Clot, Fleshpound, Bloat, etc.)
- Total Number of ZEDs by Group (Clots, Gorefasts, Robots, etc.)
- The estimated Difficulty of the wave

Each of these include Pie and Line Charts that help visually reinforce the data.
The Simulation Data is first shown for the SpawnCycle as a whole (summary data), followed by Simulation Data on a `per-wave` basis.

## How the Simulation Works
A `SpawnCycle` is simply a list of ZED squads to spawn during a specific wave. Both CD and `SpawnCycler` simulate the SpawnCycle in the following way:
- Determine the **Total Number of ZEDs to spawn**, based on `Difficulty`, `GameLength`, and the current `WaveSizeFakes` setting
- Spawn ZEDs in order from the SpawnCycle until reaching the end of the cycle
- Loop back around to the beginning of the SpawnCycle and repeat
- Count ZEDs spawned on each iteration

The **Total Number of ZEDs** to spawn is determined in the following way:
- Determine the base number of ZEDs for the wave (based on GameLength)
- Determine the `Difficulty Multiplier` (based on Difficulty)
- Compute the `WaveSize Multiplier` (based on the WaveSizeFakes setting)

#### Difficulty Multipliers
Normal: 0.85
Hard: 1.00
Suicidal: 1.30
Hell on Earth: 1.70

#### Base Number of ZEDs
Short (4 Waves): 25 // 32 // 35 // 42
Medium (7 Waves): 25 // 28 // 32 // 32 // 35 // 40 // 42
Long (10 Waves): 25 // 28 // 32 // 32 // 35 // 35 // 40 // 42 // 42

For example..
for `GameLength=2` (10 Wave), the base number of ZEDs on **Wave 6** is `35`
for `GameLength=0` (4 Wave), the base number of ZEDs on **Wave 2** is `32`

#### WaveSize Multipliers
0-1 WSF: 1.00
2 WSF: 2.0
3 WSF: 2.75
4 WSF: 3.5
5 WSF: 4.0
6 WSF: 4.5
6+ WSF: 4.5 + ((WSF - 6) * 0.211718)

For example..
for `WaveSizeFakes=5` the **WaveSizeMultiplier** would be `4.0`
for `WaveSizeFakes=16` the **WaveSizeMultiplier** be `4.5 + ((16 - 6) * 0.211718)` = `6.61718`

#### Calculating the Number of ZEDs to Spawn
These three values are used to calculate the **Total Number of ZEDs to Spawn**, described by the formula:
`NumZEDsToSpawn = DifficultyModifier * WaveSizeMultiplier * BaseNumZEDs`

For example..
On a Long Hell on Earth match, with `WaveSizeFakes=16`, the number of ZEDs to spawn on **Wave 6** would be:
`NumZEDsToSpawn = 1.70 * 35 * 6.61718` which gives `NumZEDsToSpawn=393` (floored to the nearest integer)

Now that the number of ZEDs to spawn for the given wave is known, `SpawnCycler` simply iterates over the list of Squads for that wave, choosing ZEDs in order until `NumZEDsToSpawn` is reached. During this iteration, a count is kept of each ZED type and Group spawned.

If `SpawnCycler` reaches the end of the SpawnCycle before the wave is complete, it simply starts over at the beginning.

## Simulation Results
This section details the Simulation Results, which includes:
- **Total Number of ZEDs by Category** (Trash, Medium, Large, Boss, etc.)
- **Total Number of ZEDs by Type** (Alpha Clot, Fleshpound, Bloat, etc.)
- **Total Number of ZEDs by Group** (Clots, Gorefasts, Robots, etc.)
- **The estimated Difficulty of the wave**

#### ZEDs by Category
This table shows the summary data for the number of ZEDs spawned of each **Category** in this wave.
There are **four** main Categories of ZEDs:
- Trash
- Medium
- Large
- Boss

**Trash ZEDs** include:
- Alpha Clot
- Cyst
- Slasher
- Rioter
- Gorefast
- Gorefiend
- Crawler
- Elite Crawler
- Stalker

**Medium ZEDs** include:
- Bloat
- Husk
- Siren
- E.D.A.R Trapper
- E.D.A.R Blaster
- E.D.A.R Bomber

**Large ZEDs** include:
- Scrake
- Quarter Pound
- Fleshpound
- Alpha Scrake
- Alpha Fleshpound

**Bosses** include:
- Dr. Hans Volter
- Patriarch
- King Fleshpound
- Abomination
- Abomination Spawn
- Matriarch

#### ZEDs by Type
This table shows summary data for the number of ZEDs spawned of each individual **Type**.
This is essentially information about each ZED in the above Categories.

#### ZEDs by Group
This table shows summary data for the number of ZEDs spawned of each individual **Group**.
A ZED Group contains several different types of associated ZEDs.

There are **nine** main Groups of ZEDs:
- **Clots** (Alpha Clot, Cyst, Slasher, Rioter)
- **Gorefasts** (Gorefast, Gorefiend)
- **Crawlers** / Stalkers
- **Robots** (E.D.A.R Trapper, E.D.A.R Blaster, E.D.A.R Bomber)
- **Scrakes** (Scrake, Alpha Scrake)
- **Fleshpounds** (Quarter Pound, Fleshpound, Alpha Fleshpound)
- **Albino** (Rioter, Gorefiend, Elite Crawler, Alpha Scrake, Alpha Fleshpound)
- **SpawnRage** (SpawnRaged QP/FP/AFP)
- **Other** (anything not falling into the above categories)

#### Difficulty Estimation
The **Difficulty Estimate** is a chart that details the relative difficulty of the wave, based on the following:
- The `MaxMonsters` setting
- The `Difficulty` of the match
- The `GameLength` (Short, Medium, Long) of the match
- The `WaveSizeFakes` setting

These values are used to 

Note that this chart is also created for the entire SpawnCycle, using the average `DifficultyScore` of each wave.

## Reference Documentation
[Creating a SpawnCycle](https://github.com/nybanez/spawncycler/blob/main/creation.md)
[Generating a SpawnCycle](https://github.com/nybanez/spawncycler/blob/main/generation.md)
[Converting a SpawnCycle](https://github.com/nybanez/spawncycler/blob/main/conversion.md)
