# Batman collision patch benchmarks

The tests used Batman: Arkham Asylum GOTY on Steam Deck OLED with Valve Proton 11.0-2e, PhysX 2.8.1.58, and PhysX High. They ran the game's built-in benchmark and scored 80 seconds per run.

## Uncapped performance on AC power

Both configurations used the Six-CU graphics mask, the same bridge and game settings, and automatic GPU clocks. Frame limiters and VSync were off during the scored interval.

| Configuration | Average FPS | Final five seconds | 99th-percentile frame time |
| --- | ---: | ---: | ---: |
| Graphics mask control | 82.63 | 71.4 FPS | 18.56 ms |
| Graphics mask, collision patches, and startup blocking waits | 87.56 | 71.8 FPS | 19.16 ms |

Adding the collision patches and blocking waits raised the mean by about 4.9 FPS. The final five seconds improved by 0.4 FPS and the 99th-percentile frame time rose by 0.60 ms.

## Battery draw at a 60 FPS cap

Four runs used Gaming Mode on battery with the same screen brightness, game settings, and automatic GPU clocks. The optimized setup used the graphics mask, collision patches, and startup blocking waits.

| Configuration | Average FPS | Whole-device draw |
| --- | ---: | ---: |
| Unmodified Proton-ZLUDA stack | 59.23 | 12.89 W |
| Optimized setup | 59.29 | 12.17 W |

The combined changes reduced mean draw by **0.72 W (5.6%)** in this comparison.

## Wait policy on the patched setup

Separate comparisons kept the graphics mask and collision patches active in every run and changed only the wait policy. Each row summarizes two runs per policy on battery in Gaming Mode.

| Frame limit | Original waits | Startup blocking waits |
| --- | ---: | ---: |
| 60 FPS cap | 12.24 W at 59.41 FPS | 12.07 W at 59.21 FPS |
| Uncapped | 19.25 W at 87.56 FPS | 18.74 W at 87.91 FPS |

The capped pairs went in opposite directions. Both uncapped pairs favored blocking waits, with a mean saving of 0.52 W before rounding.
