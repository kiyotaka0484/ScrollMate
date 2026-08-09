import tkinter as tk
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

WM_MOUSEWHEEL = 0x020A
WHEEL_DELTA = 120
NOTCHES = 1  # slow speed

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class ScrollMate:
    def __init__(self, root):
        self.root = root
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
            parent = user32.GetParent(current)
            if not parent or parent == current:
                break
            current = parent
        return False

    def remember_mouse(self):
        p = POINT()
        user32.GetCursorPos(ctypes.byref(p))
        hwnd = user32.WindowFromPoint(p)

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
        hwnd = user32.WindowFromPoint(p)

        if hwnd and not self.is_our_window(hwnd):
            target = hwnd
        else:
            target = self.target_hwnd

        amount = direction * WHEEL_DELTA * NOTCHES

        # Same WM_MOUSEWHEEL construction as the known-working V4.
        wparam = (amount & 0xFFFF) << 16
        lparam = ((y & 0xFFFF) << 16) | (x & 0xFFFF)

        user32.PostMessageW(target, WM_MOUSEWHEEL, wparam, lparam)

        # Browser windows can have nested parent windows.
        parent = user32.GetParent(target)
        for _ in range(5):
            if not parent:
                break
            user32.PostMessageW(parent, WM_MOUSEWHEEL, wparam, lparam)
            next_parent = user32.GetParent(parent)
            if next_parent == parent:
                break
            parent = next_parent

root = tk.Tk()
ScrollMate(root)
root.mainloop()
