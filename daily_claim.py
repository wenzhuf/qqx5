import requests
import random
import os
from datetime import datetime, timedelta

# Access secrets through environment variables
openid = os.getenv('OPENID')  # Use environment variable for openid
access_token = os.getenv('ACCESS_TOKEN')  # Use environment variable for access_token
appid = os.getenv('APPID')  # Use environment variable for appid

# Helper function to generate eas_sid
def generate_eas_sid():
    e = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    n = len(e)
    r = ""
    o = str(int(datetime.now().timestamp() * 1000))  # Get current time in milliseconds
    
    # Generate the SID with random characters and the timestamp
    for i in range(13):
        d = random.randint(0, n - 1)
        r += e[d] + o[i % len(o)]
    
    return r

# Helper function to get today's weekday number (2 for Tuesday)
def get_weekday_number():
    # Get the current UTC time
    now_utc = datetime.utcnow()
    
    # Manually adjust the UTC time to China Standard Time (UTC +8)
    china_time = now_utc + timedelta(hours=8)
    
    # Get the weekday (0=Monday, 6=Sunday)
    weekday_number = china_time.weekday()
    
    # Return the weekday in China (1=Monday, 7=Sunday)
    return weekday_number + 1

# The main function to send the request and handle the response
def send_request():
    # Prepare the headers
    eas_sid = generate_eas_sid()
    week_num = get_weekday_number()
    
    headers = {
        "Host": "comm.ams.game.qq.com",
        "Cookie": f"eas_sid={eas_sid}; refresh_token=; expires_time=; acctype=qc; openid={openid}; access_token={access_token}; appid={appid}; ieg_ams_token=; ieg_ams_session_token=; ieg_ams_token_time=; ieg_ams_sign=",
        "accept": "application/json, text/plain, */*",
        "user-agent": "Mozilla/5.0 (Linux; Android 9; SM-S908E Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.129 Safari/537.36;GameHelper",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://zsxw.qq.com",
        "x-requested-with": "com.tencent.qqxwandroid",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://zsxw.qq.com/",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    # Prepare the data for the POST request
    data = {
        "iChartId": 375145,
        "iSubChartId": 375145,
        "sIdeToken": "5PgbU2",
        "e_code": "0",
        "g_code": "0",
        "eas_url": "http%253A%252F%252Fzsxw.qq.com%252Fcp%252Fa20241219community%252Fsignin-x5.html",
        "eas_refer": "http%253A%252F%252Fnoreferrer%252F%253Freqid%253Dbf8b3a63-4733-407c-893c-29ea7826644a%2526version%253D27",
        "sMiloTag": "AMS-zsxw-0506013156-s1aZqs-704046-1110445",
        "weekNum": week_num,
        "sArea": 195
    }

    # Send the request
    url = "https://comm.ams.game.qq.com/ide/"
    response = requests.post(url, headers=headers, data=data)
    
    # Decode the response
    response_json = response.json()
    ret = response_json.get("ret")
    iRet = response_json.get("iRet")
    sMsg = response_json.get("sMsg")
    jData = response_json.get("jData", {})
    sAmsSerial = response_json.get("sAmsSerial")

    # Print the decoded message
    print(f"Main Message: {sMsg}")
    print(f"AMS Serial: {sAmsSerial}")
    print(f"Error Code: {ret}")
    
    # Check if the user has already claimed the prize
    if ret == 40002:
        print("Error: The prize has already been claimed by the user.")
    
    # Print detailed jData message if available
    if jData.get("sMsg"):
        print(f"Additional Message from jData: {jData['sMsg']}")

# Run the function to send the request
send_request()
