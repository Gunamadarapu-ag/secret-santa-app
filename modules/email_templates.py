# modules/email_templates.py

def get_common_html_template(name, body_content, cta_text=None, cta_link=None):
    """
    Returns the Acies Global Festive Theme HTML.
    This can be used for Game Links, Confirmations, Reminders, etc.
    """
    
    # 1. Prepare the Button HTML
    button_html = ""
    if cta_text and cta_link:
        button_html = f"""
        <div class="cta-container">
            <a href="{cta_link}" class="cta-button">
                {cta_text}
            </a>
        </div>
        """

    # 2. View in Browser Link (Optional fallback)
    view_browser_html = ""
    if cta_link:
        view_browser_html = f"""
        <div class="view-browser">
            Cannot see the snow or animations? <a href="{cta_link}">View in browser</a>
        </div>
        """

    # 3. The Full HTML String
    # Note: We use double curly braces {{ }} for CSS so Python ignores them.
    # We use single curly braces { } for Python variables.
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Secret Santa Game</title>
        <style>
            /* BASE STYLES */
            * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Arial', sans-serif; }}
            body {{ background-color: #0a2e4a; padding: 20px; }}
            
            .view-browser {{ text-align: center; padding-bottom: 10px; font-size: 12px; color: #ccc; }}
            .view-browser a {{ color: #fff; }}

            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background: linear-gradient(to bottom, #0a2e4a, #1a4d7a);
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 0 30px rgba(255, 255, 255, 0.2);
                position: relative;
                color: white;
            }}

            .header {{
                background: linear-gradient(to bottom, #8b0000, #c62828);
                padding: 20px;
                text-align: center;
                border-bottom: 3px solid #ffd700;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }}
            
            .logo {{
                /* 🟢 UPDATED CSS FOR LOGO */
                width: 100px; 
                height: auto; 
                background: transparent; /* No more white background */
                border: none; /* Removed the yellow circle border */
                display: flex; 
                align-items: center; 
                justify-content: center;
            }}
            /* This IMG tag refers to the CID attachment */
            .logo img {{ width: 90%; height: 90%; object-fit: contain; }}
            
            .header-text {{ flex: 1; padding-left: 15px; }}
            .header-text h1 {{ color: #ffeb3b; font-size: 24px; margin-bottom: 5px; text-shadow: 1px 1px 2px black; }}
            .header-text p {{ color: white; font-size: 14px; margin: 0; }}

            .bells-container {{ text-align: center; padding: 20px; font-size: 40px; }}
            
            .content {{ padding: 20px; text-align: center; position: relative; z-index: 2; }}
            .greeting {{ font-size: 22px; color: #ffeb3b; margin-bottom: 15px; }}
            
            /* Custom Boxes for Wishlist/Clues */
            .steps-box {{ background-color: rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px; margin: 20px 0; text-align: left; }}
            .step-item {{ margin-bottom: 15px; display: flex; align-items: flex-start; }}
            .step-icon {{ font-size: 24px; margin-right: 10px; }}
            
            .cta-container {{ margin: 30px 0; }}
            .cta-button {{
                background: linear-gradient(to right, #2e7d32, #43a047);
                color: white !important;
                padding: 15px 30px;
                border-radius: 50px;
                text-decoration: none;
                display: inline-block;
                font-weight: bold;
                font-size: 18px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }}

            .trees {{ text-align: center; font-size: 30px; padding: 10px; margin-top: 20px; }}
            .footer {{ background-color: rgba(0, 0, 0, 0.3); padding: 15px; text-align: center; font-size: 12px; color: #ccc; }}
        </style>
    </head>
    <body>
        
        {view_browser_html}

        <div class="email-container">
            <!-- Header -->
            <div class="header">
                <div class="logo">
                    <!-- CID LOGO ATTACHMENT -->
                    <img src="cid:company_logo" alt="Logo">
                </div>
                <div class="header-text">
                    <h1>The Secret Santa Game Has Begun!</h1>
                    <p>🎄 Ho Ho Ho! Let the festive fun begin! 🎄</p>
                </div>
            </div>

            <!-- Bells -->
            <div class="bells-container">
                <span>🔔</span> &nbsp;&nbsp;&nbsp; <span>🔔</span>
            </div>
            
            <div class="content">
                <h2 class="greeting">Hi {name}!</h2>
                
                <!-- DYNAMIC BODY CONTENT -->
                {body_content}
                
                <!-- BUTTON -->
                {button_html}
                
                <p style="font-size: 14px; opacity: 0.8; margin-top: 20px;">
                    Remember, the magic is in the mystery! Keep your identity secret. 🤫
                </p>
            </div>
            
            <!-- Trees -->
            <div class="trees">
                🌲 🎄 🌲 🎄 🌲
            </div>
            
            <div class="footer">
                <p>Sent with holiday cheer by <strong>Secret Santa Mail Services</strong></p>
                <p>© 2025 Acies Global. All rights reserved.</p>
            </div>
        </div>
        <!-- Note: Scripts are usually blocked by email clients, removed to keep email clean -->
    </body>
    </html>
    """
    return html
