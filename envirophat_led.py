#!/usr/bin/python3
import asyncio
from mqtt_light import *
from envirophat import leds

if __name__ == '__main__':
    args = OnOffLight.parser().parse_args()
    
    leds.off()
    c = OnOffLight(args.server, args.port, args.ctrl_topic, args.state_topic, leds.on, leds.off, {'state': 'OFF'})
    asyncio.get_event_loop().run_until_complete(c.connect())
