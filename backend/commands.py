import datetime
import os
from openai import OpenAI

# Get the API key from environment variable
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    raise RuntimeError('Please set the OPENAI_API_KEY environment variable')

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def handle_command(command: str) -> str:
    cmd = command.strip()
    lower = cmd.lower()

    if 'time' in lower:
        return datetime.datetime.now().strftime('The time is %I:%M %p')
    elif 'date' in lower:
        return datetime.datetime.now().strftime('Today is %A, %B %d, %Y')

    # Fallback to OpenAI chat completion
    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': cmd}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error getting response: {e}"


