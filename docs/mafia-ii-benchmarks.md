# Mafia II Classic GPU Clothing

GPU Clothing supports the Steam release of Mafia II Classic (App ID 50130), with
the game's installed PhysX 2.8.3 runtime. The patch routes APEX cloth simulation
to the GPU, reduces work from inactive profiling calls, and optimizes selected
GPU buffer fills. It also accelerates position and tangent-space packing in
the render path.

## Setup

1. Open Deck Physics 0.2.0 or later in Desktop Mode and select **Mafia II (Classic)**.
2. Click **Download patches** and select **GPU Clothing**, **Six-CU graphics mask**,
   and **Blocking GPU waits**.
3. Click **Set Up Game**, paste the resulting command into the game's Steam launch
   options, and set **APEX PhysX** to **High** in the game.

Setup prepares compatible files from the local game installation and mounts them
read-only for the session. The generated executable preserves the original packing routines and routes
the render calls through the accelerated routines. The patch package contains no game executable or NVIDIA DLLs.

## Built-in benchmark

The original Steam launch on Valve Proton 11.0-3 averaged **13.5 FPS** in
the built-in benchmark on Steam Deck OLED at 1280 × 800 and APEX PhysX High.
The full Deck Physics profile on Valve Proton 11.0-2e averaged **76.7 FPS**.
The two runs compare complete setups, including different Proton builds.

### Effect of render packing in the optimized profile

Two runs used Steam Deck OLED on AC with Valve Proton 11.0-2e, GPU clocks in
automatic mode, 1280 × 800, APEX PhysX High, all effects, and both VSync and
antialiasing off. GPU Clothing, the graphics mask, and blocking waits were
active in both runs. The launch log confirmed GPU clothing initialization.

| Render packing | Average FPS |
| --- | ---: |
| Original game path | 74.4 |
| Accelerated render calls | **76.7** |

The earlier battery run with the original packing path reported 73.8 FPS.
The AC pair measures the render change at those test settings.

A separate gameplay test returned to the main menu normally after selecting
**Quit** and confirming. A second test interrupted the benchmark and returned to
the main menu normally.

See the [Mafia II setup guide](https://github.com/mbushuev/deck-physics/blob/main/docs/compatibility/mafia-ii-classic.md)
for game settings and Proton requirements.
