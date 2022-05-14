# initialize global variables
from collections import defaultdict
import functions

VideoDevices = functions.returnCameraIndexes()
ClientDict = defaultdict(list)                  # form idcode; processID
Threads = []
transmitData = True
