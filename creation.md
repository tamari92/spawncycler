# SpawnCycle Creation

## Overview
When opening SpawnCycler, the initial interface you are presented with is the Creation interface.
This is where you can Create and Edit SpawnCycles.

There are **three** main components to this window:
- **WaveDefs Pane** (the larger, blank area)
- **ZED Pane** (the pane off to the right with the ZED icons)
- **Messages Box** (the bottom-most box)

The **WaveDefs Pane** is where most of the action takes place.
This is where you will add **Waves** and create and manage **Squads**.

The **ZED Pane** contains all of the ZEDs needed to create a SpawnCycle.
A mode toggle can be found at the top of this area, which allows the user to switch back and forth between the `Custom` and `Default` ZED sets.
- The **Custom** ZED set includes additional ZEDs (such as E.D.A.Rs) and is primarily designed to be used with **Forrest Mark X's** build of CD, however some other builds of CD may support these custom ZEDs as well.
- The **Default** ZED set is the primary ZED set supported by the main branch(es) of CD.

Finally, the **Messages Box** contains any System Messages outputted by the program.
Errors and general notifications will appear here.

## Adding Waves, ZEDs, and Squads
When starting from scratch, the **WaveDefs Pane** will be blank, with an **Add Wave** button at the very top.
Clicking this button creates a new **Wave Frame**.

**Note**: A valid SpawnCycle **MUST** have either **4**, **7**, or **10** Waves!

To add ZEDs to the wave, simply **click and drag** an icon from the **ZED Pane** and place it into the newly-created Wave Frame.
The ZED's icon will now appear in it's own small box inside the Wave Frame, along with a number indicating how many of that ZED there are.
This is called a **Squad**. The inner-most box that houses a Squad's ZEDs is called the **Squad Frame**.

**Figure 1** - Basic ZED Squad

When reading a SpawnCycle, CD iterates through the Squads for a given wave and attempts to spawn the ZEDs within in order.
Typically, ZEDs within the same squad will spawn with one another.

To add more ZEDs to the Squad, simply continue to **drag-and-drop** icons from the ZED Pane into the **Squad Frame**.
To create another new Squad, drag the icon into the outer-most Wave Frame instead.

**Note**: Each Squad has a maximum capacity of `10`! When a Squad is at capacity, it's border will turn red and it will no longer accept any new ZEDs dragged into it.

## Removing and Reorganizing ZEDs/Squads
Once a ZED is placed into a Squad, it can be **removed** by *dragging the ZED icon out of the Squad and onto the empty background*.
Note that in the case that there are multiple of the same ZED in a Squad, this action will only remove **one** of them.

To remove **all** of a specific ZED from a Squad, you can *right-click* the ZED to bring up a contextual menu, and select `Remove ZED from Squad`.

ZEDs can also be dragged *between Squads* and even to other waves.
The placement of the ZED depends on where it was dragged:
- Dragging the ZED onto another Squad Frame moves the ZED to that Squad
- Dragging the ZED onto another Wave Frame moves the ZED to that Wave as a new Squad

## Reorganizing Waves
By pressing the "Up" and "Down" arrows to the left of each Wave Frame, waves can be *shifted up or down*.
You can **delete** a Wave by pressing the red 'X'.

## Replacing ZEDs
ZEDs can be replaced in two ways:
- By right-clicking a ZED in a Squad and selecting `Replace ZED..`
- By using the `Batch` menu located at the top of the screen, and selecting `Replace ZEDs..`

The key difference is that replacing a ZED through the contextual right-click menu affects that ZED's Squad, while using the Batch menu replaces that ZED anywhere it appears in the *entire SpawnCycle*.

