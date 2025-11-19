import sys
import ctypes
from dataclasses import dataclass
from typing import List, Optional
import psutil

PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
PROCESS_QUERY_INFORMATION = 0x0400

if sys.platform == 'win32':
    kernel32 = ctypes.windll.kernel32
else:
    kernel32 = None

@dataclass
class ProcessInfo:
    pid: int
    name: str
    exe_path: Optional[str] = None
    
    def __str__(self) -> str:
        return f"{self.name} (PID: {self.pid})"
    
    def __hash__(self) -> int:
        return hash(self.pid)

class ProcessManager:
    @staticmethod
    def is_windows() -> bool:
        return sys.platform == 'win32'
    
    @staticmethod
    def get_running_processes() -> List[ProcessInfo]:
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                info = proc.info
                
                if info['pid'] == 0:
                    continue
                
                processes.append(ProcessInfo(
                    pid=info['pid'],
                    name=info['name'] or 'Unknown',
                    exe_path=info['exe']
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return sorted(processes, key=lambda p: p.name.lower())
    
    @staticmethod
    def open_process(pid: int) -> Optional[int]:
        if not ProcessManager.is_windows() or not kernel32:
            return None
        
        access = PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION | PROCESS_QUERY_INFORMATION
        handle = kernel32.OpenProcess(access, False, pid)
        
        return handle if handle else None
    
    @staticmethod
    def close_process(handle: int):
        if ProcessManager.is_windows() and kernel32 and handle:
            kernel32.CloseHandle(handle)