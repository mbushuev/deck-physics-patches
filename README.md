# Deck Physics Patches

Private Batman collision patches for the [Deck Physics installer](https://github.com/mbushuev/deck-physics). The installer already includes the graphics mask and blocking GPU waits for each tested game.

## Install

1. Download `DeckPhysics-Patches-0.1.0.zip` from the latest successful **Package game patches** run in Actions.
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

Each patch archive declares its Steam App ID, title, description and dependencies. The installer shows only patches for games it detects.

The archive version comes from `VERSION`. To create the 0.1.0 archive locally, run `python3 -m zipfile -c DeckPhysics-Patches-0.1.0.zip patches` from the repository root. You can also run **Package game patches** manually in Actions to refresh an expired download.
