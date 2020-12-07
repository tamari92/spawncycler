# SpawnCycle Analysis

## Overview
The `SpawnCycle Analysis` tool allows you to analyze a SpawnCycle's contents and show meaningful information about its performance by simulating a full game.

There are two main components to this window:
- Analysis Results
- Analysis Parameters

The **Analysis Results** show the results of the simulation and include the following information:
- **Total Number of ZEDs by Category** (Trash, Medium, Large, Boss, etc.)
- **Total Number of ZEDs by Type** (Alpha Clot, Fleshpound, Bloat, etc.)
- **Total Number of ZEDs by Group** (Clots, Gorefasts, Robots, etc.)
- **The estimated relative Difficulty of the wave**

Each of these include Pie and Line Charts that help visually reinforce the data.

The Simulation Data is first shown for the SpawnCycle as a whole (summary data), followed by Simulation Data on a `per-wave` basis.

The **Analysis Parameters** give you the ability to control the simulation, by setting pre-determined criteria.

![alternate_text](https://i.imgur.com/sSyeGjn.png)

**Figure 1** - SpawnCycle Analysis Tool

## Analysis Parameters
The **Analysis Parameters** allow the user to directly impact the Analysis Results.

The following parameters can be set:
- **Difficulty**
- **Wave Size Fakes**
- **Overview Only**
- **Ignore Zeroes**
- **Analyze Difficulty**
- **Max Monsters**
- **Display Charts**

#### Difficulty
The Difficulty level of the game (Normal // Hard // Suicidal // Hell on Earth)

#### Wave Size Fakes
The `WaveSizeFakes` value represents the number of Human players in the current Squad. Higher fakes increases the number of ZEDs in the wave. Typically, in Vanilla KF2, this value scales up and down accordingly with the number of players in the server. CD allows you to set a **"Faked"** value, which locks it at a specific number. `SpawnCycler` also utilizes this behavior. The `WaveSizeFakes` setting is used in conjunction with `FakesMode=ignore_humans`, which means that the WSF value is not influenced by the actual number of players at all.

Min: **0** // Max: **128**

#### Overview Only
This parameter causes all **per-wave Analysis Data** to be excluded from the report. Only the SpawnCycle summary data will be shown.

#### Ignore Zeroes
Don't display any table rows or chart elements that represent data which has zero value. Helps reduce clutter and increase focus on relevant data.

#### Analyze Difficulty
Tells `SpawnCycler` whether or not it should analyze the wave and produce an `Estimated Difficulty` curve (see below for more information on how this works).

#### Max Monsters
Used in conjunction with the **Analyze Difficulty** setting. Tells `SpawnCycler` the maximum number of ZEDs that can exist on the battlefield at any given time. Increasing this value means more ZEDs can be alive at once, which greatly impacts the overall difficulty of the wave(s).

Min: **1** // Max: **256**

#### Display Charts
Controls whether or not `SpawnCycler` should produce Pie charts representing the Group, Type, and Categorical total data for the wave. Does not affect whether or not the Difficulty chart is drawn. Use the **Analyze Difficulty** flag for that instead.

## How the Simulation Works
This section details how `SpawnCycler` simulates waves.

A `SpawnCycle` is simply a list of ZED squads to spawn during a specific wave. Both CD and `SpawnCycler` simulate the SpawnCycle in the following way:
- Determine the **Total Number of ZEDs to spawn**, based on `Difficulty`, `GameLength`, and the current `WaveSizeFakes` setting
- Spawn ZEDs in order from the SpawnCycle until reaching the end of the cycle
- Loop back around to the beginning of the SpawnCycle and repeat
- Count ZEDs spawned on each iteration

The **Total Number of ZEDs** to spawn is determined in the following way:
- Determine the base number of ZEDs for the wave (based on GameLength)
- Determine the `DifficultyMultiplier` (based on Difficulty)
- Compute the `WaveSizeMultiplier` (based on the WaveSizeFakes setting)

#### DifficultyMultipliers
```
Normal: 0.85
Hard: 1.00
Suicidal: 1.30
Hell on Earth: 1.70
```

#### Base Number of ZEDs
```
Short (4 Waves): 25 // 32 // 35 // 42
Medium (7 Waves): 25 // 28 // 32 // 32 // 35 // 40 // 42
Long (10 Waves): 25 // 28 // 32 // 32 // 35 // 35 // 40 // 42 // 42
```

For example..

for `GameLength=2` (10 Wave), the base number of ZEDs on **Wave 6** is `35`

for `GameLength=0` (4 Wave), the base number of ZEDs on **Wave 2** is `32`

#### WaveSizeMultipliers
```
0-1 WSF: 1.00
2 WSF: 2.00
3 WSF: 2.75
4 WSF: 3.50
5 WSF: 4.00
6 WSF: 4.50
6+ WSF: 4.50 + ((WSF - 6) x 0.211718)
```

For example..

for `WaveSizeFakes=5` the **WaveSizeMultiplier** would be `4.00`

for `WaveSizeFakes=16` the **WaveSizeMultiplier** would be `4.50 + ((16 - 6) x 0.211718)` = `6.61718`

#### Calculating the Number of ZEDs to Spawn
These three values are used to calculate the **Total Number of ZEDs to Spawn**, described by the formula:

`NumZEDsToSpawn = DifficultyModifier x WaveSizeMultiplier x BaseNumZEDs`

For example..

On a Long Hell on Earth match, with `WaveSizeFakes=12`, the number of ZEDs to spawn on **Wave 10** would be:

`NumZEDsToSpawn = 1.70 x 42 x 5.770308 = 411` (floored to the nearest integer)

Now that the number of ZEDs to spawn for the given wave is known, `SpawnCycler` simply iterates over the list of Squads for that wave, choosing ZEDs in order until `NumZEDsToSpawn` is reached. During each iteration, a count is kept of each ZED type and Group spawned.

If `SpawnCycler` reaches the end of the SpawnCycle before the wave is complete, it simply starts over at the beginning.

## Simulation Results
This section details the Simulation Results, which includes:
- **Total Number of ZEDs by Category** (Trash, Medium, Large, Boss, etc.)
- **Total Number of ZEDs by Type** (Alpha Clot, Fleshpound, Bloat, etc.)
- **Total Number of ZEDs by Group** (Clots, Gorefasts, Robots, etc.)
- **The estimated relative Difficulty of the wave**

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
- **Crawlers / Stalkers**
- **Robots** (E.D.A.R Trapper, E.D.A.R Blaster, E.D.A.R Bomber)
- **Scrakes** (Scrake, Alpha Scrake)
- **Fleshpounds** (Quarter Pound, Fleshpound, Alpha Fleshpound)
- **Albino** (Rioter, Gorefiend, Elite Crawler, Alpha Scrake, Alpha Fleshpound)
- **SpawnRage** (SpawnRaged QP/FP/AFP)
- **Other** (anything not falling into the above categories)

#### Difficulty Estimate
The **Difficulty Estimate** is a chart that details the relative difficulty of the wave, based on the following:
- The composition of the **currently spawned ZEDs** (influenced by `MaxMonsters`)
- The `Difficulty` of the match
- The `GameLength` (Short, Medium, Long) of the match
- The `WaveSizeFakes` setting

These values are used to determine the `DifficultyScore` for each iteration of the simulation, given by the formula:

`DifficultyScore = WaveSizeModifier x WaveDifficultyModifier x ZEDScoreModifier`

##### WaveSizeModifier
The `WaveSizeModifier` is determined through the following formula:

`WaveSizeModifier = 1 + (WaveSizeFakes / 128)`

As an example, a `WaveSizeFakes` of 12 would give:

`WaveSizeModifier = 1 + (12 / 128) = 1.09375`

This modifier follows a trend in which longer waves (due to higher WSF) results in a higher modifier. Longer waves tend to be harder to due to the sparseness of resources (ammo has to be spread over a longer period of time, for example).

##### WaveDifficultyModifier
The value of the `WaveDifficultyModifier` is determined directly by the game's `Difficulty` and `GameLength`:

`WaveDifficultyModifier = (1.50 x DoshDifficultyModifier) x (WaveNum / MaxWave)`

The `DoshDifficultyModifier` depends on the Difficulty of the game. In general, higher difficulties have a higher `DoshDifficultyModifier` because ZEDs award less money:
```
Normal: 1.00
Hard: 1.25
Suicidal: 1.50
Hell on Earth: 1.75
```

`WaveNum` is the current wave and `MaxWave` is the maximum wave for the current `GameLength`.

As an example, the `WaveDifficultyModifier` on Wave 6/10 on Hard Difficulty would be:

`WaveDifficultyModifier = (1.50 x 1.25) x (6 / 10) = 1.875 x 0.6 = 1.125`

##### ZEDScoreModifier
The value of the `ZEDScoreModifier` depends directly on what ZEDs are currently spawned, which itself is influenced by the `MaxMonsters` setting.

Each ZED Category (Trash, Medium, Large, Boss) has a specific **weight** associated with it:
```
Trash: 500 Points
Medium: 1,000 Points
Large: 2,500 Points
Boss: 7,500 Points
```

As the wave is simulated, a list is kept of all of the ZEDs that are currently "spawned". The maximum capacity of this list is directly influenced by the `MaxMonsters` setting. The higher the `MaxMonsters` is, the more ZEDs that can be alive at once.

For each ZED Category, the total score is deterined by: `NumZEDsInCategory x CategoryWeight`.

For example, **51** Trash ZEDs would give a score of `51 x 500 = 25,500 Points`.

This is then repeated for the remaining ZED categories, and combined to obtain an overall value, called the `TotalZEDScore`:

`TotalZEDScore = (NumTrash x 500) + (NumMedium x 1000) + (NumLarge x 2500) + (NumBoss x 7500)`

The game's `Difficulty` factors into the calculation as well, since on higher difficulties, ZEDs both deal more damage and have more health. Some ZEDs, like the Husk, also have alternate attacks.
```
Normal: 0.00
Hard: 1.00
Suicidal: 2.00
Hell on Earth: 3.00
```
The `ZEDDifficultyModifier` is found through the formula:

`ZEDDifficultyModifier = 1.00 + (0.50 x DifficultyMod)`

So for example..

On a Hard difficulty match, the `ZEDDifficultyModifier` would be `1.00 + (0.50 x 1.00) = 1.50`.

These two intermediate values come together to form the `ZEDScoreModifier`:

`ZEDScoreModifier = TotalZEDScore x ZEDDifficultyModifier`

As an example, the `ZEDScoreModifier` on an arbitrary wave of a Suicidal match might look like this:

`ZEDScoreModifier = ((15 x 500) + (21 x 1,000) + (13 x 2,500) + (2 x 7,500)) x 3.00 = 228,000.00`

##### Putting it all together
With the intermediate values calculated, we can now determine the `DifficultyScore` for the current Simulation iteration:

`DifficultyScore = WaveSizeModifier x WaveDifficultyModifier x* ZEDScoreModifier`

Suppose `WaveSizeModifier=1.09375`, `WaveDifficultyModifier=1.125`, and `ZEDScoreModifier=228,000.00`. This would give:

`DifficultyScore = 1.09375 x 1.125 x 228,000 = 208,546.875`

Next, suppose the current iteration were `16/273` (16 ZEDs spawned so far / 273 ZEDs to spawn total).

This would imply that this `DifficultyScore` corresponds to `WaveProgress = (16 / 273) x 100.0 = 58.6%` through the wave.

This forms a pair (x, y) of `(58.6, 208,546.875)`, which implies that `DifficultyScore` is mapped on the **Y-axis** while `WaveProgress` is mapped on the **X-axis**. This allows `SpawnCycler` to create the **Estimated Difficulty Chart**.

Note that this chart is also created for the entire SpawnCycle, using the average `DifficultyScore` of each wave.

![alternate_text](https://i.imgur.com/AkLdytV.png)

**Figure 2** - Estimated Difficulty Chart

## Reference Documentation
- [Creating a SpawnCycle](https://github.com/nybanez/spawncycler/blob/main/creation.md)
- [Generating a SpawnCycle](https://github.com/nybanez/spawncycler/blob/main/generation.md)
- [Converting a SpawnCycle](https://github.com/nybanez/spawncycler/blob/main/conversion.md)
