# Copyright (C) 2026  Anas S. Alotaibi (alotaibi811@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any later version.

import requests,time,re
from datetime import datetime, timezone, timedelta
from ratelimit import limits,sleep_and_retry

# --- Vars ---
end_time = int(time.time() * 1000)  # Current time in epoch ms
start_time = end_time - ((60 * 60 * 1000) *12)  # 12 hour ago
DNAC_URL = "https://CatalystCenter.local" #set IP or domain for DNAC/Catalyst Center
DNAC_USERNAME = "admin" #Valid Cred for Catalyst Center (Read only user is Enough)
DNAC_PASSWORD = "password" # Pass for aforementioned user

# Disable warnings for unverified HTTPS requests
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

def authenticate():
    """Authenticate to Cisco DNA Center and return the token."""
    auth_url = f"{DNAC_URL}/dna/system/api/v1/auth/token"
    response = requests.post(auth_url, auth=(DNAC_USERNAME, DNAC_PASSWORD), verify=False)
    
    if response.status_code == 200:
        return response.json()['Token']
    else:
        raise Exception(f"Failed to authenticate: {response.status_code} {response.content}")
@sleep_and_retry
@limits(calls=100,period=60)
def get_client_details(token, ip_address):
    """Get client details from Cisco DNA Center."""
    client_url = f"{DNAC_URL}/dna/data/api/v1/clients?ipv4Address={ip_address}"
    headers = {
        "x-auth-token": f"{token}",
        "Content-Type": "application/json"
    }
    response = requests.get(client_url, headers=headers, verify=False)
    
    if "API rate limit" in str(response.content): # Built before decoration by ratelimit library (DNAC Default API requests' limit per 1min is 100 requests)
        print(f"\n\n ##################({ip_address})################Mandatory Break!!! \n\n")
        time.sleep(45)
        get_client_details(token, ip_address)
    return response.json()

@sleep_and_retry
@limits(calls=100,period=60)    
def get_client_details2(token, ip_address):
    """Get client details from Cisco DNA Center."""
    normalized_mac= re.sub(r'[^0-9A-Fa-f]', '', ip_address) ## api needs mac in format: aa:AA:aa:AA:aa:aa
    mac=':'.join(normalized_mac[i:i+2] for i in range(0, 12, 2)).lower()

    client_url = f"{DNAC_URL}/dna/data/api/v1/clients?macAddress={mac}"
    headers = {
        "x-auth-token": f"{token}",
        "Content-Type": "application/json"
    }
    response = requests.get(client_url, headers=headers, verify=False)
    if "API rate limit" in str(response.content): # Built before decoration by ratelimit library (DNAC Default API requests' limit per 1min is 100 requests)
        print(f"\n\n ##################({ip_address})################Mandatory Break!!! \n\n")
        time.sleep(45)
        get_client_details2(token, ip_address)
    
    return response.json()    
@sleep_and_retry
@limits(calls=100,period=60)    
def get_client_details3(token, mac_address):
    """Get client details from Cisco DNA Center."""
    client_url = f"{DNAC_URL}/api/assurance/v1/events/view?entityId={mac_address}&offset=0&limit=1&entityType=wired_client&startTime={start_time}&endTime={end_time}&order=desc"
    headers = {
        "x-auth-token": f"{token}",
        "Content-Type": "application/json"
    }
    response = requests.get(client_url, headers=headers, verify=False)

    if "API rate limit" in str(response.content): # Built before decoration by ratelimit library (DNAC Default API requests' limit per 1min is 100 requests)
        print(f"\n\n ##################({ip_address})################Mandatory Break!!! \n\n")
        time.sleep(60)
        get_client_details3(token, ip_address)
    
    
    return response.json()


