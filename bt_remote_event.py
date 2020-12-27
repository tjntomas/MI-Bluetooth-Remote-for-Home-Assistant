"""
Script to listen to events from a bluetooth remote control and send
the events to Home Assistant.

"""

import json
import evdev # https://pypi.org/project/evdev/
import asyncio
import aiohttp
import logging
import os

# Setup logging and log levels.
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logging.getLogger('asyncio').setLevel(logging.CRITICAL)

# Get parameters from the parameters.yaml.
BASE_API      = "http://192.168.1.20:8123/api/"  # URL to your HA instance.
DEV_INPUT     = "/dev/input/event16"             
API_KEY       = "A valid HA long-lived access token"
HA_EVENT_NAME = "mi_bt_remote" # Arbitrary name of the event that will get fired.

EVENT_PATH    = "events/" + HA_EVENT_NAME
BASE_API_URL  = BASE_API + EVENT_PATH
HEADERS       = {'content-type': 'application/json','Authorization': 'Bearer {}'.format(API_KEY)}
CMD           = "cmd"
CMD_TYPE      = "cmd_type"

EVENT_LOG_TEMPLATE = "Fired event {} with event data{}"

async def run():
  device = evdev.InputDevice(DEV_INPUT)
  print("Using Bluetooth", str(device))

  # Listen for events from the remote through the async-based evdev library.
  for event in device.read_loop():
    if event.type == evdev.ecodes.EV_KEY:   
      # Get the name of the remote key pressed, one of:
      # KEY_HOME    
      # KEY_F5      
      # KEY_COMPOSE   
      # KEY_BACK       
      # KEY_UP          
      # KEY_DOWN   
      # KEY_LEFT      
      # KEY_RIGHT    
      # KEY_ENTER      
      # KEY_VOLUMEUP   
      # KEY_VOLUMEDOWN 

      # The event string returned from the evdev library looks like this:
      # key event at 1609103448.769025, 28 (KEY_ENTER), down
      # We are only interested in the key name "KEY_ENTER" and the keypress type "down".
      cmd = str(evdev.categorize(event)).split(",")[1].split("(")[1].replace(")","")

      # Get the type of keypress, one of:
      # up
      # down
      # hold
      cmd_type =str(evdev.categorize(event)).split(",")[2]

      # Compose the payload to send to HA when firing the event.
      payload = {CMD: cmd, CMD_TYPE: cmd_type}

      # Since the evdev library is async-based, we use async to send the event to HA.
      async with aiohttp.ClientSession() as session:
        await session.post(BASE_API_URL, data=json.dumps(payload), headers=HEADERS)
        logging.info(EVENT_LOG_TEMPLATE.format(HA_EVENT_NAME,payload))
        await session.close()

if __name__ == '__main__':
    # Create, start and gracefully shut down the asyncio event loop.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
