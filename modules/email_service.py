import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

def send_magic_link_emails(supabase_data, sender_email, sender_password, base_app_url):
    success_count = 0
    fail_count = 0
    logs = []

    # Connect to SMTP
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
    except Exception as e:
        return 0, 0, [f"CRITICAL: Login failed. {str(e)}"]

    # Supabase returns a list of dictionaries (the inserted rows)
    # Each row has a 'secret_token' and 'email'
    
    # Ensure base_url ends with slash or ?token= logic
    # Clean the URL just in case
    clean_url = base_app_url.split("?")[0] 

    for user in supabase_data:
        try:
            receiver_email = user['email']
            token = user['secret_token']
            name = user['name']
            
            # THE MAGIC LINK
            magic_link = f"{clean_url}?token={token}"

            subject = f"🎅 Your Secret Santa Mission is Ready!"
            body = f"""
            Ho Ho Ho, {name}! 🎄
            
            The elves have done the matching.
            
            Click the link below to reveal who you are gifting this year:
            👉 {magic_link}
            
            (Do not share this link, it is your secret key!)
            
            Happy Holidays!
            """

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server.sendmail(sender_email, receiver_email, msg.as_string())
            success_count += 1
            time.sleep(1) # Be nice to Gmail
            
        except Exception as e:
            fail_count += 1
            logs.append(f"Failed {user.get('email', 'unknown')}: {str(e)}")

    server.quit()
    return success_count, fail_count, logs
def send_confirmation_email(user_email, user_name, match_name, match_wishlist, sender_email, sender_password):
    """Sends a receipt email AFTER they reveal on the website"""
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        subject = f"✅ Confirmation: You got {match_name}!"
        body = f"""
        Hi {user_name},
        
        This is a confirmation that you have accepted your Secret Santa mission.
        
        🎯 Your Target: {match_name}
        📝 Their Wishlist: {match_wishlist}
        
        Good luck with the gift hunting!
        """
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = user_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server.sendmail(sender_email, user_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send confirmation: {e}")