![alternate_text](https://i.imgur.com/E2mHK4E.png)

# Program Settings

## Overview
The `Program Settings` window allows the user to alter SpawnCycler's behavior(s).

![alternate_text](https://i.imgur.com/Y4FzPan.png)

**Figure 1** - Settings Interface

The following settings are available:
1. Warn when using custom ZED sets
2. Warn when using custom Generator settings
3. Warn when saving invalid length
4. Autosave Enabled
5. Autosave Interval
6. Default JSON Manual Save Length
7. Default Manual Save Filetype
8. New Squad Minimum ZED Amount
9. Default Analyze Sample GameLength

### Warn when using custom ZED sets
Sets whether or not SpawnCycler should warn when switching to non-standard ZED sets.

### Warn when using custom Generator settings
Sets whether or not SpawnCycler should warn when using non-standard Generator settings.

### Warn when saving invalid length
Sets whether or not SpawnCycler should warn when saving a SpawnCycle that is not exactly 4, 7, or 10 waves long.

### Autosave Enabled
Toggles Autosave functionality. An autosave is only possible if the file is named, has unsaved changes, and autosave is enabled.

For JSON files, Autosaving saves the SpawnCycle's data into the GameLength slot that was either most recently loaded from or saved to. Otherwise, it uses an adaptive setting wherein it saves the data into the smallest compatible GameLength.

For example, loading the 4 Wave SpawnCycle from a JSON will make that the autosave destination, but in the case that two more waves are added, the 7 Wave slot is used to autosave instead.

### Autosave Interval
Sets how often SpawnCycler will attempt to Autosave your work.

### Default JSON Manual Save Length
Sets the default GameLength destination when saving JSON formatted SpawnCycles.

The available options are:
- **Always Ask**: Always ask the user to confirm if there are multiple destinations available.
- **Adaptive**: Use the closest GameLength to the currently-defined amount of waves.
- **Preferred Medium**: Use the 7 Wave length whenever possible, otherwise use the *Adaptive* setting.
- **Preferred Long**: Use the 10 Wave length whenever possible, otherwise use the *Adaptive* setting.

### Default Manual Save Filetype
Sets the filetype that SpawnCycler prefers when Saving files:
- **Adaptive**: Use the last filetype that was opened or saved to.
- **Standard (.txt)**: Use the standard SpawnCycle format accepted by most CD builds.
- **Custom (.json)**: Use the JSON SpawnCycle format accepted by the Forrest Mark X CD build.

### New Squad Minimum ZED Amount
Sets the minimum amount of ZEDs added when creating a new Squad via dragging. Perfect for quickly making Squads with a specific amount of the same ZED.

### Default Analyze Sample GameLength
Sets the default GameLength used by the Analyzer.

The available options are:
- **Last Used**: Use the last GameLength that was selected when the Analyzer was closed. If this is the first time opening the Analyzer, use the *Preferred Long* setting.
- **Adaptive**: Use the closest GameLength to the currently-defined amount of waves.
- **Preferred Short**: Use the 4 Wave length whenever possible, otherwise use the *Adaptive* setting.
- **Preferred Medium**: Use the 7 Wave length whenever possible, otherwise use the *Adaptive* setting.
- **Preferred Long**: Use the 10 Wave length whenever possible, otherwise use the *Adaptive* setting.


## Reference Documentation
- [SpawnCycle Creation](https://github.com/tamari92/spawncycler/blob/main/creation.md)
- [SpawnCycle Analysis](https://github.com/tamari92/spawncycler/blob/main/analysis.md)
- [SpawnCycle Generation](https://github.com/tamari92/spawncycler/blob/main/generation.md)
- [SpawnCycle Conversion](https://github.com/tamari92/spawncycler/blob/main/conversion.md)