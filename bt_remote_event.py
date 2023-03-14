"""
Script to listen to events from a bluetooth remote control and send
the events to Home Assistant.
Author: Tomas Jansson, https://github.com/tjntomas
Co-author : Quentin C.
"""

import array
import asyncio
import json
import evdev
import aiohttp
import logging
import os
import sys
import re

from evdev import InputDevice, categorize, ecodes

# Set up logging and log levels.
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logging.basicConfig(level=os.environ.get("LOGLEVEL", "ERROR"))

DEBUG         = True
GRAB_DEVICE   = True # If set to True, the devices will be locked to this script and the system will not receive any events.
BASE_API      = "http://hommeassistant:8123/api/"  # URL to your HA instance.
HAAPIKEY       = "API KEY"
HA_EVENT_TYPE = "phys_remote_g20" # Arbitrary name of the event that will get fired.
EVENT_PATH    = "events/" + HA_EVENT_TYPE
API_EVENT_ENDPOINT  = BASE_API + EVENT_PATH
HEADERS       = {'content-type': 'application/json','Authorization': 'Bearer {}'.format(HAAPIKEY)}

logging.info('BTREMOTE Events to Homeassistant')

async def sendEvent(device):

  async for event in device.async_read_loop():

      if event.type == evdev.ecodes.EV_KEY:

        # extract data from event
        source = device.name
        eventParms = str(categorize(event)).split(',')
        eventType = eventParms[len(eventParms) - 1].strip()
        cmd = re.sub(r"'|\[|\]|\)|\(",'',str(eventParms[1].split('(')[1]))

        # # send data to HA 
        payload = json.dumps({"cmd": cmd, "event": eventType,  "device": source })

        # # Since the evdev library is async-based, we use async to send the event to HA.
        async with aiohttp.ClientSession() as session:
             r = await session.post(API_EVENT_ENDPOINT, data=payload, headers=HEADERS)
             r.close()
             if(DEBUG): logging.info(payload)

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

for device in devices:

    if(GRAB_DEVICE): device.grab()
    asyncio.ensure_future(sendEvent(device))
    logging.info("listing events from [" + str(device)+"]")

if __name__ == '__main__':
  
  loop = asyncio.get_event_loop()

  try:
    loop.run_forever()
  except KeyboardInterrupt:
    if(DEBUG): logging.info("[CTRL+C] exit program")
    stored_exception=sys.exc_info()

sys.exit()
