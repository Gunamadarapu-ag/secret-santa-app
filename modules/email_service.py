import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

def send_secret_santa_emails(matches_df, sender_email, sender_password):
    success_count = 0
    fail_count = 0
    logs = []

    try:
        # Connect to Gmail SMTP Server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
    except Exception as e:
        return 0, 0, [f"CRITICAL: Could not login. Check App Password. Error: {str(e)}"]

    # Iterate through matches
    for index, row in matches_df.iterrows():
        try:
            giver_email = row['Giver_Email']
            giver_name = row['Giver_Name']
            receiver_name = row['Receiver_Name']
            # Optional: Add Gift hints here if available

            subject = f"🤫 Secret Santa Assignment for {giver_name}!"
            body = f"""
            Hi {giver_name},
            
            You are the Secret Santa for: 
            🎁 **{receiver_name}** 🎁
            
            Location: {row['Location']}
            
            Remember to keep it a secret!
            
            Happy Holidays!
            """

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = giver_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server.sendmail(sender_email, giver_email, msg.as_string())
            success_count += 1
            # Sleep to avoid Gmail spam blocking (1 second)
            time.sleep(1) 
            
        except Exception as e:
            fail_count += 1
            logs.append(f"Failed to send to {giver_email}: {str(e)}")

    server.quit()
    return success_count, fail_count, logs