import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Callable, Optional

class ScriptEditorWidget(ttk.Frame):
    def __init__(self, parent, on_execute: Callable, on_save: Optional[Callable] = None):
        super().__init__(parent)
        
        self.on_execute = on_execute
        self.on_save = on_save
        self.current_file = None
        
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(toolbar, text="▶️ Run Script", command=self._execute, width=12).pack(side="left", padx=2)
        ttk.Button(toolbar, text="💾 Save", command=self._save, width=10).pack(side="left", padx=2)
        ttk.Button(toolbar, text="📂 Load", command=self._load, width=10).pack(side="left", padx=2)
        ttk.Button(toolbar, text="🗑️ Clear", command=self._clear, width=10).pack(side="left", padx=2)
        ttk.Button(toolbar, text="❓ Help", command=self._show_help, width=10).pack(side="left", padx=2)
        
        editor_container = ttk.Frame(self)
        editor_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.line_numbers = tk.Text(
            editor_container,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            background='#f0f0f0',
            state='disabled',
            wrap='none'
        )
        self.line_numbers.pack(side="left", fill="y")
        
        text_frame = ttk.Frame(editor_container)
        text_frame.pack(side="left", fill="both", expand=True)
        
        self.text_editor = tk.Text(
            text_frame,
            wrap="none",
            undo=True,
            maxundo=-1,
            font=("Consolas", 10),
            insertwidth=2,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#ffffff",
            selectbackground="#264f78"
        )
        
        vsb = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_editor.yview)
        hsb = ttk.Scrollbar(text_frame, orient="horizontal", command=self.text_editor.xview)
        
        self.text_editor.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.text_editor.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        output_frame = ttk.LabelFrame(self, text="Output Console 📟", padding=5)
        output_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.output_text = tk.Text(
            output_frame,
            height=8,
            wrap="word",
            font=("Consolas", 9),
            bg="#0c0c0c",
            fg="#cccccc",
            state='disabled'
        )
        
        output_vsb = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=output_vsb.set)
        
        self.output_text.pack(side="left", fill="both", expand=True)
        output_vsb.pack(side="right", fill="y")
        
        self._configure_syntax_highlighting()
        
        self.text_editor.bind("<KeyRelease>", self._on_text_change)
        self.text_editor.bind("<Return>", self._on_return)
        self.text_editor.bind("<Tab>", self._on_tab)
        self.text_editor.bind("<Control-s>", lambda e: self._save())
        self.text_editor.bind("<Control-Return>", lambda e: self._execute())
        
        self._update_line_numbers()
        self._insert_template()
    
    def _configure_syntax_highlighting(self):
        self.text_editor.tag_configure("keyword", foreground="#569cd6")
        self.text_editor.tag_configure("builtin", foreground="#4ec9b0")
        self.text_editor.tag_configure("string", foreground="#ce9178")
        self.text_editor.tag_configure("comment", foreground="#6a9955")
        self.text_editor.tag_configure("number", foreground="#b5cea8")
        self.text_editor.tag_configure("function", foreground="#dcdcaa")
        
        self.keywords = {
            'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'return',
            'import', 'from', 'as', 'try', 'except', 'finally', 'with',
            'lambda', 'yield', 'raise', 'assert', 'break', 'continue', 'pass',
            'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is'
        }
        
        self.builtins = {
            'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict',
            'readInt', 'writeInt', 'readFloat', 'writeFloat', 'scan', 'getResults'
        }
    
    def _highlight_syntax(self):
        for tag in ["keyword", "builtin", "string", "comment", "number", "function"]:
            self.text_editor.tag_remove(tag, "1.0", "end")
        
        content = self.text_editor.get("1.0", "end-1c")
        
        import re
        for match in re.finditer(r'#.*$', content, re.MULTILINE):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.text_editor.tag_add("comment", start, end)
        
        for match in re.finditer(r'(["\'])(?:(?=(\\?))\2.)*?\1', content):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.text_editor.tag_add("string", start, end)
        
        for match in re.finditer(r'\b\w+\b', content):
            word = match.group(0)
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            
            if word in self.keywords:
                self.text_editor.tag_add("keyword", start, end)
            elif word in self.builtins:
                self.text_editor.tag_add("builtin", start, end)
    
    def _on_text_change(self, event=None):
        self._update_line_numbers()
        self.after_idle(self._highlight_syntax)
    
    def _update_line_numbers(self):
        self.line_numbers.config(state='normal')
        self.line_numbers.delete("1.0", "end")
        
        line_count = int(self.text_editor.index('end-1c').split('.')[0])
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.insert("1.0", line_numbers_string)
        self.line_numbers.config(state='disabled')
    
    def _on_return(self, event):
        current_line = self.text_editor.get("insert linestart", "insert lineend")
        
        indent = len(current_line) - len(current_line.lstrip())
        
        if current_line.rstrip().endswith(':'):
            indent += 4
        
        self.text_editor.insert("insert", "\n" + " " * indent)
        return "break"
    
    def _on_tab(self, event):
        self.text_editor.insert("insert", "    ")
        return "break"
    
    def _insert_template(self):
        template = """# MemMeowMeow Script 🐾
# Use help() to see available functions

# Example: Find and modify health value
# results = scan(100, DataType.INT32)
# print(f"Found {len(results)} matches")
# 
# if results:
#     addr = results[0].address
#     current = readInt(addr)
#     print(f"Current value: {current}")
#     writeInt(addr, 999)
#     print("Health set to 999!")

"""
        self.text_editor.insert("1.0", template)
        self._highlight_syntax()
    
    def _execute(self):
        code = self.text_editor.get("1.0", "end-1c")
        if code.strip():
            self.on_execute(code)
    
    def _save(self):
        if not self.current_file:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".py",
                filetypes=[("Python Scripts", "*.py"), ("All Files", "*.*")]
            )
            if filepath:
                self.current_file = filepath
        
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(self.text_editor.get("1.0", "end-1c"))
                self._append_output(f"✅ Saved to {self.current_file}\n", "success")
                if self.on_save:
                    self.on_save(self.current_file)
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save: {e}")
    
    def _load(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Python Scripts", "*.py"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", content)
                self.current_file = filepath
                self._highlight_syntax()
                self._append_output(f"📂 Loaded {filepath}\n", "success")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load: {e}")
    
    def _clear(self):
        if messagebox.askyesno("Clear Editor", "Clear all script content?"):
            self.text_editor.delete("1.0", "end")
            self.current_file = None
            self._clear_output()
    
    def _show_help(self):
        help_window = tk.Toplevel(self)
        help_window.title("Script Help 🐾")
        help_window.geometry("600x500")
        
        help_text = tk.Text(help_window, wrap="word", font=("Consolas", 9), padx=10, pady=10)
        help_text.pack(fill="both", expand=True)
        
        help_content = """MemMeowMeow Scripting API 🐾

MEMORY OPERATIONS:
  readBytes(address, size) -> bytes
  writeBytes(address, data) -> bool
  
  readInt(address) -> int (4 bytes)
  readInt64(address) -> int (8 bytes)
  readFloat(address) -> float
  readDouble(address) -> double
  readString(address, length=256) -> str
  
  writeInt(address, value) -> bool
  writeInt64(address, value) -> bool
  writeFloat(address, value) -> bool
  writeDouble(address, value) -> bool

SCANNING:
  scan(value, DataType.INT32) -> List[ScanResult]
  getResults() -> List[ScanResult]
  filterChanged(DataType.INT32)
  filterUnchanged(DataType.INT32)

DATA TYPES:
  DataType.INT8, INT16, INT32, INT64
  DataType.UINT8, UINT16, UINT32, UINT64
  DataType.FLOAT, DOUBLE, STRING

EXAMPLES:

# Find health value
results = scan(100, DataType.INT32)
print(f"Found {len(results)} addresses")

# Read and modify first result
if results:
    addr = results[0].address
    value = readInt(addr)
    print(f"Current: {value}")
    writeInt(addr, 999)

# Scan for float value
scan(1.5, DataType.FLOAT)

# Read string from memory
name = readString(0x12345678, 50)
print(f"Name: {name}")

SHORTCUTS:
  Ctrl+S: Save script
  Ctrl+Enter: Run script
"""
        help_text.insert("1.0", help_content)
        help_text.config(state="disabled")
    
    def set_output(self, text: str, is_error: bool = False):
        self._clear_output()
        self._append_output(text, "error" if is_error else "normal")
    
    def _append_output(self, text: str, tag: str = "normal"):
        self.output_text.config(state='normal')
        self.output_text.insert("end", text)
        
        if tag == "error":
            start_idx = self.output_text.index("end-1c linestart")
            self.output_text.tag_add("error", start_idx, "end")
            self.output_text.tag_config("error", foreground="#f44747")
        elif tag == "success":
            start_idx = self.output_text.index("end-1c linestart")
            self.output_text.tag_add("success", start_idx, "end")
            self.output_text.tag_config("success", foreground="#4ec9b0")
        
        self.output_text.see("end")
        self.output_text.config(state='disabled')
    
    def _clear_output(self):
        self.output_text.config(state='normal')
        self.output_text.delete("1.0", "end")
        self.output_text.config(state='disabled')
    
    def get_script(self) -> str:
        return self.text_editor.get("1.0", "end-1c")
    
    def set_script(self, content: str):
        self.text_editor.delete("1.0", "end")
        self.text_editor.insert("1.0", content)
        self._highlight_syntax()