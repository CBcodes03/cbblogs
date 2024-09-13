def genotp():
    import math
    import random
    digits="0123456789"
    otp=""
    for i in range(6):
        otp+=digits[math.floor(random.random()*10)]
    return otp
def send_vmail(otp, emailid):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    # Create the email message
    message = MIMEMultipart()
    message['From'] = 'cbblogs58@gmail.com'
    message['To'] = emailid
    message['Subject'] = 'Verification'
    message.attach(MIMEText(f'OTP is: {otp}', 'plain'))

    # Set up the SMTP server
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.set_debuglevel(1)
    s.starttls()
    s.login("cbblogs58@gmail.com", "orhn nagd xhpc swsq")

    # Send the email
    s.sendmail(from_addr="cbblogs58@gmail.com", to_addrs=emailid, msg=message.as_string())
    s.quit()
    return None
def new_post_notify(link):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import sqlite3
    #fetch user emails
    conn = sqlite3.connect('cbblogs.db')
    cursor = conn.cursor()
    query = "SELECT email FROM users"
    cursor.execute(query)
    emails=[str(row[0]) for row in cursor.fetchall()]
    conn.commit()
    conn.close()
    # Create the email message
    for i in emails:
        message = MIMEMultipart()
        message['From'] = 'cbblogs58@gmail.com'
        message['To'] = f"{i}"
        message['Subject'] = 'NEW POST'
        message.attach(MIMEText(f'check out this new post on cbblogs {link}', 'plain'))

        # Set up the SMTP server
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.set_debuglevel(1)
        s.starttls()
        s.login("cbblogs58@gmail.com", "orhn nagd xhpc swsq")

        # Send the email
        s.sendmail(from_addr="cbblogs58@gmail.com", to_addrs={i}, msg=message.as_string())
        s.quit()
    return None
