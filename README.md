# 🐾 **MemMeowMeow v0.2.0 – The Feral RAM Gremlin's Forbidden Playground**

MemMeowMeow is a _tiny, adorable, slightly unhinged_ memory scanner and editor that tip-taps through your system RAM like a mischievous kitten knocking cups off tables.

It does **process scanning**, **value editing**, **freezing**, **Python scripting**, and other serious things—but with **silly little paws** and **maximum chaos energy**.

Use responsibly. Meow responsibly. 😼

---

## ✨ Features (enhanced with chaos)

### 🔍 **Sniff-Sniff Scanner**
- Browse and attach to active processes like a curious cat finding warm laptops
- Scan for exact values hiding inside a process's squishy brain
- Filter results so your cat brain doesn't explode
- Support for Int8/16/32/64, UInt8/16/32/64, Float, Double, and Strings

### 🛠️ **Advanced Tools (Big Brain Stuff)**
- **Memory Viewer** 📊 - See raw bytes in a hex dungeon
- **Pointer Scanner** 🎯 - Find those sneaky indirect addresses (the bois that point to stuff)
- **Address Calculator** 🧮 - Do the maffs (hex ↔️ decimal converter & offset calculator)
- **Statistics** 📈 - See how much chaos you've caused

### 📝 **Python Scripting (Code Chaos Zone)**
- Full Python scripting engine with memory access
- Syntax highlighting (fancy colors!)
- Auto-indentation (because tabs vs spaces is violence)
- Save/load scripts
- Built-in help system
- Script library manager

### ❄️ **Freeze-o-Tron 9000**
- Lock values so they stay still like a laser pointer dot
- Freeze individual addresses or ALL THE THINGS
- Real-time value monitoring
- Unfreeze when you're done being evil

### 💾 **Cheat Tables (Save Ur Chaos)**
- Save addresses and scripts to `.mmt` files
- Load tables back later
- Auto-restore frozen states
- JSON-based format (human readable!)

### ⚡ **Quality of Life**
- Tabbed interface (scanner, scripts, tools)
- Dark mode text editors (easy on the eyes)
- Pagination for large result sets
- Context menus everywhere
- Keyboard shortcuts
- Status updates with personality

---

## 📦 Installation

### Requirements

- 🐍 Python 3.10+
- 🪟 Windows OS (for memory poking magic)
- 🧠 A sense of humor

### Install Dependencies

```bash
# Clone or download this chaos
cd MemMeowMeow

# Install it
pip install -e .
```

Or manually install dependencies:

```bash
pip install pillow psutil
```

---

## 🚀 Usage

### Run MemMeowMeow:

```bash
python -m main
```

Or if installed as a package:

```bash
MemMeowMeow
```

---

## 🧠 How to Use (cat-proof guide)

### 1. **Pick a Victim** 🎯
   - Open the process list
   - Search for your target process
   - Click "Attach Meow 🐈" or double-click
   - MeowMeow latches on and starts sniffing memory zones

### 2. **First Sniff** 👃
   - Enter a value your victim—uh, _target_—process is using
   - Pick a data type (Int32, Float, etc.)
   - Pick a comparison (= for exact match, >, <, etc.)
   - Click "First Sniff 🐾"
   - Watch MeowMeow dig through RAM like a maniac

### 3. **Filter Filter Filter** 🔽
   - Use "Changed", "Unchanged", "Increased", or "Decreased"
   - Narrow it down like the world's slowest cat stalking a laser dot
   - Repeat until you find THE ONE

### 4. **Adopt Addresses** 👶
   - Double-click results to add them to your table
   - Give them silly names (optional)
   - They're yours now. Congrats on your new children.

### 5. **Edit or Freeze** ✏️❄️
   - Double-click values to edit them
   - Right-click for context menu
   - Toggle freeze to lock values
   - Watch the chaos unfold

### 6. **Script Some Chaos** 📝
   - Switch to "Code Chaos Zone" tab
   - Write Python code to automate everything
   - Use `readInt()`, `writeInt()`, `scan()`, etc.
   - Press Ctrl+Enter to run
   - Break reality

### 7. **Save Your Work** 💾
   - File → "Yeet Table To Disk"
   - Save as `.mmt` file
   - Load it later to continue your reign of terror

---

## 🗂️ Project Structure

```
src/
├── core/
│   ├── memory.py         # Memory reading/writing wizardry
│   ├── process.py        # Process management (victim selection)
│   ├── scanner.py        # Memory scanning engine (sniff-sniff)
│   ├── types.py          # Data type handling
│   └── scripting.py      # Python script execution engine
├── gui/
│   ├── main_window.py    # Main window (the big kahuna)
│   └── widgets/
│       ├── process_list.py       # Process zoo
│       ├── scan_panel.py         # Scan controls
│       ├── address_table.py      # Address management
│       └── script_editor.py      # Code editor with syntax highlighting
└── main.py               # Entry point (start here)
```

