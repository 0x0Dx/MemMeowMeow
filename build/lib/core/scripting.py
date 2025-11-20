from typing import Any, Dict, Optional, List
from dataclasses import dataclass
import traceback

@dataclass
class ScriptResult:
    success: bool
    output: str
    error: Optional[str] = None
    return_value: Any = None

class ScriptEngine:
    def __init__(self, memory_reader=None, scanner=None, process_info=None):
        self.memory_reader = memory_reader
        self.scanner = scanner
        self.process_info = process_info
        self.globals_dict = {}
        self.locals_dict = {}
        self._setup_namespace()
    
    def _setup_namespace(self):
        from core.types import DataType, TypeConverter
        
        self.globals_dict.update({
            '__builtins__': __builtins__,
            'DataType': DataType,
            'TypeConverter': TypeConverter,
            'print': self._script_print,
            'help': self._script_help,
        })
        
        if self.memory_reader:
            self.globals_dict.update({
                'readBytes': self._read_bytes,
                'writeBytes': self._write_bytes,
                'readInt': lambda addr: self._read_typed(addr, DataType.INT32),
                'readInt64': lambda addr: self._read_typed(addr, DataType.INT64),
                'readFloat': lambda addr: self._read_typed(addr, DataType.FLOAT),
                'readDouble': lambda addr: self._read_typed(addr, DataType.DOUBLE),
                'readString': lambda addr, length=256: self._read_string(addr, length),
                'writeInt': lambda addr, val: self._write_typed(addr, val, DataType.INT32),
                'writeInt64': lambda addr, val: self._write_typed(addr, val, DataType.INT64),
                'writeFloat': lambda addr, val: self._write_typed(addr, val, DataType.FLOAT),
                'writeDouble': lambda addr, val: self._write_typed(addr, val, DataType.DOUBLE),
            })
        
        if self.scanner:
            self.globals_dict.update({
                'scan': self._scan_value,
                'getResults': lambda: self.scanner.results,
                'filterChanged': lambda dt: self.scanner.filter_changed(dt),
                'filterUnchanged': lambda dt: self.scanner.filter_unchanged(dt),
            })
        
        self.output_buffer = []
    
    def _script_print(self, *args, **kwargs):
        output = ' '.join(str(arg) for arg in args)
        self.output_buffer.append(output)
    
    def _script_help(self):
        help_text = """
MemMeowMeow Script API 🐾

Memory Read/Write:
  readBytes(address, size) -> bytes
  writeBytes(address, data) -> bool
  readInt(address) -> int
  readInt64(address) -> int
  readFloat(address) -> float
  readDouble(address) -> float
  readString(address, length=256) -> str
  writeInt(address, value) -> bool
  writeInt64(address, value) -> bool
  writeFloat(address, value) -> bool
  writeDouble(address, value) -> bool

Scanner:
  scan(value, data_type) -> List[ScanResult]
  getResults() -> List[ScanResult]
  filterChanged(data_type) -> List[ScanResult]
  filterUnchanged(data_type) -> List[ScanResult]

Types:
  DataType.INT8, INT16, INT32, INT64
  DataType.UINT8, UINT16, UINT32, UINT64
  DataType.FLOAT, DOUBLE
  DataType.STRING
"""
        self._script_print(help_text)
    
    def _read_bytes(self, address: int, size: int) -> Optional[bytes]:
        if not self.memory_reader:
            raise RuntimeError("No memory reader available")
        return self.memory_reader.read_bytes(address, size)
    
    def _write_bytes(self, address: int, data: bytes) -> bool:
        if not self.memory_reader:
            raise RuntimeError("No memory reader available")
        return self.memory_reader.write_bytes(address, data)
    
    def _read_typed(self, address: int, data_type) -> Any:
        from core.types import TypeConverter
        data = self._read_bytes(address, data_type.byte_size)
        if data:
            return TypeConverter.from_bytes(data, data_type)
        return None
    
    def _write_typed(self, address: int, value: Any, data_type) -> bool:
        from core.types import TypeConverter
        data = TypeConverter.to_bytes(value, data_type)
        return self._write_bytes(address, data)
    
    def _read_string(self, address: int, length: int) -> Optional[str]:
        data = self._read_bytes(address, length)
        if data:
            try:
                return data.decode('utf-8', errors='ignore').rstrip('\x00')
            except:
                return None
        return None
    
    def _scan_value(self, value: Any, data_type) -> List:
        if not self.scanner:
            raise RuntimeError("No scanner available")
        return self.scanner.scan_exact_value(value, data_type)
    
    def execute(self, code: str) -> ScriptResult:
        self.output_buffer = []
        
        try:
            compiled = compile(code, '<script>', 'exec')
            exec(compiled, self.globals_dict, self.locals_dict)
            
            output = '\n'.join(self.output_buffer)
            return ScriptResult(
                success=True,
                output=output if output else "Script executed successfully",
                return_value=self.locals_dict.get('__result__')
            )
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            return ScriptResult(
                success=False,
                output='\n'.join(self.output_buffer),
                error=error_msg
            )
    
    def execute_file(self, filepath: str) -> ScriptResult:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.execute(code)
        except Exception as e:
            return ScriptResult(
                success=False,
                output="",
                error=f"Failed to load script: {str(e)}"
            )
    
    def update_context(self, memory_reader=None, scanner=None, process_info=None):
        if memory_reader:
            self.memory_reader = memory_reader
        if scanner:
            self.scanner = scanner
        if process_info:
            self.process_info = process_info
        self._setup_namespace()

class CheatTable:
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []
        self.scripts: List[Dict[str, Any]] = []
    
    def add_entry(self, address: int, description: str, data_type, frozen: bool = False):
        self.entries.append({
            'address': address,
            'description': description,
            'data_type': data_type,
            'frozen': frozen
        })
    
    def add_script(self, name: str, code: str, auto_run: bool = False):
        self.scripts.append({
            'name': name,
            'code': code,
            'auto_run': auto_run,
            'enabled': False
        })
    
    def save(self, filepath: str):
        import json
        data = {
            'entries': [
                {
                    **entry,
                    'data_type': entry['data_type'].display_name
                }
                for entry in self.entries
            ],
            'scripts': self.scripts
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str):
        import json
        from core.types import DataType
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.entries = [
            {
                **entry,
                'data_type': DataType.from_string(entry['data_type'])
            }
            for entry in data.get('entries', [])
        ]
        self.scripts = data.get('scripts', [])