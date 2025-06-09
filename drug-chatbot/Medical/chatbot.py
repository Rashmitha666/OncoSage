import requests

API_URL = "http://localhost:8000/ask"  # Update if hosted elsewhere

def ask_question(topic, question):
    payload = {
        "topic": topic,
        "question": question
    }
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()

        print("\n🔍 Answers from multiple sources:\n")
        for idx, item in enumerate(data["answers"], 1):
            print(f"{idx}. {item['answer']}")
            print(f"   📚 Source: {item['source']}")
            if "source_url" in item:
                print(f"   🔗 URL: {item['source_url']}\n")

    except Exception as e:
        print(f"⚠️  Error: {e}")

def main():
    print("🧠 AI Medical Chatbot Interface\n")
    while True:
        topic = input("Enter topic (e.g., Aspirin or Lung cancer): ").strip()
        question = input("Enter your question: ").strip()
        if not topic or not question:
            print("❗ Please provide both topic and question.\n")
            continue

        ask_question(topic, question)

        again = input("\n❓ Do you want to ask another question? (y/n): ").strip().lower()
        if again != 'y':
            break

if __name__ == "__main__":
    main()
