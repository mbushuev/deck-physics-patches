# Mafia II Classic GPU Clothing

GPU Clothing supports the Steam release of Mafia II Classic (App ID 50130), with
the game's installed PhysX 2.8.3 runtime. The patch routes APEX cloth simulation
to the GPU, reduces work from inactive profiling calls, and optimizes selected
GPU buffer fills.

## Setup

1. Open Deck Physics 0.2.0 or later in Desktop Mode and select **Mafia II (Classic)**.
2. Click **Download patches** and select **GPU Clothing**, **Six-CU graphics mask**,
   and **Blocking GPU waits**.
3. Click **Set Up Game**, paste the resulting command into the game's Steam launch
   options, and set **APEX PhysX** to **High** in the game.

Setup prepares compatible files from the local game installation and mounts them
read-only for the session. The original game executable handles vertex packing
and menu transitions. The patch package contains no game executable or NVIDIA DLLs.

## Built-in benchmark

The test used Steam Deck OLED on battery with Valve Proton 11.0-2e, GPU clocks
in automatic mode, 1280 × 800, APEX PhysX High, all effects, and both VSync and
antialiasing off. All three patches above were active. The benchmark reported
**73.8 FPS average**. The launch log confirmed GPU clothing initialization.

A separate gameplay test returned to the main menu normally after selecting
**Quit** and confirming. A second test interrupted the benchmark and returned to
the main menu normally.

See the [Mafia II setup guide](https://github.com/mbushuev/deck-physics/blob/main/docs/compatibility/mafia-ii-classic.md)
for game settings and Proton requirements.
