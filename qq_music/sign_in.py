import requests
import os
import json

import time
from .zzc_sign import zzc_sign
from util.bark import send_bark_notification

def current_millis_str() -> str:
    ms = int(time.time() * 1000)
    return str(ms).zfill(13)

MUSIC_KEY = os.getenv("MUSIC_KEY")
MUSIC_UIN = os.getenv("MUSIC_UIN")
headers = {
    "Host": "u6.y.qq.com",
    "Cookie": f"qm_keyst={MUSIC_KEY}; uin=o0{str(MUSIC_UIN)}",
    "content-type": "application/x-www-form-urlencoded",
    "accept": "application/json",
    "sec-fetch-site": "same-site",
    "accept-language": "en-US,en;q=0.9",
    "sec-fetch-mode": "cors",
    "origin": "https://i2.y.qq.com",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12A365 QQMusic/14.4.0 Mskin/black Mcolor/00cc6cff Bcolor/00000000 skinid[901] NetType/WIFI WebView/WKWebView Released[1] en-US DeviceModel/iPhone16,2 skin_css/skin2_1_901 Pixel/1290 FreeFlow/0 teenMode/0 nft_released/[1] ui_mode/1 model130200/1 FontMode/0]  IAP[0]  H5/1",
    "referer": "https://i2.y.qq.com/",
    "sec-fetch-dest": "empty",
}

def get_task():
    data = {"comm":{"g_tk":929272714,"uin":MUSIC_UIN,"format":"json","inCharset":"utf-8","outCharset":"utf-8","notice":0,"platform":"h5","needNewCode":1,"ct":23,"cv":0,"mesh_devops":"DevopsBase"},"req_0":{"module":"music.actCenter.ActCenterSignNewSvr","method":"GetSignInSummary","param":{"ActID":"Z25hHGi"}},"req_1":{"module":"music.actCenter.ActCenterSignNewSvr","method":"GetSignInTaskList","param":{"ActID":"Z25hHGi","ScenesID":"3"}},"req_2":{"module":"music.actCenter.ActCenterSignNewSvr","method":"GetSignInCalendar","param":{"ActID":"Z25hHGi"}}}
    data = json.dumps(data, separators=(',', ':'))
    url = f"https://u6.y.qq.com/cgi-bin/musics.fcg?_webcgikey=GetSignInSummary_GetSignInTaskList_GetSignInCalendar&_={current_millis_str()}&sign={zzc_sign(data)}"
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    response_json = response.json()
    daily_tasks = response_json["req_1"]["data"]["TaskListInfo"]["TaskList"]["ContinueTaskList"]
    pending_task_ids = []
    today_task_id = ""
    for idx, task in daily_tasks.items():
        task_id = task["ID"]
        task_name = task["Name"]
        task_status = task["State"]
        if task_status != 1:
            pending_task_ids.append(task_id)
        if task_status == 2:
            today_task_id = task_id
        print(f"Task {str(idx)}: {task_name} (ID: {task_id}, Status: {str(task_status)})")
    return today_task_id

def award_price(task_id):
    if not task_id:
        print("No pending award found for today.")
        return
    data = {"comm":{"g_tk":929272714,"uin":MUSIC_UIN,"format":"json","inCharset":"utf-8","outCharset":"utf-8","notice":0,"platform":"h5","needNewCode":1,"ct":23,"cv":0,"mesh_devops":"DevopsAccSignIn"},"req_0":{"module":"music.actCenter.ActCenterSignNewSvr","method":"AwardPrize","param":{"ActID":"Z25hHGi","TaskID":f"{task_id}"}}}
    data = json.dumps(data, separators=(',', ':'))
    url = f"https://u6.y.qq.com/cgi-bin/musics.fcg?_webcgikey=AwardPrize&_={current_millis_str}&sign={zzc_sign(data)}"
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    response_json = response.json()
    print(f"Response：{response_json}")

def sign_in():
    data = {"comm":{"g_tk":929272714,"uin":MUSIC_UIN,"format":"json","inCharset":"utf-8","outCharset":"utf-8","notice":0,"platform":"h5","needNewCode":1,"ct":23,"cv":0,"mesh_devops":"DevopsBase"},"req_0":{"module":"music.actCenter.ActCenterSignNewSvr","method":"SignIn","param":{"ActID":"Z25hHGi","ScenesID":"3"}}}
    data = json.dumps(data, separators=(',', ':'))
    url = f"https://u6.y.qq.com/cgi-bin/musics.fcg?_webcgikey=SignIn&_={current_millis_str}&sign={zzc_sign(data)}"
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    response_json = response.json()
    print(f"Response：{response_json}")
    if response_json.get("req_0", {}).get("data", {}).get("Info").get("IsSignIn") == 1:
        send_bark_notification(title='QQMusic Daily Signin', body=f'Successfully Signin! Monly Signin Count:{response_json["req_0"]["data"]["Info"]["MonthSignInCount"]} Days', group_name='QQMusic')

sign_in()
today_task_id = get_task()
award_price(today_task_id)