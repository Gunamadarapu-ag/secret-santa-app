import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import time

# --- CONFIGURATION ---
# We use the filename directly. Make sure 'logo.png' is in your main project folder.
LOCAL_LOGO_FILENAME = "logo_aciesGlobal_2024_light.png" 
#last updated: 05-12-2025
# --- HTML TEMPLATE GENERATOR ---
def get_html_template(name, body_content, cta_text=None, cta_link=None):
    """
    Injects content into your Custom Festive Design.
    Note: The logo source is now 'cid:company_logo' which maps to the attachment.
    """
    
    # Button Logic
    button_html = ""
    if cta_text and cta_link:
        button_html = f"""
        <div class="cta-container">
            <a href="{cta_link}" class="cta-button">
                {cta_text}
            </a>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            /* (Your CSS styles remain the same, kept brief here for readability) */
            body {{ background-color: #0a2e4a; padding: 20px; font-family: Arial, sans-serif; }}
            .email-container {{ max-width: 600px; margin: 0 auto; background: linear-gradient(to bottom, #0a2e4a, #1a4d7a); border-radius: 15px; }}
            .header {{ background: linear-gradient(to bottom, #8b0000, #c62828); padding: 20px; display: flex; align-items: center; }}
            .logo {{ width: 80px; height: 80px; overflow: hidden; display: flex; align-items: center; justify-content: center; }}
            .logo img {{ width: 90%; height: 90%; object-fit: contain; }}
            .content {{ padding: 20px; color: white; text-align: center; }}
            .cta-button {{ background: linear-gradient(to right, #2e7d32, #43a047); color: white; padding: 15px 30px; border-radius: 50px; text-decoration: none; display: inline-block; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <!-- Header -->
            <div class="header">
                <div class="logo">
                    <!-- HERE IS THE MAGIC: cid points to the attachment -->
                    <img src="cid:company_logo" alt="Logo">
                </div>
                <div style="flex: 1; padding-left: 15px; text-align: center;">
                    <h1 style="color: #ffeb3b; margin: 0; font-size: 24px;">Secret Santa Begins!</h1>
                </div>
            </div>
            
            <div class="content">
                <h2 style="color: #ffeb3b;">Hi {name}!</h2>
                {body_content}
                {button_html}
            </div>
            
            <div style="text-align: center; padding: 20px; color: #ccc; font-size: 12px;">
                <p>Powered by HR Secret Santa Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

# --- HELPER: ATTACH IMAGE ---
def attach_image_to_email(msg):
    """Reads local logo.png and attaches it with Content-ID"""
    try:
        # Check if file exists
        if os.path.exists(LOCAL_LOGO_FILENAME):
            with open(LOCAL_LOGO_FILENAME, 'rb') as f:
                img_data = f.read()
                image = MIMEImage(img_data, name=LOCAL_LOGO_FILENAME)
                # This Header ID matches the <img src="cid:company_logo"> in HTML
                image.add_header('Content-ID', '<company_logo>')
                image.add_header('Content-Disposition', 'inline', filename=LOCAL_LOGO_FILENAME)
                msg.attach(image)
        else:
            print(f"⚠️ Warning: {LOCAL_LOGO_FILENAME} not found. Logo will be broken.")
    except Exception as e:
        print(f"Error attaching image: {e}")

# --- FUNCTION 1: SEND GAME START LINKS ---
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
            
            body = """
            <p>The most magical time of the year is here! Our Secret Santa game has officially started.</p>
            <p><strong>Step 1:</strong> Create your Wishlist.</p>
            <p><strong>Step 2:</strong> Create clues for your target.</p>
            """
            
            html_content = get_html_template(user['name'], body, "Enter Secret Santa Portal", link)

            # IMPORTANT: Use 'related' type to support images
            msg = MIMEMultipart('related')
            msg['From'] = sender_email
            msg['To'] = user['email']
            msg['Subject'] = "🎅 Your Secret Mission Begins!"

            # Attach HTML
            msg_alternative = MIMEMultipart('alternative')
            msg.attach(msg_alternative)
            msg_alternative.attach(MIMEText(html_content, 'html'))

            # Attach Image (The Magic Step)
            attach_image_to_email(msg)

            server.sendmail(sender_email, user['email'], msg.as_string())
            success += 1
            time.sleep(1)
        except Exception as e:
            fail += 1
            logs.append(f"Error {user['email']}: {e}")
            
    server.quit()
    return success, fail, logs

# --- FUNCTION 2: SEND CONFIRMATION ---
def send_confirmation_email(user_email, user_name, match_name, match_wishlist, sender_email, sender_password):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        body = f"""
        <p>We received your Proof! You are officially safe.</p>
        <p>Your Target was: <strong style="color: #ffeb3b;">{match_name}</strong></p>
        <p>Their Wishlist: <em>"{match_wishlist}"</em></p>
        """
        
        html_content = get_html_template(user_name, body)

        msg = MIMEMultipart('related')
        msg['From'] = sender_email
        msg['To'] = user_email
        msg['Subject'] = "✅ Proof Received: You are Safe!"
        
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        msg_alternative.attach(MIMEText(html_content, 'html'))

        # Attach Image
        attach_image_to_email(msg)
        
        server.sendmail(sender_email, user_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send confirmation: {e}")