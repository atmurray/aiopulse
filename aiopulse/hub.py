"""Acmeda Pulse Hub Interface."""

import asyncio
import logging
import warnings
from collections.abc import AsyncGenerator, Callable

# from aiopulse import Roller, Room, Scene, Timer
import aiopulse
import aiopulse.const as const
import aiopulse.errors as errors
import aiopulse.transport
import aiopulse.utils as utils
from aiopulse.callbacks import CallbackMixin
from aiopulse.const import CommandType, ResponseType

_LOGGER = logging.getLogger(__name__)


class Hub(CallbackMixin):
    """Representation of an Acmeda Pulse Hub."""

    def __init__(
        self,
        host: str | None = None,
        loop: asyncio.events.AbstractEventLoop | None = None,
    ) -> None:
        """Init the hub."""
        super().__init__()
        if loop is not None:
            warnings.warn(
                "loop parameter is deprecated and will be removed in v0.6.0",
                DeprecationWarning,
                stacklevel=2,
            )
            self.loop: asyncio.events.AbstractEventLoop = loop
        else:
            self.loop = asyncio.get_running_loop()
        self.topic: bytes = str.encode("Smart_Id1_y:")
        self.sequence: int = 4
        self.handshake: asyncio.Event = asyncio.Event()
        self.command_lock: asyncio.Lock = asyncio.Lock()
        self.health_lock: asyncio.Lock = asyncio.Lock()
        self.response_task: asyncio.Task[None] | None = None
        self.running: bool = False

        self.id: str | None = None
        self.host: str | None = host
        self.mac_address: str | None = None
        self.ip_address: str | None = None
        self.firmware_name: str | None = None
        self.wifi_module: str | None = None

        self.protocol = aiopulse.transport.HubTransportTcp(host)

        self.rollers: dict[int, aiopulse.Roller] = {}
        self.rooms: dict[bytes, aiopulse.Room] = {}
        self.scenes: dict[bytes, aiopulse.Scene] = {}
        self.timers: dict[bytes, aiopulse.Timer] = {}

        self.handshake.clear()

    def __str__(self) -> str:
        """Returns string representation of the hub."""
        return (
            f"ID: {self.id} "
            f"Host: {self.host} "
            f"MAC: {self.mac_address} "
            f"Firmware: {self.firmware_name} "
            f"WiFi: {self.wifi_module} "
        )

    @staticmethod
    async def discover(  # type: ignore[misc]
        timeout: int = 5,
        loop: asyncio.events.AbstractEventLoop | None = None,
        bind_address: str | None = None,
    ) -> AsyncGenerator["Hub", None]:
        """Use a broadcast udp packet to find hubs on the lan.

        Args:
            timeout: Timeout for each discovery attempt in seconds.
            loop: Deprecated. The event loop to use.
            bind_address: Local interface to bind to (e.g., '10.0.0.24').
                         If None, binds to all interfaces.
        """
        discover_client = aiopulse.transport.HubTransportUdpBroadcast()

        await discover_client.connect(bind_address=bind_address)

        hubs: dict[tuple[str, int], Hub] = {}

        retries = 3

        try:
            async with asyncio.timeout(timeout * retries):
                for _ in range(1):
                    discover_client.send(
                        const.HEADER + CommandType.DISCOVER.to_bytes(4, "big")
                    )
                    _LOGGER.info("Discovering hubs on the LAN...")
                    while True:
                        addr = None
                        try:
                            async with asyncio.timeout(timeout):
                                (response, addr) = await discover_client.receive()
                                _LOGGER.debug(
                                    "%s: Received discover response: %s",
                                    addr[0],
                                    response.hex(),
                                )
                        except TimeoutError:
                            pass

                        if addr and addr not in hubs:
                            _LOGGER.info(f"{addr[0]}: Discovered hub on port {addr[1]}")
                            hub: Hub | None = None
                            try:
                                hub = Hub(addr[0], loop)
                                discover_client.send(
                                    const.HEADER
                                    + CommandType.DISCOVER.to_bytes(4, "big")
                                )
                                await hub.connect()
                                await hub.disconnect()
                                hubs[addr] = hub
                                yield hub
                            except errors.CannotConnectException:
                                _LOGGER.warning(
                                    f"{addr[0]}: Couldn't connect to discovered hub"
                                )
                            except errors.InvalidResponseException:
                                _LOGGER.warning(
                                    f"{addr[0]}: Couldn't interrogate discovered hub"
                                )
        except TimeoutError:
            pass
        _LOGGER.info("Discovery complete")

        await discover_client.close()

    async def connect(self, host: str | None = None) -> bool:
        """Try and connect to the hub."""
        if host:
            self.host = host

        try:
            await self.protocol.connect(self.host)
        except OSError as inst:
            raise errors.CannotConnectException(str(inst))

        if self.handshake.is_set():
            _LOGGER.warning(f"{self.host} Handshake already completed")
            return False

        if self.protocol.is_udp:  # udp
            # self.protocol.send(const.HEADER + const.COMMAND_DISCOVER)
            # response = await self.get_response()
            self.protocol.send(const.HEADER + CommandType.CONNECT.to_bytes(4, "big"))
            raw_id = await self.get_response(ResponseType.CONNECT.to_bytes(4, "big"))
        else:  # TCP
            self.protocol.send(const.HEADER + CommandType.CONNECT.to_bytes(4, "big"))
            raw_id = await self.get_response(ResponseType.CONNECT.to_bytes(4, "big"))

        self.id = raw_id[2:].decode("utf-8")

        self.protocol.send(const.HEADER + CommandType.LOGIN.to_bytes(4, "big") + raw_id)
        response = await self.get_response(ResponseType.LOGIN.to_bytes(4, "big"))

        if response[0] != 0:
            raise errors.InvalidResponseException

        self.protocol.send(
            const.HEADER
            + CommandType.SETID.to_bytes(4, "big")
            + bytes.fromhex("05")
            + self.topic
            + bytes.fromhex("16000e0001000000000000000c000600120311073816ff9b")
        )

        response = await self.get_response(ResponseType.SETID.to_bytes(4, "big"))
        self.response_parse(response)

        self.protocol.send(
            const.HEADER
            + CommandType.UNKNOWN1.to_bytes(4, "big")
            + bytes.fromhex("05")
            + self.topic
            + bytes.fromhex("1100150002000000000000006002010030ffa9")
        )

        response = await self.get_response(
            ResponseType.UNKNOWN1.to_bytes(4, "big")
            + bytes.fromhex("06")
            + self.topic
            + bytes.fromhex("16000f0002000000000000000c000600120311073816ff9d")
        )
        self.response_parse(response)

        response = await self.get_response(ResponseType.SETID.to_bytes(4, "big"))
        self.response_parse(response)

        _LOGGER.info(f"{self.host}: Handshake complete")
        self.handshake.set()

        return True

    async def disconnect(self) -> None:
        """Disconnect from the hub."""
        _LOGGER.debug(f"{self.host}: Disconnecting")
        await self.protocol.close()
        self.handshake.clear()
        _LOGGER.info(f"{self.host}: Disconnected")

    async def get_response(self, target_response: bytes | None = None) -> bytes:
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

    def response_hubinfo(self, message: bytes) -> None:
        """Receive start of hub information."""
        if len(message) < 10:
            raise errors.InvalidResponseException(
                f"Hub info message too short: {len(message)} bytes",
                response=message,
            )
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
        _LOGGER.info(f"{self.host}: Hub info: {self}")
        self.notify_callback(const.UpdateType.info)

    def response_roller_updated(self, message: bytes) -> None:
        """Receive change of roller information."""
        if len(message) < 10:
            raise errors.InvalidResponseException(
                f"Roller updated message too short: {len(message)} bytes",
                response=message,
            )
        ptr = 2  # sequence?
        ptr += 4
        ptr += 2  # unknown field
        ptr += 2  # unknown field
        room_id, ptr = utils.unpack_bytes(message, ptr)
        ptr += 4  # unknown field
        roller_type, ptr = utils.unpack_int(message, ptr, 1)
        ptr += 2  # unknown field
        roller_name, ptr = utils.unpack_string(message, ptr)
        ptr += 10  # unknown field
        roller_id, ptr = utils.unpack_int(message, ptr, 6)
        roller_percent, ptr = utils.unpack_roller_percent(message, ptr)
        roller_flags, ptr = utils.unpack_int(message, ptr, 1)
        ptr += 2  # checksum
        if roller_id not in self.rollers:
            self.rollers[roller_id] = aiopulse.Roller(self, roller_id)
        roller = self.rollers[roller_id]
        roller.name = roller_name
        # doesn't seem to come through in update
        # roller.serial = roller_serial
        roller.room_id = room_id
        roller.type = roller_type
        if room_id in self.rooms:
            roller.room = self.rooms[room_id]
        else:
            roller.room = None
        roller.closed_percent = roller_percent
        roller.flags = roller_flags
        _LOGGER.info(f"{self.host}: Roller updated: {roller}")
        roller.notify_callback()
        self.notify_callback(const.UpdateType.rollers)

    def response_discard(self, message: bytes) -> None:
        """Discard response."""

    def response_roomlist(self, message: bytes) -> None:
        """Receive room list."""
        if len(message) < 12:
            raise errors.InvalidResponseException(
                f"Room list message too short: {len(message)} bytes",
                response=message,
            )
        ptr = 12
        room_count, ptr = utils.unpack_int(message, ptr, 1)
        for _ in range(room_count):
            _, ptr = utils.unpack_bytes(message, ptr, 2)
            room_id, ptr = utils.unpack_bytes(message, ptr)
            _, ptr = utils.unpack_bytes(message, ptr, 4)
            icon, ptr = utils.unpack_int(message, ptr, 1)
            _, ptr = utils.unpack_bytes(message, ptr, 2)
            room_name, ptr = utils.unpack_string(message, ptr)
            if room_id not in self.rooms:
                self.rooms[room_id] = aiopulse.Room(self, room_id)
            self.rooms[room_id].icon = icon
            self.rooms[room_id].name = room_name
            _LOGGER.info(f"{self.host}: Room updated: {self.rooms[room_id]}")
        self.notify_callback(const.UpdateType.rooms)

    def response_rollerlist(self, message: bytes) -> None:
        """Receive roller blind list."""
        if len(message) < 12:
            raise errors.InvalidResponseException(
                f"Roller list message too short: {len(message)} bytes",
                response=message,
            )
        ptr = 2  # sequence?
        ptr += 10
        roller_count, ptr = utils.unpack_int(message, ptr, 1)
        for _ in range(roller_count):
            start = ptr
            ptr += 4  # unknown field
            roller_id, ptr = utils.unpack_int(message, ptr, 6)
            ptr += 2  # unknown field
            room_id, ptr = utils.unpack_bytes(message, ptr)
            ptr += 4  # unknown field
            roller_type, ptr = utils.unpack_int(message, ptr, 1)
            ptr += 2  # unknown field
            roller_name, ptr = utils.unpack_string(message, ptr)
            ptr += 8  # unknown field
            roller_serial, ptr = utils.unpack_string(message, ptr)
            roller_percent, ptr = utils.unpack_roller_percent(message, ptr)
            roller_flags, ptr = utils.unpack_int(message, ptr, 1)

            _LOGGER.debug(f"{message[start:ptr].hex()}")
            if roller_id not in self.rollers:
                self.rollers[roller_id] = aiopulse.Roller(self, roller_id)
            roller = self.rollers[roller_id]
            roller.name = roller_name
            roller.serial = roller_serial
            roller.room_id = room_id
            roller.type = roller_type
            if room_id in self.rooms:
                roller.room = self.rooms[room_id]
            else:
                roller.room = None
            roller.closed_percent = roller_percent
            roller.flags = roller_flags
            _LOGGER.info(f"{self.host}: Roller updated: {roller}")
            roller.notify_callback()

        self.notify_callback(const.UpdateType.rollers)

    def response_scenelist(self, message: bytes) -> None:
        """Receive scene list."""
        if len(message) < 12:
            raise errors.InvalidResponseException(
                f"Scene list message too short: {len(message)} bytes",
                response=message,
            )
        ptr = 0
        _, ptr = utils.unpack_bytes(message, ptr, 12)
        scene_count, ptr = utils.unpack_int(message, ptr, 1)
        for _ in range(scene_count):
            _, ptr = utils.unpack_bytes(message, ptr, 2)
            scene_id, ptr = utils.unpack_bytes(message, ptr)
            _, ptr = utils.unpack_bytes(message, ptr, 4)
            icon, ptr = utils.unpack_int(message, ptr, 1)
            _, ptr = utils.unpack_bytes(message, ptr, 2)
            scene_name, ptr = utils.unpack_string(message, ptr)
            _, ptr = utils.unpack_bytes(message, ptr, 5)
            # Not sure what is being read next but it seems to be variable
            while message[ptr : ptr + 2] == b"R\x02":
                _, ptr = utils.unpack_bytes(message, ptr, 2)
                _, ptr = utils.unpack_bytes(message, ptr)

            if scene_id not in self.scenes:
                self.scenes[scene_id] = aiopulse.Scene(self, scene_id)
            self.scenes[scene_id].icon = icon
            self.scenes[scene_id].name = scene_name
            _LOGGER.info(f"{self.host}: Scene updated: {self.scenes[scene_id]}")
        _, ptr = utils.unpack_bytes(message, ptr, 2)
        self.notify_callback(const.UpdateType.scenes)

    def response_timerlist(self, message: bytes) -> None:
        """Receive timer list."""
        if len(message) < 12:
            raise errors.InvalidResponseException(
                f"Timer list message too short: {len(message)} bytes",
                response=message,
            )
        ptr = 0
        _, ptr = utils.unpack_bytes(message, ptr, 12)
        timer_count, ptr = utils.unpack_int(message, ptr, 1)
        for _ in range(timer_count):
            _, ptr = utils.unpack_bytes(message, ptr, 2)
            timer_id, ptr = utils.unpack_bytes(message, ptr)
            _, ptr = utils.unpack_bytes(message, ptr, 4)
            icon, ptr = utils.unpack_int(message, ptr, 1)
            _, ptr = utils.unpack_bytes(message, ptr, 2)
            timer_name, ptr = utils.unpack_string(message, ptr)
            _, ptr = utils.unpack_bytes(message, ptr, 4)  # '   !\x02\x01\x00'
            state, ptr = utils.unpack_int(message, ptr, 1)
            _, ptr = utils.unpack_bytes(message, ptr, 4)  # '   ;\x02\x01\x00'
            hour, ptr = utils.unpack_int(message, ptr, 1)
            _, ptr = utils.unpack_bytes(message, ptr, 4)  # '   <\x02\x01\x00'
            minute, ptr = utils.unpack_int(message, ptr, 1)
            _, ptr = utils.unpack_bytes(message, ptr, 4)  # '   "\x02\x04\x00'
            days, ptr = utils.unpack_int(message, ptr, 1)
            _, ptr = utils.unpack_bytes(message, ptr, 4)  # '\x00\x00\x00   ='
            _, ptr = utils.unpack_bytes(message, ptr, 2)  # '\x02\x01'
            timer_type, ptr = utils.unpack_bytes(message, ptr, 4)

            entity: aiopulse.Roller | aiopulse.Scene | None = None
            if timer_type == b"\x00\x01\x03\x01":  # Device Timer
                _, ptr = utils.unpack_bytes(message, ptr, 8)
                percent, ptr = utils.unpack_int(message, ptr, 1)
                _, ptr = utils.unpack_bytes(message, ptr, 5)
                roller_id, ptr = utils.unpack_int(message, ptr, 6)
                _LOGGER.debug(f"Timer {timer_name} at {percent}%")
                if roller_id in self.rollers:
                    entity = self.rollers[roller_id]
            elif timer_type == b"\x00\x00\x10\x02":  # Scene Timer
                scene_id, ptr = utils.unpack_bytes(message, ptr)
                if scene_id in self.scenes:
                    entity = self.scenes[scene_id]
            else:
                _LOGGER.error(
                    f"{self.host}: Unexpected timer type received: {timer_type.hex()}"
                )
                return

            if timer_id not in self.timers:
                self.timers[timer_id] = aiopulse.Timer(self, timer_id)
            self.timers[timer_id].icon = icon
            self.timers[timer_id].name = timer_name
            self.timers[timer_id].state = state
            self.timers[timer_id].hour = hour
            self.timers[timer_id].minute = minute
            self.timers[timer_id].days = days
            self.timers[timer_id].entity = entity

            _LOGGER.info(f"Timer added: {self.timers[timer_id]}")
        _, ptr = utils.unpack_bytes(message, ptr, 2)
        self.notify_callback(const.UpdateType.timers)

    def response_authinfo(self, message: bytes) -> None:
        """Receive acmeda account information."""
        if len(message) < 15:
            raise errors.InvalidResponseException(
                f"Auth info message too short: {len(message)} bytes",
                response=message,
            )
        ptr = 15
        _, ptr = utils.unpack_string(message, ptr)

    def response_position(self, message: bytes) -> None:
        """Receive change of roller position information."""
        if len(message) < 12:
            raise errors.InvalidResponseException(
                f"Position message too short: {len(message)} bytes",
                response=message,
            )
        ptr = 12
        roller_id, ptr = utils.unpack_int(message, ptr, 6)
        roller_percent, ptr = utils.unpack_roller_percent(message, ptr)
        roller_flags, ptr = utils.unpack_int(message, ptr, 1)
        if roller_id in self.rollers:
            self.rollers[roller_id].closed_percent = roller_percent
            self.rollers[roller_id].flags = roller_flags
            self.rollers[roller_id].notify_callback()
            _LOGGER.info(f"{self.host}: Roller updated: {self.rollers[roller_id]}")
        else:
            _LOGGER.warning(
                f"{self.host}: Received position update for unknown roller {roller_id}"
            )

    def response_rollerhealth(self, message: bytes) -> None:
        """Receive change of roller health information."""
        if len(message) < 12:
            raise errors.InvalidResponseException(
                f"Roller health message too short: {len(message)} bytes",
                response=message,
            )
        ptr = 12
        roller_id, ptr = utils.unpack_int(message, ptr, 6)
        # letter A and then 4 bytes
        unknown, ptr = utils.unpack_bytes(message, ptr, 5)
        _LOGGER.debug(f"{unknown.hex()}")
        # letter B and then 4 bytes
        unknown, ptr = utils.unpack_bytes(message, ptr, 5)
        _LOGGER.debug(f"{unknown.hex()}")
        # letter C and then 4 bytes
        unknown, ptr = utils.unpack_bytes(message, ptr, 5)
        _LOGGER.debug(f"{unknown.hex()}")
        # unknown
        unknown, ptr = utils.unpack_bytes(message, ptr, 3)
        _LOGGER.debug(f"{unknown.hex()}")
        # battery level
        charge_int, ptr = utils.unpack_int(message, ptr, 1)
        charge_fraction, ptr = utils.unpack_int(message, ptr, 1)
        charge: float = charge_int + charge_fraction / 256.0
        roller_battery = round(
            min(100, max(0, 100.0 * (charge - 9.45) / (12.375 - 9.45)))
        )
        _LOGGER.debug(f"Battery: {charge} {roller_battery}")
        # unknown
        unknown, ptr = utils.unpack_bytes(message, ptr, 8)
        _LOGGER.debug(f"{unknown.hex()}")
        ptr += 2  # checksum
        if roller_id in self.rollers:
            self.rollers[roller_id].battery = roller_battery
            _LOGGER.info(
                f"{self.host}: Roller health updated: {self.rollers[roller_id]}"
            )
            self.rollers[roller_id].health_updated()
            self.rollers[roller_id].notify_callback()
        if self.health_lock.locked():
            self.health_lock.release()

    def response_discover(self, message: bytes) -> None:
        """Receive after discover broadcast packet."""
        if len(message) < 10:
            raise errors.InvalidResponseException(
                f"Discover message too short: {len(message)} bytes",
                response=message,
            )
        ptr = 0
        _, ptr = utils.unpack_bytes(message, ptr, 10)
        _, ptr = utils.unpack_bytes(message, ptr)
        pass

    class Receiver:
        """Wraps around a function that gets called for received messages."""

        def __init__(self, name: str, function: "Callable[[Hub, bytes], None]") -> None:
            """Constructor for message receiver class."""
            self.name = name
            self.function = function

        def execute(self, target: "Hub", message: bytes) -> None:
            """Executor function."""
            self.function(target, message)

    msgmap = {
        bytes.fromhex("1600"): Receiver("hub info", response_hubinfo),
        bytes.fromhex("0d00"): Receiver("hub info updated", response_discard),
        bytes.fromhex("0101"): Receiver("room list", response_roomlist),
        bytes.fromhex("3301"): Receiver("scene list", response_scenelist),
        bytes.fromhex("2101"): Receiver("roller list", response_rollerlist),
        bytes.fromhex("4101"): Receiver("timer list", response_timerlist),
        bytes.fromhex("0800"): Receiver("auth info", response_authinfo),
        bytes.fromhex("2301"): Receiver("position", response_position),
        bytes.fromhex("2501"): Receiver("roller info updated", response_roller_updated),
        bytes.fromhex("4301"): Receiver("timer created", response_discard),
        bytes.fromhex("4501"): Receiver("timer device updated", response_discard),
        bytes.fromhex("4901"): Receiver("timer info updated", response_discard),
        bytes.fromhex("4701"): Receiver("timer deleted", response_discard),
        bytes.fromhex("2b01"): Receiver("roller health", response_rollerhealth),
        bytes.fromhex("0f00"): Receiver("discover response", response_discover),
    }

    def rec_ping(self, message: bytes) -> None:
        """Receive a ping from the hub."""
        _LOGGER.debug(f"{self.host}: Received hub ping response")

    def rec_message(self, message: bytes) -> None:
        """Receive and decode a message from the hub."""
        if message:
            if message[0] != 6:
                _LOGGER.error(f"{self.host}: First message byte not 0x06")
                raise errors.InvalidResponseException

            if message[1 : (1 + len(self.topic))] != self.topic:
                _LOGGER.error(
                    f"{self.host}: Received invalid topic: "
                    f"{message[1 : (1 + len(self.topic))].hex()}, "
                    f"expected: {self.topic.hex()}"
                )
                raise errors.InvalidResponseException

            ptr = 1 + len(self.topic)
            _, ptr = utils.unpack_int(message, ptr, 2)
            mtype = message[ptr : (ptr + 2)]
            ptr = ptr + 2
            if mtype in self.msgmap:
                _LOGGER.info(f"{self.host}: Parsing {self.msgmap[mtype].name}")
                self.msgmap[mtype].execute(self, message[ptr:])
            else:
                _LOGGER.warning(
                    "%s: Unable to parse message %s message %s",
                    self.host,
                    mtype.hex(),
                    message.hex(),
                )
        else:
            """message is the acknowledgement of a command"""
            if self.command_lock.locked():
                self.command_lock.release()

    respmap = {
        22: Receiver("ping", rec_ping),
        145: Receiver("message", rec_message),
    }

    def response_parse(self, response: bytes) -> None:
        """Decode response."""
        while response:
            ptr = 0
            header, ptr = utils.unpack_bytes(response, ptr, 4)
            if header != bytes.fromhex("00000003"):
                _LOGGER.warning(f"{self.host}: Unknown response: {response[0:4].hex()}")
                raise errors.InvalidResponseException

            try:
                msg_len, ptr = utils.unpack_int(response, ptr, 1)
                msg_blocks = 1

                if msg_len > 127:
                    msg_blocks, ptr = utils.unpack_int(response, ptr, 1)

                msg_end = ptr + msg_len + 128 * (msg_blocks - 1)

                if msg_end > len(response):
                    raise errors.InvalidResponseException

                _, ptr = utils.unpack_bytes(response, ptr, 2)
                mtype, ptr = utils.unpack_int(response, ptr, 1)

                message = response[ptr:msg_end]
                response = response[msg_end:]

                if mtype in Hub.respmap:
                    _LOGGER.debug(
                        f"{self.host}: Received response: {mtype} "
                        f"{Hub.respmap[mtype].name} content: {message.hex()}"
                    )
                    Hub.respmap[mtype].execute(self, message)
                else:
                    _LOGGER.warning(
                        f"{self.host}: Received unknown response type: "
                        f"{mtype}, "
                        f"trying to decode anyway. Message: {message.hex()}"
                    )
                    self.rec_message(message)

            except Exception:
                logging.exception(
                    f"{self.host}: Exception raised when parsing response: "
                    f"{response.hex()}"
                )
                raise errors.InvalidResponseException

    async def response_parser(self) -> None:
        """Receive a response from the hub and work out what message it is."""
        _LOGGER.debug(f"{self.host}: Starting response parser")
        while self.handshake.is_set():
            """Only catch exceptions that can be recovered from without reconnecting"""
            try:
                async with asyncio.timeout(30):
                    response = await self.get_response()
                if len(response) > 0:
                    self.response_parse(response)
            except TimeoutError:
                _LOGGER.debug(f"{self.host}: Receive timeout, sending ping keepalive")
                self.protocol.send(const.HEADER + CommandType.PING.to_bytes(4, "big"))
            except errors.InvalidResponseException:
                _LOGGER.debug(f"{self.host}: Invalid response, sending ping keepalive")
                self.protocol.send(const.HEADER + CommandType.PING.to_bytes(4, "big"))

    async def update(self) -> None:
        """Update all hub information (includes scenes, rooms, and rollers)."""
        await self.send_command(
            CommandType.GET_HUB_INFO.to_bytes(4, "big"),
            bytes.fromhex("F000"),
            bytes.fromhex("000000000000FF"),
        )
        _LOGGER.debug(f"{self.host}: Hub update command sent")

    async def send_command(
        self,
        command: bytes,
        message_type: bytes,
        message: bytes,
        timeout: float = 3.0,
        retries: int = 3,
    ) -> None:
        """Send payload to the hub."""
        if not self.running:
            raise errors.NotRunningException
        await self.handshake.wait()
        data = message_type + utils.pack_int(self.sequence, 2) + message
        checksum = bytes([sum(data) & 0xFF])
        self.sequence += 2
        command_header = const.HEADER + command + bytes.fromhex("05") + self.topic
        length = len(data) + 1  # bytes.fromhex('0C00')
        buffer = command_header + utils.pack_int(length, 2) + data + checksum
        _LOGGER.debug(f"{self.host}: Sending buffer {buffer.hex()}")

        await self.command_lock.acquire()

        attempt = 0
        while attempt < retries:
            self.protocol.send(buffer)

            try:
                await asyncio.wait_for(self.command_lock.acquire(), timeout=timeout)
                _LOGGER.info(f"{self.host}: command successful.")
                break
            except TimeoutError:
                attempt += 1
                _LOGGER.warning(f"{self.host}: command timed out.")

        if self.command_lock.locked():
            self.command_lock.release()

    async def send_healthcheck(
        self, command: bytes, message_type: bytes, message: bytes
    ) -> None:
        """Send payload to the hub."""
        await self.health_lock.acquire()

        await self.send_command(command, message_type, message)

        try:
            await asyncio.wait_for(self.health_lock.acquire(), timeout=5.0)

        except TimeoutError:
            _LOGGER.warning(f"{self.host}: Health-check timed out.")

        if self.health_lock.locked():
            self.health_lock.release()

    async def run(self) -> None:
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
                # await self.update()
                self._schedule_callback(self.update)
                await self.response_parser()
            except errors.CannotConnectException as inst:
                _LOGGER.warning(f"{self.host}: Connect failed {inst}")
            except errors.InvalidResponseException as inst:
                _LOGGER.warning(f"{self.host}: Handshake failed {inst}")
                await self.disconnect()
            except errors.NotConnectedException:
                _LOGGER.debug(f"{self.host}: Disconnected, stopping parser")
            except OSError as inst:
                _LOGGER.warning(f"{self.host}: Unexpected protocol failure: {inst}")
            except Exception as inst:
                _LOGGER.error(f"{self.host}: Uncaught exception occurred: {inst}")
                del self.protocol
                self.protocol = aiopulse.transport.HubTransportTcp(self.host)
            finally:
                if self.handshake.is_set():
                    await self.disconnect()
                if self.running:
                    await asyncio.sleep(5)
        _LOGGER.debug(f"{self.host}: Stopped")

    async def stop(self) -> None:
        """Tell hub to stop and await for it to disconnect."""
        if not self.running:
            _LOGGER.warning(f"{self.host}: Already stopped")
            return
        _LOGGER.debug(f"{self.host}: Stopping")
        self.rooms.clear()
        self.scenes.clear()
        self.timers.clear()
        self.rollers.clear()
        self.running = False
        await self.disconnect()
