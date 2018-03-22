import asyncio
from mqtt_light import *

if __name__ == '__main__':
    args = OnOffLight.parser().parse_args()
    
    c = OnOffLight(args.server, args.port, args.ctrl_topic, args.state_topic, lambda : print("ON"), lambda: print("OFF"), {'state': 'OFF'})
    asyncio.get_event_loop().run_until_complete(c.connect())
