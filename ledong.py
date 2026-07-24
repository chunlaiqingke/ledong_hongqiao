import requests
import json

url = "https://stmember.styd.cn/v2/reserve/submit?"

headers = {
    "Host": "stmember.styd.cn",
    "Connection": "keep-alive",
    "client-timezone": "+0800",
    "brand-code": "n9Lk2rX52Nz",
    "xweb_xhr": "1",
    "shop-id": "3691365947604836",
    "theme-compatible": "1",
    "mina-version": "independent",
    "Content-Type": "application/json",
    "app-id": "mina",
    "wx-token": "gVIsckNTWFUCsktsrkI5HrDqcfLglTft",
    "Accept": "*/*",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://servicewechat.com/wx28e6b769802e5485/3/page-frame.html",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,  q=0.9",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/132.0.0.0 Safari/537.36 "
        "MicroMessenger/7.0.20.1781(0x6700143B) "
        "NetType/WIFI "
        "MiniProgramEnv/Windows "
        "WindowsWechat/WMPF "
        "WindowsWechat(0x63090a13) "
        "UnifiedPCWindowsWechat(0xf2541923) "
        "XWEB/19823"
    )
}

# cookies = {
#     "acw_tc": "76b20f7917813716813476352ee9a040256bf5f5acd73910263119f965270c"
# }

payload = {
    "schedule_id": 0,
    "coach_id": 0,
    "course_id": 0,
    "seat": [],
    "consume_type": "wechat",
    "consume_id": "wechat",
    "current_reservation_num": 1,
    "reserve_type": "venues",
    "remark": "",
    "venues_id": "3692708846239935",
    "venues_date": "2026/06/24",
    "venues_site_time": [
        {
            "site_id": 3692729935134806,
            "site_name": "1号场",
            "start_time": "18:00",
            "start_timestamp": 1782295200,
            "end_timestamp": 1782298800,
            "end_time": "19:00",
            "times": "1",
            "price": "130"
        }
    ],
    "activity_id": 0
}

response = requests.post(
    url,
    headers=headers,
    # cookies=cookies,
    data=json.dumps(payload),
    timeout=10000,
    verify=False
)

print("HTTP Status Code:", response.status_code)
print("Response JSON:")
print(response.json())