import sys
import tkinter as tk
from tkinter import messagebox

def main():
    try:
        from gui.main_window import MainWindow
        root = tk.Tk()
        app = MainWindow(root)
        root.mainloop()
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Make sure all dependencies are installed: pip install -e .")
        print(f"Python path: {sys.path}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        try:
            messagebox.showerror("Fatal Error", f"Application crashed: {str(e)}")
        except:
            print(f"Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()