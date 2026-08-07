Summary
scripts reads your Outlook Desktop Received Emails, find IP or MAC address in email body, Fetch Information for Client Connected from Cisco Catalyst Center then reply accordingly 
with following automated email:
#Start of auto generated email
```
Hello...


Device MAC: 3X:4X:50:70:2A:BB
Device IP: 192.168.100.1
Device Type: Dell-Device ## Workstation
Wired/Wireless: Wired
Host Name: USER01.COM
Device status: connected
Device Vendor: Dell Inc.
Device Vlan Num: 1
Location: SWITCH1-BRANCH-1
Interface Num: GigabitEthernet1/0/1
Network Device IP: 192.168.1.10 ## Switch
Authentication Status: Authentication Started_2026-08-07 01:33:00 (AUTH ## Client Authenticated - DOT1X ## STARTED

Bye!!
```
#End of Auto-generated email

Requirements:
[+] Catalyst Center reachable for the script with valid credentials(read-only is enough), set at new777.py file code: DNAC_URL, DNAC_USERNAME, and DNAC_PASSWORD
[+] logged in Outlook Desktop to read emails,
    [+] Script expect to read from sub-folder named: "auto" in inbox where received emails has subject name: "anas check ip" and in body any IP/s or MAC/s separated by new line/comma or and other means to be readable
    [+] you must set up the variable: allowed_domain in auto_email.py which used to restrict the response to specific domain, e.g. you enterprise domain-name
[+] Python requirements are to be installed used by cmd/terminal: pip install requests pywin32 ratelimit

To be done to start auto-reply emails:
1- python auto_email.py
2- Send to the email address for the machine that running the script with Outlook Desktop 
and wait less than a minute to receive your information obtained from Cisco Catalyst Center

