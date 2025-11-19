import tkinter as tk
from tkinter import ttk
from typing import Callable
from core.types import DataType

class ScanPanelWidget(ttk.Frame):
    def __init__(self, parent, on_scan: Callable, on_filter: Callable):
        super().__init__(parent, padding=10)
        
        self.on_scan = on_scan
        self.on_filter = on_filter
        self.is_first_scan = True
        
        input_frame = ttk.Frame(self)
        input_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(input_frame, text="Num Num Value 🍬:").pack(side="left", padx=(0, 5))
        
        self.value_var = tk.StringVar()
        self.value_entry = ttk.Entry(input_frame, textvariable=self.value_var, width=20)
        self.value_entry.pack(side="left", padx=(0, 10))
        
        ttk.Label(input_frame, text="Byte Flavor 🍭:").pack(side="left", padx=(0, 5))
        
        self.type_var = tk.StringVar(value="Int32")
        type_combo = ttk.Combobox(
            input_frame,
            textvariable=self.type_var,
            values=[dt.display_name for dt in DataType],
            state="readonly",
            width=10
        )
        type_combo.pack(side="left", padx=(0, 10))
        
        ttk.Label(input_frame, text="Sniff Mode 🐽:").pack(side="left", padx=(0, 5))
        
        self.scan_type_var = tk.StringVar(value="=")
        self.scan_type_combo = ttk.Combobox(
            input_frame,
            textvariable=self.scan_type_var,
            values=["=", "!=", ">", "<"],
            state="readonly",
            width=5
        )
        self.scan_type_combo.pack(side="left", padx=(0, 10))
        
        self.scan_button = ttk.Button(
            input_frame,
            text="First Sniff 🐾",
            command=self._on_scan_click
        )
        self.scan_button.pack(side="left")
        
        filter_frame = ttk.LabelFrame(self, text="Sniff Adjustments 🔍✨", padding=5)
        filter_frame.pack(fill="x")
        
        filter_buttons = [
            ("Changed 🤯", "changed"),
            ("Unchanged 😴", "unchanged"),
            ("Increased 📈", "increased"),
            ("Decreased 📉", "decreased"),
        ]
        
        for i, (text, filter_type) in enumerate(filter_buttons):
            btn = ttk.Button(
                filter_frame,
                text=text,
                command=lambda ft=filter_type: self._on_filter_click(ft)
            )
            btn.grid(row=i // 2, column=i % 2, padx=2, pady=2, sticky="ew")
        
        filter_frame.grid_columnconfigure(0, weight=1)
        filter_frame.grid_columnconfigure(1, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            maximum=100,
            mode="determinate"
        )
        self.progress_bar.pack(fill="x", pady=(10, 0))
        
        self.set_enabled(False)
    
    def set_enabled(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.value_entry.config(state=state)
        self.scan_type_combo.config(state="readonly" if enabled else "disabled")
        self.scan_button.config(state=state)
        
        for child in self.winfo_children():
            if isinstance(child, ttk.LabelFrame):
                for btn in child.winfo_children():
                    if isinstance(btn, ttk.Button):
                        btn.config(state=state if not self.is_first_scan else "disabled")
    
    def set_progress(self, value: float):
        self.progress_var.set(value)
        self.update_idletasks()
    
    def _on_scan_click(self):
        value = self.value_var.get().strip()
        if not value:
            return
        
        try:
            data_type = DataType.from_string(self.type_var.get())
            self.on_scan(value, data_type)
            self.is_first_scan = False
            
            self.scan_button.config(text="Next Sniff 🐾🐽")
            
            for child in self.winfo_children():
                if isinstance(child, ttk.LabelFrame):
                    for btn in child.winfo_children():
                        if isinstance(btn, ttk.Button):
                            btn.config(state="normal")
        except Exception as e:
            print(f"Scan error: {e}")
    
    def _on_filter_click(self, filter_type: str):
        value = self.value_var.get().strip()
        data_type = DataType.from_string(self.type_var.get())
        
        if filter_type in ["changed", "unchanged", "increased", "decreased"]:
            self.on_filter(filter_type, "", data_type)
        else:
            if not value:
                return
            scan_type = self.scan_type_var.get()
            self.on_filter(scan_type, value, data_type)
