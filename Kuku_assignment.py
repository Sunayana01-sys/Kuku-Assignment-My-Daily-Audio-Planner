import tkinter as tk
from tkinter import messagebox
from gtts import gTTS
from googletrans import Translator
import random
import requests
import os
from PIL import Image, ImageTk
import pandas as pd
from collections import Counter

# ------------------ Content Functions ------------------ #
def get_motivational_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random")
        if response.status_code == 200:
            data = response.json()
            quote = data[0]['q']
            author = data[0]['a']
            return f"{quote} — {author}"
    except:
        pass
    return "Stay positive, work hard, and make it happen!"

def get_daily_tip():
    tips = [
        "Break big tasks into smaller steps to avoid overwhelm.",
        "Use the Pomodoro technique: 25 min focus + 5 min break.",
        "Write your top 3 tasks every morning.",
        "Avoid multitasking — focus on one thing at a time.",
        "Review your day each night to plan for tomorrow."
    ]
    return random.choice(tips)

def get_health_tip():
    tips = [
        "Drink 8 glasses of water today.",
        "Take a 10-minute walk after meals.",
        "Eat at least 1 fruit today.",
        "Avoid added sugar for the rest of the day.",
        "Stretch your neck and shoulders if you've been sitting too long."
    ]
    return random.choice(tips)

def get_news_update():
    try:
        response = requests.get("https://gnews.io/api/v4/top-headlines?lang=en&max=1&token=1b05b058c2b8d9024736136942bf0e5a")
        if response.status_code == 200:
            article = response.json()["articles"][0]
            return f"Top News: {article['title']}. {article['description']}"
    except:
        pass
    return "India's digital economy is on the rise, according to recent reports."

def get_weather_update(city="Bangalore"):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=e6cc8ae335d7756e0c415b464abd3821&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            return f"The current weather in {city} is {temp}°C with {desc}."
    except:
        pass
    return "Weather update is currently unavailable. Please check your city settings."

def get_recommendations(user_name):
    try:
        df = pd.read_csv("user_listening_history.csv")
        df_user = df[df['user_name'].str.lower() == user_name.lower()]

        if df_user.empty:
            return "We don't have enough listening history to recommend shows."

        genre_counts = Counter(df_user['genre'])
        top_genre = genre_counts.most_common(1)[0][0]

        new_episodes = df_user[(df_user['genre'] == top_genre) & (df_user['new_episodes'].str.lower() == 'yes')]['show_name'].tolist()

        rec_text = f"\nBased on your interest in '{top_genre}', we recommend:"
        if new_episodes:
            for show in new_episodes:
                rec_text += f"\n🔸 {show} (New episodes available!)"
        else:
            rec_text += "\n(No new episodes found, but you can revisit past favorites!)"

        return rec_text
    except Exception as e:
        return f"Error in recommendation system: {e}"

# ------------------ Planner Generator Function ------------------ #
def generate_planner():
    name = name_entry.get()
    language = language_var.get()

    selected_content = [option for option, var in zip(content_options, content_vars) if var.get() == 1]

    if not name:
        messagebox.showerror("Input Error", "Please enter your name.")
        return

    if len(selected_content) != 2:
        messagebox.showerror("Selection Error", "Please select exactly 2 content types.")
        return

    planner_text = f"Hello {name}! Here's your personalized audio planner for today.\n"

    for content in selected_content:
        if content == "Motivational Quote":
            planner_text += "\nMotivational Quote: " + get_motivational_quote()
        elif content == "Daily Tip":
            planner_text += "\nDaily Tip: " + get_daily_tip()
        elif content == "Health Tip":
            planner_text += "\nHealth Tip: " + get_health_tip()
        elif content == "News Update":
            planner_text += "\nNews Update: " + get_news_update()
        elif content == "Weather Update":
            planner_text += "\nWeather Update: " + get_weather_update()

    planner_text += "\n\n🎙️ Audio Recommendations:"
    planner_text += get_recommendations(name)

    # Translate if Hindi selected
    if language == "Hindi":
        try:
            translator = Translator()
            translated = translator.translate(planner_text, dest='hi')
            planner_text = translated.text
        except:
            messagebox.showwarning("Translation Error", "Could not translate to Hindi. Proceeding in English.")

    # Text to Speech
    try:
        tts = gTTS(text=planner_text, lang='hi' if language == "Hindi" else 'en')
        tts.save("planner_audio.mp3")
        os.system("start planner_audio.mp3" if os.name == 'nt' else "play planner_audio.mp3")
    except:
        messagebox.showerror("Audio Error", "Could not generate or play the audio.")

# ------------------ UI Setup ------------------ #
root = tk.Tk()
root.title("🎧 My Daily Audio Planner")
root.geometry("600x700")
root.configure(bg="#fff9f5")

try:
    logo_img = Image.open("kuku_logo_red.png")
    logo_img = logo_img.resize((160, 60))
    logo = ImageTk.PhotoImage(logo_img)
    tk.Label(root, image=logo, bg="#fff9f5").pack(pady=10)
except:
    tk.Label(root, text="KUKU FM", font=("Helvetica", 24, "bold"), fg="red", bg="#fff9f5").pack(pady=10)

tk.Label(root, text="Welcome to Your Personalized Audio Planner!", font=("Georgia", 14), fg="#333", bg="#fff9f5").pack(pady=5)

# Name Input
tk.Label(root, text="Enter your name:", font=("Arial", 12), bg="#fff9f5").pack()
name_entry = tk.Entry(root, font=("Arial", 12), width=30)
name_entry.pack(pady=5)

# Language Selection
tk.Label(root, text="Choose audio language:", font=("Arial", 12), bg="#fff9f5").pack(pady=(10, 2))
language_var = tk.StringVar(value="English")
tk.Radiobutton(root, text="English", variable=language_var, value="English", font=("Arial", 11), bg="#fff9f5").pack(anchor='w', padx=100)
tk.Radiobutton(root, text="Hindi", variable=language_var, value="Hindi", font=("Arial", 11), bg="#fff9f5").pack(anchor='w', padx=100)

# Content Options
tk.Label(root, text="Pick exactly 2 content types:", font=("Arial", 12, "bold"), bg="#fff9f5").pack(pady=(15, 5))
content_options = ["Motivational Quote", "Daily Tip", "Health Tip", "News Update", "Weather Update"]
content_vars = [tk.IntVar() for _ in content_options]
emoji_map = {
    "Motivational Quote": "💪",
    "Daily Tip": "📌",
    "Health Tip": "🍎",
    "News Update": "📰",
    "Weather Update": "☀️"
}
for option, var in zip(content_options, content_vars):
    tk.Checkbutton(root, text=f"{emoji_map[option]} {option}", variable=var, font=("Arial", 11), bg="#fff9f5").pack(anchor='w', padx=100)

# Generate Button
tk.Button(root, text="🎧 Generate My Planner", command=generate_planner,
          bg="#e63946", fg="white", font=("Arial", 12, "bold"), padx=10, pady=5).pack(pady=30)

root.mainloop()
