import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

def send_game_links(data, sender_email, sender_pass, base_url):
    success = 0
    fail = 0
    logs = []
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_pass)
    except Exception as e:
        return 0, 0, [f"Login Failed: {e}"]

    clean_url = base_url.split("?")[0]

    for user in data:
        try:
            link = f"{clean_url}?token={user['secret_token']}"
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = user['email']
            msg['Subject'] = "🎅 The Secret Santa Game Has Begun!"
            
            body = f"""
            Hi {user['name']}!
            
            The game is on. You have been assigned a target.
            
            Step 1: Click the link to set your Wishlist.
            Step 2: Create clues for your target.
            
            👉 Play Here: {link}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            server.sendmail(sender_email, user['email'], msg.as_string())
            success += 1
            time.sleep(1)
        except Exception as e:
            fail += 1
            logs.append(f"Error {user['email']}: {e}")
            
    server.quit()
    return success, fail, logs