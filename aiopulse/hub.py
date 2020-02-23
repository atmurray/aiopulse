""" Acmeda Pulse Hub Interface """
import asyncio
import async_timeout
import binascii
import logging

_LOGGER = logging.getLogger(__name__)

from aiopulse.utils import * # pylint: disable=unused-wildcard-import
from aiopulse.transport import * # pylint: disable=unused-wildcard-import
from aiopulse.const import * # pylint: disable=unused-wildcard-import
from aiopulse.errors import * # pylint: disable=unused-wildcard-import
from aiopulse.elements import * # pylint: disable=unused-wildcard-import

class Hub:
	""" Represenation of an Acmeda Pulse Hub """

	def __init__(self, host = None):
		""" Init the hub """
		self.topic = str.encode("Smart_Id1_y:")
		self.sequence = 4
		self.handshake = asyncio.Event()
		self.event_update = asyncio.Event()

		self.response_task = None
		
		self.name = "Acmeda Pulse WiFi Hub"
		self.id = None
		self.host = host
		self.mac_address = None
		self.ip_address = None
		self.firmware_name = None
		self.wifi_module = None

		self.protocol = HubTransportTcp(host)

		self.rollers = {}
		self.rooms = {}
		self.scenes = {}

	@staticmethod
	async def discover(timeout=5):
		""" Use a broadcast udp packet to find hubs on the lan """

		discover_client = HubTransportUdpBroadcast()
		
		await discover_client.connect()
	
		hubs = {}

		retries=3

		try:
			with async_timeout.timeout(timeout*retries):
				for _ in range(1):
					discover_client.send(HEADER + COMMAND_DISCOVER)
					#discover_client.send(bytes.fromhex("000000030300001b"))
					while True:
						addr = None
						try:
							with async_timeout.timeout(timeout):
								(_, addr) = await discover_client.receive()
						except asyncio.TimeoutError:
							pass

						if addr and not addr in hubs:
							_LOGGER.info("Discovered hub %s:%s", addr[0], addr[1])
							try:
								hub = Hub(addr[0])
								await hub.connect()
								await hub.do_handshake()
								await hub.protocol.close()
								hubs[addr] = hub
								yield hub
							except NotConnectedException:
								_LOGGER.error("Not connected")
		except asyncio.TimeoutError:
			pass
		_LOGGER.info("Discovery complete")

		await discover_client.close()
		
	async def connect(self, host=None):
		""" try and connect to the hub """
		if host:
			self.host = host
		
		await self.protocol.connect(self.host)
		
		self.handshake.clear()
		return True
				
	def send_command(self, command, message=None):
		""" send a command to the hub """
		if message:
			self.protocol.send(HEADER + command + bytes.fromhex('05') + self.topic + message)
		else:
			self.protocol.send(HEADER + command)
		
	async def get_response(self, target_response=None):
		""" Get a response, throw exception if it doesn't match expected response """
		response = await self.protocol.receive()
		if not target_response:
			return response
		length = len(HEADER + target_response)
		if len(response) < length:
			raise InvalidResponseException
		if response[0:length] != HEADER + target_response:
			raise InvalidResponseException
		return response[length:]
	
	def response_hubinfo(self, message):
		""" receive start of hub information """
		_LOGGER.debug("Received hub information")
		ptr=10
		self.firmware_name, ptr = unpack_string(message, ptr)
		ptr+=2
		_, ptr = unpack_string(message, ptr)
		ptr+=2
		self.wifi_module, ptr = unpack_string(message, ptr)
		ptr+=2
		self.mac_address, ptr = unpack_string(message, ptr)
		ptr+=2
		self.ip_address, ptr = unpack_string(message, ptr)	
				
	def response_hubinfoend(self, message):
		""" receive end of hub information """
		_LOGGER.debug("Received end of hub information")
		self.event_update.set()
	
	def response_roomlist(self, message):
		""" receive room list """
		_LOGGER.debug("Received room list")
		ptr=12
		room_count, ptr = unpack_int(message, ptr, 1)
		for _ in range(room_count):
			_, ptr = unpack_bytes(message, ptr, 2)
			room_id, ptr = unpack_string(message, ptr)
			_, ptr = unpack_bytes(message, ptr, 4)
			icon, ptr = unpack_int(message, ptr, 1)
			_, ptr = unpack_bytes(message, ptr, 2)
			room_name, ptr = unpack_string(message, ptr)
			if not room_id in self.rooms:
				self.rooms[room_id] = Room(self, room_id)
			self.rooms[room_id].icon = icon
			self.rooms[room_id].name = room_name			

	def response_scenelist(self, message):
		""" receive scene list """
		_LOGGER.debug("Received scene list")
		ptr=12
		scene_count, ptr = unpack_int(message, ptr, 1)
		ptr+=2
		for _ in range(scene_count):
			scene_id, ptr = unpack_string(message, ptr)
			_, ptr = unpack_bytes(message, ptr, 4)
			icon, ptr = unpack_int(message, ptr, 1)
			_, ptr = unpack_bytes(message, ptr, 2)
			scene_name, ptr = unpack_string(message, ptr)
			_, ptr = unpack_bytes(message, ptr, 7)
			_, ptr = unpack_string(message, ptr)
			_, ptr = unpack_bytes(message, ptr, 2)
			if not scene_id in self.scenes:
				self.scenes[scene_id] = Scene(self, scene_id)
			self.scenes[scene_id].icon = icon
			self.scenes[scene_id].name = scene_name			
				
	def response_timerlist(self, message):
		""" receive timer list """
		_LOGGER.debug("Received timer list")
		pass
		
	def response_rollerlist(self, message):
		""" receive roller blind list """
		_LOGGER.debug("Received roller list")
		ptr = 12
		roller_count, ptr = unpack_int(message, ptr, 1)
		for _ in range(roller_count):
			ptr += 4 # unknown field
			roller_id, ptr = unpack_int(message, ptr, 6)
			ptr += 2 # unknown field
			room_id, ptr = unpack_string(message, ptr)
			ptr += 7 # unknown field
			roller_name, ptr = unpack_string(message, ptr)
			ptr += 8 # unknown field
			_, ptr = unpack_string(message, ptr)
			ptr += 4
			roller_battery, ptr = unpack_int(message, ptr, 1)
			ptr += 5 # unknown field
			roller_percent, ptr = unpack_int(message, ptr, 1)
			ptr += 1
			if not roller_id in self.rollers:
				self.rollers[roller_id] = Roller(self, roller_id)
			self.rollers[roller_id].name = roller_name
			self.rollers[roller_id].room_id = room_id
			self.rollers[roller_id].battery = roller_battery
			self.rollers[roller_id].closed_percent = roller_percent
			self.rollers[roller_id].notify_callback()
				
	def response_authinfo(self, message):
		""" receive acmeda account information """
		_LOGGER.debug("Received account information")
		ptr=15
		_, ptr = unpack_string(message, ptr)
		
	def response_position(self, message):
		""" receive change of roller position information """
		_LOGGER.debug("Received change of roller position")
		ptr = 12
		roller_id, ptr = unpack_int(message, ptr, 6)
		ptr += 10
		roller_percent, ptr = unpack_int(message, ptr, 1)
		if roller_id in self.rollers:
			self.rollers[roller_id].closed_percent = roller_percent
			self.rollers[roller_id].notify_callback()

	def response_discover(self, message):
		""" receive after discover broadcast packet """
		_LOGGER.debug("Received broadcast response")
		pass

	msgmap = {
		bytes.fromhex('1600') : response_hubinfo,
		bytes.fromhex('4101') : response_hubinfoend,
		bytes.fromhex('0101') : response_roomlist,
		bytes.fromhex('3301') : response_scenelist,
		bytes.fromhex('2101') : response_rollerlist,
		bytes.fromhex('0800') : response_authinfo,
		bytes.fromhex('2301') : response_position,
		bytes.fromhex('2b01') : response_position,
		bytes.fromhex('0f00') : response_discover,
	}

	def rec_ping(self, message):
		""" receive a ping from the hub """
		_LOGGER.debug("Received hub ping response")
		pass

	def rec_message(self, message):
		""" receive and decode a message from the hub """

		if message:
			if message[0] != 6:
				raise InvalidResponseException

			if message[1:(1+len(self.topic))] != self.topic:
				raise InvalidResponseException
			ptr=1+len(self.topic)
			_, ptr = unpack_int(message, 2, ptr)
			mtype = message[ptr:(ptr+2)]
			ptr=ptr+2		
			if mtype in self.msgmap:
				self.msgmap[mtype](self, message[ptr:])
			else:
				_LOGGER.warning("Unknown message type %s message %s", binascii.hexlify(mtype), binascii.hexlify(message))
	
	def rec_null(self, message):
		""" receive an empty message from the hub """
		_LOGGER.debug("Received empty message")
		pass
	
	respmap = {
		RESPONSE_PING : rec_ping,
		bytes.fromhex('03000091'): rec_message,	
		bytes.fromhex('01000091'): rec_message,	
		bytes.fromhex('02000091'): rec_message,	
		bytes.fromhex('23000091'): rec_message,	
		bytes.fromhex('28000091'): rec_message,
		bytes.fromhex('34000091'): rec_message, # move
		bytes.fromhex('42000091'): rec_message,	
		bytes.fromhex('43000091'): rec_message, # account info
		bytes.fromhex('44000091'): rec_message,	# response move
		RESPONSE_DISCOVER: rec_message, # response from broadcast discovery
		bytes.fromhex('5F000091'): rec_message,
		bytes.fromhex('60000091'): rec_message, # room list
		bytes.fromhex('65000091'): rec_message, # timer list
	}

	def response_parse(self, response):
		""" decode response """
		if response[0:4] != bytes.fromhex('00000003'):
			_LOGGER.warning("Unknown response: %s", binascii.hexlify(response[0:4]))
			raise InvalidResponseException
	
		message_type = response[4:8]
		
		if (message_type[0] > 127):
			message_type = response[5:9]
			message = response[9:]
		else:
			message = response[8:]
	
		mtype = bytes(message_type)
		if mtype in Hub.respmap:
			Hub.respmap[mtype](self, message)
		else:
			_LOGGER.warning("Unknown type: %s message: %s", binascii.hexlify(mtype), binascii.hexlify(message))
		
	async def response_parser(self):
		""" receive a response from the hub and work out what message it is """
		try:
			while True:
				try:
					with async_timeout.timeout(30):
						response = await self.protocol.receive()
					if len(response) > 0:
						self.response_parse(response)
				except asyncio.TimeoutError:
					self.send_command(COMMAND_PING)
				except InvalidResponseException:
					self.send_command(COMMAND_PING)	
		except NotConnectedException:
			_LOGGER.info("Disconnected, stopping parser")

	async def do_handshake(self):
		""" complete handshake with the hub """
		if self.protocol.is_udp: # udp
			#self.send_command(COMMAND_DISCOVER)
			#response = await self.get_response()
			self.send_command(COMMAND_CONNECT)
			raw_id = await self.get_response(RESPONSE_CONNECT)
		else: # TCP
			self.send_command(COMMAND_CONNECT)
			raw_id = await self.get_response(RESPONSE_CONNECT)

		self.id = raw_id[2:].decode("utf-8")

		self.send_command(COMMAND_LOGIN + raw_id)
		response = await self.get_response(RESPONSE_LOGIN)

		if response[0] != 0:
			raise InvalidResponseException

		self.send_command(COMMAND_SETID, bytes.fromhex('16000e0001000000000000000c000600120311073816ff9b'))
		await self.get_response(RESPONSE_SETID)

		self.send_command(COMMAND_UNKNOWN1, bytes.fromhex('1100150002000000000000006002010030ffa9'))
		await self.get_response(RESPONSE_UNKNOWN1 + bytes.fromhex('06') + self.topic + bytes.fromhex('16000f0002000000000000000c000600120311073816ff9d'))
		await self.get_response(RESPONSE_SETID)

		self.response_task = asyncio.create_task(self.response_parser())

		self.handshake.set()

		_LOGGER.info("Handshake complete")

		return True

	async def update(self):
		""" update all hub information (includes scenes, rooms, and rollers) """
		self.event_update.clear()
		if not self.handshake.is_set():
			raise NotConnectedException
		await self.send_payload(COMMAND_GET_HUB_INFO, bytes.fromhex('F000'), bytes.fromhex('000000000000FF'))
		await self.event_update.wait()
		_LOGGER.info("Hub update command sent")

	async def send_payload(self, command, message_type, message):
		""" send payload to the hub """
		data = message_type + pack_int(self.sequence,2) + message
		checksum = bytes([sum(data) & 0xFF])
		self.sequence += 2
		command_header = HEADER + command + bytes.fromhex('05') + self.topic
		length = len(data) + 1 #bytes.fromhex('0C00') 
		self.protocol.send(command_header + pack_int(length, 2) + data + checksum)
