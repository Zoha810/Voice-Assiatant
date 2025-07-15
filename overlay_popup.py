import tkinter as tk
import threading

def show_popup(text="Hey Aaron"):
    def popup():
        root = tk.Tk()
        root.overrideredirect(True)
        root.attributes('-topmost', True)
        root.geometry("350x70+750+50")
        root.configure(bg="#1e1e1e")

        frame = tk.Frame(root, bg="#1e1e1e", padx=20, pady=10)
        frame.pack(expand=True, fill="both")

        label = tk.Label(frame, text=text,
                         fg="white", bg="#1e1e1e",
                         font=("Segoe UI", 16, "bold"))
        label.pack()

        root.after(2000, root.destroy)
        root.mainloop()

    threading.Thread(target=popup, daemon=True).start()
