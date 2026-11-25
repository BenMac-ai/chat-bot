from chatbot import Chatbot


def main():
    bot = Chatbot("Masika")
    print("Chatbot started. Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in {"exit", "quit", "bye"}:
            print(f"{bot.name}: {bot.respond(user_input)}")
            break

        print(f"{bot.name}: {bot.respond(user_input)}")


if __name__ == "__main__":
    main()
