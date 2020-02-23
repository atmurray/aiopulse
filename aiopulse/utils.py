""" Serialisation / Deserialisation helpers """

def unpack_int(buffer, ptr, length):
	""" Unpack an int of specified length from the buffer and advance the pointer """
	return (
		int.from_bytes(buffer[ptr:(ptr+length)], 'little', signed=False),
		ptr + length
		)

def pack_int(value, length):
	""" Unpack an int for serialisation """
	return value.to_bytes(length, 'little', signed=False)

def unpack_bytes(buffer, ptr, length=None):
	""" Unpack a specified number of bytes from the buffer and advance the pointer """
	ptr_new = ptr
	if not length:
		length, ptr_new = unpack_int(buffer, ptr, 2)
	return (
		buffer[(ptr_new):(ptr_new+length)],
		ptr_new + length
		)
		
def unpack_string(buffer, ptr, length=None):
	""" Unpack a specified number of characters from the buffer and advance the pointer """
	str_new, ptr_new = unpack_bytes(buffer, ptr, length=None)
	return (
		str_new.decode("utf-8"),
		ptr_new
		)