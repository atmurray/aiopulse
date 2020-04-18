"""Acmeda Pulse Hub Interface."""
import asyncio
import binascii
import logging
from typing import (
    Any,
    List,
    Callable,
    Optional,
)
import functools

import async_timeout

import aiopulse.const as const
import aiopulse.utils as utils
import aiopulse.errors as errors
import aiopulse.elements as elements
import aiopulse.transport

_LOGGER = logging.getLogger(__name__)


class Hub:
    """Representation of an Acmeda Pulse Hub."""

    def __init__(
        self, host=None, loop: Optional[asyncio.events.AbstractEventLoop] = None
    ):
        """Init the hub."""
        self.loop: asyncio.events.AbstractEventLoop = (loop or asyncio.get_event_loop())
        self.topic = str.encode("Smart_Id1_y:")
        self.sequence = 4
        self.handshake = asyncio.Event()
        self.event_update = asyncio.Event()
        self.response_task = None
        self.running = False

        self.name = "Acmeda Pulse WiFi Hub"
        self.id = None
        self.host = host
        self.mac_address = None
        self.ip_address = None
        self.firmware_name = None
        self.wifi_module = None

        self.protocol = aiopulse.transport.HubTransportTcp(host)

        self.rollers = {}
        self.rooms = {}
        self.scenes = {}

        self.handshake.clear()
        self.update_callbacks: List[Callable] = []

    def callback_subscribe(self, callback):
        """Add a callback for hub updates."""
        self.update_callbacks.append(callback)

    def callback_unsubscribe(self, callback):
        """Remove a callback for hub updates."""
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)

    def async_add_job(
        self, target: Callable[..., Any], *args: Any
    ) -> Optional[asyncio.Future]:
        """Add a job from within the event loop.

        This method must be run in the event loop.

        target: target to call.
        args: parameters for method to call.
        """
        task = None

        # Check for partials to properly determine if coroutine function
        check_target = target
        while isinstance(check_target, functools.partial):
            check_target = check_target.func

        if asyncio.iscoroutine(check_target):
            task = self.loop.create_task(target)  # type: ignore
        elif asyncio.iscoroutinefunction(check_target):
            task = self.loop.create_task(target(*args))
        else:
            task = self.loop.run_in_executor(  # type: ignore
                None, target, *args
            )

        return task

    def notify_callback(self):
        """Tell callback that the hub has been updated."""
        for callback in self.update_callbacks:
            self.async_add_job(callback)

    @staticmethod
    async def discover(timeout=5):
        """Use a broadcast udp packet to find hubs on the lan."""
        discover_client = aiopulse.transport.HubTransportUdpBroadcast()

        await discover_client.connect()

        hubs = {}

        retries = 3

        try:
            with async_timeout.timeout(timeout * retries):
                for _ in range(1):
                    discover_client.send(const.HEADER + const.COMMAND_DISCOVER)
                    # discover_client.send(bytes.fromhex("000000030300001b"))
                    while True:
                        addr = None
                        try:
                            with async_timeout.timeout(timeout):
                                (_, addr) = await discover_client.receive()
                        except asyncio.TimeoutError:
                            pass

                        if addr and addr not in hubs:
                            _LOGGER.info(f"{addr[0]}: Discovered hub on port {addr[1]}")
                            try:
                                hub = Hub(addr[0])
                                await hub.connect()
                                await hub.disconnect()
                                hubs[addr] = hub
                                yield hub
                            except errors.CannotConnectException:
                                _LOGGER.warning(
                                    f"{hub.host}: Couldn't connect to discovered hub"
                                )
                            except errors.InvalidResponseException:
                                _LOGGER.warning(
                                    f"{hub.host}: Couldn't interrogate discovered hub"
                                )
        except asyncio.TimeoutError:
            pass
        _LOGGER.info("Discovery complete")

        await discover_client.close()

    async def connect(self, host=None):
        """Try and connect to the hub."""
        if host:
            self.host = host

        try:
            await self.protocol.connect(self.host)
        except OSError:
            raise errors.CannotConnectException

        if self.handshake.is_set():
            _LOGGER.warning(f"{self.host} Handshake already completed")
            return False

        if self.protocol.is_udp:  # udp
            # self.send_command(const.COMMAND_DISCOVER)
            # response = await self.get_response()
            self.send_command(const.COMMAND_CONNECT)
            raw_id = await self.get_response(const.RESPONSE_CONNECT)
        else:  # TCP
            self.send_command(const.COMMAND_CONNECT)
            raw_id = await self.get_response(const.RESPONSE_CONNECT)

        self.id = raw_id[2:].decode("utf-8")

        self.send_command(const.COMMAND_LOGIN + raw_id)
        response = await self.get_response(const.RESPONSE_LOGIN)

        if response[0] != 0:
            raise errors.InvalidResponseException

        self.send_command(
            const.COMMAND_SETID,
            bytes.fromhex("16000e0001000000000000000c000600120311073816ff9b"),
        )
        await self.get_response(const.RESPONSE_SETID)

        self.send_command(
            const.COMMAND_UNKNOWN1,
            bytes.fromhex("1100150002000000000000006002010030ffa9"),
        )
        await self.get_response(
            const.RESPONSE_UNKNOWN1
            + bytes.fromhex("06")
            + self.topic
            + bytes.fromhex("16000f0002000000000000000c000600120311073816ff9d")
        )
        await self.get_response(const.RESPONSE_SETID)

        _LOGGER.info(f"{self.host}: Handshake complete")
        self.handshake.set()

        return True

    async def disconnect(self):
        """Disconnect from the hub."""
        _LOGGER.debug(f"{self.host}: Disconnecting")
        await self.protocol.close()
        self.handshake.clear()
        _LOGGER.info(f"{self.host}: Disconnected")

    def send_command(self, command, message=None):
        """Send a command to the hub."""
        if message:
            self.protocol.send(
                const.HEADER + command + bytes.fromhex("05") + self.topic + message
            )
        else:
            self.protocol.send(const.HEADER + command)

    async def get_response(self, target_response=None):
        """Get a response, throw exception if it doesn't match expected response."""
        response = await self.protocol.receive()
        if not target_response:
            return response
        length = len(const.HEADER + target_response)
        if len(response) < length:
            raise errors.InvalidResponseException
        if response[0:length] != const.HEADER + target_response:
            raise errors.InvalidResponseException
        return response[length:]

    def response_hubinfo(self, message):
        """Receive start of hub information."""
        ptr = 10
        self.firmware_name, ptr = utils.unpack_string(message, ptr)
        ptr += 2
        _, ptr = utils.unpack_string(message, ptr)
        ptr += 2
        self.wifi_module, ptr = utils.unpack_string(message, ptr)
        ptr += 2
        self.mac_address, ptr = utils.unpack_string(message, ptr)
        ptr += 2
        self.ip_address, ptr = utils.unpack_string(message, ptr)

    def response_hubinfoend(self, message):
        """Receive end of hub information."""
        self.event_update.set()
        self.notify_callback()

    def response_roomlist(self, message):
        """Receive room list."""
        ptr = 12
        room_count, ptr = utils.unpack_int(message, ptr, 1)
        for _ in range(room_count):
            _, ptr = utils.unpack_bytes(message, ptr, 2)
            room_id, ptr = utils.unpack_string(message, ptr)
            _, ptr = utils.unpack_bytes(message, ptr, 4)
            icon, ptr = utils.unpack_int(message, ptr, 1)
            _, ptr = utils.unpack_bytes(message, ptr, 2)
            room_name, ptr = utils.unpack_string(message, ptr)
            if room_id not in self.rooms:
                self.rooms[room_id] = elements.Room(self, room_id)
            self.rooms[room_id].icon = icon
            self.rooms[room_id].name = room_name

    def response_scenelist(self, message):
        """Receive scene list."""
        ptr = 12
        scene_count, ptr = utils.unpack_int(message, ptr, 1)
        ptr += 2
        for _ in range(scene_count):
            scene_id, ptr = utils.unpack_string(message, ptr)
            _, ptr = utils.unpack_bytes(message, ptr, 4)
            icon, ptr = utils.unpack_int(message, ptr, 1)
            _, ptr = utils.unpack_bytes(message, ptr, 2)
            scene_name, ptr = utils.unpack_string(message, ptr)
            _, ptr = utils.unpack_bytes(message, ptr, 7)
            _, ptr = utils.unpack_bytes(message, ptr)
            _, ptr = utils.unpack_bytes(message, ptr, 2)
            if scene_id not in self.scenes:
                self.scenes[scene_id] = elements.Scene(self, scene_id)
            self.scenes[scene_id].icon = icon
            self.scenes[scene_id].name = scene_name

    def response_timerlist(self, message):
        """Receive timer list."""
        pass

    def response_roller_updated(self, message):
        """Receive change of roller information."""
        ptr = 2  # sequence?
        ptr += 6
        ptr += 2  # unknown field
        room_id, ptr = utils.unpack_string(message, ptr)
        ptr += 4  # unknown field
        roller_type, ptr = utils.unpack_int(message, ptr, 1)
        ptr += 2  # unknown field
        roller_name, ptr = utils.unpack_string(message, ptr)
        ptr += 10  # unknown field
        roller_id, ptr = utils.unpack_int(message, ptr, 6)
        ptr += 4
        # battery level seems to be out of 25, convert to percentage
        roller_battery, ptr = utils.unpack_int(message, ptr, 1)
        roller_battery *= 4
        ptr += 5  # unknown field
        roller_percent, ptr = utils.unpack_int(message, ptr, 1)
        roller_flags, ptr = utils.unpack_int(message, ptr, 1)
        ptr += 2  # checksum
        if roller_id not in self.rollers:
            self.rollers[roller_id] = elements.Roller(self, roller_id)
        self.rollers[roller_id].name = roller_name
        # doesn't seem to come through in update
        # self.rollers[roller_id].serial = roller_serial
        self.rollers[roller_id].room_id = room_id
        self.rollers[roller_id].type = roller_type
        if room_id in self.rooms:
            self.rollers[roller_id].room = self.rooms[room_id]
        else:
            self.rollers[roller_id].room = None
        self.rollers[roller_id].battery = roller_battery
        self.rollers[roller_id].closed_percent = roller_percent
        self.rollers[roller_id].flags = roller_flags
        self.rollers[roller_id].notify_callback()
        self.notify_callback()

    def response_rollerlist(self, message):
        """Receive roller blind list."""
        ptr = 2  # sequence?
        ptr += 10
        roller_count, ptr = utils.unpack_int(message, ptr, 1)
        for _ in range(roller_count):
            ptr += 4  # unknown field
            roller_id, ptr = utils.unpack_int(message, ptr, 6)
            ptr += 2  # unknown field
            room_id, ptr = utils.unpack_string(message, ptr)
            ptr += 4  # unknown field
            roller_type, ptr = utils.unpack_int(message, ptr, 1)
            ptr += 2  # unknown field
            roller_name, ptr = utils.unpack_string(message, ptr)
            ptr += 8  # unknown field
            roller_serial, ptr = utils.unpack_string(message, ptr)
            ptr += 4
            # battery level seems to be out of 25, convert to percentage
            roller_battery, ptr = utils.unpack_int(message, ptr, 1)
            roller_battery *= 4
            ptr += 5  # unknown field
            roller_percent, ptr = utils.unpack_int(message, ptr, 1)
            roller_flags, ptr = utils.unpack_int(message, ptr, 1)
            if roller_id not in self.rollers:
                self.rollers[roller_id] = elements.Roller(self, roller_id)
            self.rollers[roller_id].name = roller_name
            self.rollers[roller_id].serial = roller_serial
            self.rollers[roller_id].room_id = room_id
            self.rollers[roller_id].type = roller_type
            if room_id in self.rooms:
                self.rollers[roller_id].room = self.rooms[room_id]
            else:
                self.rollers[roller_id].room = None
            self.rollers[roller_id].battery = roller_battery
            self.rollers[roller_id].closed_percent = roller_percent
            self.rollers[roller_id].flags = roller_flags
            self.rollers[roller_id].notify_callback()

    def response_authinfo(self, message):
        """Receive acmeda account information."""
        ptr = 15
        _, ptr = utils.unpack_string(message, ptr)

    def response_position(self, message):
        """Receive change of roller position information."""
        ptr = 12
        roller_id, ptr = utils.unpack_int(message, ptr, 6)
        ptr += 10
        roller_percent, ptr = utils.unpack_int(message, ptr, 1)
        roller_flags, ptr = utils.unpack_int(message, ptr, 1)
        if roller_id in self.rollers:
            self.rollers[roller_id].closed_percent = roller_percent
            self.rollers[roller_id].flags = roller_flags
            self.rollers[roller_id].notify_callback()

    def response_calibration(self, message):
        """Receive change of roller calibration information."""
        ptr = 12
        roller_id, ptr = utils.unpack_int(message, ptr, 6)
        ptr += 5  # letter A and then 4 bytes
        ptr += 5  # letter B and then 4 bytes
        ptr += 5  # letter C and then 4 bytes
        ptr += 5  # unknown
        ptr += 8  # unknown
        ptr += 2  # checksum

    def response_discover(self, message):
        """Receive after discover broadcast packet."""
        pass

    class Receiver:
        """Wraps around a function that gets called for received messages."""

        def __init__(self, name, function):
            """Constructor for message receiver class."""
            self.name = name
            self.function = function

        def execute(self, target, message):
            """Executor function."""
            self.function(target, message)

    msgmap = {
        bytes.fromhex("1600"): Receiver("hub info", response_hubinfo),
        bytes.fromhex("4101"): Receiver("hub info end", response_hubinfoend),
        bytes.fromhex("0101"): Receiver("room list", response_roomlist),
        bytes.fromhex("3301"): Receiver("scene list", response_scenelist),
        bytes.fromhex("2101"): Receiver("roller list", response_rollerlist),
        bytes.fromhex("0800"): Receiver("auth info", response_authinfo),
        bytes.fromhex("2301"): Receiver("position", response_position),
        bytes.fromhex("2501"): Receiver("roller info updated", response_roller_updated),
        bytes.fromhex("2b01"): Receiver("calibration", response_calibration),
        bytes.fromhex("0f00"): Receiver("discover response", response_discover),
    }

    def rec_ping(self, message):
        """Receive a ping from the hub."""
        _LOGGER.debug(f"{self.host}: Received hub ping response")
        pass

    def rec_message(self, message):
        """Receive and decode a message from the hub."""
        if message:
            if message[0] != 6:
                _LOGGER.error(f"{self.host}: First message byte not 0x06")
                raise errors.InvalidResponseException

            if message[1 : (1 + len(self.topic))] != self.topic:
                _LOGGER.error(
                    f"{self.host}: Received invalid topic: "
                    f"{message[1 : (1 + len(self.topic))]}, "
                    f"expected: {self.topic}"
                )
                raise errors.InvalidResponseException

            ptr = 1 + len(self.topic)
            _, ptr = utils.unpack_int(message, 2, ptr)
            mtype = message[ptr : (ptr + 2)]
            ptr = ptr + 2
            if mtype in self.msgmap:
                _LOGGER.info(f"{self.host}: Parsing {self.msgmap[mtype].name}")
                self.msgmap[mtype].execute(self, message[ptr:])
            else:
                _LOGGER.warning(
                    f"{self.host}: Unable to parse message %s message %s",
                    binascii.hexlify(mtype),
                    binascii.hexlify(message),
                )

    respmap = {
        const.RESPONSE_PING: Receiver("ping", rec_ping),
        bytes.fromhex("01000091"): Receiver("scene list", rec_message),
        bytes.fromhex("02000091"): Receiver("roller list", rec_message),
        bytes.fromhex("03000091"): Receiver("acknowledge", rec_message),
        bytes.fromhex("04000091"): Receiver(
            "04000091", rec_message
        ),  # Unknown from quentinsf
        bytes.fromhex("23000091"): Receiver("hub info end", rec_message),
        bytes.fromhex("28000091"): Receiver("discover", rec_message),
        bytes.fromhex("34000091"): Receiver("moving", rec_message),
        bytes.fromhex("42000091"): Receiver("unknown", rec_message),
        bytes.fromhex("43000091"): Receiver("account info", rec_message),
        bytes.fromhex("44000091"): Receiver("response move", rec_message),
        const.RESPONSE_DISCOVER: Receiver("discover", rec_message),
        bytes.fromhex("56000091"): Receiver("roller room change", rec_message),
        bytes.fromhex("57000091"): Receiver("roller name change", rec_message),
        bytes.fromhex("59000091"): Receiver("roller name change", rec_message),
        bytes.fromhex("5b000091"): Receiver(
            "room list", rec_message
        ),  # after adding second room
        bytes.fromhex("5F000091"): Receiver("hub info", rec_message),
        bytes.fromhex("60000091"): Receiver("room list", rec_message),
        bytes.fromhex("62000091"): Receiver(
            "62000091", rec_message
        ),  # Unknown from quentinsf
        bytes.fromhex("63000091"): Receiver("hub info", rec_message),
        bytes.fromhex("65000091"): Receiver("timer list", rec_message),
        bytes.fromhex("6f000091"): Receiver("timer list", rec_message),
    }

    def response_parse(self, response):
        """Decode response."""
        if response[0:4] != bytes.fromhex("00000003"):
            _LOGGER.warning(
                f"{self.host}: Unknown response: {binascii.hexlify(response[0:4])}"
            )
            raise errors.InvalidResponseException

        try:
            message_type = response[4:8]

            if message_type[0] > 127:
                message_type = response[5:9]
                message = response[9:]
            else:
                message = response[8:]

            mtype = bytes(message_type)
            if mtype in Hub.respmap:
                _LOGGER.debug(
                    f"{self.host}: Received response: {binascii.hexlify(mtype)} "
                    f"{Hub.respmap[mtype].name} content: {message}"
                )
                Hub.respmap[mtype].execute(self, message)
            else:
                _LOGGER.warning(
                    f"{self.host}: Received unknown response type: "
                    f"{binascii.hexlify(mtype)}, "
                    f"trying to decode anyway. Message: {binascii.hexlify(message)}"
                )
                self.rec_message(message)
        except Exception:
            logging.exception(
                f"{self.host}: Exception raised when parsing response: "
                f"{binascii.hexlify(response)}"
            )
            raise errors.InvalidResponseException

    async def response_parser(self):
        """Receive a response from the hub and work out what message it is."""
        try:
            _LOGGER.debug(f"{self.host}: Starting response parser")
            while True:
                try:
                    with async_timeout.timeout(30):
                        response = await self.protocol.receive()
                    if len(response) > 0:
                        self.response_parse(response)
                except asyncio.TimeoutError:
                    self.send_command(const.COMMAND_PING)
                except errors.InvalidResponseException:
                    self.send_command(const.COMMAND_PING)
        except errors.NotConnectedException:
            _LOGGER.debug(f"{self.host}: Disconnected, stopping parser")

    async def update(self):
        """Update all hub information (includes scenes, rooms, and rollers)."""
        self.event_update.clear()
        await self.send_payload(
            const.COMMAND_GET_HUB_INFO,
            bytes.fromhex("F000"),
            bytes.fromhex("000000000000FF"),
        )
        _LOGGER.debug(f"{self.host}: Hub update command sent")

    async def send_payload(self, command, message_type, message):
        """Send payload to the hub."""
        if not self.running:
            raise errors.NotRunningException
        await self.handshake.wait()
        data = message_type + utils.pack_int(self.sequence, 2) + message
        checksum = bytes([sum(data) & 0xFF])
        self.sequence += 2
        command_header = const.HEADER + command + bytes.fromhex("05") + self.topic
        length = len(data) + 1  # bytes.fromhex('0C00')
        self.protocol.send(command_header + utils.pack_int(length, 2) + data + checksum)

    async def run(self):
        """Start hub by connecting then awaiting for messages.

        Runs until the stop() method is called.
        """
        if self.running:
            _LOGGER.warning(f"{self.host}: Already running")
            return
        self.running = True
        while self.running:
            try:
                _LOGGER.info(f"{self.host}: Connecting")
                await self.connect()
            except errors.CannotConnectException:
                _LOGGER.warning(f"{self.host}: Connect failed")
                continue
            except errors.InvalidResponseException:
                _LOGGER.warning(f"{self.host}: Handshake failed")
                await self.disconnect()
                continue
            try:
                await self.update()
                await self.response_parser()
            except errors.InvalidResponseException:
                _LOGGER.warning(f"{self.host}: Protocol error")
            if self.running:
                await self.disconnect()
                await asyncio.sleep(5)
        _LOGGER.debug(f"{self.host}: Stopped")

    async def stop(self):
        """Tell hub to stop and await for it to disconnect."""
        if not self.running:
            _LOGGER.warning(f"{self.host}: Already stopped")
            return
        _LOGGER.debug(f"{self.host}: Stopping")
        self.running = False
        await self.disconnect()
