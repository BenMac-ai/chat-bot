
import re
from datetime import datetime


class Chatbot:

    def __init__(self, name="Masika AI"):
        self.name = name
        self.user_name = None
        self.history = []
        self.created_at = datetime.now()

    def respond(self, user_input: str) -> str:

        text = (user_input or "").strip()

        if not text:
            return "I didn't catch that. Please try again."

        normalized = text.lower()

        # GREETINGS
        if normalized in {
            "hello", "hi", "hey",
            "good morning", "good afternoon",
            "good evening"
        }:
            if self.user_name:
                reply = f"Hello again, {self.user_name}! How can I help you?"
            else:
                reply = "Hello! I'm Masika AI. How can I help you today?"

        # USER NAME REGISTRATION
        elif re.search(r"\bmy name is\b|\bcall me\b", normalized):

            match = re.search(
                r"(?:my name is|call me)\s+([a-zA-Z]+)",
                text,
                re.IGNORECASE
            )

            if match:
                self.user_name = match.group(1).capitalize()
                reply = f"Nice to meet you, {self.user_name}! I'll remember your name during this session."
            else:
                reply = "Please tell me your name."

        # USER NAME RECALL
        elif "what is my name" in normalized or "do you know my name" in normalized:

            if self.user_name:
                reply = f"Your name is {self.user_name}."
            else:
                reply = "I haven't learned your name yet. What should I call you?"

        # BOT IDENTITY
        elif "your name" in normalized:
            reply = f"My name is {self.name}, your personal AI assistant."

        elif "who created you" in normalized or "who made you" in normalized:
            reply = "I was developed using Python by my developer."

        elif "tell me about yourself" in normalized:
            reply = (
                "I'm Masika AI, a Python-powered conversational assistant. "
                "I'm designed to communicate, assist with questions "
                "and grow through new integrations."
            )

        # CAPABILITIES
        elif "help" in normalized or "what can you do" in normalized:
            reply = (
                "Here are some things I can do:\n"
                "- Have basic conversations\n"
                "- Remember your name during this session\n"
                "- Answer predefined questions\n"
                "- Maintain conversation history\n"
                "- Assist with simple programming questions"
            )

        # WELLBEING
        elif "how are you" in normalized:
            reply = "I'm doing great! Ready to help you with anything."

        # THANK YOU
        elif "thank you" in normalized or "thanks" in normalized:
            reply = "You're very welcome! It's always a pleasure to help."

        # PROGRAMMING
        elif "what is python" in normalized:
            reply = (
                "Python is a high-level programming language "
                "used in web development, automation, artificial "
                "intelligence and data science."
            )

        elif "what is programming" in normalized:
            reply = (
                "Programming is the process of writing instructions "
                "that tell a computer how to perform specific tasks."
            )

        elif "i love coding" in normalized:
            reply = "That's fantastic! Coding gives you the power to turn ideas into reality."

        # WEATHER
        elif "weather" in normalized:
            reply = (
                "I don't have live weather access yet. "
                "We can integrate a weather API to give me real-time weather information."
            )

        # TIME
        elif "what time is it" in normalized:
            reply = f"The current system time is {datetime.now().strftime('%I:%M %p')}."

        # DATE
        elif "what is today's date" in normalized or "what is the date" in normalized:
            reply = f"Today's date is {datetime.now().strftime('%d %B %Y')}."

        # CONVERSATION HISTORY
        elif "how many messages" in normalized:
            reply = f"We have exchanged {len(self.history)} messages so far."

        # GOODBYE
        elif normalized in {"bye", "goodbye", "exit", "quit"}:
            reply = "Goodbye! Thanks for chatting with Masika AI. See you again!"

        # UNKNOWN QUESTIONS
        else:
            reply = (
                f"That's an interesting question, {self.user_name or 'there'}! "
                "I don't have enough information to answer it accurately yet. "
                "I'm ready to explore more topics as my capabilities grow."
            )

        # SAVE CONVERSATION
        self.history.append({
            "user": text,
            "bot": reply,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return reply

    # GET CONVERSATION HISTORY
    def get_history(self):
        return self.history

    # CLEAR CONVERSATION HISTORY
    def clear_history(self):
        self.history.clear()


# RUN CHATBOT IN TERMINAL
if __name__ == "__main__":

    bot = Chatbot()

    print("=" * 45)
    print(f"       {bot.name} IS ONLINE")
    print("=" * 45)
    print("Type 'exit' to stop the conversation.\n")

    while True:

        user_message = input("You: ")

        response = bot.respond(user_message)

        print(f"\n{bot.name}: {response}\n")

        if user_message.strip().lower() in {"exit", "quit", "bye", "goodbye"}:
            break
