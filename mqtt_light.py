import logging
import asyncio

from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_0
from functools import wraps
import json

class MQTTLight(object):
    def __init__(self, server, port, ctrl_topic, state_topic=None, initial_state=None, change_cb=(lambda x: None)):
        self.__state = dict(initial_state) if initial_state else {}
        self.__ctrl_topic = ctrl_topic
        self.__state_topic = state_topic
        self.__server = server
        self.__port = port
        self.__client = None
        self.__change_cb = change_cb

        self.state_update(self.__state)

    @staticmethod
    def parser():
        import argparse
        p = argparse.ArgumentParser(description="MQTT Light Control")
        p.add_argument('server', type=str, help="MQTT broker")
        p.add_argument('-p', '--port', type=int, default=1883)
        p.add_argument('ctrl_topic', type=str, help="Control Topic")
        p.add_argument('--state_topic', type=str, help="State Topic", default=None)
        return p

    @asyncio.coroutine
    def connect(self):
        C = MQTTClient(config={'auto_reconnect':False})
        self.__client = C
        yield from C.connect("mqtt://" + self.__server + ":" + str(self.__port))
        _ = yield from self.publish_state()
        yield from C.subscribe([
                (self.__ctrl_topic, QOS_0),
             ])
        try:
            try:
                while True:
                    message = yield from C.deliver_message()
                    packet = message.publish_packet
                    _ = yield from self.command_topic(json.loads(packet.payload.data.decode("utf-8")))
            except KeyboardInterrupt:
                pass
            yield from C.unsubscribe([self.__ctrl_topic])
            yield from C.disconnect()
        except ClientException as ce:
            print("Client exception: %s" % ce)

    @asyncio.coroutine
    def command_topic(self, cmd):
        self.state_update(cmd)
        _ = yield from self.publish_state()

    def state_update(self, d):
        for c in d:
            try:
                if self.__getattribute__(c)(d[c]):
                    self.__state[c] = d[c]
            except AttributeError:
                print("ignored attribute update:", c)
        self.__change_cb(self.__state)

    @asyncio.coroutine
    def publish_state(self):
        if self.__state_topic:
            _ = yield from self.__client.publish(self.__state_topic, message=json.dumps(self.__state).encode())

class OnOffLight(MQTTLight):
    def __init__(self, server, port, ctrl_topic, state_topic=None, on_func=None, off_func=None, initial_state=None, change_cb=(lambda x: None)):
        self.on_func = on_func
        self.off_func = off_func
        self.__state = None
        super().__init__(server, port, ctrl_topic, state_topic, initial_state, change_cb)

    def state(self, arg=None):
        if arg == None:
            return self.__state

        d = {'ON': self.on_func,
             'OFF':self.off_func}
        if arg in d:
            if not self.__state == arg:
                self.__state = arg
                return (d[arg]() or True)
            return None
        raise ValueError()
