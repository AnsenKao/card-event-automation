import smtplib
from email.mime.text import MIMEText

class EmailSender:
    """A class to handle sending emails."""

    def __init__(self, smtp_server, smtp_port, smtp_user, smtp_password, from_email):
        """Initializes the EmailSender with SMTP server details and sender email.

        Args:
            smtp_server: The SMTP server address.
            smtp_port: The SMTP server port.
            smtp_user: The SMTP username.
            smtp_password: The SMTP password.
            from_email: The sender's email address.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email

    def send_email(self, to_email, subject, body):
        """Sends an email.

        Args:
            to_email: The recipient's email address.
            subject: The subject of the email.
            body: The body of the email.
        """
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = to_email

        try:
            # Try SMTP_SSL first (for ports like 465)
            if self.smtp_port == 465:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.from_email, to_email, msg.as_string())
            else:
                # Use SMTP with STARTTLS (for ports like 587)
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()  # Enable encryption
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.from_email, to_email, msg.as_string())
            
            print(f"Email sent successfully to {to_email}")
        except Exception as e:
            print(f"Error sending email: {e}")

# Example usage (replace with your actual details from .env or config):
# if __name__ == '__main__':
#     # These would typically be loaded from environment variables or a config file
#     import os
#     import dotenv
#     dotenv.load_dotenv()

#     SENDER_EMAIL = os.getenv("SENDER_EMAIL")
#     SMTP_SERVER = os.getenv("SMTP_SERVER")
#     SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # Default to 587
#     SMTP_USER = os.getenv("SMTP_USER")
#     SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
#     RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

#     email_sender_instance = EmailSender(
#         smtp_server=SMTP_SERVER,
#         smtp_port=SMTP_PORT,
#         smtp_user=SMTP_USER,
#         smtp_password=SMTP_PASSWORD,
#         from_email=SENDER_EMAIL
#     )
#     email_sender_instance.send_email(
#         to_email=RECIPIENT_EMAIL,
#         subject="Test Email from EmailSender Class",
#         body="This is a test email sent from the Python EmailSender class."
#     )

