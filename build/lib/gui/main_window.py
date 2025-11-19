import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from threading import Thread
from core.process import ProcessManager, ProcessInfo
from core.memory import MemoryReader
from core.scanner import MemoryScanner, ScanResult
from core.types import DataType, TypeConverter
from gui.widgets.process_list import ProcessListWidget
from gui.widgets.scan_panel import ScanPanelWidget
from gui.widgets.address_table import AddressTableWidget

class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MemMeowMeow 🐾 — The RAM Gremlin Habitat")
        self.root.geometry("1400x800")
        
        self.current_process: Optional[ProcessInfo] = None
        self.process_handle: Optional[int] = None
        self.memory_reader: Optional[MemoryReader] = None
        self.scanner: Optional[MemoryScanner] = None
        self.selected_addresses: List[ScanResult] = []
        
        self._setup_ui()
        self._setup_menu()
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._update_frozen_addresses()
    
    def _setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh Process Zoo 🐒", command=self._refresh_processes)
        file_menu.add_separator()
        file_menu.add_command(label="Yeet MeowMeow Away ❌", command=self._on_close)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="What The Heck Is This 😼", command=self._show_about)
    
    def _setup_ui(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        left_frame = ttk.LabelFrame(main_container, text="Processes", padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.process_list = ProcessListWidget(left_frame, self._on_process_selected)
        self.process_list.pack(fill="both", expand=True)
        
        center_frame = ttk.Frame(main_container)
        center_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        
        self.scan_panel = ScanPanelWidget(
            center_frame,
            self._on_scan,
            self._on_filter
        )
        self.scan_panel.pack(fill="x", pady=(0, 10))
        
        results_frame = ttk.LabelFrame(center_frame, text="Scan Results", padding=10)
        results_frame.pack(fill="both", expand=True)
        
        self.results_table = AddressTableWidget(
            results_frame,
            self._on_address_selected,
            show_freeze=False
        )
        self.results_table.pack(fill="both", expand=True)
        
        right_frame = ttk.LabelFrame(main_container, text="Selected Addresses", padding=10)
        right_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        
        self.address_table = AddressTableWidget(
            right_frame,
            None,
            show_freeze=True
        )
        self.address_table.set_freeze_callback(self._on_address_freeze)
        self.address_table.set_edit_callback(self._on_address_edit)
        self.address_table.set_delete_callback(self._on_address_delete)
        self.address_table.pack(fill="both", expand=True)
        
        main_container.grid_columnconfigure(0, weight=1, minsize=300)
        main_container.grid_columnconfigure(1, weight=2, minsize=500)
        main_container.grid_columnconfigure(2, weight=1, minsize=400)
        main_container.grid_rowconfigure(0, weight=1)
        
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _refresh_processes(self):
        self.process_list.refresh()
        self.status_var.set("🐾 Process zoo restocked with fresh lil critters")
    
    def _on_process_selected(self, process: ProcessInfo):
        try:
            if self.process_handle:
                ProcessManager.close_process(self.process_handle)
            
            self.process_handle = ProcessManager.open_process(process.pid)
            if not self.process_handle:
                messagebox.showerror(
                    "Meow Malfunction 💥",
                    "MemMeowMeow bonked its head on Windows.\n"
                    "Couldn't grab that process—maybe try admin mode?"
                )
                return
            
            self.current_process = process
            self.memory_reader = MemoryReader(self.process_handle)
            self.scanner = MemoryScanner(self.memory_reader)
            
            self.results_table.clear()
            self.address_table.clear()
            self.selected_addresses.clear()
            
            self.scan_panel.set_enabled(True)
            self.root.title(f"MemMeowMeow 🐾 — Nibbling on {process}…")
            self.status_var.set(f"😼 Latched onto {process}! Found {len(self.memory_reader.regions)} snackable memory zones.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to attach to process: {e}")
            self.status_var.set("Error attaching to process")
    
    def _on_scan(self, value: str, data_type: DataType):
        if not self.scanner:
            messagebox.showwarning(
                "Uh Oh Spaghetti Meow 🍝",
                "You told me to scan but didn’t pick a process...\n"
                "What am I sniffing, the AIR??"
            )
            return
        
        self.scan_panel.set_enabled(False)
        self.status_var.set("🔍 MeowMeow is sniffing through the RAM bushes...")

        def scan_thread():
            try:
                results = self.scanner.scan_exact_value(
                    value,
                    data_type,
                    lambda progress: self.root.after(0, self.scan_panel.set_progress, progress * 100)
                )
                
                self.root.after(0, self._on_scan_complete, results)
                
            except Exception as e:
                self.root.after(0, self._on_scan_error, str(e))
        
        Thread(target=scan_thread, daemon=True).start()
    
    def _on_scan_complete(self, results: List[ScanResult]):
        self.results_table.set_results(results)
        self.scan_panel.set_enabled(True)
        self.scan_panel.set_progress(0)
        self.status_var.set(f"🎉 Sniff-sniff complete! Found {len(results)} juicy byte-nuggets.")
        
        if len(results) > 10000:
            messagebox.showinfo(
                "WOAH THERE 😳",
                f"Found {len(results)} matches.\n"
                "That's a LOT of RAM noodles. Maybe filter before MeowMeow explodes?"
            )

    
    def _on_scan_error(self, error_msg: str):
        messagebox.showerror("Scan Error", f"Scan failed: {error_msg}")
        self.scan_panel.set_enabled(True)
        self.scan_panel.set_progress(0)
        self.status_var.set("💀 MeowMeow tripped over a pointer and faceplanted.")
    
    def _on_filter(self, filter_type: str, value: str, data_type: DataType):
        if not self.scanner or not self.scanner.results:
            messagebox.showwarning("Warning", "No results to filter")
            return
        
        try:
            if filter_type == "changed":
                results = self.scanner.filter_changed(data_type)
            elif filter_type == "unchanged":
                results = self.scanner.filter_unchanged(data_type)
            elif filter_type == "increased":
                results = self.scanner.filter_results(
                    lambda current, old: current > old,
                    None,
                    data_type
                )
            elif filter_type == "decreased":
                results = self.scanner.filter_results(
                    lambda current, old: current < old,
                    None,
                    data_type
                )
            else:
                predicates = {
                    "=": lambda a, b: a == b,
                    "!=": lambda a, b: a != b,
                    ">": lambda a, b: a > b,
                    "<": lambda a, b: a < b,
                }
                comp_value = TypeConverter.from_bytes(
                    TypeConverter.to_bytes(value, data_type),
                    data_type
                )
                results = self.scanner.filter_results(
                    predicates[filter_type],
                    comp_value,
                    data_type
                )
            
            self.results_table.set_results(results)
            self.status_var.set(f"Filter applied - {len(results)} matches remaining")
            
        except Exception as e:
            messagebox.showerror("Error", f"Filter failed: {e}")
    
    def _on_address_selected(self, result: ScanResult):
        if result not in self.selected_addresses:
            self.selected_addresses.append(result)
            self.address_table.add_result(result)
            self.status_var.set(f"✨ Adopted lil address 0x{result.address:X} into the MeowMeow daycare.")
    
    def _on_address_freeze(self, result: ScanResult, frozen: bool):
        result.frozen = frozen
        if frozen:
            self.status_var.set(f"❄️ Froze 0x{result.address:X} in a tiny ice cube.")
        else:
            self.status_var.set(f"🔥 Thawed 0x{result.address:X} back into gooey RAM sludge.")
    
    def _on_address_edit(self, result: ScanResult, new_value: str):
        if not self.memory_reader:
            return
        
        try:
            data = TypeConverter.to_bytes(new_value, result.data_type)
            if self.memory_reader.write_bytes(result.address, data):
                result.update_value(data)
                self.address_table.refresh_result(result)
                self.status_var.set(f"🛠️ Bonked new value into 0x{result.address:X} with a tiny hammer.")
            else:
                messagebox.showerror("Error", "Failed to write memory")
        except Exception as e:
            messagebox.showerror("Error", f"Edit failed: {e}")
    
    def _on_address_delete(self, result: ScanResult):
        if result in self.selected_addresses:
            self.selected_addresses.remove(result)
            self.status_var.set(f"Removed address 0x{result.address:X}")
    
    def _update_frozen_addresses(self):
        if self.memory_reader:
            for result in self.selected_addresses:
                if result.frozen:
                    self.memory_reader.write_bytes(result.address, result.value)
                else:
                    data = self.memory_reader.read_bytes(result.address, len(result.value))
                    if data:
                        result.update_value(data)
            
            self.address_table.refresh_all()
        
        self.root.after(100, self._update_frozen_addresses)
    
    def _show_about(self):
        messagebox.showinfo(
            "About MemMeowMeow 🐾✨",
            "MemMeowMeow 🐾 v0.1.0\n\n"
            "A feral byte-goblin disguised as a cute kitten.\n"
            "It tip-taps through your RAM, meowing at pointers and\n"
            "occasionally committing tax fraud (allegedly).\n\n"
            "✨ Feature Chaos:\n"
            "- 👃 Sniff-Sniff Memory Diving\n"
            "- 🔍 Peeky-Squeaky Value Finder\n"
            "- ❄️ Freeze-o-Tron 9000 (Lock num nums)\n"
            "- 🛠️ Byte Bonker Deluxe\n\n"
            "Handle responsibly. It is VERY small and VERY stupid."
        )

    
    def _on_close(self):
        if self.process_handle:
            ProcessManager.close_process(self.process_handle)
        self.root.destroy()