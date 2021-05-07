# SpawnCycle Generation

## Overview
The `SpawnCycle Generation` tool allows the user to pseudo-randomly generate an entire `SpawnCycle` meeting pre-determined criteria.

There are three sets of parameters the user can alter to affect the Generation results:
- General Settings
- Category Settings
- ZED Settings

## General Settings
The **General Settings** allow the user to affect the overall behavior of the Generator. The following settings can be modified:
```
- SpawnCycle Length
- Min / Max Squads Per Wave
- Min / Max Squad Size
- Albino Min Wave
- Large ZED Min Wave
- SpawnRage Min Wave
- Boss Min Wave
```

#### SpawnCycle Length
This slider allows the user to control how many waves the Generator will create: either `4` (Short), `7` (Medium), or `10` (Long) waves.

#### Min / Max Squads Per Wave
These sliders allow the user to control the **minimum** and **maximum** number of Squads to be generated per wave. The MAX value cannot be lower than the MIN value. Setting both values equal will cause an exact number of Squads to be generated each wave.

#### Min / Max Squad Size
These sliders allow the user to control the **minimum** and **maximum** number of ZEDs to be generated as part of each individual Squad. The MAX value cannot be lower than the MIN value. Setting both values equal will cause an exact number of ZEDs to be generated for each Squad. The Generator cannot create more ZEDs than the Squad cap of `10`.

#### Albino Min Wave
Sets the minimum wave that **Albino ZEDs** (Elite Crawler, Rioter, Gorefiend, etc) are allowed to appear. Note that changing the **SpawnCycle Length** parameter affects the maximum value of this field.

#### Large ZED Min Wave
Sets the minimum wave that **Large ZEDs** are allowed to appear. If the **Category Density** sliders are configured such that only Large ZEDs will be generated, then this slider **must** be set to `1`. Note that changing the **SpawnCycle Length** parameter affects the maximum value of this field.

#### SpawnRage Min Wave
Sets the minimum wave that **Fleshpounds, Quarter Pounds, and Alpha Fleshpounds** are allowed to spawn **Enraged**. Note that changing the **SpawnCycle Length** parameter affects the maximum value of this field.

#### Boss Min Wave
Sets the minimum wave that **Bosses** are allowed to appear. If the **Category Density** sliders are configured such that only Bosses will be generated, then this slider **must** be set to `1`. Note that changing the **SpawnCycle Length** parameter affects the maximum value of this field.

![alternate_text](https://i.imgur.com/oYIXlSS.png)

**Figure 1** - General Settings

## Category Settings
The **Category Settings** allow the user to affect the way **ZED Categories** are chosen.

Four sliders are present:
```
- Trash Density
- Medium Density
- Large Density
- Boss Density
```

These sliders affect the **relative probability** that their corresponding ZED Category will be chosen compared to the other categories.

For example:

If a category's Density is at `0%`, then that category will not be chosen at all.

If a single category is at `100%` Density, while the other categories are set to `50%` Density, then that category has **twice the chance to be chosen**.

If two categories are at the **same** density (ie: 100% // 100% or 50% // 50%), then those categories have **equal chance to be chosen**.

It is not possible to generate a SpawnCycle with all Category Densities set to `0%`.

![alternate_text](https://i.imgur.com/1E3qSvv.png)

**Figure 2** - Category Settings

## ZED Settings
Similar to the **Category Settings**, the **ZED Settings** allow the user to affect the way **each individual ZED Type** is chosen within their respective categories.

There are Density sliders for each individual ZED, and like with the **Category** sliders, these influence the **relative probability** of the respective ZED being chosen compared to the other ZEDs.

For example:

If the `Bloat Density` is set to `0%`, then Bloats will not appear at all in the SpawnCycle.

If the `Crawler Density` is set to `100%` and the `Alpha Clot Density` is set to `50%`, then Crawlers are **2x more likely** to be chosen than Alpha Clots.

For ZEDs with an **Albino** variant (Alpha Clot, Crawler, Gorefast), there is an additional slider that allows the user to influence the chance for that Albino ZED to appear instead of the lesser variant.

For ZEDs that can become **SpawnRaged** (Fleshpound, Quarter Pound), there is an additional slider that allows the user to influence the chance for those ZEDs to spawn Enraged.

![alternate_text](https://i.imgur.com/fHwuxup.png)

**Figure 3** - ZED Settings

## Custom Settings
Like in the **Creation Window**, the current **ZED Set** can be swapped between `Default` and `Custom` ZEDs.

The **Custom** ZED Set is designed to be used with **Forrest Mark X's** build of Controlled Difficulty, and supports additional ZED Types such as **E.D.A.Rs** and **Bosses**. More Albino ZEDs appear as well, such as the **Alpha Fleshpound** and **Alpha Scrake**, Albino variants of the original SC and FP. These ZEDs are **not** supported by most other builds of CD, so this setting should be used at the user's own risk.

The **Default** ZED Set is the ZED Set supported by most established builds of CD.

## Presets
The Generator tool supports several `Presets`, including:
- `Light` (predominantly Trash ZEDs)
- `Moderate` (decent mixture of Trash and Large ZEDs)
- `Heavy` (predominantly Large ZEDs)
- `Albino` (predominantly Albino ZEDs)
- `Poundemonium` (predominantly Larges, spawning earlier in the cycle)
- `GSO` (almost all Fleshpounds, spawning very early in the cycle)
- `Min Settings` (all settings are at their minimum value)
- `Max Settings` (all settings are at their maximum value)
- `Putrid Pollution` (predominantly Bloats)
- `Sonic Subversion` (predominantly Sirens)
- `Android Annihilation` (predominantly E.D.A.Rs)
- `Arachnophobia` (predominantly Crawlers)
- `Cloaked Carnage` (predominantly Stalkers)
- `Hellish Inferno` (predominantly Husks)
- `Trash Only` (only Trash ZEDs spawn)
- `Medium Only` (only Medium ZEDs spawn)
- `Large Only` (only Large ZEDs spawn)
- `Boss Only` (only Bosses spawn)
- `Large-less` (no Large ZEDs or Bosses at all)
- `Custom Craziness` (predominantly Custom ZEDs)
- `Boss Rush` (predominantly Bosses)

## Reference Documentation
- [Creating a SpawnCycle](https://github.com/nybanez/spawncycler/blob/main/creation.md)
- [Analyzing a SpawnCycle](https://github.com/nybanez/spawncycler/blob/main/analysis.md)
- [Converting a SpawnCycle](https://github.com/nybanez/spawncycler/blob/main/conversion.md)
