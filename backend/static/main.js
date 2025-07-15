const chat = document.getElementById('chat');
const form = document.getElementById('text-form');
const input = document.getElementById('text-input');
const voiceBtn = document.getElementById('voice-btn');

function add(who, txt) {
  const d = document.createElement('div');
  d.innerHTML = `<strong>${who}:</strong> ${txt}`;
  chat.appendChild(d);
}

function speakClient(text) {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  }
}

form.addEventListener('submit', async e => {
  e.preventDefault();
  const txt = input.value;
  add('You', txt);
  input.value = '';

  const res = await fetch('/api/command', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text: txt})
  });
  const j = await res.json();
  add('Assistant', j.response);
  speakClient(j.response);
});

voiceBtn.addEventListener('click', async () => {
  add('System', 'Listening...');
  const res = await fetch('/api/speak_and_listen', {method: 'POST'});
  const j = await res.json();
  add('You', j.text);
  add('Assistant', j.response);
  speakClient(j.response);
});