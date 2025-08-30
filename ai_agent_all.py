import cohere
import smtplib
from email.message import EmailMessage
import ast

# === CONFIG ===
COHERE_API_KEY = "30u0hQyQyexPHfoLhtGu0kaILMChO8UFvgFBH65a"
EMAIL_SENDER = "rohandobarkar1@gmail.com"
EMAIL_PASSWORD = "kiat pkzn eqyf njuc"
co = cohere.Client(COHERE_API_KEY)

def classify_and_process(prompt: str):
    system_instruction = (
        "You're an intelligent assistant. If the user's input is an instruction to send an email, respond ONLY with "
        "a Python dictionary like: {'type': 'email', 'to': 'abc@gmail.com', 'subject': '...', 'body': '...'}.\n"
        "If it's just a normal query (not an email to send), respond with: {'type': 'normal', 'answer': '...'}.\n"
        "Do not say anything else.\n\n"
        f"User input: {prompt}"
    )

    try:
        response = co.chat(
            model="command-r-plus",
            message=system_instruction,
            temperature=0.4,
            chat_history=[]
        )
        raw = response.text.strip()
        return ast.literal_eval(raw)
    except Exception as e:
        print("❌ Failed to understand response:", e)
        return None

def send_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"\n✅ Email sent to {to_email}")
    except Exception as e:
        print(f"\n❌ Failed to send email: {e}")

def main():
    print("🧠 Intelligent Agent: Send email or answer prompt based on input.")
    print("Type your prompt (or 'exit' to quit):\n")

    while True:
        user_prompt = input("🧾 Prompt > ")
        if user_prompt.strip().lower() == "exit":
            print("👋 Goodbye.")
            break

        result = classify_and_process(user_prompt)

        if result is None:
            print("⚠️ Could not process the input.\n")
            continue

        if result.get('type') == 'email':
            send_email(result['to'], result['subject'], result['body'])
        elif result.get('type') == 'normal':
            print(f"\n💬 Response:\n{result['answer']}\n")
        else:
            print("⚠️ Unexpected response type.\n")

if __name__ == "__main__":
    main()
