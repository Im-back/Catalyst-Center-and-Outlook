# Copyright (C) 2026  Anas S. Alotaibi (alotaibi811@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any later version.

import win32com.client as win32
import re
import time
from new777 import mymain ## I know my filename looks so bad but I like it!!

# --- Vars ---
TARGET_SUBJECT = "anas check ip"  # Set your target subject keyword
TARGET_SUBJECT2 = "anas check ip "
CC_EMAIL = ""      # Set your CC recipient
CHECK_INTERVAL = 15   # Polling interval in seconds && after sync 15 so total 30sec
allowed_domain="@Domain.name" #e.g. @mycompany.xxx
banner = """
    ==================================================
    AUTOMATION SCRIPT (Catalyst Center&Outlook Desktop)
                         v1.0.0
            Written on 2026 By Anas S. Alotaibi
    ==================================================
    """
def extract_ip(text):
    """
    Finds the first IPv4 address in the provided text.
    Matches standard IP format: 0.0.0.0 to 255.255.255.255 or any of the known 3 formats of MAC Address
    """
    #r"(?:Gi[0-9]+/[0-9]+/[0-9]+|Gi[0-9]+)
    ip_pattern = r'\b(?:[0-9A-Fa-f]{2}[\:\-]){5}[0-9A-Fa-f]{2}|(?:[0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}|[0-9]{,3}\.[0-9]{,3}\.[0-9]{,3}\.[0-9]{,3}'
    match = re.findall(ip_pattern, text)
    if match:
        return match
    return None


def process_unread_emails():
    #following are relevant enterprise's Exchange/outlook that used to apply schema URL and GUID of MIP/ Sensitivity label or custom MAPI
    #LABEL_GUID = "{x-x-x-x-x}"
    #schema_url = f"http://schemas.microsoft.com/mapi/string/{{x-x-x-x-x}}/Property_name"
    
    
    # Connect to Outlook Desktop app
    outlook = win32.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    namespace.SendAndReceive(True) #sync without pop up window
    time.sleep(15)
    inbox = namespace.GetDefaultFolder(6)  # 6 = Inbox
    tfolder=inbox.Folders["auto"] # I made sub-folder named auto under inbox
    # Filter for emails that are BOTH unread AND contain the target subject(anas check ip)
    # Note: Outlook Restrict query syntax uses SQL-style criteria
    query = f"[UnRead] = True AND ([Subject] = '{TARGET_SUBJECT}' OR [Subject] = '{TARGET_SUBJECT2}')"
    
    #messages = inbox.Items.Restrict(query)
    messages = tfolder.Items.Restrict(query)

    messages.sort("[ReceivedTime]",False) #checks from oldest to newest
    if messages.Count == 0:
        print("No matching unread emails found.")
        return

    print(f"Found {messages.Count} unread email(s) matching criteria.")

    for mail in list(messages):
        sender = mail.SenderEmailAddress.lower()
        subject = mail.Subject
        body = mail.Body
        
        ### ensure to reply domain emails only
        if mail.SenderEmailType == "EX":
            email_c= mail.Sender
            ex_email=email_c.GetExchangeUser()
            if not ex_email.PrimarySmtpAddress.lower().endswith(allowed_domain):
                print(f"\nSkipping since domain is not allowed {sender}\n")
                mail.Unread = False
                mail.Save()
                continue
        if mail.SenderEmailType == "SMTP":
            if not sender.endswith(allowed_domain):
                print(f"\nSkipping since domain is not allowed {sender}\n")
                mail.Unread = False
                mail.Save()
                continue
                
        print(f"\nProcessing email from: {sender} | Subject: {subject}")

        # Extract IP/MAC from body
        extracted_ip = extract_ip(body)

        if extracted_ip:
            print(f"Found IP Address: {extracted_ip}")
            #!!!!added
            result=mymain(extracted_ip)
            resf="<br>".join(result)
            #
            # 1. Create Reply object
            reply_mail = mail.Reply()  # Preserves thread history and auto-populates 'To'
            reply_mail.Subject = f"Auto-reply Checking IP/MAC addresses"
            #reply_mail.PropertyAccessor.SetProperty(schema_url, LABEL_GUID) refer to LABEL_GUID and LABEL_GUID above
            
            # 2. Add CC
            reply_mail.CC = CC_EMAIL

            # 3. Construct Body (reply_mail.Body retains the quoted original message)
            reply_body = f"""Hello...<br>{resf}<br><br>
            Bye!!"""
            reply_mail.HTMLBody = reply_body + reply_mail.HTMLBody

            # 4. Send Reply
            reply_mail.Send()
            print(f"Successfully replied to {sender} and CC'd {CC_EMAIL}.")

            # 5. Mark original email as read so it won't be processed again
            mail.UnRead = False
            mail.Save()

        else:
            #mail.UnRead = False
            #mail.Save()
            print("No IP/MAC address found in email body. Skipping reply.")


# --- Main Loop (Polling) ---
if __name__ == "__main__":
    print(banner)
    print(f"Starting email monitor... Checking every {CHECK_INTERVAL} seconds.")
    try:
        while True:
            process_unread_emails()
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")