def mymain(ip): ## Sorry am getting messy since this value can work for both IP and Mac Addresses based on match from Regular Expression
    
    try:
        # Authenticate and fetch the token
        token = authenticate()
        # Get client details
        for x in ip:

            if re.search(r"^[0-9]{,3}\.[0-9]{,3}\.[0-9]{,3}\.[0-9]{,3}$",x):
                client_details = get_client_details(token, x)

            else:
                client_details = get_client_details2(token, x)

            if not client_details or len(client_details.get('response')) == 0: 
                print("\n" + "following couldn't be retrieve: " + str(x) + "\n")
                yield f"<br><b>[-] No data has been found for {x}</b><br>"
                continue
            
            #check client
            devType = client_details.get('response')[0].get("deviceType") or 'N/F'
            devForm= client_details.get('response')[0].get("formFactor") or 'N/F'
            clientConnection = client_details.get("response")[0].get("connectedNetworkDevice").get("connectedNetworkDeviceName") or 'N/F'
            swIP = client_details.get("response")[0].get("connectedNetworkDevice").get("connectedNetworkDeviceManagementIp") or 'N/F'
            connectionStatus = client_details.get("response")[0].get("connectionStatus") or 'N/F'
            dVlan = client_details.get("response")[0].get("connection").get("vlanId") or 'N/F'
            dPort = client_details.get("response")[0].get("connectedNetworkDevice").get("interfaceName") or 'N/F'
            dVendor = client_details.get("response")[0].get("vendor") or 'N/F'
            dIP= client_details.get("response")[0].get("ipv4Address") or 'N/F'
            mac=client_details.get("response")[0].get("macAddress") or 'N/F'
            conType = client_details.get("response")[0].get("type") or 'N/F'
            hostName= client_details.get("response")[0].get("username") or 'N/F'
            netType= client_details.get('response')[0].get('connectedNetworkDevice').get('connectedNetworkDeviceType') or 'N/F'
            client_details3 = get_client_details3(token, mac)
            #check authentication of client
            if not client_details3 or len(client_details3) == 2:
                yield f"<br><br>Device MAC: {mac}<br>Device IP: {dIP}<br>Device Type: {devType} ## {devForm}<br>Wired/Wireless: {conType}<br>Host Name: {hostName}<br>Device status: {connectionStatus}<br>Device Vendor: {dVendor}<br>Device Vlan Num: {dVlan}<br>Location: {clientConnection}<br>Interface Num: {dPort}<br>Network Device IP: {swIP} ## {netType}"
            else:   
                q1=re.search("[0-9]{5,}",client_details3.get("response")[0]["name"])
                timeE=int(q1.group())/1000
                timeF=datetime.fromtimestamp(timeE,tz=timezone(timedelta(hours=3)))
                nameF=re.sub("[0-9]{5,}",timeF.strftime("%Y-%m-%d %H:%M:%S"),client_details3.get("response")[0]["name"])
                auth_stat= nameF + " (" + client_details3.get("response")[0]["details"][2]["value"] or 'N/A' + "|" + client_details3.get("response")[0]["details"][1]["value"] or 'N/A' +"|"+ client_details3.get("response")[0]["details"][3]["value"] or 'N/A' +") "
                if  'FAIL' in client_details3.get("response")[0]["details"][1]["value"]:
                    auth=client_details3.get("response")[0]["details"][2]["value"] or 'N/A'
                else:
                    auth=client_details3.get("response")[0]["details"][3]["value"] or 'N/A'
                v1=client_details3.get("response")[0]["details"][1]["value"] or 'N/A'
                yield f"<br><br>Device MAC: {mac}<br>Device IP: {dIP}<br>Device Type: {devType} ## {devForm}<br>Wired/Wireless: {conType}<br>Host Name: {hostName}<br>Device status: {connectionStatus}<br>Device Vendor: {dVendor}<br>Device Vlan Num: {dVlan}<br>Location: {clientConnection}<br>Interface Num: {dPort}<br>Network Device IP: {swIP} ## {netType}<br>Authentication Status: {auth_stat} ## {auth} ## {v1}"
                
            
            
            
            
            
            
            
            
           
    except Exception as e:
        print(str(e))