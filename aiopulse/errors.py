class HubBaseException(Exception):
	""" Base Exception for protocol """
	pass

class NotConnectedException(HubBaseException):
	""" Exception thrown when the hub isn't connected """
	pass

class InvalidResponseException(HubBaseException):
	""" Exception thrown when an invalid response is received """
	pass