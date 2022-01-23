#!/usr/bin/env python3

import logging
from time import sleep
from hardware.display_hal import DisplayHAL


if __name__ == "__main__":
  try:
    display = DisplayHAL()

    logging.info("Show Score")
    display.show_score(2, 5)
    sleep(2)

    logging.info("Update Score")
    display.show_score(3,5)
    sleep(2)

    logging.info("Show end display")
    display.end_display(2, "Team B: ")
    sleep(2)

  except KeyboardInterrupt:
    logging.info("Keyboard Interrupt")
  finally:
    display.close()