# Display setup

## Installation
### Setup script

To setup everything needed, to run the displaycontrol there is a setup script, which can be executed with the following command:

```bash
scripts/display-pi-setup
```

After this you have to activate SPI by adding `dtparam=spi=on` to the `boot/config.txt`. Next the Raspberry Pi needs to be rebooted.

### Manual
#### SDK

The sdk needed to use this program is stored in a submodule. To use it the following commands should be executed:

```bash
git submodule init
git submodule update
```

!!! INFO
    To update the sdk to the latest commit run

    ```bash
    git submodule update --remote --merge
    ```

#### PYTHONPATH
To get nicer imports and automatic documentation add the `src` folder to your `PYTHONPATH`

```bash
export PYTHONPATH="$(pwd)/src:$(pwd)/lib/sdk"
```

#### Python Dependencies

Install all python dependencies run:

```bash
pip3 install -Ur requirements.txt
```

#### I2C

I2C is needed to communicate with the Adafruit Motorshield. It can be activated with a baudrate of 1MHz by adding the following lines to the */boot/config.txt*.

```
dtparam=i2c_arm=on
dtparam=i2c_arm_baudrate=1000000
```

!!! INFO
    Those settings are applied with the next reboot.


#### Display

In order to use the display the following packages are needed:

```bash
pip3 install Adafruit-Blinka
pip3 install adafruit-circuitpython-rgb-display
sudo apt-get install python3-pil -y
```

#### Audio

In order to use a USB audio card and play sound using Python the following packages are needed:

```bash
sudo apt-get install alsa-utils
sudo apt-get install python3-pygame
sudo apt-get install python3-sdl2
```

## Setup

### Audio

For the use of the displaycontrol with the USB audio card the *alsa.conf* file needs to be changed.

First execute `sudo aplay -l check device ID` to check the ID of your card. The output should look something like this:

```bash
sudo aplay -l check device ID
**** List of PLAYBACK Hardware Devices ****
card 0: Headphones [bcm2835 Headphones], device 0: bcm2835 Headphones [bcm2835 Headphones]
  Subdevices: 8/8
  Subdevice #0: subdevice #0
  Subdevice #1: subdevice #1
  Subdevice #2: subdevice #2
  Subdevice #3: subdevice #3
  Subdevice #4: subdevice #4
  Subdevice #5: subdevice #5
  Subdevice #6: subdevice #6
  Subdevice #7: subdevice #7
card 1: Device [USB Audio Device], device 0: USB Audio [USB Audio]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
```

The line we are interested in is `card 1: Device [USB Audio Device], device 0: USB Audio [USB Audio]`. This shows the card ID of the used device is 1.

Now edit the config file using nano:

```bash
sudo nano /usr/share/alsa/alsa.conf
```

Change the two follwing values in the file:

```bash
defaults.ctl.card <ID>
defaults.pcm.card <ID>
```

### Autostart

The game can be started automatically using `systemd`. Register the service by executing the script `scripts/systemd-setup`. It takes the name of the service (without .service) as first argument.

**Example for *gamecontrol.service***
```bash
scripts/systemd-setup gamecontrol
```