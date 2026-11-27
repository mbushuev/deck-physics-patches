# Deck Physics Patches

Optional per-game performance patches for the [Deck Physics installer](https://github.com/mbushuev/deck-physics). The installer already includes the graphics mask and blocking GPU waits for each tested game.

| Game | Patch set and test results |
| --- | --- |
| Batman: Arkham Asylum GOTY | [Collision patches and battery measurements](docs/batman-benchmarks.md) |
| Mafia II Classic | [GPU clothing and benchmark results](docs/mafia-ii-benchmarks.md) |

## Install

In Desktop Mode, open Deck Physics, select a game, and click **Download patches**.
Select the patches and click **Set Up Game**. The installer downloads only the
selected game's patch set.

### Install from an archive

1. Download `DeckPhysics-Patches-0.2.0.zip` from the latest successful **Package game patches** run in Actions.
2. Extract it into the folder containing `Install.sh`. Merge the `patches/` folder when prompted.
3. Run `Install.sh` on the Steam Deck in Desktop Mode and select the patches you want. Keep the individual `.deckphysx.zip` files zipped.

```text
Install.sh
patches/
  batman-arkham-asylum-goty/
    cloth-bounds.deckphysx.zip
    cloth-triangle-groups.deckphysx.zip
    cloth-triangle-reads.deckphysx.zip
    cloth-shape-reads.deckphysx.zip
```

Each patch archive declares its Steam App ID, title, description and dependencies. The installer shows the patches for the selected game's profile.

The archive version comes from `VERSION`. To create the 0.2.0 archive locally, run `python3 -m zipfile -c DeckPhysics-Patches-0.2.0.zip patches` from the repository root. You can also run **Package game patches** manually in Actions to refresh an expired download.

## Mafia II Classic

The optional GPU Clothing patch requires Deck Physics 0.2.0 or later. It uses the Steam Classic executable and its installed PhysX 2.8.3 runtime.
Enable **GPU Clothing**, **Six-CU graphics mask**, and **Blocking GPU waits** in
Deck Physics. Set APEX PhysX to High in the game.

Build the patch on x86-64 Linux with Python 3.11 or later, a C compiler targeting
Steam Linux Runtime 4, and GNU Binutils.

    python3 sources/mafia-ii-classic/package.py

Copy the resulting archive to the installer's `patches/mafia-ii-classic/` folder.
The archive contains the preparation scripts and the patch's own compiled code.
Setup generates the game-specific files from the matching local DLLs. The
launcher mounts them read-only for the game session. The installed game files
stay intact.

## Update the patch catalog

After rebuilding a patch archive, run

    python3 tools/Build-PatchCatalog.py

Commit the updated archive and catalog together. The installer verifies each
download against the catalog. Generated game executables and PhysX modules
stay in the user's local installation.
