![alternate_text](https://i.imgur.com/7RFICg8.png)

# SpawnCycle Conversion

## Overview
The `SpawnCycle Conversion` tool allows the user to bundle multiple `SpawnCycles` together to be used with **Forrest Mark X's** build of Controlled Difficulty.

The FMX CD build offers an improved scheme for representing SpawnCycle data, and allows the user to include the following:
```
- SpawnCycle Name
- Author
- Creation Date
- Short SpawnCycle
- Medium SpawnCycle
- Long SpawnCycle
```

The primary feature of this system is the ability to include **variants** of the SpawnCycle at different `GameLengths` (Short, Medium, Long). CD can then choose the appropriate variant of the SpawnCycle automatically depending on the `GameLength` of the current match.

By default, `SpawnCycler` outputs SpawnCycles in the format used by most CD builds, which is not compatible with this customized version of the mod.

This tool allows the user to format multiple variants of their SpawnCycle with ease.

![alternate_text](https://i.imgur.com/BzMsgNQ.png)

**Figure 1** - SpawnCycle Converter

## Getting Started
To get started, simply set a `Name`, `Author`, and `Creation Date`.
Then, select up to **three** `SpawnCycles` to include in the package.

Note that at least **one** SpawnCycle is required.

Selected SpawnCycles are **parsed** for syntax and must meet the length requirements of their respective fields (ie: the "Long" SpawnCycle **must** have 10 Waves).

After everything is set, the **Convert** button can be pressed, after which a **JSON-formatted** SpawnCycle is produced.

## Reference Documentation
- [SpawnCycle Creation](https://github.com/tamari92/spawncycler/blob/main/creation.md)
- [SpawnCycle Analysis](https://github.com/tamari92/spawncycler/blob/main/analysis.md)
- [SpawnCycle Generation](https://github.com/tamari92/spawncycler/blob/main/generation.md)
- [Program Settings](https://github.com/tamari92/spawncycler/blob/main/settings.md)