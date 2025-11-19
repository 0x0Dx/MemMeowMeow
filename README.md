# 🐾 **MemMeowMeow – The Cutest Menace to Your Memory**

MemMeowMeow is a _tiny, adorable, slightly feral_ memory scanner and editor that tip-taps through your system RAM like a mischievous kitten knocking cups off tables.

It does **process scanning**, **value editing**, **freezing**, and other serious things—
but with **silly little paws**.

Use responsibly. Meow responsibly. 😼

---

## ✨ Features (meow-enhanced)

- 🐱 **Process Sniff-Sniff** – Browse and attach to active processes like a curious cat finding warm laptops.
- 🔍 **Memory Sniffer 3000** – Scan for exact values hiding inside a process’s squishy brain.
- 🎚️ **Fancy Filter Frenzy** – Filter results so your cat brain doesn’t explode.
- ✏️ **Value Bonking** – Edit memory values in real time (tap tap tap).
- ❄️ **Freeze Beam** – Lock values so they stay still like a laser pointer dot.
- 🔢 **Many Num Nums** – Ints, floats, doubles, and strings supported.

---

## 📦 Installation

### Requirements

- 🐍 Python 3.10+
- 🪟 Windows OS (for memory poking magic)

### Install Dependencies

```bash
pip install -e .
```

Or manually:

```bash
pip install pillow psutil
```

---

## 🚀 Usage

### Run directly:

```bash
python -m src.main
```

Or if installed:

```bash
MemMeowMeow
```

---

## 🧠 How to Use (cat-proof)

1. **Pick a Process**
   Open the list, sniff around, and click “Attach.”
2. **First Scan**
   Enter a value your victim—uh, _target_—process is using.
3. **Filter Filter Filter**
   Narrow it down like the world’s slowest cat stalking a laser dot.
4. **Add Addresses**
   Double-click the ones you like. Adopt them. They’re yours now.
5. **Edit or Freeze**
   Change values, freeze them, commit crimes, etc.

---

## 🗂️ Project Structure (organized chaos)

```
src/
├── core/
│   ├── memory.py         # Memory reading/writing
│   ├── process.py        # Process management
│   ├── scanner.py        # Memory scanning
│   └── types.py          # Data type handling
├── gui/
│   ├── main_window.py    # Main window (the big one)
│   └── widgets/
│       ├── process_list.py
│       ├── scan_panel.py
│       └── address_table.py
└── utils/
```

---

## 🏗️ Architecture (yes it actually works)

### Core

- Separation of concerns so nothing gets too feral
- Clean APIs
- Type hints because we are _responsible degenerates_

### GUI

- Widgety goodness
- MVC-ish
- Event-driven so everything meows at each other nicely

---

## 🧪 Development

### Tests

```bash
pytest tests/
```

### Formatting

```bash
black src/
ruff check src/
```

---

## 📜 License

MIT License (meow-friendly)

---

## 💖 Contributing

Pull requests welcome!
Just keep the vibe cute, silly, and only mildly unhinged.
