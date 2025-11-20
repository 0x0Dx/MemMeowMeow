import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from typing import Optional, List
from threading import Thread
from core.process import ProcessManager, ProcessInfo
from core.memory import MemoryReader
from core.scanner import MemoryScanner, ScanResult
from core.types import DataType, TypeConverter
from gui.widgets.process_list import ProcessListWidget
from gui.widgets.scan_panel import ScanPanelWidget
from gui.widgets.address_table import AddressTableWidget
from gui.widgets.script_editor import ScriptEditorWidget
from core.scripting import ScriptEngine, CheatTable

class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MemMeowMeow 🐾 – The Feral RAM Gremlin's Forbidden Playground")
        self.root.geometry("1600x900")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self.current_process: Optional[ProcessInfo] = None
        self.process_handle: Optional[int] = None
        self.memory_reader: Optional[MemoryReader] = None
        self.scanner: Optional[MemoryScanner] = None
        self.selected_addresses: List[ScanResult] = []
        self.script_engine: Optional[ScriptEngine] = None
        self.cheat_table = CheatTable()
        self.current_table_path = None
        
        self._setup_menu()
        self._setup_ui()
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self._update_frozen_addresses()
    
    def _setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 File (where stuff lives)", menu=file_menu)
        file_menu.add_command(label="📋 New Chaos Table", command=self._new_table)
        file_menu.add_command(label="📂 Summon Existing Table", command=self._load_table)
        file_menu.add_command(label="💾 Yeet Table To Disk", command=self._save_table)
        file_menu.add_command(label="💾 Yeet Table Somewhere Else", command=self._save_table_as)
        file_menu.add_separator()
        file_menu.add_command(label="🔄 Refresh The Process Zoo 🦝", command=self._refresh_processes)
        file_menu.add_separator()
        file_menu.add_command(label="❌ Abandon Ship", command=self._on_close)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="✏️ Edit (poke stuff)", menu=edit_menu)
        edit_menu.add_command(label="➕ Manually Adopt An Address 👶", command=self._add_address_manually)
        edit_menu.add_command(label="🗑️ Yeet Selected Into The Void", command=self._remove_selected_address)
        edit_menu.add_command(label="📝 Rename Address (give it a silly name)", command=self._rename_address)
        edit_menu.add_separator()
        edit_menu.add_command(label="⚙️ Settings (boring toggles)", command=self._show_settings)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🛠️ Tools (fancy stuff)", menu=tools_menu)
        tools_menu.add_command(label="🔍 Pointer Scanner (find the sneaky bois)", command=self._show_pointer_scanner)
        tools_menu.add_command(label="📊 Memory Viewer (hex dungeon)", command=self._show_memory_viewer)
        tools_menu.add_command(label="🎯 Address Calculator (maffs)", command=self._show_address_calculator)
        tools_menu.add_separator()
        tools_menu.add_command(label="📝 Script Manager (your code zoo)", command=self._show_script_manager)
        tools_menu.add_command(label="🤖 Auto-Assembler (ASM go brrr)", command=self._show_assembler)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Help (cuz u stuck)", menu=help_menu)
        help_menu.add_command(label="📖 Read The Forbidden Texts", command=self._show_documentation)
        help_menu.add_command(label="⌨️ Button Combos That Do Things", command=self._show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="😼 About This Goofy Tool", command=self._show_about)
    
    def _setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        scan_tab = ttk.Frame(self.notebook)
        self.notebook.add(scan_tab, text="🔍 Sniff-Sniff Scanner")
        self._setup_scanner_tab(scan_tab)
        
        script_tab = ttk.Frame(self.notebook)
        self.notebook.add(script_tab, text="📝 Code Chaos Zone")
        self._setup_script_tab(script_tab)
        
        tools_tab = ttk.Frame(self.notebook)
        self.notebook.add(tools_tab, text="🛠️ Big Brain Tools")
        self._setup_tools_tab(tools_tab)
        
        self.status_var = tk.StringVar(value="zzz... MeowMeow is sleeping 😴")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _setup_scanner_tab(self, parent):
        """Setup the main scanner interface"""
        main_container = ttk.Frame(parent)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        left_frame = ttk.LabelFrame(main_container, text="🎯 Victim Selection (pick ur target)", padding=10)
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
        
        results_frame = ttk.LabelFrame(center_frame, text="📊 Found Byte Nuggets (scan results lol)", padding=10)
        results_frame.pack(fill="both", expand=True)
        
        self.results_table = AddressTableWidget(
            results_frame,
            self._on_address_selected,
            show_freeze=False
        )
        self.results_table.pack(fill="both", expand=True)
        
        right_frame = ttk.LabelFrame(main_container, text="📌 The Adopted Children (ur fav addies)", padding=10)
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
    
    def _setup_script_tab(self, parent):
        self.script_editor = ScriptEditorWidget(
            parent,
            self._on_execute_script,
            self._on_save_script
        )
        self.script_editor.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _setup_tools_tab(self, parent):
        tools_container = ttk.Frame(parent, padding=10)
        tools_container.pack(fill="both", expand=True)
        
        info_frame = ttk.LabelFrame(tools_container, text="📊 Process Brain Scan (what's inside?)", padding=10)
        info_frame.pack(fill="x", pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=8, wrap="word", font=("Consolas", 9))
        self.info_text.pack(fill="both", expand=True)
        self.info_text.insert("1.0", "No process selected... pick a victim first! 😈")
        self.info_text.config(state="disabled")
        
        actions_frame = ttk.LabelFrame(tools_container, text="⚡ Quick Chaos Buttons (do stuff fast)", padding=10)
        actions_frame.pack(fill="both", expand=True)
        
        btn_frame = ttk.Frame(actions_frame)
        btn_frame.pack(fill="both", expand=True)
        
        actions = [
            ("🔄 Re-Sniff Memory Zones", self._rescan_memory),
            ("📋 Yeet Results To File", self._export_results),
            ("🧹 Nuke Everything", self._clear_all),
            ("❄️ Freeze ALL The Things", self._freeze_all),
            ("🔥 Unfreeze ALL The Things", self._unfreeze_all),
            ("📊 Show Me The Numbers", self._show_statistics),
        ]
        
        for i, (text, command) in enumerate(actions):
            btn = ttk.Button(btn_frame, text=text, command=command, width=25)
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
    
    def _refresh_processes(self):
        self.process_list.refresh()
        self.status_var.set("🐾 Restocked the process zoo with fresh critters!")
    
    def _on_process_selected(self, process: ProcessInfo):
        try:
            if self.process_handle:
                ProcessManager.close_process(self.process_handle)
            
            self.process_handle = ProcessManager.open_process(process.pid)
            if not self.process_handle:
                messagebox.showerror(
                    "BONK! 🔨",
                    f"MeowMeow bonked head on {process.name} 💥\n\n"
                    "Windows said NO. Try running as admin?\n"
                    "(or pick a less protected process lol)"
                )
                return
            
            self.current_process = process
            self.memory_reader = MemoryReader(self.process_handle)
            self.scanner = MemoryScanner(self.memory_reader)
            self.script_engine = ScriptEngine(self.memory_reader, self.scanner, process)
            
            self.results_table.clear()
            self.address_table.clear()
            self.selected_addresses.clear()
            
            self.scan_panel.set_enabled(True)
            self.root.title(f"MemMeowMeow 🐾 – Currently Nomming On: {process.name}")
            self.status_var.set(
                f"😼 LATCHED ONTO {process.name} (PID: {process.pid})! "
                f"Found {len(self.memory_reader.regions)} juicy memory zones to sniff! 🍖"
            )
            
            self._update_process_info()
            
        except Exception as e:
            messagebox.showerror("OH NO 😱", f"MeowMeow tripped and fell:\n{e}\n\nTry again maybe?")
            self.status_var.set("💀 Attachment failed spectacularly")
    
    def _update_process_info(self):
        if not self.current_process or not self.memory_reader:
            return
        
        mb_size = self.memory_reader.total_memory_size / (1024*1024)
        
        info = f"""🎮 Process Name: {self.current_process.name}
🔢 PID (the forbidden number): {self.current_process.pid}
📂 Lives At: {self.current_process.exe_path or 'idk lol, Windows is hiding it'}

🗺️ Memory Regions (places to sniff): {len(self.memory_reader.regions)}
💾 Total Sniffable RAM: {mb_size:.2f} MB ({mb_size * 1024:.0f} KB of pure chaos)

✅ Readable Zones: {len(self.memory_reader.regions)} (all of them are yummy)
🐾 MeowMeow Status: Ready to cause trouble!
"""
        
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", info)
        self.info_text.config(state="disabled")
    
    def _on_scan(self, value: str, data_type: DataType):
        if not self.scanner:
            messagebox.showwarning(
                "UH OH SPAGHETTI-O 🍝", 
                "You told MeowMeow to scan but didn't pick a process...\n\n"
                "What am I scanning? THE AIR?? 🌬️"
            )
            return
        
        self.scan_panel.set_enabled(False)
        self.status_var.set("👃 *sniff sniff* MeowMeow is digging through the RAM bushes...")

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
        
        if len(results) == 0:
            self.status_var.set("💀 Found NOTHING. Skill issue? Try different value lol")
        elif len(results) == 1:
            self.status_var.set("🎯 JACKPOT! Found exactly 1 address! *chef's kiss* 😘")
        elif len(results) > 10000:
            self.status_var.set(f"😳 HOLY HECK found {len(results)} matches! That's... a lot. Maybe filter?")
            messagebox.showinfo(
                "TOO MANY BYTE NUGGETS 🍗",
                f"Found {len(results)} matches.\n\n"
                "That's enough RAM noodles to feed a small army!\n"
                "Consider using filters before MeowMeow's brain explodes 💥"
            )
        else:
            self.status_var.set(f"✨ Scan complete! Found {len(results)} juicy byte-nuggets hiding in RAM!")
    
    def _on_scan_error(self, error_msg: str):
        messagebox.showerror(
            "SCAN GO BOOM 💥", 
            f"MeowMeow tripped over a pointer and faceplanted:\n\n{error_msg}\n\n"
            "Maybe try scanning for something else?"
        )
        self.scan_panel.set_enabled(True)
        self.scan_panel.set_progress(0)
        self.status_var.set("💀 Scan failed. MeowMeow is embarrassed.")
    
    def _on_filter(self, filter_type: str, value: str, data_type: DataType):
        if not self.scanner or not self.scanner.results:
            messagebox.showwarning(
                "NOTHING TO FILTER BRO 🤷",
                "You need to scan for something first!\n"
                "Can't filter air molecules lol"
            )
            return
        
        try:
            if filter_type == "changed":
                results = self.scanner.filter_changed(data_type)
            elif filter_type == "unchanged":
                results = self.scanner.filter_unchanged(data_type)
            elif filter_type == "increased":
                results = self.scanner.filter_results(
                    lambda current, old: current > old, None, data_type
                )
            elif filter_type == "decreased":
                results = self.scanner.filter_results(
                    lambda current, old: current < old, None, data_type
                )
            else:
                predicates = {
                    "=": lambda a, b: a == b,
                    "!=": lambda a, b: a != b,
                    ">": lambda a, b: a > b,
                    "<": lambda a, b: a < b,
                }
                comp_value = TypeConverter.from_bytes(
                    TypeConverter.to_bytes(value, data_type), data_type
                )
                results = self.scanner.filter_results(
                    predicates[filter_type], comp_value, data_type
                )
            
            self.results_table.set_results(results)
            self.status_var.set(f"🔽 Filtered down to {len(results)} matches! Getting warmer! 🔥")
        except Exception as e:
            messagebox.showerror("FILTER BROKE 💔", f"Filter machine go boom:\n{e}")
    
    def _on_address_selected(self, result: ScanResult):
        if result not in self.selected_addresses:
            self.selected_addresses.append(result)
            self.address_table.add_result(result)
            self.cheat_table.add_entry(
                result.address,
                f"Address_{len(self.selected_addresses)}",
                result.data_type,
                False
            )
            self.status_var.set(f"👶 Adopted lil address 0x{result.address:X} into the MeowMeow daycare!")
    
    def _on_address_freeze(self, result: ScanResult, frozen: bool):
        result.frozen = frozen
        if frozen:
            self.status_var.set(f"❄️ Put 0x{result.address:X} in a tiny ice cube! It can't move now! *evil laugh*")
        else:
            self.status_var.set(f"🔥 Thawed 0x{result.address:X}! It's free to wiggle again!")
    
    def _on_address_edit(self, result: ScanResult, new_value: str):
        if not self.memory_reader:
            return
        
        try:
            data = TypeConverter.to_bytes(new_value, result.data_type)
            if self.memory_reader.write_bytes(result.address, data):
                result.update_value(data)
                self.address_table.refresh_result(result)
                self.status_var.set(f"🔨 BONKED new value into 0x{result.address:X} with a tiny hammer! *bonk*")
            else:
                messagebox.showerror(
                    "WRITE FAIL 😭",
                    "Couldn't write to memory!\n"
                    "Maybe Windows blocked MeowMeow? 🚫"
                )
        except Exception as e:
            messagebox.showerror("EDIT GO BOOM 💥", f"Failed to edit value:\n{e}")
    
    def _on_address_delete(self, result: ScanResult):
        if result in self.selected_addresses:
            self.selected_addresses.remove(result)
            self.status_var.set(f"🗑️ Yeeted 0x{result.address:X} into the void! Bye bye!")
    
    def _on_execute_script(self, code: str):
        if not self.script_engine:
            messagebox.showwarning(
                "NO VICTIM SELECTED 🎯",
                "Attach to a process first!\n\n"
                "Scripts need something to mess with!"
            )
            return
        
        self.status_var.set("🤖 Executing ur forbidden code...")
        result = self.script_engine.execute(code)
        
        if result.success:
            self.script_editor.set_output(result.output or "✅ Script ran successfully! (it didn't print anything tho)")
            self.status_var.set("✨ Script executed! MeowMeow is proud of u! 🐾")
        else:
            self.script_editor.set_output(result.error, is_error=True)
            self.status_var.set("💀 Script exploded. Check the error log lol")
    
    def _on_save_script(self, filepath: str):
        self.cheat_table.add_script(
            name=filepath.split('/')[-1],
            code=self.script_editor.get_script(),
            auto_run=False
        )
        self.status_var.set(f"💾 Saved script to: {filepath}")
    
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
    
    def _new_table(self):
        if messagebox.askyesno(
            "NEW TABLE TIME 📋", 
            "Create new table?\n\nAny unsaved chaos will be lost forever! 💀"
        ):
            self.address_table.clear()
            self.selected_addresses.clear()
            self.cheat_table = CheatTable()
            self.current_table_path = None
            self.status_var.set("📋 Fresh new table created! Time to make more chaos!")
    
    def _load_table(self):
        filepath = filedialog.askopenfilename(
            title="Pick a table to summon 📂",
            filetypes=[("MemMeowMeow Table", "*.mmt"), ("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                self.cheat_table.load(filepath)
                self.current_table_path = filepath
                self.address_table.clear()
                self.selected_addresses.clear()
                for entry in self.cheat_table.entries:
                    result = ScanResult(
                        address=entry['address'],
                        value=b'',
                        data_type=entry['data_type'],
                        frozen=entry.get('frozen', False)
                    )
                    self.selected_addresses.append(result)
                    self.address_table.add_result(result)
                
                self.status_var.set(f"📂 Summoned table from: {filepath.split('/')[-1]} ✨")
                messagebox.showinfo(
                    "TABLE LOADED 🎉",
                    f"Successfully loaded {len(self.cheat_table.entries)} addresses!\n"
                    f"And {len(self.cheat_table.scripts)} scripts!"
                )
            except Exception as e:
                messagebox.showerror("LOAD FAIL 💥", f"Couldn't load table:\n{e}")
    
    def _save_table(self):
        if self.current_table_path:
            self._save_table_to_path(self.current_table_path)
        else:
            self._save_table_as()
    
    def _save_table_as(self):
        filepath = filedialog.asksaveasfilename(
            title="Where should MeowMeow yeet this table? 💾",
            defaultextension=".mmt",
            filetypes=[("MemMeowMeow Table", "*.mmt"), ("JSON Files", "*.json")]
        )
        if filepath:
            self._save_table_to_path(filepath)
    
    def _save_table_to_path(self, filepath: str):
        try:
            self.cheat_table.entries.clear()
            for result in self.selected_addresses:
                self.cheat_table.add_entry(
                    result.address,
                    f"Address_0x{result.address:X}",
                    result.data_type,
                    result.frozen
                )
            
            self.cheat_table.save(filepath)
            self.current_table_path = filepath
            self.status_var.set(f"💾 Table yeeted to: {filepath.split('/')[-1]} 🎯")
            messagebox.showinfo("SAVE SUCCESS ✅", "Table saved successfully!")
        except Exception as e:
            messagebox.showerror("SAVE FAIL 😭", f"Couldn't save table:\n{e}")
    
    def _add_address_manually(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("🎯 Manually Adopt An Address")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        
        ttk.Label(dialog, text="Enter Address (hex, like 0x12345678):", font=("Arial", 10)).pack(pady=10)
        addr_entry = ttk.Entry(dialog, width=30, font=("Consolas", 10))
        addr_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Pick a Data Type:", font=("Arial", 10)).pack(pady=10)
        type_var = tk.StringVar(value="Int32")
        type_combo = ttk.Combobox(
            dialog,
            textvariable=type_var,
            values=[dt.display_name for dt in DataType],
            state="readonly",
            width=28
        )
        type_combo.pack(pady=5)
        
        def add_it():
            try:
                addr_str = addr_entry.get().strip()
                if addr_str.startswith("0x") or addr_str.startswith("0X"):
                    address = int(addr_str, 16)
                else:
                    address = int(addr_str, 16 if len(addr_str) > 6 else 10)
                
                data_type = DataType.from_string(type_var.get())
                result = ScanResult(
                    address=address,
                    value=b'\x00' * data_type.byte_size,
                    data_type=data_type,
                    frozen=False
                )
                
                self.selected_addresses.append(result)
                self.address_table.add_result(result)
                self.status_var.set(f"👶 Manually adopted 0x{address:X}! Welcome to the family!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("INVALID ADDRESS 😵", f"That address looks weird:\n{e}")
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="✅ Add It!", command=add_it, width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="❌ Nevermind", command=dialog.destroy, width=15).pack(side="left", padx=5)
    
    def _remove_selected_address(self):
        selection = self.address_table.tree.selection()
        if selection:
            result = self.address_table.result_map.get(selection[0])
            if result:
                self._on_address_delete(result)
                self.address_table.tree.delete(selection[0])
                del self.address_table.result_map[selection[0]]
                self.address_table._update_info()
        else:
            messagebox.showinfo("NOTHING SELECTED 🤷", "Select an address first!")
    
    def _rename_address(self):
        messagebox.showinfo(
            "COMING SOON-ISH 🚧",
            "MeowMeow is still learning how to do this!\n\n"
            "For now, addresses get auto-named. Deal with it! 😼"
        )
    
    def _show_settings(self):
        settings = tk.Toplevel(self.root)
        settings.title("⚙️ Settings (toggles and stuff)")
        settings.geometry("500x400")
        
        ttk.Label(
            settings, 
            text="🎛️ MeowMeow Settings (mess with these at your own risk)",
            font=("Arial", 12, "bold")
        ).pack(pady=15)
        
        settings_frame = ttk.Frame(settings, padding=20)
        settings_frame.pack(fill="both", expand=True)
        
        ttk.Label(settings_frame, text="Scan Speed (how fast MeowMeow sniffs):").grid(row=0, column=0, sticky="w", pady=10)
        speed_var = tk.StringVar(value="Normal")
        speed_combo = ttk.Combobox(
            settings_frame,
            textvariable=speed_var,
            values=["Slow (careful sniff)", "Normal (balanced)", "Fast (zoomy boi)", "LUDICROUS SPEED 🚀"],
            state="readonly",
            width=25
        )
        speed_combo.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(settings_frame, text="Freeze Update Rate (ms):").grid(row=1, column=0, sticky="w", pady=10)
        freeze_var = tk.IntVar(value=100)
        freeze_spinbox = ttk.Spinbox(settings_frame, from_=10, to=1000, textvariable=freeze_var, width=24)
        freeze_spinbox.grid(row=1, column=1, padx=10, pady=10)
        
        auto_attach_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            settings_frame,
            text="Auto-attach to last process on startup",
            variable=auto_attach_var
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=10)
        
        show_hex_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            settings_frame,
            text="Show addresses in hex (if off, uses decimal like a weirdo)",
            variable=show_hex_var
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=10)
        
        confirm_exit_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            settings_frame,
            text="Ask before closing (prevent accidents)",
            variable=confirm_exit_var
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=10)
        
        ttk.Button(
            settings,
            text="✅ Save Settings (actually doesn't work yet lol)",
            command=lambda: [
                messagebox.showinfo("SAVED (not really)", "Settings saved! (jk they reset on restart) 😼"),
                settings.destroy()
            ]
        ).pack(pady=10)
    
    def _show_pointer_scanner(self):
        ptr_window = tk.Toplevel(self.root)
        ptr_window.title("🔍 Pointer Scanner (find the sneaky indirect bois)")
        ptr_window.geometry("700x600")
        
        ttk.Label(
            ptr_window,
            text="🎯 Pointer Scanner - Find addresses that point to your value",
            font=("Arial", 12, "bold")
        ).pack(pady=15)
        
        input_frame = ttk.LabelFrame(ptr_window, text="Scan Parameters", padding=15)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(input_frame, text="Target Address (the address you wanna find pointers to):").grid(row=0, column=0, sticky="w", pady=5)
        target_entry = ttk.Entry(input_frame, width=30, font=("Consolas", 10))
        target_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(input_frame, text="Max Offset (how far pointers can be):").grid(row=1, column=0, sticky="w", pady=5)
        offset_spinbox = ttk.Spinbox(input_frame, from_=0, to=4096, width=28)
        offset_spinbox.set(1024)
        offset_spinbox.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(input_frame, text="Max Depth (pointer chain length):").grid(row=2, column=0, sticky="w", pady=5)
        depth_spinbox = ttk.Spinbox(input_frame, from_=1, to=7, width=28)
        depth_spinbox.set(3)
        depth_spinbox.grid(row=2, column=1, padx=10, pady=5)
        
        results_frame = ttk.LabelFrame(ptr_window, text="Results (pointer chains found)", padding=10)
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        results_text = tk.Text(results_frame, wrap="word", font=("Consolas", 9))
        results_text.pack(fill="both", expand=True)
        results_text.insert("1.0", "Click 'Start Scanning' to find pointers!\n\nThis might take a while... 🐌")
        
        def start_scan():
            results_text.delete("1.0", "end")
            results_text.insert("1.0", "🔍 Scanning for pointers... this is gonna take a hot minute...\n\n")
            results_text.insert("end", "⚠️ POINTER SCANNING NOT FULLY IMPLEMENTED YET ⚠️\n\n")
            results_text.insert("end", "But when it is, it'll:\n")
            results_text.insert("end", "1. Search memory for values that equal your target address\n")
            results_text.insert("end", "2. Follow pointer chains up to your specified depth\n")
            results_text.insert("end", "3. Display all pointer paths that lead to your address\n\n")
            results_text.insert("end", "Example output:\n")
            results_text.insert("end", "\"game.exe\"+0x123456 -> [+0x10] -> [+0x20] -> YOUR_ADDRESS\n\n")
            results_text.insert("end", "MeowMeow is still learning this advanced sorcery! 🧙‍♂️✨")
        
        ttk.Button(
            ptr_window,
            text="🚀 Start Scanning (might lag ur PC lol)",
            command=start_scan
        ).pack(pady=10)
    
    def _show_memory_viewer(self):
        viewer = tk.Toplevel(self.root)
        viewer.title("📊 Memory Viewer (raw byte dungeon)")
        viewer.geometry("900x600")
        
        if not self.memory_reader:
            ttk.Label(
                viewer,
                text="⚠️ No process attached! Pick a victim first! ⚠️",
                font=("Arial", 14)
            ).pack(expand=True)
            return
        
        control_frame = ttk.Frame(viewer, padding=10)
        control_frame.pack(fill="x")
        
        ttk.Label(control_frame, text="Address to view:").pack(side="left", padx=5)
        addr_entry = ttk.Entry(control_frame, width=20, font=("Consolas", 10))
        addr_entry.pack(side="left", padx=5)
        
        ttk.Label(control_frame, text="Bytes to read:").pack(side="left", padx=5)
        size_spinbox = ttk.Spinbox(control_frame, from_=16, to=4096, width=10)
        size_spinbox.set(256)
        size_spinbox.pack(side="left", padx=5)
        
        hex_text = tk.Text(viewer, wrap="none", font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4")
        hex_scroll = ttk.Scrollbar(viewer, orient="vertical", command=hex_text.yview)
        hex_text.configure(yscrollcommand=hex_scroll.set)
        hex_text.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        hex_scroll.pack(side="right", fill="y", pady=10)
        
        def view_memory():
            try:
                addr_str = addr_entry.get().strip()
                if addr_str.startswith("0x"):
                    address = int(addr_str, 16)
                else:
                    address = int(addr_str, 16)
                
                size = int(size_spinbox.get())
                data = self.memory_reader.read_bytes(address, size)
                
                hex_text.delete("1.0", "end")
                
                if not data:
                    hex_text.insert("1.0", "❌ Couldn't read memory at that address!\nMaybe it's protected or doesn't exist? 🤷")
                    return
                
                hex_text.insert("end", f"Memory at 0x{address:X} ({size} bytes):\n\n")
                hex_text.insert("end", "Address    | 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F | ASCII\n")
                hex_text.insert("end", "-" * 80 + "\n")
                
                for i in range(0, len(data), 16):
                    addr = address + i
                    hex_text.insert("end", f"0x{addr:08X} | ")
                    
                    chunk = data[i:i+16]
                    hex_str = " ".join(f"{b:02X}" for b in chunk)
                    hex_str += "   " * (16 - len(chunk))  # Padding
                    hex_text.insert("end", hex_str + " | ")
                    
                    ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
                    hex_text.insert("end", ascii_str + "\n")
                
            except Exception as e:
                hex_text.delete("1.0", "end")
                hex_text.insert("1.0", f"💥 Error viewing memory:\n{e}\n\nMake sure the address is valid!")
        
        ttk.Button(control_frame, text="👁️ View", command=view_memory).pack(side="left", padx=5)
        
        if self.selected_addresses:
            addr_entry.insert(0, f"0x{self.selected_addresses[0].address:X}")
            view_memory()
    
    def _show_address_calculator(self):
        calc = tk.Toplevel(self.root)
        calc.title("🧮 Address Calculator (do the maffs)")
        calc.geometry("500x450")
        
        ttk.Label(
            calc,
            text="🧮 Address Calculator & Converter",
            font=("Arial", 12, "bold")
        ).pack(pady=15)
        
        convert_frame = ttk.LabelFrame(calc, text="Hex ↔️ Decimal Converter", padding=15)
        convert_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(convert_frame, text="Hex (0x...):").grid(row=0, column=0, sticky="w", pady=5)
        hex_entry = ttk.Entry(convert_frame, width=30, font=("Consolas", 10))
        hex_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(convert_frame, text="Decimal:").grid(row=1, column=0, sticky="w", pady=5)
        dec_entry = ttk.Entry(convert_frame, width=30, font=("Consolas", 10))
        dec_entry.grid(row=1, column=1, padx=10, pady=5)
        
        def hex_to_dec():
            try:
                val = hex_entry.get().strip()
                if val.startswith("0x"):
                    val = val[2:]
                dec = int(val, 16)
                dec_entry.delete(0, "end")
                dec_entry.insert(0, str(dec))
            except:
                messagebox.showerror("INVALID HEX 😵", "That doesn't look like valid hex!")
        
        def dec_to_hex():
            try:
                dec = int(dec_entry.get().strip())
                hex_entry.delete(0, "end")
                hex_entry.insert(0, f"0x{dec:X}")
            except:
                messagebox.showerror("INVALID NUMBER 😵", "That doesn't look like a valid number!")
        
        btn_frame = ttk.Frame(convert_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Hex → Dec", command=hex_to_dec).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Dec → Hex", command=dec_to_hex).pack(side="left", padx=5)
        
        math_frame = ttk.LabelFrame(calc, text="Address Math (add/subtract offsets)", padding=15)
        math_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(math_frame, text="Base Address:").grid(row=0, column=0, sticky="w", pady=5)
        base_entry = ttk.Entry(math_frame, width=30, font=("Consolas", 10))
        base_entry.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(math_frame, text="Offset (+/-):").grid(row=1, column=0, sticky="w", pady=5)
        offset_entry = ttk.Entry(math_frame, width=30, font=("Consolas", 10))
        offset_entry.grid(row=1, column=1, padx=10, pady=5)
        
        result_var = tk.StringVar(value="Result will appear here")
        ttk.Label(math_frame, textvariable=result_var, font=("Consolas", 11, "bold")).grid(row=3, column=0, columnspan=2, pady=10)
        
        def calculate():
            try:
                base_str = base_entry.get().strip()
                if base_str.startswith("0x"):
                    base = int(base_str, 16)
                else:
                    base = int(base_str)
                
                offset_str = offset_entry.get().strip()
                if offset_str.startswith("0x"):
                    offset = int(offset_str, 16)
                else:
                    offset = int(offset_str)
                
                result = base + offset
                result_var.set(f"Result: 0x{result:X} ({result})")
            except Exception as e:
                messagebox.showerror("MATH ERROR 🤯", f"Couldn't calculate:\n{e}")
        
        ttk.Button(math_frame, text="🧮 Calculate", command=calculate).grid(row=2, column=0, columnspan=2, pady=10)
    
    def _show_script_manager(self):
        manager = tk.Toplevel(self.root)
        manager.title("📝 Script Manager (your code zoo)")
        manager.geometry("600x500")
        
        ttk.Label(
            manager,
            text="📝 Saved Scripts",
            font=("Arial", 12, "bold")
        ).pack(pady=15)
        
        list_frame = ttk.Frame(manager, padding=10)
        list_frame.pack(fill="both", expand=True, padx=10)
        
        script_list = tk.Listbox(list_frame, font=("Arial", 10))
        script_list.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=script_list.yview)
        scrollbar.pack(side="right", fill="y")
        script_list.configure(yscrollcommand=scrollbar.set)
        
        # Populate with saved scripts
        for i, script in enumerate(self.cheat_table.scripts):
            script_list.insert("end", f"{i+1}. {script['name']} {'[AUTO]' if script.get('auto_run') else ''}")
        
        if not self.cheat_table.scripts:
            script_list.insert("end", "No scripts saved yet! Go write some chaos code! 😼")
        
        btn_frame = ttk.Frame(manager, padding=10)
        btn_frame.pack(fill="x")
        
        def load_script():
            selection = script_list.curselection()
            if selection:
                script = self.cheat_table.scripts[selection[0]]
                self.script_editor.set_script(script['code'])
                self.notebook.select(1)
                manager.destroy()
        
        def delete_script():
            selection = script_list.curselection()
            if selection:
                if messagebox.askyesno("DELETE SCRIPT 🗑️", "Really yeet this script into the void?"):
                    del self.cheat_table.scripts[selection[0]]
                    script_list.delete(selection[0])
        
        ttk.Button(btn_frame, text="📂 Load Script", command=load_script).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ Delete Script", command=delete_script).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="❌ Close", command=manager.destroy).pack(side="right", padx=5)
    
    def _show_assembler(self):
        asm_window = tk.Toplevel(self.root)
        asm_window.title("🤖 Auto-Assembler (ASM go brrr)")
        asm_window.geometry("800x600")
        
        ttk.Label(
            asm_window,
            text="🤖 Auto-Assembler - Inject Assembly Code",
            font=("Arial", 12, "bold")
        ).pack(pady=15)
        
        ttk.Label(
            asm_window,
            text="⚠️ ADVANCED FEATURE - CAN CRASH GAMES ⚠️",
            font=("Arial", 10, "bold"),
            foreground="red"
        ).pack(pady=5)
        
        editor_frame = ttk.LabelFrame(asm_window, text="Assembly Code", padding=10)
        editor_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        asm_text = tk.Text(editor_frame, wrap="none", font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4")
        asm_scroll = ttk.Scrollbar(editor_frame, orient="vertical", command=asm_text.yview)
        asm_text.configure(yscrollcommand=asm_scroll.set)
        asm_text.pack(side="left", fill="both", expand=True)
        asm_scroll.pack(side="right", fill="y")
        
        template = """; Example: NOP out some instructions
; address: 0x12345678
; original bytes: 89 45 FC  (mov [ebp-04],eax)

; Inject at address:
alloc(newmem, 2048)
label(return)

newmem:
  ; Your code here
  mov [ebp-04],eax
  jmp return

; Hook
0x12345678:
  jmp newmem
return:

; ⚠️ AUTO-ASSEMBLER NOT FULLY IMPLEMENTED YET ⚠️
; This would require:
; - x86/x64 assembler (keystone-engine)
; - Code cave allocation
; - Hook injection
; - Detour management

; MeowMeow is still too smol to handle this! 🐱
"""
        asm_text.insert("1.0", template)
        
        btn_frame = ttk.Frame(asm_window, padding=10)
        btn_frame.pack(fill="x")
        
        def inject():
            messagebox.showinfo(
                "NOT IMPLEMENTED 🚧",
                "Auto-assembler requires additional libraries:\n\n"
                "- keystone-engine (x86/x64 assembler)\n"
                "- capstone (disassembler)\n\n"
                "These are big boi dependencies that MeowMeow\n"
                "doesn't have installed yet!\n\n"
                "But the UI is ready when they are! 😼"
            )
        
        ttk.Button(btn_frame, text="💉 Inject Code", command=inject).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🧹 Clear", command=lambda: asm_text.delete("1.0", "end")).pack(side="left", padx=5)
    
    def _rescan_memory(self):
        if self.memory_reader:
            self.status_var.set("🔄 Re-sniffing memory zones...")
            self.memory_reader._scan_memory_regions()
            self._update_process_info()
            self.status_var.set(f"✅ Memory rescanned! Found {len(self.memory_reader.regions)} zones!")
        else:
            messagebox.showinfo("NO PROCESS 🤷", "Attach to a process first!")
    
    def _export_results(self):
        if not self.scanner or not self.scanner.results:
            messagebox.showinfo("NOTHING TO EXPORT 📋", "Scan for something first!")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="Where should MeowMeow dump these results? 📋",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"MemMeowMeow Scan Results 🐾\n")
                    f.write(f"Total Results: {len(self.scanner.results)}\n")
                    f.write("=" * 50 + "\n\n")
                    for result in self.scanner.results:
                        f.write(f"0x{result.address:X},{result.get_value()}\n")
                self.status_var.set(f"📋 Exported {len(self.scanner.results)} results to file! ✅")
                messagebox.showinfo("EXPORT SUCCESS 🎉", f"Dumped {len(self.scanner.results)} addresses!")
            except Exception as e:
                messagebox.showerror("EXPORT FAIL 💥", f"Couldn't export:\n{e}")
    
    def _clear_all(self):
        if messagebox.askyesno(
            "NUKE EVERYTHING? 💣",
            "This will delete:\n"
            "• All scan results\n"
            "• All saved addresses\n"
            "• Everything in the tables\n\n"
            "Are you SURE? This can't be undone!"
        ):
            self.results_table.clear()
            self.address_table.clear()
            self.selected_addresses.clear()
            if self.scanner:
                self.scanner.clear_results()
            self.status_var.set("💥 EVERYTHING HAS BEEN YEETED INTO THE VOID!")
    
    def _freeze_all(self):
        if not self.selected_addresses:
            messagebox.showinfo("NOTHING TO FREEZE ❄️", "Add some addresses first!")
            return
        
        for result in self.selected_addresses:
            result.frozen = True
        self.address_table.refresh_all()
        self.status_var.set(f"❄️ Froze ALL {len(self.selected_addresses)} addresses! They're icicles now!")
        messagebox.showinfo("FREEZE SUCCESSFUL ❄️", f"Put {len(self.selected_addresses)} addresses in tiny ice cubes!")
    
    def _unfreeze_all(self):
        if not self.selected_addresses:
            messagebox.showinfo("NOTHING TO THAW 🔥", "Add some addresses first!")
            return
        
        frozen_count = sum(1 for r in self.selected_addresses if r.frozen)
        for result in self.selected_addresses:
            result.frozen = False
        self.address_table.refresh_all()
        self.status_var.set(f"🔥 Thawed ALL {frozen_count} frozen addresses! They're free!")
        messagebox.showinfo("THAW SUCCESSFUL 🔥", f"Unfroze {frozen_count} addresses! They're gooey again!")
    
    def _show_statistics(self):
        if not self.memory_reader:
            messagebox.showinfo("NO DATA 📊", "Attach to a process first!")
            return
        
        scan_results = len(self.scanner.results) if self.scanner and self.scanner.results else 0
        frozen = sum(1 for r in self.selected_addresses if r.frozen)
        
        stats = f"""📊 MeowMeow Statistics 📊

🎯 Current Target: {self.current_process.name if self.current_process else 'None'}
🔢 Process PID: {self.current_process.pid if self.current_process else 'N/A'}

🗺️ Memory Regions Found: {len(self.memory_reader.regions)}
💾 Total Readable Memory: {self.memory_reader.total_memory_size / (1024*1024):.2f} MB

🔍 Last Scan Results: {scan_results} matches
📌 Tracked Addresses: {len(self.selected_addresses)}
❄️ Frozen Addresses: {frozen}
🔥 Unfrozen Addresses: {len(self.selected_addresses) - frozen}

📝 Saved Scripts: {len(self.cheat_table.scripts)}
📋 Table Entries: {len(self.cheat_table.entries)}
"""
        messagebox.showinfo("📊 MeowMeow Stats", stats)
    
    def _show_documentation(self):
        self.notebook.select(1)
        self.script_editor._show_help()
        self.status_var.set("📖 Opened the forbidden documentation texts!")
    
    def _show_shortcuts(self):
        shortcuts = """⌨️ Keyboard Shortcuts ⌨️

Ctrl+S         - Save table/script
Ctrl+N         - New table
Ctrl+O         - Load table
Ctrl+Return    - Execute script (in script tab)
F5             - Refresh process list
F9             - Start new scan
Escape         - Stop current scan

Double-Click   - Add address to table (from results)
Right-Click    - Context menu (on addresses)

📝 Script Tab:
  Tab          - Insert 4 spaces
  Ctrl+Return  - Run script
  Ctrl+S       - Save script

🐾 Pro Tips:
  - Hold Shift while double-clicking for instant freeze
  - Use Ctrl+F in script tab to find text (coming soon)
  - Right-click addresses for quick actions
"""
        messagebox.showinfo("⌨️ Shortcuts", shortcuts)
    
    def _show_about(self):
        messagebox.showinfo(
            "😼 About MemMeowMeow",
            "MemMeowMeow 🐾 v0.2.0 Enhanced Edition\n\n"
            "A feral byte-goblin disguised as a smol kitten.\n"
            "It tip-taps through your RAM with tiny paws,\n"
            "meowing at pointers and occasionally\n"
            "committing tax fraud (allegedly).\n\n"
            "✨ ENHANCED FEATURES ✨\n"
            "• 🔍 Memory scanner (sniff-sniff)\n"
            "• 📝 Python scripting (code chaos)\n"
            "• ❄️ Value freezing (ice cube mode)\n"
            "• 📊 Hex viewer (byte dungeon)\n"
            "• 🎯 Pointer scanner (sneaky boi finder)\n"
            "• 💾 Cheat tables (save ur chaos)\n"
            "• 🛠️ Address calculator (do maffs)\n"
            "• 🤖 Script manager (code zoo)\n\n"
            "⚠️ Use responsibly (or don't, I'm a cat not a cop) ⚠️\n\n"
            "Built with love, chaos, and smol paws 🐾"
        )
    
    def _on_close(self):
        if messagebox.askyesno(
            "ABANDON SHIP? 🚢",
            "Really close MemMeowMeow?\n\n"
            "(unsaved changes will be lost forever!)"
        ):
            if self.process_handle:
                ProcessManager.close_process(self.process_handle)
            self.root.destroy()