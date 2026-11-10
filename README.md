# Deck PhysX game patches

Private patch packages for the Deck PhysX installer.

## Install

1. Download `deck-physx-patches.zip` from the latest successful **Package game patches** run in Actions.
2. Extract it into the folder containing `Install.sh`. The archive places the game folders under `patches/`.
3. Run `Install.sh` on the Steam Deck in Desktop Mode and select the patches you want. Keep the individual `.deckphysx.zip` files zipped.

```text
Install.sh
patches/
  alice-madness-returns/
  batman-arkham-asylum-goty/
```

Each patch archive declares its Steam App ID, title, description and dependencies. The installer shows only patches for games it detects.

To create the same archive locally, run `python3 -m zipfile -c deck-physx-patches.zip patches` from the repository root. You can also run **Package game patches** manually in Actions to refresh an expired download.