---

## 🎮 Scripting API

### Memory Operations

```python
# Read values
value = readInt(0x12345678)           # Read 4-byte integer
value = readInt64(0x12345678)         # Read 8-byte integer
value = readFloat(0x12345678)         # Read float
value = readDouble(0x12345678)        # Read double
name = readString(0x12345678, 50)     # Read string (50 chars max)
data = readBytes(0x12345678, 100)     # Read raw bytes

# Write values
writeInt(0x12345678, 999)             # Write integer
writeInt64(0x12345678, 999999)        # Write 64-bit integer
writeFloat(0x12345678, 1.5)           # Write float
writeDouble(0x12345678, 3.14159)      # Write double
writeBytes(0x12345678, b'\x90\x90')   # Write raw bytes
```

### Scanning

```python
# Scan for value
results = scan(100, DataType.INT32)
print(f"Found {len(results)} matches")

# Get current results
results = getResults()

# Filter results
filterChanged(DataType.INT32)         # Only changed values
filterUnchanged(DataType.INT32)       # Only unchanged values
```

### Example Scripts

```python
# Find and modify health
results = scan(100, DataType.INT32)
if results:
    health_addr = results[0].address
    writeInt(health_addr, 999)
    print("Health set to 999!")

# Auto-health script
import time
while True:
    if readInt(health_addr) < 100:
        writeInt(health_addr, 999)
        print("Healed!")
    time.sleep(0.1)
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Save table/script |
| `Ctrl+N` | New table |
| `Ctrl+O` | Load table |
| `Ctrl+Return` | Execute script |
| `F5` | Refresh process list |
| `F9` | Start new scan |
| `Double-Click` | Add address (from results) |
| `Right-Click` | Context menu |

---

## 🎯 Pro Tips

- **Narrow it down**: Start with "=" for exact value, then use "Changed" or "Increased" to filter
- **Use scripts**: Automate repetitive tasks with Python
- **Freeze carefully**: Freezing the wrong address can crash games
- **Save often**: Use cheat tables to save your work
- **Hex viewer**: Right-click addresses to view them in the memory viewer
- **Pointer scanning**: For values that move, use the pointer scanner (when you find them, they stay found!)

---

## 🚨 Known Limitations

- **Windows only**: Linux/Mac support requires different memory APIs
- **Admin rights**: Some processes require administrator privileges
- **Protected processes**: Anti-cheat systems may block access
- **Performance**: Scanning large memory spaces takes time
- **Pointer scanner**: Currently displays UI but full functionality pending
- **Auto-assembler**: UI ready, but needs keystone-engine library

---

## 🧪 Development

### Run Tests

```bash
pytest tests/
```

### Format Code

```bash
black src/
ruff check src/
```

### Dependencies

- `psutil` - Process enumeration and management
- `tkinter` - GUI framework (built into Python)
- `pillow` - Image handling (if needed)

---

## 📜 License

MIT License (meow-friendly)

Use this tool for:
- ✅ Single-player games
- ✅ Learning about memory
- ✅ Reverse engineering
- ✅ Personal projects

Do NOT use for:
- ❌ Online multiplayer cheating
- ❌ Violating ToS/EULA
- ❌ Commercial cheating services
- ❌ Being a jerk

---

## 💖 Contributing

Pull requests welcome!

Just keep the vibe:
- ✅ Cute
- ✅ Silly
- ✅ Functional
- ✅ Well-documented
- ✅ Only mildly unhinged

---

## ⚠️ Disclaimer

MemMeowMeow is for **educational purposes** only.

- Using this on online games may violate Terms of Service
- Some games have anti-cheat that will detect and ban you
- Modifying memory can crash programs
- I'm a cat, not a lawyer
- Don't blame MeowMeow if your game bans you

**Use at your own risk. Meow responsibly.** 🐾

---

## 🙏 Credits

Built with love, chaos, and way too much coffee by someone who thought "what if Cheat Engine but with cat energy?"

Special thanks to:
- Cheat Engine (inspiration)
- Every cat that's ever knocked something off a table
- The Python community
- You, for actually reading this far

---

## 🐱 Fun Facts

- MeowMeow can scan ~100MB of memory per second
- The freeze update rate is 100ms (10 times per second)
- The code contains exactly 47 cat emojis (I counted)
- This README took longer to write than some features
- MeowMeow has never paid taxes

---

**Remember**: With great power comes great responsibility to be silly. 🐾

Now go forth and cause some (ethical) chaos! 😼