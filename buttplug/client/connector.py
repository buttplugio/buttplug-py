from abc import abstractmethod
from ..core.messages import ButtplugMessage


class ButtplugClientConnector:

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def disconnect(self):
        pass

    @abstractmethod
    async def send(self, msg: ButtplugMessage):
        pass
