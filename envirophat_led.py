#!/usr/bin/python3
import asyncio
from mqtt_light import *
from envirophat import leds
import shelve

STATE_FILENAME = '/tmp/.envirophat_light_state'

def get_initial_state():
    with shelve.open(STATE_FILENAME) as s:
        state = dict(s)
        if 'state' not in state:
            return {'state': 'OFF'}

def change_cb(new_state):
    with shelve.open(STATE_FILENAME) as s:
        s.update(new_state)

if __name__ == '__main__':
    args = OnOffLight.parser().parse_args()

    leds.off()
    c = OnOffLight(args.server, args.port, args.ctrl_topic, args.state_topic, leds.on, leds.off, get_initial_state(), change_cb)
    asyncio.get_event_loop().run_until_complete(c.connect())
