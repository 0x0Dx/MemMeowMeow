from enum import Enum
from struct import pack, unpack
from sys import byteorder
from typing import Union

class DataType(Enum):
    INT8 = ("Int8", 1, True)
    UINT8 = ("UInt8", 1, False)
    INT16 = ("Int16", 2, True)
    UINT16 = ("UInt16", 2, False)
    INT32 = ("Int32", 4, True)
    UINT32 = ("UInt32", 4, False)
    INT64 = ("Int64", 8, True)
    UINT64 = ("UInt64", 8, False)
    FLOAT = ("Float", 4, None)
    DOUBLE = ("Double", 8, None)
    STRING = ("String", None, None)
    
    def __init__(self, display_name: str, size: int, signed: bool):
        self.display_name = display_name
        self.byte_size = size
        self.signed = signed
    
    @classmethod
    def from_string(cls, name: str):
        for dtype in cls:
            if dtype.display_name.lower() == name.lower():
                return dtype
        raise ValueError(f"Unknown data type: {name}")
    
    @property
    def is_numeric(self) -> bool:
        return self != DataType.STRING

class TypeConverter:
    @staticmethod
    def to_bytes(value: Union[str, int, float], data_type: DataType) -> bytes:
        try:
            if data_type == DataType.STRING:
                if isinstance(value, bytes):
                    return value
                return str(value).encode('utf-8')
            
            if data_type in (DataType.FLOAT, DataType.DOUBLE):
                fmt = 'f' if data_type == DataType.FLOAT else 'd'
                return pack(f'={fmt}', float(value))
            
            num_value = int(value)
            return num_value.to_bytes(
                data_type.byte_size,
                byteorder=byteorder,
                signed=data_type.signed
            )
        except (ValueError, OverflowError) as e:
            raise ValueError(f"Cannot convert '{value}' to {data_type.display_name}: {e}")
    
    @staticmethod
    def from_bytes(data: bytes, data_type: DataType) -> Union[str, int, float]:
        try:
            if data_type == DataType.STRING:
                return data.decode('utf-8', errors='replace').rstrip('\x00')
            
            if data_type in (DataType.FLOAT, DataType.DOUBLE):
                fmt = 'f' if data_type == DataType.FLOAT else 'd'
                return round(unpack(f'={fmt}', data)[0], 6)
            
            return int.from_bytes(data, byteorder=byteorder, signed=data_type.signed)
        except Exception as e:
            raise ValueError(f"Cannot convert bytes to {data_type.display_name}: {e}")
