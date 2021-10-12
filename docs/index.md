# Watcherstream Setup

## Development

To write code and generate the documentation you need to install the packages listed in `requirements.txt` with `pip`

```bash
pip install -r requirements.txt
```

To use the surrortg-sdk initialize and update the submodule with:

```bash
git submodule init
git submodule update
```

!!! Note
    To import modules from the **surrortg-sdk** you have to extend the `PYTHONPATH`:
    ```python
    import sys, os
    sys.path.insert(1, os.path.join(os.path.dirname(
      os.path.abspath(__file__)), os.pardir, "lib", "surrortg-sdk"))

    from surrortg import <...>
    ```

### Documentation

The Documentation is generated with the help of [mkdocstrings](https://mkdocstrings.github.io/#). To implement a module, class or function into your documentation you have to reference it as follows:

```md
::: library.module

::: library.module.class

::: library.module.function
```

## Run

To run the watcherstream you have to create a Docker image from the `Dockerfile` and run it in a container by running the `docker-setup` script.

!!! info
    To use Docker on Windows you need to install the [wsl](https://fireship.io/lessons/windows-10-for-web-dev/)

Now set up OBS like explained in the [Surrogate docs](https://docs.surrogate.tv/watcherstream.html#obs-mode) but change the **recording path** to the *srtg_hls* Folder in this repository.

Next generate the configuration for the watcherstream (`srtg.toml`) by running `scripts/generate-config`. The script takes the **Device Id** and **Game Token** as argument.

```bash
python3 scripts/generate-config <device_id> <token>
```

!!! danger
    Never upload the game token