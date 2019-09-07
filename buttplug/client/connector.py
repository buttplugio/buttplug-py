from abc import abstractmethod
from ..core.messages import ButtplugMessage
from typing import List
from ..core.errors import ButtplugError


class ButtplugClientConnectorError(ButtplugError):
    """Raised when connector has connection issues.

    Attributes:

        message (str): Describes the nature of the exception
    """
    pass


class ButtplugClientConnectorObserver(object):
    @abstractmethod
    async def handle_message(self, msg: ButtplugMessage):
        pass


class ButtplugClientConnector(object):
    def __init__(self):
        self._observers: List[ButtplugClientConnectorObserver] = list()
        self._connected: bool = False

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def send(self, msg: ButtplugMessage):
        pass

    @property
    def connected(self):
        return self._connected

    def add_observer(self, obs: ButtplugClientConnectorObserver):
        self._observers.append(obs)

    def remove_observer(self, obs: ButtplugClientConnectorObserver):
        self._observers.remove(obs)

    async def _notify_observers(self, msg: ButtplugMessage):
        for obs in self._observers:
            await obs._handle_message(msg)
