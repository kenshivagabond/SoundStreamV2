import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


GMAIL_ADDRESS = "sae4.etude@gmail.com"
GMAIL_APP_PASSWORD = "oxwf psob zqyn gjgn"  

def send_reset_email(to_email, username, new_password):
    subject = " SoundStream - Réinitialisation de votre mot de passe"
    body = f"""
Bonjour {username},

Votre mot de passe SoundStream a été réinitialisé.

Votre nouveau mot de passe est : {new_password}

Connectez-vous ici : http://127.0.0.1:8000/login
Pensez à changer votre mot de passe après connexion.

— L'équipe SoundStream
"""
    msg = MIMEMultipart()
    msg['From'] = GMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
        print(f"Mail envoyé à {to_email}")
    except Exception as e:
        print(f"Erreur envoi mail : {e}")