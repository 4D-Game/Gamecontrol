# Gamecontrol

The *Gamecontrol* repository contains the code for the Raspberry Pi wich controls the whole game. In the following this Raspberry Pi is called **Gamecontrol**. In addition the repository contains the code used to access the displays and play sounds. The Raspberry Pi wich runs this code is further called **Displaycontrol**.

## Structure

The entry point for the gamecontrol is the `CrazyComet` class in *src/main.py*. This is a subclass of `Game` from `game_sdk.gamecontrol` (See the [sdk documentation](https://4d-game.github.io/sdk)). To start the game `CrazyComet.run()` is executed.

The entry point for the display is the `Display` class in *src/display.py*. It is a subclass of `Game` from `game_sdk.passive` (See the [sdk documentation](https://4d-game.github.io/sdk)). To start the game `Display.run()` is executed.

Apart from this the *src* folder consists of a *hardware*, *controls*, *fonts* and *assets* folder which will be explained below.

### Hardware
This is the hardware abstraction layer. It is used to expose hardware interfaces to the rest of the programm.

As defined in the `HAL` baseclass, every `HAL` class should have the following methods:

- `__init__()`
- `close()`

!!! NOTE
    Every class in the hardware abstraction layer should inherit from `HAL`

### Controls

This folder contains all classes wich interact with the game. They usually instantiate one or more `HAL` classes to control the hardware depending on the game.

### Fonts

This folder contains the fonts used to display text on the displays.

### Assets

This folder contains assets like images or audio files.

