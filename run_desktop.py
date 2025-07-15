import threading
import time
import tkinter as tk
from tkinter import messagebox

from wakeword_listener import WakeWordListener
from overlay_popup import show_popup
from voice_assistant import handle_command, listen
from core import assistant

# Function when wake word is detected
def on_wake_word():
    show_popup("Hey Aaron detected!", "Yes, how can I help you?")
    assistant.speak("Yes, how can I help you?")
    command = listen()
    if command:
        handle_command(command)

if __name__ == "__main__":
    # Initialize data and background tasks
    assistant.init_all_files()
    assistant.start_schedule_checker()

    # Show popup when app starts
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Aaron Assistant", "Aaron is now listening for the wake word.")

    # Start listening for wake word in a separate thread
    listener = WakeWordListener(on_detect=on_wake_word)
    threading.Thread(target=listener.listen, daemon=True).start()

    # Keep the application running
    while True:
        time.sleep(1)
