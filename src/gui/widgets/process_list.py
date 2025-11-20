import tkinter as tk
from tkinter import ttk
from typing import Callable
from core.process import ProcessManager, ProcessInfo

class ProcessListWidget(ttk.Frame):
    def __init__(self, parent, on_select: Callable[[ProcessInfo], None]):
        super().__init__(parent)
        
        self.on_select = on_select
        self.processes = []
        
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(search_frame, text="Sniff for Process 🐽:").pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True)
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("pid",),
            show="tree headings",
            selectmode="browse"
        )
        self.tree.heading("#0", text="Process Name 🐾")
        self.tree.heading("pid", text="PID 🔢")
        self.tree.column("#0", width=200)
        self.tree.column("pid", width=80, anchor="e")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Button(button_frame, text="Attach Meow 🐈", command=self._on_attach).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame, text="Refresh List 🔄", command=self.refresh).pack(side="left")
        
        self.tree.bind("<Double-1>", lambda e: self._on_attach())
        
        self.refresh()
    
    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.processes = ProcessManager.get_running_processes()
        self._populate_tree()
    
    def _populate_tree(self, search_term: str = ""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        search_lower = search_term.lower()
        for proc in self.processes:
            if not search_term or search_lower in proc.name.lower():
                self.tree.insert(
                    "",
                    "end",
                    text=proc.name,
                    values=(proc.pid,),
                    tags=(proc.pid,)
                )
    
    def _on_search(self, *args):
        self._populate_tree(self.search_var.get())
    
    def _on_attach(self):
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        pid = int(item["values"][0])
        
        process = next((p for p in self.processes if p.pid == pid), None)
        if process:
            self.on_select(process)
