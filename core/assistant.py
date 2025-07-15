import os
import json
import datetime
import pyttsx3
import time
import threading
import requests
import wikipedia
import pyjokes
import webbrowser
import math
import re
import shutil
import platform
import psutil
from pathlib import Path
from deep_translator import GoogleTranslator
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import sys
print("[DEBUG] Python executable:", sys.executable)

# ========== File Paths ==========
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

TODO_FILE = DATA_DIR / "todo.json"
REMINDER_FILE = DATA_DIR / "reminders.json"
CALENDAR_FILE = DATA_DIR / "calendar.json"
COMMAND_LOG = DATA_DIR / "command_log.json"

# ========== Supported Languages ==========
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ur": "Urdu",
    "hi": "Hindi",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "ar": "Arabic",
    "zh-CN": "Chinese (Simplified)"
}

# ========== Initialize TTS ==========
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

# ========== Speak Function ==========
def speak(text, lang="en"):
    if lang != "en":
        try:
            translated = GoogleTranslator(source="auto", target=lang).translate(text)
        except Exception:
            translated = text  # fallback
    else:
        translated = text

    print(f"[Aaron says] {translated}")
    engine.say(translated)
    engine.runAndWait()

# ========== File Initialization ==========
def ensure_json_file(path: Path, default_data: dict):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2)
        print(f"Created: {path.name}")

def init_all_files():
    ensure_json_file(TODO_FILE, {"tasks": []})
    ensure_json_file(REMINDER_FILE, {"reminders": []})
    ensure_json_file(CALENDAR_FILE, {"events": []})
    ensure_json_file(COMMAND_LOG, {"commands": []})

