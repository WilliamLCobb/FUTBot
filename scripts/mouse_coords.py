import time
import platform
from FifaBrowser import *

hid = None
if platform.system() == 'Windows':
    hid = HIDInput_Windows(correction=(0, 0))
else:
    hid = HIDInput_OSX(correction=(0, 5))

while True:
    print hid.mouse_position()
    time.sleep(3)