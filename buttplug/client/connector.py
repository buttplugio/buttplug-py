from abc import abstractmethod
from ..core.messages import ButtplugMessage
from typing import List


class ButtplugClientConnectorObserver(object):
    @abstractmethod
    async def handle_message(self, msg: ButtplugMessage):
        pass


class ButtplugClientConnector(object):

    def __init__(self):
        self._observers: List[ButtplugClientConnectorObserver] = list()

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def send(self, msg: ButtplugMessage):
        pass

    def add_observer(self, obs: ButtplugClientConnectorObserver):
        self._observers.append(obs)

    def remove_observer(self, obs: ButtplugClientConnectorObserver):
        self._observers.remove(obs)

    async def _notify_observers(self, msg: ButtplugMessage):
        for obs in self._observers:
            await obs.handle_message(msg)
