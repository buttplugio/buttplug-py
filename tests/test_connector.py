"""Tests for connector and message sorter."""

import asyncio

import pytest

from buttplug._messages import Ok
from buttplug._utils.message_sorter import MessageSorter


class TestMessageSorter:
    """Tests for MessageSorter request/response correlation."""

    async def test_get_next_id_increments(self):
        """get_next_id returns incrementing IDs."""
        sorter = MessageSorter()

        assert sorter.get_next_id() == 1
        assert sorter.get_next_id() == 2
        assert sorter.get_next_id() == 3

    async def test_wait_and_resolve(self):
        """wait_for_response resolves when resolve is called."""
        sorter = MessageSorter()
        msg_id = sorter.get_next_id()
        response = Ok(id=msg_id)

        # Start waiting in background
        async def wait():
            return await sorter.wait_for_response(msg_id)

        wait_task = asyncio.create_task(wait())

        # Give task time to start waiting
        await asyncio.sleep(0.01)

        # Resolve the request
        resolved = await sorter.resolve(msg_id, response)
        assert resolved is True

        # Check the result
        result = await wait_task
        assert isinstance(result, Ok)
        assert result.id == msg_id

    async def test_resolve_unknown_id(self):
        """resolve returns False for unknown message IDs."""
        sorter = MessageSorter()
        response = Ok(id=999)

        resolved = await sorter.resolve(999, response)
        assert resolved is False

    async def test_timeout(self):
        """wait_for_response raises TimeoutError on timeout."""
        sorter = MessageSorter()
        msg_id = sorter.get_next_id()

        with pytest.raises(asyncio.TimeoutError):
            await sorter.wait_for_response(msg_id, timeout=0.01)

    async def test_reject_all(self):
        """reject_all cancels all pending requests."""
        sorter = MessageSorter()
        msg_id1 = sorter.get_next_id()
        msg_id2 = sorter.get_next_id()

        # Start two waits
        task1 = asyncio.create_task(sorter.wait_for_response(msg_id1))
        task2 = asyncio.create_task(sorter.wait_for_response(msg_id2))

        await asyncio.sleep(0.01)

        # Reject all
        error = RuntimeError("Test error")
        await sorter.reject_all(error)

        # Both should raise the error
        with pytest.raises(RuntimeError, match="Test error"):
            await task1

        with pytest.raises(RuntimeError, match="Test error"):
            await task2

    async def test_pending_count(self):
        """pending_count tracks number of pending requests."""
        sorter = MessageSorter()

        assert sorter.pending_count == 0

        msg_id = sorter.get_next_id()
        task = asyncio.create_task(sorter.wait_for_response(msg_id))
        await asyncio.sleep(0.01)

        assert sorter.pending_count == 1

        await sorter.resolve(msg_id, Ok(id=msg_id))
        await task

        assert sorter.pending_count == 0

    async def test_id_wraps_at_max(self):
        """Message ID wraps around at protocol maximum."""
        sorter = MessageSorter()
        sorter._next_id = 4294967295  # Max uint32

        id1 = sorter.get_next_id()
        id2 = sorter.get_next_id()

        assert id1 == 4294967295
        assert id2 == 1  # Wrapped back to 1 (not 0, which is reserved)
