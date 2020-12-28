# Use a bluetooth remote control connected to a linux device with Home Assistant

I wanted to be able to use a spare Xiaomi MI Remote control and get the keypresses as events into Home Assistant so I can use it as general purpose remote. The remote I used can be bought for around $12 on banggood.com or wish.com.  https://www.wish.com/product/5f9a27f4f2a9e4083c908f7b?share=web

![MM](/miremote.jpg)

I paired the remote control with a NUC running Ubuntu that I use as a media player, but a Raspberry Pi or any other maching running a linux OS should work. I then wrote a simple python3 script to listen to the remote keypress events and send the events to Home Assistant.

To use the script, you need to:
1. Install the dependencies in the script. They should all be present on your system with the exception of the evdev module which you can find here. https://pypi.org/project/evdev/
1. Look in /dev/input and make a note of the highest numbered device
2. Pair the remote control to the computer, as you would pair any bluetooth device.
3. Look again in /dev/input and make note of the new device that has been created. This is your bluetooth remote control.
4. Fill in the name of the path to your remote control device in the python script, i.e. "/dev/input/event9"
5. Add the details for your Home Assistant instance in the script.

In total, you will need to edit the following lines in the script:
````python
BASE_API      = "http://192.168.1.20:8123/api/"  # URL to your HA instance.
DEV_INPUT     = "/dev/input/event9"             
API_KEY       = "A valid HA long-lived access token"
HA_EVENT_NAME = "mi_bt_remote" # Arbitrary name of the event that will get fired.
````

Then run the script with 
````python
sudo python3 bt_remote_event.py
````
to see that it works. Sudo is necessary to access the input device. Then, in Home Assistant, you can subscribe to the mi_bt_remote event in developer tools.

Now, set up the script as a daemon by copying the btmon.service file to your service directory. You need to edit the path to the pytthon script in the service file. Enable the service and start it. The daemon need to be run as user root.

You can now use the events as triggers in automations in Home Assistant.
