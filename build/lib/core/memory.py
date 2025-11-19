import sys
import ctypes
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class MemoryRegion:
    base_address: int
    size: int
    protection: int
    state: int
    
    @property
    def end_address(self) -> int:
        return self.base_address + self.size
    
    def contains(self, address: int) -> bool:
        return self.base_address <= address < self.end_address
    
    def __repr__(self) -> str:
        return f"MemoryRegion(0x{self.base_address:X}, size={self.size})"

class MemoryReader:
    PAGE_READONLY = 0x02
    PAGE_READWRITE = 0x04
    PAGE_WRITECOPY = 0x08
    PAGE_EXECUTE_READ = 0x20
    PAGE_EXECUTE_READWRITE = 0x40
    PAGE_EXECUTE_WRITECOPY = 0x80
    PAGE_GUARD = 0x100
    
    MEM_COMMIT = 0x1000
    
    READABLE_PROTECTIONS = [
        PAGE_READONLY,
        PAGE_READWRITE,
        PAGE_WRITECOPY,
        PAGE_EXECUTE_READ,
        PAGE_EXECUTE_READWRITE,
        PAGE_EXECUTE_WRITECOPY
    ]
    
    def __init__(self, process_handle: int):
        self.handle = process_handle
        self._regions: List[MemoryRegion] = []
        
        if sys.platform == 'win32':
            self.kernel32 = ctypes.windll.kernel32
            self._scan_memory_regions()
        else:
            raise OSError("Memory operations only supported on Windows")
    
    def _scan_memory_regions(self):
        self._regions.clear()
        
        class MEMORY_BASIC_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("BaseAddress", ctypes.c_void_p),
                ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", ctypes.c_ulong),
                ("RegionSize", ctypes.c_size_t),
                ("State", ctypes.c_ulong),
                ("Protect", ctypes.c_ulong),
                ("Type", ctypes.c_ulong),
            ]
        
        mbi = MEMORY_BASIC_INFORMATION()
        address = 0
        max_address = 0x7FFFFFFF0000
        
        while address < max_address:
            result = self.kernel32.VirtualQueryEx(
                self.handle,
                ctypes.c_void_p(address),
                ctypes.byref(mbi),
                ctypes.sizeof(mbi)
            )
            
            if result == 0:
                break
            
            if (mbi.State == self.MEM_COMMIT and 
                mbi.Protect in self.READABLE_PROTECTIONS and
                not (mbi.Protect & self.PAGE_GUARD)):
                
                self._regions.append(MemoryRegion(
                    base_address=mbi.BaseAddress,
                    size=mbi.RegionSize,
                    protection=mbi.Protect,
                    state=mbi.State
                ))
            
            address += mbi.RegionSize
    
    def read_bytes(self, address: int, size: int) -> Optional[bytes]:
        buffer = ctypes.create_string_buffer(size)
        bytes_read = ctypes.c_size_t()
        
        result = self.kernel32.ReadProcessMemory(
            self.handle,
            ctypes.c_void_p(address),
            buffer,
            size,
            ctypes.byref(bytes_read)
        )
        
        if result and bytes_read.value == size:
            return buffer.raw[:bytes_read.value]
        
        return None
    
    def write_bytes(self, address: int, data: bytes) -> bool:
        bytes_written = ctypes.c_size_t()
        
        result = self.kernel32.WriteProcessMemory(
            self.handle,
            ctypes.c_void_p(address),
            data,
            len(data),
            ctypes.byref(bytes_written)
        )
        
        return bool(result and bytes_written.value == len(data))
    
    @property
    def regions(self) -> List[MemoryRegion]:
        return self._regions
    
    @property
    def total_memory_size(self) -> int:
        return sum(region.size for region in self._regions)