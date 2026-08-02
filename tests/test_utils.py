
from aiopulse.utils import (
    pack_int,
    unpack_bytes,
    unpack_int,
    unpack_roller_percent,
    unpack_string,
)


class TestUnpackInt:
    def test_unpack_single_byte(self):
        value, ptr = unpack_int(b"\x2a\x00\x00\x00", 0, 1)
        assert value == 0x2A
        assert ptr == 1

    def test_unpack_two_bytes(self):
        value, ptr = unpack_int(b"\x34\x12\x00\x00", 0, 2)
        assert value == 0x1234
        assert ptr == 2

    def test_unpack_four_bytes(self):
        value, ptr = unpack_int(b"\xef\xcd\xab\x89", 0, 4)
        assert value == 0x89ABCDEF
        assert ptr == 4

    def test_unpack_with_offset(self):
        value, ptr = unpack_int(b"\x00\x00\x2a\x00", 2, 1)
        assert value == 0x2A
        assert ptr == 3

    def test_unpack_zero(self):
        value, ptr = unpack_int(b"\x00\x00\x00\x00", 0, 2)
        assert value == 0
        assert ptr == 2

    def test_unpack_max_value(self):
        value, ptr = unpack_int(b"\xff\xff\xff\xff", 0, 4)
        assert value == 0xFFFFFFFF
        assert ptr == 4


class TestPackInt:
    def test_pack_single_byte(self):
        result = pack_int(0x2A, 1)
        assert result == b"\x2a"

    def test_pack_two_bytes(self):
        result = pack_int(0x1234, 2)
        assert result == b"\x34\x12"

    def test_pack_four_bytes(self):
        result = pack_int(0x89ABCDEF, 4)
        assert result == b"\xef\xcd\xab\x89"

    def test_pack_zero(self):
        result = pack_int(0, 2)
        assert result == b"\x00\x00"

    def test_pack_max_value(self):
        result = pack_int(0xFFFFFFFF, 4)
        assert result == b"\xff\xff\xff\xff"


class TestUnpackBytes:
    def test_unpack_bytes_with_length(self):
        data, ptr = unpack_bytes(b"\x01\x02\x03\x04", 0, 2)
        assert data == b"\x01\x02"
        assert ptr == 2

    def test_unpack_bytes_without_length(self):
        data, ptr = unpack_bytes(b"\x04\x00\x01\x02\x03\x04", 0)
        assert data == b"\x01\x02\x03\x04"
        assert ptr == 6

    def test_unpack_bytes_with_offset(self):
        data, ptr = unpack_bytes(b"\xAA\xBB\x03\x00\x01\x02\x03", 2)
        assert data == b"\x01\x02\x03"
        assert ptr == 7

    def test_unpack_bytes_empty(self):
        data, ptr = unpack_bytes(b"\x00\x00", 0)
        assert data == b""
        assert ptr == 2


class TestUnpackString:
    def test_unpack_string_ascii(self):
        text, ptr = unpack_string(b"\x05\x00HelloExtra", 0)
        assert text == "Hello"
        assert ptr == 7

    def test_unpack_string_unicode(self):
        text, ptr = unpack_string(b"\x06\x00\xc3\xa9\x63\x72\x61\x73", 0)
        assert text == "\xe9cras"
        assert ptr == 8

    def test_unpack_string_with_offset(self):
        text, ptr = unpack_string(b"\xAA\xBB\x03\x00ABC", 2)
        assert text == "ABC"
        assert ptr == 7


class TestUnpackRollerPercent:
    def test_roller_open(self):
        # roller_state = b"\x10" means open
        buffer = b"\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00"
        percent, ptr = unpack_roller_percent(buffer, 0)
        assert percent == 0
        assert ptr == 11

    def test_roller_closed(self):
        # roller_state = b"\x12" means closed
        buffer = b"\x00\x00\x00\x00\x12\x00\x00\x00\x00\x00\x00"
        percent, ptr = unpack_roller_percent(buffer, 0)
        assert percent == 100
        assert ptr == 11

    def test_roller_percent_value(self):
        # roller_state = b"\x00" -> read percent byte
        buffer = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x32"
        percent, ptr = unpack_roller_percent(buffer, 0)
        assert percent == 50
        assert ptr == 11
