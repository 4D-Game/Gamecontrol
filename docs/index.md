# Gamecontrol Setup

## Development

To write code and generate the documentation you need to install the packages listed in `requirements.txt` with `pip`

```bash
pip install -r requirements.txt
```

### PYTHONPATH
To get nicer imports and automatic documentation add the `src` folder to your `PYTHONPATH`

```bash
export PYTHONPATH="$(pwd)/src:$(pwd)/lib"
```

### Documentation

The Documentation is generated with the help of [mkdocstrings](https://mkdocstrings.github.io/#). To implement a module, class or function into your documentation you have to reference it as follows:

```md
::: library.module

::: library.module.class

::: library.module.function
```

### I2C
Change the I2C Frequency/Speed on Raspberry Pi3

Open `/boot/config.txt` file with `sudo nano /boot/config.txt` and add in line `dtparam=i2c_arm=on` with a comma the new baudrate:

```bash
dtparam=i2c_arm=on,i2c_arm_baudrate=1000000
```
`reboot` the Raspberry Pi

A simple shellscript can be included for verification. See link for more information: (https://gist.github.com/ribasco/c22ab6b791e681800df47dd0a46c7c3a)