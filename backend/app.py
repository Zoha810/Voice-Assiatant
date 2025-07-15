import os
import threading
from flask import Flask, request, jsonify, render_template
from speech import listen, speak
from wakeword import WakeWordDetector
from commands import handle_command

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
    static_url_path='/static'
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/command', methods=['POST'])
def text_command():
    data = request.get_json(force=True)
    cmd = data.get('text', '')
    resp = handle_command(cmd)
    # Speak the AI response for text commands as well
    speak(resp)
    return jsonify({'text': cmd, 'response': resp})

@app.route('/api/speak_and_listen', methods=['POST'])
def speak_and_listen():
    # Prompt and listen
    speak("Yes? How can I help?")
    cmd = listen(timeout=5, phrase_time_limit=8) or ''
    resp = handle_command(cmd)
    # Speak the AI response
    speak(resp)
    return jsonify({'text': cmd, 'response': resp})

if __name__ == '__main__':
    # Start wake‑word detector thread
    detector = WakeWordDetector(callback=lambda: None)
    threading.Thread(target=detector.run, daemon=True).start()

    # Run server, auto‑increment port if busy
    port = int(os.environ.get('PORT', 5002))
    while True:
        try:
            app.run(host='0.0.0.0', port=port, debug=True)
            break
        except OSError as e:
            if 'Address already in use' in str(e):
                print(f"Port {port} in use, trying {port+1}...")
                port += 1
            else:
                raise