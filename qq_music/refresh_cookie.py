import argparse
import json
import requests

from util.bark import send_bark_notification

def print_response(response: requests.Response) -> None:
    """Prints the response status and content in a readable format."""
    print("Status Code:", response.status_code)
    try:
        print("Response JSON:\n", response.json())
    except ValueError:
        print("Raw Response:\n", response.text)

def claim_points(key, uin) -> None:
    """Main function to send a POST request to the QQ Music API."""
    url = (
        "https://u6.y.qq.com/cgi-bin/musics.fcg"
        "?_webcgikey=EveryDaySignLvzScore"
        "&_=1746607488509"
        "&sign=zzc32bd12fispgjhvch9sp1b4lwmt2al0pnq1882f9a3"
    )

    headers = {
        "Host": "u6.y.qq.com",
        "Cookie": (
            f"qm_keyst={key}; "
            f"uin=o0{uin}; "
        ),
        "content-type": "application/x-www-form-urlencoded",
        "accept": "application/json",
        "sec-fetch-site": "same-site",
        "accept-language": "en-US,en;q=0.9",
        "sec-fetch-mode": "cors",
        "origin": "https://i2.y.qq.com",
        "user-agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 18_4_1 like Mac OS X) "
            "AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12A365 QQMusic/14.4.0 "
            "Mskin/black Mcolor/00cc6cff Bcolor/00000000 skinid[901] NetType/WIFI "
            "WebView/WKWebView Released[1] en-US DeviceModel/iPhone16,2 "
            "skin_css/skin2_1_901 Pixel/1290 FreeFlow/0 teenMode/0 "
            "nft_released/[1] ui_mode/1 model130200/1 FontMode/0]  "
            "IAP[0]  H5/1  TMEXRay/09a6de87b9ebae2abd4e8c77f4533586:54c34c78c02d1262:1  "
            "QBWebViewType/1 WKType/1"
        ),
        "referer": "https://i2.y.qq.com/",
        "sec-fetch-dest": "empty",
        "Accept-Encoding": "deflate, gzip"
    }

    raw_data = (
        '{"comm":{'
        '"g_tk":401248577,'
        f'"uin":{uin},'
        '"format":"json",'
        '"inCharset":"utf-8",'
        '"outCharset":"utf-8",'
        '"notice":0,'
        '"platform":"h5",'
        '"needNewCode":1,'
        '"ct":23,'
        '"cv":0,'
        '"traceid":"296bfe8f04a5c908dec0dae891a52b92:acb4b16c30cdd782:0:0"'
        '},'
        '"req_0":{'
        '"module":"music.lvz.MuFest13TaskSvr",'
        '"method":"EveryDaySignLvzScore",'
        '"param":{"Uin":"' + str(uin) +'","Cmd":"get"}'
        '}}'
    )
    response = requests.post(url, headers=headers, data=raw_data)
    # print_response(response)
    response.raise_for_status()
    result = response.json()
    if result['code'] != 0:
        raise RuntimeError("签到失败，响应：" + json.dumps(result, ensure_ascii=False))
    else:
        reward_points = result["req_0"]["data"]["Total"]
        msg = result["req_0"]["data"]["Msg"] or "N/A"
        if msg or int(reward_points) <= 0:
            push_msg = f"签到成功, 获得 {reward_points} 积分。消息：{msg}"
        else:
            push_msg = f"签到成功, 获得 {reward_points} 积分。"
        print(push_msg)
        send_bark_notification(title='QQMusic Claim Rewards', body=push_msg, group_name='QQMusic')

def refresh_cookies(qm_keyst: str, uin, sign: str) -> None:
    # 1. Prepare request data
    data = {
        "req1":{
            "module":"QQConnectLogin.LoginServer",
            "method":"QQLogin",
            "param":{
                "musicid":uin,
                "musickey":qm_keyst
            }
        }
    }
    # 2. Prepare requests
    base = "https://u6.y.qq.com/cgi-bin/musics.fcg"
    params = {
        "sign": sign,
        "format": "json",
        "inCharset": "utf8",
        "outCharset": "utf-8",
        "data": json.dumps(data,separators=(',', ':'))
    }
    resp = requests.get(base, params=params)
    resp.raise_for_status()
    result = resp.json()
    if result['code'] != 0:
        raise RuntimeError("刷新失败，响应：" + json.dumps(result, ensure_ascii=False))
    else:
        print("刷新成功")
        new_key = result["req1"]["data"]["musickey"]
        return new_key

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", required=True, help="qm_keyst")
    parser.add_argument("--uin", type=int, required=True, help="uin")
    parser.add_argument("--sign", required=True, help="sign")
    args = parser.parse_args()

    try:
        new_key = refresh_cookies(args.key, args.uin, args.sign)
        
        with open(".cookie", "w") as f:
            f.write(new_key)
        
        claim_points(new_key, uin=args.uin)
    except Exception as e:
        err_msg = str(e)
        print(f"Error occurred: {err_msg}")
        send_bark_notification(title='QQMusic', body=f'签到失败。\nError occurred: {err_msg}', group_name='QQMusic')
        raise
