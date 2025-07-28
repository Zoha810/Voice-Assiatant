  const chat = document.getElementById('chat');
    const form = document.getElementById('text-form');
    const input = document.getElementById('text-input');
    const voiceBtn = document.getElementById('voice-btn');
    const sendBtn = document.getElementById('send-btn');
    const stopBtn = document.getElementById('stop-btn');
    const app = document.getElementById('app');
    const chatContainer = document.getElementById('chat-container');

    function add(who, txt) {
      const d = document.createElement('div');
      let className = '';
      if (who === 'You') {
        className = 'ml-auto bg-blue-500 text-white max-w-[75%] rounded-2xl rounded-br-none p-3 shadow-sm';
      } else if (who === 'Aoran') {
        className = 'mr-auto bg-gray-200 text-gray-800 max-w-[75%] rounded-2xl rounded-bl-none p-3 shadow-sm';
      } else {
        className = 'mx-auto bg-gray-300 text-gray-600 text-sm max-w-[75%] rounded-full p-2 text-center';
      }
      d.innerHTML = `<strong>${who}:</strong> ${txt}`;
      d.className = `animate-message ${className}`;
      chat.appendChild(d);
      // Auto-scroll to the latest message
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function speakClient(text) {
  if ('speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Get available voices and select a natural-sounding one
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(voice => 
      voice.name.includes('Natural') || 
      voice.name.includes('Google') || 
      voice.lang.includes('en-US')
    ) || voices[0]; // Fallback to first available voice
    
    // Configure utterance for more natural speech
    utterance.voice = preferredVoice;
    utterance.pitch = 1.0; // Default pitch (0.5 to 2.0)
    utterance.rate = 1.0;  // Slightly slower for clarity (0.1 to 10)
    utterance.volume = 0.9; // Slightly lower than max (0 to 1)
    
    // Event handlers for UI updates
    utterance.onstart = () => {
      sendBtn.disabled = true;
      voiceBtn.disabled = true;
      stopBtn.classList.remove('hidden');
      app.setAttribute('aria-busy', 'true');
    };
    
    utterance.onend = () => {
      sendBtn.disabled = false;
      voiceBtn.disabled = false;
      stopBtn.classList.add('hidden');
      app.setAttribute('aria-busy', 'false');
      input.focus(); // Return focus to input
    };
    
    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error);
      sendBtn.disabled = false;
      voiceBtn.disabled = false;
      stopBtn.classList.add('hidden');
      app.setAttribute('aria-busy', 'false');
      input.focus();
    };
    
    // Stop button functionality
    stopBtn.onclick = () => {
      window.speechSynthesis.cancel();
      sendBtn.disabled = false;
      voiceBtn.disabled = false;
      stopBtn.classList.add('hidden');
      app.setAttribute('aria-busy', 'false');
      input.focus();
    };
    
    // Ensure voices are loaded before speaking
    if (voices.length === 0) {
      window.speechSynthesis.onvoiceschanged = () => {
        const updatedVoices = window.speechSynthesis.getVoices();
        utterance.voice = updatedVoices.find(voice => 
          voice.name.includes('Natural') || 
          voice.name.includes('Google') || 
          voice.lang.includes('en-US')
        ) || updatedVoices[0];
        window.speechSynthesis.speak(utterance);
      };
    } else {
      window.speechSynthesis.speak(utterance);
    }
  } else {
    console.warn('Speech synthesis not supported in this browser.');
    // Optionally notify user via UI
  }
}

    function showLoading() {
      add('Aoran', '<span class="loading">Processing<span class="animate-pulse">.</span><span class="animate-pulse delay-100">.</span><span class="animate-pulse delay-200">.</span></span>');
      sendBtn.disabled = true;
      voiceBtn.disabled = true;
      app.setAttribute('aria-busy', 'true');
    }

    function hideLoading() {
      const loading = chat.querySelector('.loading');
      if (loading) loading.parentElement.remove();
      sendBtn.disabled = false;
      voiceBtn.disabled = false;
      app.setAttribute('aria-busy', 'false');
    }

    form.addEventListener('submit', async e => {
      e.preventDefault();
      const txt = input.value.trim();
      if (!txt) return; // Prevent empty submissions
      add('You', txt);
      input.value = '';
      showLoading();

      try {
        const res = await fetch('/api/command', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({text: txt})
        });
        if (!res.ok) throw new Error('Network error');
        const j = await res.json();
        hideLoading();
        add('Aoran', j.response);
        speakClient(j.response);
      } catch (error) {
        hideLoading();
        add('Aoran', 'Error: Could not process your request.');
      }
    });

    voiceBtn.addEventListener('click', async () => {
      add('Aoran', 'Listening...');
      showLoading();
      try {
        const res = await fetch('/api/speak_and_listen', {method: 'POST'});
        if (!res.ok) throw new Error('Network error');
        const j = await res.json();
        hideLoading();
        add('You', j.text);
        add('Aoran', j.response);
        speakClient(j.response);
      } catch (error) {
        hideLoading();
        add('Aoran', 'Error: Could not process voice input.');
      }
    });