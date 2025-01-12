import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'  # Use your email provider's SMTP server
SMTP_PORT = 587                 # For TLS
EMAIL_ADDRESS = 'tomacarmen7787@gmail.com'
EMAIL_PASSWORD = 'lsob klqi ndlk muth'


subject = "Welcome to the Bank"
body = "Welcome to the Bank! You have successfully created an account. Thank you for choosing us."

# Connect to the SMTP server
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()  # Upgrade connection to secure
server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

def sendWelcomeEmail(recipient : str):
    message = MIMEMultipart()
    message['From'] = EMAIL_ADDRESS
    message['To'] = recipient
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        server.sendmail(EMAIL_ADDRESS, message['To'], message.as_string())
        print("INFO:     Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

def mail_server_quit():
    server.quit()
    print("INFO:     Shutting down mail server")

