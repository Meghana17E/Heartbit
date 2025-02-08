
from flask import Flask, request, jsonify, render_template
import random
from textblob import TextBlob

app = Flask(__name__)

# Global state variables
state = "greet"
nickname = None
iteration_count = 0

# Data for responses
playlists = {
    "cheerup": "https://open.spotify.com/album/0qRhFH2PLpHPPYUGxwFwHO",
    "relaxing": "https://open.spotify.com/playlist/relaxing",
    "workout": "https://open.spotify.com/playlist/workout",
    "focus": "https://open.spotify.com/playlist/focus",
    "party": "https://open.spotify.com/playlist/party",
}
quotes = [
    "Happiness is not something ready-made. It comes from your own actions. - Dalai Lama",
    "Keep your face always toward the sunshine—and shadows will fall behind you. - Walt Whitman",
    "The best way to predict the future is to create it. - Peter Drucker",
]
breathing_exercise = "Take a deep breath in for 4 seconds, hold for 7 seconds, and exhale slowly for 8 seconds. Repeat 3 times."

# Store user gratitude entries
gratitude_entries = []

def chatbot_response(user_message):
    global state, nickname, gratitude_entries

    # Greeting the user and asking for the name
    if state == "greet":
        state = "ask_name"
        return "Hello, human! Welcome to Heartbit. What is your name?"

    # Asking for a nickname
    elif state == "ask_name":
        name = user_message.strip()
        state = "ask_nickname"
        return f"Nice to meet you, {name}! Do you have a nickname? (yes/no)"

    elif state == "ask_nickname":
        if "yes" in user_message.lower():
            state = "get_nickname"
            return "What is your nickname?"
        elif "no" in user_message.lower():
            nickname = "Champion"
            state = "waiting_for_feeling"
            return f"Alright, I'll call you {nickname}. How are you feeling today?"
        else:
            return "I didn't quite understand that. Do you have a nickname? (yes/no)"

    elif state == "get_nickname":
        nickname = user_message.strip()
        state = "waiting_for_feeling"
        return f"Nice to meet you, {nickname}! How are you feeling today?"

    # Handling feelings
    elif state == "waiting_for_feeling":
        if "done" in user_message.lower() or "fine" in user_message.lower():
            state = "finished"
            return "I'm glad to hear that! Take care and have a great day!"

        blob = TextBlob(user_message)
        if blob.polarity > 0.5:
            state = "offer_support"
            return "You seem to be in great spirits! Would you like a playlist (cheer-up, party), or an inspiring quote?"
        elif 0 < blob.polarity <= 0.5:
            state = "offer_support"
            return "Glad you’re doing well! Would you like a relaxing playlist or a motivational quote?"
        elif -0.5 <= blob.polarity < 0:
            state = "offer_support"
            return "Sorry to hear that. Would a cheer-up playlist, breathing exercise, or motivational quote help?"
        elif blob.polarity < -0.5:
            state = "ask_gratitude"
            return "You seem to be feeling really low. Sometimes writing down things we’re grateful for can help. Would you like to write a gratitude journal? (yes/no)"

    # Offering support
    elif state == "offer_support":
        if "playlist" in user_message.lower():
            state = "choose_playlist"
            return "Great! What kind of playlist would you like? Options: cheer-up, relaxing, workout, focus, party."
        elif "quote" in user_message.lower():
            response = random.choice(quotes)
        elif "breathing" in user_message.lower():
            response = breathing_exercise
        else:
            response = "I didn't quite understand that. Would you like a playlist, quote, or breathing exercise?"

        state = "waiting_for_feeling"  # Stay in the feelings loop
        return f"{response}\n\nHow are you feeling now?"
    
    elif state == "choose_playlist":
        playlist_key = user_message.lower().strip()
        if playlist_key in playlists:
            state = "waiting_for_feeling"
            return f"Here’s your {playlist_key} playlist: <a href='{playlists[playlist_key]}' target='_blank'>Click here</a>\n\nHow are you feeling now?"
        else:
            return f"I couldn't find that playlist. Please choose from: {', '.join(playlists.keys())}."
            state = "choose_playlist"

    # Gratitude journal
    elif state == "ask_gratitude":
        if "yes" in user_message.lower():
            state = "get_gratitude"
            return "Great! Write down one thing you’re grateful for, and I’ll be here to listen."
        elif "no" in user_message.lower():
            state = "waiting_for_feeling"
            return "Alright. How are you feeling now?"
        else:
            return "I didn't quite understand that. Would you like to write a gratitude journal? (yes/no)"

    elif state == "get_gratitude":
        gratitude_entry = user_message.strip()
        if "done" in gratitude_entry.lower() or "move on" in gratitude_entry.lower():
            state = "waiting_for_feeling"
            response = "That's wonderful! Gratitude journaling can be very uplifting. Here are your entries so far:\n"
            response += "\n".join(f"- {entry}" for entry in gratitude_entries)
            gratitude_entries = []  # Clear entries after showing
            return f"{response}\n\nHow are you feeling now?"
        else:
            gratitude_entries.append(gratitude_entry)
            return f"That’s wonderful! You wrote: \"{gratitude_entry}\". Write another thing you’re grateful for, or type 'done' to move on."

    # Default fallback
    return "I didn’t quite understand that. Could you rephrase?"
    
@app.route('/')
def index():
    return render_template('app.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    response = chatbot_response(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
