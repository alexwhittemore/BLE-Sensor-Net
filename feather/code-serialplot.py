"""
Just print a sine and triangle wave to demo serial plotters
"""

import time
import board
import ulab.numpy as np

sintable = np.linspace(0, 2*3.14159, 41)
while True:
    for val in sintable[:-1]:  # Drop the last value since the next cycle already has it.
        print(f"{np.sin(val)} {val}")
        time.sleep(.1)
