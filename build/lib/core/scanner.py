from dataclasses import dataclass
from typing import List, Callable, Optional
from core.memory import MemoryReader
from core.types import DataType, TypeConverter

@dataclass
class ScanResult:
    address: int
    value: bytes
    data_type: DataType
    frozen: bool = False
    
    def get_value(self) -> any:
        return TypeConverter.from_bytes(self.value, self.data_type)
    
    def update_value(self, new_value: bytes):
        self.value = new_value
    
    def __str__(self) -> str:
        return f"0x{self.address:X}: {self.get_value()}"
    
    def __hash__(self) -> int:
        return hash(self.address)

class MemoryScanner:
    def __init__(self, memory_reader: MemoryReader):
        self.memory = memory_reader
        self.results: List[ScanResult] = []
        self._is_scanning = False
    
    @property
    def is_scanning(self) -> bool:
        return self._is_scanning
    
    def scan_exact_value(
        self,
        value: any,
        data_type: DataType,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> List[ScanResult]:
        self._is_scanning = True
        self.results.clear()
        
        try:
            search_bytes = TypeConverter.to_bytes(value, data_type)
            search_size = len(search_bytes)
            
            total_size = self.memory.total_memory_size
            scanned_size = 0
            
            for region in self.memory.regions:
                if region.size < search_size:
                    scanned_size += region.size
                    continue
                
                data = self.memory.read_bytes(region.base_address, region.size)
                if not data:
                    scanned_size += region.size
                    if progress_callback:
                        progress_callback(min(scanned_size / total_size, 1.0))
                    continue
                
                offset = 0
                while offset != -1:
                    offset = data.find(search_bytes, offset)
                    if offset != -1:
                        address = region.base_address + offset
                        self.results.append(ScanResult(
                            address=address,
                            value=search_bytes,
                            data_type=data_type
                        ))
                        offset += 1 
                
                scanned_size += region.size
                if progress_callback:
                    progress_callback(min(scanned_size / total_size, 1.0))
            
            return self.results
            
        finally:
            self._is_scanning = False
    
    def filter_results(
        self,
        predicate: Callable[[any, any], bool],
        compare_value: any,
        data_type: DataType
    ) -> List[ScanResult]:
        filtered = []
        
        for result in self.results:
            current_data = self.memory.read_bytes(result.address, data_type.byte_size)
            if not current_data:
                continue
            
            try:
                current_value = TypeConverter.from_bytes(current_data, data_type)
                old_value = result.get_value()
                
                if predicate(current_value, old_value if compare_value is None else compare_value):
                    result.update_value(current_data)
                    filtered.append(result)
            except ValueError:
                continue
        
        self.results = filtered
        return self.results
    
    def filter_changed(self, data_type: DataType) -> List[ScanResult]:
        filtered = []
        
        for result in self.results:
            current_data = self.memory.read_bytes(result.address, data_type.byte_size)
            if not current_data:
                continue
            
            if current_data != result.value:
                result.update_value(current_data)
                filtered.append(result)
        
        self.results = filtered
        return self.results
    
    def filter_unchanged(self, data_type: DataType) -> List[ScanResult]:
        filtered = []
        
        for result in self.results:
            current_data = self.memory.read_bytes(result.address, data_type.byte_size)
            if not current_data:
                continue
            
            if current_data == result.value:
                filtered.append(result)
        
        self.results = filtered
        return self.results
    
    def clear_results(self):
        self.results.clear()