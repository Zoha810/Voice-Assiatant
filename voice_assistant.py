
import speech_recognition as sr
from core import assistant
import wikipedia
import pyjokes
import re
import os

assistant.init_all_files()

# Language can be changed by saying: change language to Urdu
user_language = "en"

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Say something...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("❌ I didn't catch that.")
            return ""
        except sr.RequestError:
            print("⚠️ Voice service error.")
            return ""

def handle_command(command):
    global user_language

    if "add task" in command:
        task = command.replace("add task", "").strip()
        result = assistant.add_task(task)

    elif "show tasks" in command or "view tasks" in command:
        result = assistant.view_tasks()

    elif "remove task" in command:
        task = command.replace("remove task", "").strip()
        result = assistant.remove_task(task)

    elif "set reminder" in command:
        try:
            parts = command.replace("set reminder", "").strip().split(" at ")
            message, time = parts[0], parts[1]
            result = assistant.set_reminder(message.strip(), time.strip())
        except:
            result = "Could not set reminder. Please say it like: set reminder buy milk at 10:30"

    elif "show reminders" in command:
        result = assistant.view_reminders()

    elif "daily briefing" in command:
        result = assistant.get_daily_briefing(lang=user_language)
        return

    elif "tell me a joke" in command or "joke" in command:
        joke = pyjokes.get_joke()
        assistant.speak(joke, lang=user_language)
        return

    elif "wikipedia" in command:
        topic = command.replace("wikipedia", "").strip()
        try:
            summary = wikipedia.summary(topic, sentences=2)
            assistant.speak(summary, lang=user_language)
        except:
            assistant.speak("Sorry, I couldn't find information.", lang=user_language)
        return

    elif "play" in command and "youtube" in command:
        query = command.replace("play", "").replace("on youtube", "").strip()
        result = assistant.play_youtube(query)

    elif "calculate" in command:
        expression = command.replace("calculate", "").strip()
        result = assistant.calculate(expression)

    elif "convert" in command and "to" in command:
        try:
            parts = command.split()
            amount = float(parts[1])
            from_curr = parts[2]
            to_curr = parts[4]
            result = assistant.convert_currency(amount, from_curr, to_curr)
        except:
            result = "Sorry, I couldn't convert currencies. Try: convert 5 USD to PKR"

    elif "meaning of" in command or "define" in command:
        word = command.replace("meaning of", "").replace("define", "").strip()
        result = assistant.lookup_dictionary(word)

    elif "translate" in command:
        try:
            parts = command.split("to")
            text = parts[0].replace("translate", "").strip()
            lang = parts[1].strip()
            result = assistant.translate_text(text, target_lang=lang)
        except:
            result = "Please say: translate hello to spanish"

    elif "start timer" in command:
        try:
            minutes = int(re.findall(r"\d+", command)[0])
            result = assistant.start_timer(minutes)
        except:
            result = "Please say like: start timer for 2 minutes"

    elif "start stopwatch" in command:
        result = assistant.start_stopwatch()

    elif "read pdf" in command:
        result = assistant.read_pdf("sample.pdf")

    elif "shutdown" in command:
        result = assistant.shutdown_system()

    elif "open" in command and "app" in command:
        app_name = command.replace("open", "").replace("app", "").strip()
        result = assistant.open_app(app_name)

    elif "screenshot" in command:
        result = assistant.take_screenshot()

    elif "covid" in command:
        result = assistant.get_covid_stats()

    elif "score" in command:
        result = assistant.get_live_score()

    elif "change language to" in command:
        for code, name in assistant.SUPPORTED_LANGUAGES.items():
            if name.lower() in command:
                user_language = code
                assistant.speak(f"Language changed to {name}", lang=code)
                return
        assistant.speak("Sorry, that language is not supported.")
        return

    else:
        result = assistant.get_chat_response(command)

    print(result)
    assistant.speak(result, lang=user_language)

if __name__ == "__main__":
    while True:
        cmd = listen()
        if cmd:
            handle_command(cmd)
