# Gamecontrol Setup

## Development

To write code and generate the documentation you need to install the packages listed in `requirements.txt` with `pip`

```bash
pip install -r requirements.txt
```

The sdk needed to use this program is stored in a submodule. To use it the following commands should be executed:

```bash
git submodule init
git submodule update
```

!!! INFO
    To update the sdk to the latest commit run

    ```bash
    git submodule update --recursive --remote
    ```

### PYTHONPATH
To get nicer imports and automatic documentation add the `src` folder to your `PYTHONPATH`

```bash
export PYTHONPATH="$(pwd)/src:$(pwd)/lib/sdk"
```

### Documentation

The Documentation is generated with the help of [mkdocstrings](https://mkdocstrings.github.io/#). To implement a module, class or function into your documentation you have to reference it as follows:

```md
::: library.module

::: library.module.class

::: library.module.function
```