import cohere
import smtplib
from email.message import EmailMessage
import ast

# ==== CONFIGURATION ====
COHERE_API_KEY = "30u0hQyQyexPHfoLhtGu0kaILMChO8UFvgFBH65a"
EMAIL_SENDER = "rohandobarkar1@gmail.com"
EMAIL_PASSWORD = "kiat pkzn eqyf njuc"  # App password

# ==== COHERE SETUP ====
co = cohere.Client(COHERE_API_KEY)

def extract_email_details(prompt: str):
    system_message = (
        "You are an email formatting assistant. From the given user message, "
        "extract the recipient email (to), subject, and body, and return ONLY a valid Python dictionary like:\n"
        "{'to': 'email@example.com', 'subject': 'Subject here', 'body': 'Body text here'}"
    )

    try:
        response = co.chat(
            model="command-r-plus",
            temperature=0.3,
            message=prompt,
            chat_history=[],
            preamble=system_message,
        )
        raw = response.text.strip()
        return ast.literal_eval(raw)
    except Exception as e:
        print("❌ Failed to parse Cohere chat response:", e)
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
    print("📨 Enter your prompt (paragraph). End input with a blank line:\n")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    user_prompt = "\n".join(lines)

    print("\n⏳ Using Cohere chat to extract email details...")
    email_details = extract_email_details(user_prompt)

    if email_details:
        send_email(email_details['to'], email_details['subject'], email_details['body'])
    else:
        print("⚠️ Could not extract valid email details. Try rephrasing your input.")

if __name__ == "__main__":
    main()
