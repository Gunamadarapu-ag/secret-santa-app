import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import time

# IMPORT THE TEMPLATE
from modules.email_templates import get_common_html_template

# --- CONFIGURATION ---
# Ensure this file is in your root folder
LOCAL_LOGO_FILENAME = "logo_aciesGlobal_2024_light.png" 

# --- HELPER: ATTACH IMAGE ---
def attach_image_to_email(msg):
    """Reads local logo and attaches it with Content-ID"""
    try:
        if os.path.exists(LOCAL_LOGO_FILENAME):
            with open(LOCAL_LOGO_FILENAME, 'rb') as f:
                img_data = f.read()
                image = MIMEImage(img_data, name=LOCAL_LOGO_FILENAME)
                image.add_header('Content-ID', '<company_logo>')
                image.add_header('Content-Disposition', 'inline', filename=LOCAL_LOGO_FILENAME)
                msg.attach(image)
        else:
            print(f"⚠️ Warning: {LOCAL_LOGO_FILENAME} not found.")
    except Exception as e:
        print(f"Error attaching image: {e}")

# --- EMAIL TYPE 1: START GAME ---
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

    clean_url = base_url.split("?")[0].rstrip("/")

    for user in data:
        try:
            link = f"{clean_url}/?token={user['secret_token']}"
            
            body_html = f"""
            <p class="message" style="font-size: 16px; line-height: 1.6; margin-bottom: 25px;">
                Warm holiday greetings! You've been chosen as a <strong>Secret Santa</strong>.
                <br>Your mission: Bring joy to your assigned Child!
            </p>
            
            <div class="steps-box">
                <div class="step-item">
                    <div class="step-icon">🎁</div>
                    <div><strong>Step 1:</strong> Create Your Wish List</div>
                </div>
                <div class="step-item">
                    <div class="step-icon">🕵️</div>
                    <div><strong>Step 2:</strong> Craft Clues & Assign a Dare</div>
                </div>
            </div>
            """
            
            html_content = get_common_html_template(user['name'], body_html, "🎅 Enter Portal", link)

            msg = MIMEMultipart('related')
            msg['From'] = sender_email
            msg['To'] = user['email']
            msg['Subject'] = "🎅 Your Secret Santa Mission Begins!"

            msg_alternative = MIMEMultipart('alternative')
            msg.attach(msg_alternative)
            msg_alternative.attach(MIMEText(html_content, 'html'))

            attach_image_to_email(msg)

            server.sendmail(sender_email, user['email'], msg.as_string())
            success += 1
            time.sleep(1)
        except Exception as e:
            fail += 1
            logs.append(f"Error {user['email']}: {e}")
            
    server.quit()
    return success, fail, logs

# --- EMAIL TYPE 2: CONFIRMATION ---
def send_confirmation_email(user_email, user_name, match_name, match_wishlist, sender_email, sender_password):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        body_html = f"""
        <p style="font-size: 18px;">We received your Proof! <strong>You are officially safe.</strong></p>
        <div class="steps-box" style="text-align: center;">
            <p>Your Target was:</p>
            <h3 style="color: #ffeb3b; font-size: 24px;">{match_name}</h3>
            <p>Their Wishlist: <em>"{match_wishlist}"</em></p>
        </div>
        """
        
        html_content = get_common_html_template(user_name, body_html, cta_text=None, cta_link=None)

        msg = MIMEMultipart('related')
        msg['From'] = sender_email
        msg['To'] = user_email
        msg['Subject'] = "✅ Proof Received: You are Safe!"
        
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        msg_alternative.attach(MIMEText(html_content, 'html'))

        attach_image_to_email(msg)
        
        server.sendmail(sender_email, user_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send confirmation: {e}")

# --- EMAIL TYPE 3: NUDGE LAZY SANTAS (ADDED BACK!) ---
def send_clue_reminders(data, sender_email, sender_pass, base_url):
    success = 0
    fail = 0
    logs = []
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_pass)
    except Exception as e:
        return 0, 0, [f"Login Failed: {e}"]

    clean_url = base_url.split("?")[0].rstrip("/")

    for user in data:
        try:
            link = f"{clean_url}/?token={user['secret_token']}"
            
            # CUSTOM WARNING BODY
            # --- CUSTOM "LAZY SANTA" BODY ---
            body_html = f"""
            <p class="message" style="font-size: 18px;"><strong>Dear Lazy Santa {user['name']},</strong></p>
            
            <div class="steps-box" style="background-color: #fff0f0; border: 2px dashed #ff4b4b; text-align: center; padding: 20px; color: #333333;">
                <p style="font-size: 16px; margin: 0 0 10px 0; color: #333333;">
                    😴 We know you are too busy to wake up from your bed...
                </p>
                
                <h2 style="color: #d32f2f; margin: 10px 0;">⏰ PLEASE WAKE UP! ⏰</h2>
                
                <p style="color: #333333;">You need to fill up the clues! If you hit snooze one more time, the system might accidentally whisper:</p>
                
                <div style="background: white; padding: 10px; border-radius: 5px; margin: 15px auto; display: inline-block; box-shadow: 0 2px 5px rgba(0,0,0,0.1); color: #d32f2f;">
                    <em>"The Lazy Santa is actually {user['name']}!"</em>
                </div>
                
                <p style="font-size: 14px; margin-top: 10px; color: #333333;">Don't let that happen. Click the button below!</p>
            </div>
            """
            
            # We use the common template but with the warning body
            html_content = get_common_html_template(user['name'], body_html, "🚀 Submit Clues Immediately", link)

            msg = MIMEMultipart('related')
            msg['From'] = sender_email
            msg['To'] = user['email']
            msg['Subject'] = "⚠️ Action Required: Your Secret Identity is at Risk!"
            
            msg_alternative = MIMEMultipart('alternative')
            msg.attach(msg_alternative)
            msg_alternative.attach(MIMEText(html_content, 'html'))

            attach_image_to_email(msg)

            server.sendmail(sender_email, user['email'], msg.as_string())
            success += 1
            time.sleep(1)
        except Exception as e:
            fail += 1
            logs.append(f"Error {user['email']}: {e}")
            
    server.quit()
    return success, fail, logs