# ========== Reminder Checker ==========
def check_reminders():
    now = datetime.datetime.now().strftime("%H:%M")
    updated = []

    try:
        with open(REMINDER_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            for r in data["reminders"]:
                if r["time"] == now:
                    speak(f"Reminder: {r['msg']}")
                    if r["repeat"]:
                        updated.append(r)
                else:
                    updated.append(r)

            f.seek(0)
            json.dump({"reminders": updated}, f, indent=2)
            f.truncate()
    except Exception as e:
        print(f"[Reminder Error] {e}")
# ========== Calendar Event Checker ==========
def check_events():
    now = datetime.datetime.now()
    upcoming = []

    try:
        with open(CALENDAR_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            for e in data["events"]:
                event_time = datetime.datetime.strptime(f"{e['date']} {e['time']}", "%Y-%m-%d %H:%M")
                if now >= event_time and (now - event_time).seconds < 60:
                    speak(f"Event: {e['title']}")
                else:
                    upcoming.append(e)

            f.seek(0)
            json.dump({"events": upcoming}, f, indent=2)
            f.truncate()
    except Exception as e:
        print(f"[Event Error] {e}")
# ========== Background Scheduler ==========
def start_schedule_checker():
    def loop():
        while True:
            check_reminders()
            check_events()
            time.sleep(60)

    threading.Thread(target=loop, daemon=True).start()
# ========== Command Logging ==========
def log_command(command_text):
    try:
        with open(COMMAND_LOG, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data["commands"].append({
                "command": command_text,
                "time": datetime.datetime.now().isoformat()
            })
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
    except Exception as e:
        print(f"[Log Error] {e}")
def view_command_log():
    try:
        with open(COMMAND_LOG, "r", encoding="utf-8") as f:
            data = json.load(f)
            return "\n".join(f"{c['time']} - {c['command']}" for c in data["commands"])
    except:
        return "No commands logged yet."
def remove_task(task_name):
    try:
        with open(TODO_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            tasks = data.get("tasks", [])
            updated_tasks = [t for t in tasks if t["task"].lower() != task_name.lower()]
            if len(tasks) == len(updated_tasks):
                return "Task not found."
            data["tasks"] = updated_tasks
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
        return f"Removed task: {task_name}"
    except Exception as e:
        return f"Error removing task: {e}"
def view_tasks():
    try:
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not data["tasks"]:
                return "No tasks found."
            return "\n".join(f"{t['task']} (Priority: {t['priority']})" for t in data["tasks"])
    except:
        return "Error loading tasks."
def set_reminder(message, time_str, repeat=False):
    try:
        with open(REMINDER_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data["reminders"].append({
                "msg": message,
                "time": time_str,
                "repeat": repeat
            })
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
        return f"Reminder set for {time_str}"
    except Exception as e:
        return f"Error setting reminder: {e}"
def view_reminders():
    try:
        with open(REMINDER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not data["reminders"]:
                return "No reminders found."
            return "\n".join(
                f"{r['time']} - {r['msg']} (Repeat: {'Yes' if r['repeat'] else 'No'})"
                for r in data["reminders"]
            )
    except:
        return "Error loading reminders."
def schedule_event(title, date, time_str):
    try:
        with open(CALENDAR_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data["events"].append({
                "title": title,
                "date": date,
                "time": time_str
            })
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
        return f"Event scheduled: {title} on {date} at {time_str}"
    except Exception as e:
        return f"Error scheduling event: {e}"
def view_events():
    try:
        with open(CALENDAR_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not data["events"]:
                return "No events scheduled."
            return "\n".join(
                f"{e['date']} {e['time']} - {e['title']}" for e in data["events"]
            )
    except:
        return "Error loading events."
def search_wikipedia(query, sentences=2, lang="en"):
    try:
        wikipedia.set_lang(lang)
        summary = wikipedia.summary(query, sentences=sentences)
        speak(summary, lang=lang)
        return summary
    except Exception:
        speak("Sorry, I couldn't find anything.")
        return "No results found."
def tell_joke(lang="en"):
    joke = pyjokes.get_joke()
    speak(joke, lang=lang)
    return joke
def play_youtube(query):
    try:
        speak(f"Playing {query} on YouTube")
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return f"Opened YouTube for {query}"
    except Exception as e:
        return f"YouTube error: {e}"
def calculate(expression):
    try:
        expression = re.sub(r'[^0-9\+\-\*/\(\)\.\s]', '', expression)
        result = eval(expression)
        speak(f"The answer is {result}")
        return result
    except Exception as e:
        return f"Calculation error: {e}"
def convert_currency(amount, from_curr, to_curr):
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_curr.upper()}"
        res = requests.get(url).json()
        rate = res["rates"].get(to_curr.upper())
        if rate:
            converted = float(amount) * rate
            speak(f"{amount} {from_curr} is {converted:.2f} {to_curr}")
            return converted
        return "Conversion failed."
    except Exception as e:
        return f"Currency conversion error: {e}"
def lookup_dictionary(word):
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        res = requests.get(url).json()
        if isinstance(res, list):
            meaning = res[0]['meanings'][0]['definitions'][0]['definition']
            speak(f"The meaning of {word} is {meaning}")
            return meaning
        return "Word not found."
    except Exception as e:
        return f"Dictionary error: {e}"
def translate_text(text, target_lang="es"):
    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        speak(translated, lang=target_lang)
        return translated
    except Exception as e:
        return f"Translation error: {e}"
def start_timer(minutes):
    try:
        seconds = int(minutes) * 60
        speak(f"Timer started for {minutes} minutes")
        time.sleep(seconds)
        speak("Time's up!")
        return "Timer finished."
    except Exception as e:
        return f"Timer error: {e}"
def start_stopwatch():
    try:
        speak("Stopwatch started. Say 'stop stopwatch' to stop.")
        start_time = time.time()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        end_time = time.time()
        duration = end_time - start_time
        speak(f"Stopwatch stopped. Duration: {int(duration)} seconds")
        return f"Duration: {int(duration)} seconds"
def read_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        speak(text[:500])
        return text[:1000]  # limit for preview
    except Exception as e:
        return f"PDF read error: {e}"
def shutdown_system():
    try:
        speak("Shutting down the system.")
        if platform.system() == "Windows":
            os.system("shutdown /s /t 1")
        elif platform.system() == "Linux":
            os.system("shutdown now")
        return "Shutdown command sent."
    except Exception as e:
        return f"Shutdown error: {e}"

def open_app(app_name):
    try:
        speak(f"Opening {app_name}")
        os.system(f"start {app_name}")
        return f"Opened {app_name}"
    except Exception as e:
        return f"App open error: {e}"
def take_screenshot(filename="screenshot.png"):
    try:
        import pyautogui
        img = pyautogui.screenshot()
        img.save(filename)
        speak(f"Screenshot saved as {filename}")
        return f"Saved screenshot: {filename}"
    except Exception as e:
        return f"Screenshot error: {e}"
def get_covid_stats(country="Pakistan"):
    try:
        url = f"https://www.worldometers.info/coronavirus/country/{country.lower().replace(' ', '-')}/"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        cases = soup.find_all("div", class_="maincounter-number")
        stats = [c.text.strip() for c in cases[:3]]
        msg = f"COVID-19 in {country}: Cases: {stats[0]}, Deaths: {stats[1]}, Recovered: {stats[2]}"
        speak(msg)
        return msg
    except Exception as e:
        return f"COVID data error: {e}"
def get_live_score(team="Pakistan"):
    try:
        url = "https://www.espncricinfo.com/live-cricket-score"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        matches = soup.find_all("a", class_="ds-no-tap-higlight")
        for m in matches:
            if team.lower() in m.text.lower():
                speak(m.text.strip())
                return m.text.strip()
        return f"No live score found for {team}"
    except Exception as e:
        return f"Score fetch error: {e}"
def set_voice_speed(value):
    try:
        engine.setProperty('rate', int(value))
        return f"Voice speed set to {value}"
    except Exception as e:
        return f"Voice speed error: {e}"

def set_voice_volume(value):
    try:
        engine.setProperty('volume', float(value))
        return f"Voice volume set to {value}"
    except Exception as e:
        return f"Voice volume error: {e}"
def search_local_files(keyword, root_dirs=None, limit=10):
    """
    Search for files containing the keyword in their name across all directories.
    """
    if root_dirs is None:
        # Automatically detect all fixed drives (C:, D:, etc.)
        root_dirs = [part.mountpoint for part in psutil.disk_partitions() if "fixed" in part.opts.lower()]

    found_files = []

    for root in root_dirs:
        for dirpath, _, filenames in os.walk(root):
            for file in filenames:
                if keyword.lower() in file.lower():
                    full_path = os.path.join(dirpath, file)
                    found_files.append(full_path)
                    if len(found_files) >= limit:
                        break
            if len(found_files) >= limit:
                break
        if len(found_files) >= limit:
            break

    if found_files:
        speak(f"I found {len(found_files)} file(s) matching '{keyword}'.")
        return "\n".join(found_files)
    else:
        speak("No files found matching your search.")
        return "No files found."
if __name__ == "__main__":
    init_all_files()
    print("✅ Assistant backend is working correctly.")

