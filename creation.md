![alternate_text](https://i.imgur.com/ceMe580.png)

# SpawnCycle Creation

## Overview
When opening SpawnCycler, the initial interface you are presented with is the Main interface.
This is where you can Create and Edit SpawnCycles and where a majority of interaction with the program takes place.

![alternate_text](https://i.imgur.com/pWy4ol6.png)

**Figure 1** - SpawnCycler Main Window

There are several components to this window:
1. **Wave Definitions Pane**
2. **ZED Pane**
3. **Messages Box**
4. **Options Bar**
5. **ZED Set Selector**
6. **Autosave Toggle**

The **Wave Definitions Pane** is where most of the action takes place.
This is where you do the majority of editing tasks such adding **Waves** and creating and managing **Squads**.

The **ZED Pane** contains all of the ZEDs needed to create a SpawnCycle.

The **Messages Box** contains any System Messages outputted by the program.
Errors and general notifications will appear here.

The **Options Bar** contains all of the main functionalities of the program.

A **ZED Set Selection** button can be found above the ZED Pane, which allows the user to switch back and forth between three sets of ZEDs:
- Default
- Custom
- Omega

The **Default** ZED set is the primary ZED set supported by the main branch(es) of CD.

The **Custom** ZED set includes additional ZEDs (such as E.D.A.Rs) and is primarily designed to be used with **Forrest Mark X's** build of CD, however some other builds of CD may support these custom ZEDs as well.

The **Omega** ZED set contains ZEDs seen in the Zedternal gamemode, which are compatible with the FMX CD build.

Finally, the **Autosave Toggle** allows you to toggle Autosave functionality off/on.

## Managing Waves & Squads
### Adding Waves
When starting from scratch, the **Wave Definitions Pane** will be blank, with an **Add Wave** button at the very top.
Clicking this button creates a new **Wave Frame** and adds a new wave to your SpawnCycle.

![alternate_text](https://i.imgur.com/eI0yMG5.png)
**Figure 3** - Wave Frame

```
Note that a valid SpawnCycle MUST have either 4, 7, or 10 Waves! SpawnCycler will warn you if you attempt to save a SpawnCycle of invalid length.
```

#### Wave Options
Each Wave Frame has a set of Wave Options located to the left of the frame. These buttons allow you to manage the wave.

![alternate_text](https://i.imgur.com/QQgDtwS.png)

**Figure 4** - Wave Options

To shift a wave up or down, use the up and down arrow buttons.
To remove a wave, click the red "X". All ZED data will be lost!
To clear a wave of all ZEDs, click the eraser button. All ZED data will be lost!

### Adding & Removing ZEDs
To add ZEDs to the newly-created wave, simply **click and drag** an icon from the **ZED Pane** and place it into the Wave Frame.
The ZED's icon will now appear in it's own small box inside the Wave Frame, along with a number indicating how many of that ZED there are.
This is called a **Squad**. The inner-most box that houses a Squad's ZEDs is called the **Squad Frame**. This is shown as **2** in the below image.

ZEDs can also be added by clicking the **"+"** button to the right of each ZED's counter. The counter itself can also be directly typed into to set an amount.

```
Note that Squads have a maximum capacity of 10 ZEDs! After a Squad has reached capacity, it's border will turn red and it will no longer accept new ZEDs.
```

To *remove* ZEDs from a Squad, simply click and drag the ZED's icon out of the Squad. This action removes exactly one ZED. Additionally, the **"-"** button can be clicked, which is found to the left of the ZED's counter. Similarly with adding, ZEDs can also be removed from a squad by typing a lower value than what is present.

To remove **all** of a specific ZED from a Squad, simply right click on the ZED's icon and select "Remove ZED From Squad". Setting a ZED's counter to "0" also removes it from the Squad.

![alternate_text](https://i.imgur.com/sHK31jd.png)

**Figure 5** - A Basic ZED Squad

When reading a SpawnCycle, CD iterates through the Squads for a given wave and attempts to spawn the ZEDs within in order.
*Typically, ZEDs within the same squad will spawn with one another.*

Above a Wave's Frame, the **total number of ZEDs added to the Wave** can be seen (shown in the above image as **1**). This allows you to accurately predict how many ZEDs will spawn before the cycle repeats during a wave. When using the **Analysis** tool, one can determine where to place specific ZEDs so that they spawn at a particular point in the wave (based on the size of the wave).

### Reorganizing ZEDs/Squads
ZEDs can also be dragged *between Squads* and even to other waves to reorganize them.
The placement of the ZED depends on where it was dragged:
- Dragging the ZED onto another Squad Frame moves the ZED to that Squad
- Dragging the ZED onto another Wave Frame moves the ZED to that Wave as a new Squad

## Replacing ZEDs
ZEDs can be replaced in two ways:
1. By right-clicking a ZED in a Squad and selecting `Replace ZED with..`
2. By using the `Batch` menu located at the top of the screen, and selecting `Replace ZEDs..`

The key difference is that replacing a ZED through the contextual right-click menu affects that ZED's Squad, while using the Batch menu replaces that ZED anywhere it appears in the *entire SpawnCycle*.

## Reference Documentation
- [SpawnCycle Generation](https://github.com/tamari92/spawncycler/blob/main/generation.md)
- [SpawnCycle Analysis](https://github.com/tamari92/spawncycler/blob/main/analysis.md)
- [SpawnCycle Conversion](https://github.com/tamari92/spawncycler/blob/main/conversion.md)
- [Program Settings](https://github.com/tamari92/spawncycler/blob/main/settings.md)