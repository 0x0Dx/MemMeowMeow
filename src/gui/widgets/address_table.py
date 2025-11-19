import tkinter as tk
from tkinter import ttk, simpledialog
from typing import Callable, Optional, List
from core.scanner import ScanResult

class AddressTableWidget(ttk.Frame):
    def __init__(self, parent, on_select: Optional[Callable], show_freeze: bool = False):
        super().__init__(parent)
        
        self.on_select = on_select
        self.show_freeze = show_freeze
        self.results: List[ScanResult] = []
        self.result_map = {}
        
        self.freeze_callback = None
        self.edit_callback = None
        self.delete_callback = None
        
        columns = ["address", "value"]
        if show_freeze:
            columns.insert(0, "frozen")
        
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        
        if show_freeze:
            self.tree.heading("frozen", text="❄ Freeze-Meow")
            self.tree.column("frozen", width=90, anchor="center")
        
        self.tree.heading("address", text="Addy (The Forbidden Numbers 🧮😼)")
        self.tree.column("address", width=180, anchor="w")
        
        self.tree.heading("value", text="Vibez (Value) ✨")
        self.tree.column("value", width=150, anchor="e")
        
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.page_size = 1000
        self.current_page = 0
        
        self.info_var = tk.StringVar(value="no brain cells found 😔")
        info_label = ttk.Label(self, textvariable=self.info_var)
        info_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        
        if not show_freeze:
            page_frame = ttk.Frame(self)
            page_frame.grid(row=3, column=0, columnspan=2, pady=(5, 0))
            
            ttk.Button(page_frame, text="⏮ first", command=self._first_page, width=5).pack(side="left", padx=2)
            ttk.Button(page_frame, text="◀ back", command=self._prev_page, width=5).pack(side="left", padx=2)
            ttk.Button(page_frame, text="next ▶", command=self._next_page, width=5).pack(side="left", padx=2)
            ttk.Button(page_frame, text="last ⏭", command=self._last_page, width=5).pack(side="left", padx=2)
        
        if on_select and not show_freeze:
            self.tree.bind("<Double-1>", self._on_double_click)
        
        if show_freeze:
            self.tree.bind("<Double-1>", self._on_edit_double_click)
            self.tree.bind("<Button-3>", self._on_right_click)
            
            self.context_menu = tk.Menu(self, tearoff=0)
            self.context_menu.add_command(label="❄ toggle freeze mode", command=self._toggle_freeze)
            self.context_menu.add_command(label="✏ edit vibez", command=self._edit_value)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="📋 copy addy", command=self._copy_address)
            self.context_menu.add_command(label="📋 copy vibez", command=self._copy_value)
            self.context_menu.add_separator()
            self.context_menu.add_command(label="🗑 yeet address", command=self._delete_address)
    
    def set_freeze_callback(self, callback: Callable):
        self.freeze_callback = callback
    
    def set_edit_callback(self, callback: Callable):
        self.edit_callback = callback
    
    def set_delete_callback(self, callback: Callable):
        self.delete_callback = callback
    
    def set_results(self, results: List[ScanResult]):
        self.results = results
        self.current_page = 0
        self._update_display()
    
    def add_result(self, result: ScanResult):
        if result not in self.results:
            self.results.append(result)
            self._add_result_to_tree(result)
            self._update_info()
    
    def clear(self):
        self.results.clear()
        self.result_map.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.info_var.set("nothing here but tumbleweeds 🌾💀")
    
    def refresh_result(self, result: ScanResult):
        for item_id, res in self.result_map.items():
            if res == result:
                self._update_tree_item(item_id, result)
                break
    
    def refresh_all(self):
        for item_id, result in self.result_map.items():
            self._update_tree_item(item_id, result)
    
    def _update_display(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.result_map.clear()
        
        start = self.current_page * self.page_size
        end = min(start + self.page_size, len(self.results))
        
        for result in self.results[start:end]:
            self._add_result_to_tree(result)
        
        self._update_info()
    
    def _add_result_to_tree(self, result: ScanResult):
        try:
            value_str = str(result.get_value())
        except:
            value_str = "idk bro 💀"
        
        if self.show_freeze:
            frozen_mark = "❄" if result.frozen else ""
            values = (frozen_mark, f"0x{result.address:X}", value_str)
        else:
            values = (f"0x{result.address:X}", value_str)
        
        item_id = self.tree.insert("", "end", values=values)
        self.result_map[item_id] = result
    
    def _update_tree_item(self, item_id: str, result: ScanResult):
        try:
            value_str = str(result.get_value())
        except:
            value_str = "idk bro 💀"
        
        if self.show_freeze:
            frozen_mark = "❄" if result.frozen else ""
            values = (frozen_mark, f"0x{result.address:X}", value_str)
        else:
            values = (f"0x{result.address:X}", value_str)
        
        self.tree.item(item_id, values=values)
    
    def _update_info(self):
        total = len(self.results)
        if total == 0:
            self.info_var.set("no results… skill issue 🤷‍♂️")
        elif self.show_freeze:
            frozen_count = sum(1 for r in self.results if r.frozen)
            self.info_var.set(f"{total} addies found ({frozen_count} iced ❄)")
        else:
            total_pages = (total + self.page_size - 1) // self.page_size
            self.info_var.set(f"page {self.current_page + 1}/{total_pages} — {total} goofy results 😼")
    
    def _first_page(self):
        self.current_page = 0
        self._update_display()
    
    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._update_display()
    
    def _next_page(self):
        max_page = (len(self.results) + self.page_size - 1) // self.page_size - 1
        if self.current_page < max_page:
            self.current_page += 1
            self._update_display()
    
    def _last_page(self):
        self.current_page = (len(self.results) + self.page_size - 1) // self.page_size - 1
        self._update_display()
    
    def _on_double_click(self, event):
        selection = self.tree.selection()
        if selection and self.on_select:
            result = self.result_map.get(selection[0])
            if result:
                self.on_select(result)
    
    def _on_edit_double_click(self, event):
        self._edit_value()
    
    def _on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _toggle_freeze(self):
        selection = self.tree.selection()
        if selection and self.freeze_callback:
            result = self.result_map.get(selection[0])
            if result:
                result.frozen = not result.frozen
                self.freeze_callback(result, result.frozen)
                self.refresh_result(result)
                self._update_info()
    
    def _edit_value(self):
        selection = self.tree.selection()
        if selection and self.edit_callback:
            result = self.result_map.get(selection[0])
            if result:
                new_value = simpledialog.askstring(
                    "Edit Vibez 😼✏️",
                    f"gib new vibez for addy 0x{result.address:X}:",
                    initialvalue=str(result.get_value())
                )
                if new_value is not None:
                    self.edit_callback(result, new_value)
    
    def _copy_address(self):
        selection = self.tree.selection()
        if selection:
            result = self.result_map.get(selection[0])
            if result:
                self.clipboard_clear()
                self.clipboard_append(f"0x{result.address:X}")
    
    def _copy_value(self):
        selection = self.tree.selection()
        if selection:
            result = self.result_map.get(selection[0])
            if result:
                self.clipboard_clear()
                self.clipboard_append(str(result.get_value()))
    
    def _delete_address(self):
        selection = self.tree.selection()
        if selection and self.delete_callback:
            result = self.result_map.get(selection[0])
            if result:
                self.tree.delete(selection[0])
                del self.result_map[selection[0]]
                self.results.remove(result)
                self.delete_callback(result)
                self._update_info()
