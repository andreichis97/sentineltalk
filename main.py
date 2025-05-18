# main.py

from agents import Runner
from agents_setup import driver_agent
from sentinel_tools import chat_memory

def run_turn(user_input: str) -> str:
    chat_memory.add_message("user", "user_input")
    result = Runner.run_sync(driver_agent, user_input)
    chat_memory.add_message("chatbot", result.final_output)
    return result.final_output

if __name__ == "__main__":
    print("🛰️  Welcome to SentinelTalk! (type EXIT to quit)\n")
    while True:
        user_text = input(">> ").strip()
        if user_text.upper() == "EXIT":
            print("Goodbye! 👋")
            chat_memory.clear_messages
            break
        try:
            reply = run_turn(user_text)
            print(reply, "\n")
        except Exception as e:
            print("⚠️ Error:", e, "\n")
