import ctypes
import sys
from ctypes import wintypes

tk = None

WM_MOUSEWHEEL = 0x020A
WHEEL_DELTA = 120
NOTCHES = 1  # slow speed

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

def load_user32():
    if sys.platform != "win32":
        raise OSError("ScrollMate requires Windows.")

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
    user32.GetCursorPos.restype = wintypes.BOOL
    user32.WindowFromPoint.argtypes = [POINT]
    user32.WindowFromPoint.restype = wintypes.HWND
    user32.GetParent.argtypes = [wintypes.HWND]
    user32.GetParent.restype = wintypes.HWND
    user32.IsWindow.argtypes = [wintypes.HWND]
    user32.IsWindow.restype = wintypes.BOOL
    user32.PostMessageW.argtypes = [
        wintypes.HWND,
        wintypes.UINT,
        wintypes.WPARAM,
        wintypes.LPARAM,
    ]
    user32.PostMessageW.restype = wintypes.BOOL
    return user32

class ScrollMate:
    def __init__(self, root):
        if tk is None:
            raise RuntimeError("Tkinter is required to run ScrollMate.")

        self.root = root
        self.user32 = load_user32()
        self.target_x = None
        self.target_y = None
        self.target_hwnd = None

        # NORMAL Windows window
        root.title("ScrollMate")
        root.resizable(True, True)
        root.minsize(100, 150)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.94)
        root.configure(bg="#202020")
        root.geometry("120x210")

        root.update_idletasks()
        self.own_hwnd = root.winfo_id()

        # A real client-area drag handle.
        handle = tk.Frame(root, bg="#202020", height=22, cursor="fleur")
        handle.pack(fill="x", padx=2, pady=(2, 0))
        handle.pack_propagate(False)

        drag_label = tk.Label(
            handle,
            text="ScrollMate  •  drag here",
            bg="#202020",
            fg="#aaaaaa",
            font=("Segoe UI", 8),
            cursor="fleur"
        )
        drag_label.pack(fill="both", expand=True)

        def start_drag(e):
            self.drag_x = e.x_root
            self.drag_y = e.y_root
            self.win_x = root.winfo_x()
            self.win_y = root.winfo_y()

        def drag(e):
            root.geometry(
                f"+{self.win_x + e.x_root - self.drag_x}+"
                f"{self.win_y + e.y_root - self.drag_y}"
            )

        # Bind both the strip AND the label. The label fills the strip,
        # so it must receive the drag events too.
        for widget in (handle, drag_label):
            widget.bind("<Button-1>", start_drag)
            widget.bind("<B1-Motion>", drag)

        # Buttons
        panel = tk.Frame(
            root, bg="#202020",
            highlightbackground="#555555",
            highlightthickness=1
        )
        panel.pack(fill="both", expand=True, padx=2, pady=2)

        panel.grid_rowconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        tk.Button(
            panel, text="▲",
            font=("Segoe UI", 26, "bold"),
            fg="white", bg="#303030",
            activeforeground="white",
            activebackground="#555555",
            bd=0, relief="flat",
            command=lambda: self.scroll(+1)
        ).grid(row=0, column=0, sticky="nsew", padx=4, pady=(4, 2))

        tk.Button(
            panel, text="▼",
            font=("Segoe UI", 26, "bold"),
            fg="white", bg="#303030",
            activeforeground="white",
            activebackground="#555555",
            bd=0, relief="flat",
            command=lambda: self.scroll(-1)
        ).grid(row=1, column=0, sticky="nsew", padx=4, pady=(2, 4))

        # EXACTLY the working V4 idea:
        # remember the last mouse position that is outside ScrollMate.
        self.remember_mouse()

    def is_our_window(self, hwnd):
        current = hwnd
        for _ in range(10):
            if current == self.own_hwnd:
                return True
            parent = self.user32.GetParent(current)
            if not parent or parent == current:
                break
            current = parent
        return False

    def remember_mouse(self):
        p = POINT()
        if not self.user32.GetCursorPos(ctypes.byref(p)):
            self.root.after(20, self.remember_mouse)
            return

        hwnd = self.user32.WindowFromPoint(p)

        if hwnd and not self.is_our_window(hwnd):
            self.target_x = p.x
            self.target_y = p.y
            self.target_hwnd = hwnd

        self.root.after(20, self.remember_mouse)

    def scroll(self, direction):
        if self.target_x is None or self.target_hwnd is None:
            return

        x = self.target_x
        y = self.target_y

        # Re-identify the window at the saved page position.
        p = POINT(x, y)
        hwnd = self.user32.WindowFromPoint(p)

        if hwnd and not self.is_our_window(hwnd):
            target = hwnd
        else:
            target = self.target_hwnd

        if not target or not self.user32.IsWindow(target):
            return

        amount = direction * WHEEL_DELTA * NOTCHES

        # Same WM_MOUSEWHEEL construction as the known-working V4.
        wparam = ((ctypes.c_short(amount).value & 0xFFFF) << 16)
        lparam = ((y & 0xFFFF) << 16) | (x & 0xFFFF)

        self.user32.PostMessageW(target, WM_MOUSEWHEEL, wparam, lparam)

        # Browser windows can have nested parent windows.
        parent = self.user32.GetParent(target)
        for _ in range(5):
            if not parent:
                break
            self.user32.PostMessageW(parent, WM_MOUSEWHEEL, wparam, lparam)
            next_parent = self.user32.GetParent(parent)
            if next_parent == parent:
                break
            parent = next_parent

def main():
    global tk

    try:
        import tkinter as tk_module
    except ModuleNotFoundError as exc:
        raise SystemExit("Tkinter is not available in this Python environment.") from exc

    tk = tk_module

    if sys.platform != "win32":
        raise SystemExit("ScrollMate runs on Windows only.")

    root = tk.Tk()
    ScrollMate(root)
    root.mainloop()

if __name__ == "__main__":
    main()
