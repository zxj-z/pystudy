import execjs
import requests
import time
import random
import pandas as pd
from urllib.parse import urlencode


# ====================== 配置区 ======================
# 1. 读取你的签名JS文件
with open("1.js", "r", encoding="utf-8") as f:
    js_code = f.read()
ctx = execjs.compile(js_code)

# 2. 接口基础地址
BASE_URL = "https://api.qimai.cn/rank/index"

# 3. 榜单筛选参数
# brand: free=免费榜 / paid=付费榜 / gross=畅销榜
# device: iphone / ipad
# country: cn=中国 / us=美国 等
# genre: 36=应用总榜 / 6014=游戏总榜，其他分类自行抓包替换
QUERY_PARAMS = {
    "brand": "paid",
    "device": "iphone",
    "country": "cn",
    "genre": "36",
    "date": "",  # 空字符串为实时榜单
    "page": 1
}

# 4. 请求头（建议替换为你自己浏览器的User-Agent和Cookie）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://www.qimai.cn/rank",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 5. 爬取前100名，共5页（每页20条）
TOTAL_PAGE = 5
# ===================================================


def get_signature(params: dict) -> str:
    """
    调用1.js生成analysis签名
    注意：请根据你1.js里的实际函数名、入参修改此处调用方式
    示例默认函数名为 getAnalysis，入参为接口路径 + 参数字典
    """
    api_path = "/rank/index"
    # 如果你的JS函数只需要参数字符串，可改为 urlencode(params)
    analysis = ctx.call("getAnalysis", api_path, params)
    return analysis


def crawl_one_page(page: int) -> list:
    """爬取单页榜单数据"""
    params = QUERY_PARAMS.copy()
    params["page"] = page

    # 生成签名
    params["analysis"] = get_signature(params)

    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # 解析应用列表（根据实际返回结构调整字段）
        app_list = []
        rank_info = data.get("rankInfo", [])
        for item in rank_info:
            app_info = item.get("appInfo", {})
            app_list.append({
                "排名": item.get("index"),
                "应用名称": app_info.get("appName"),
                "AppID": app_info.get("appId"),
                "开发商": app_info.get("publisher"),
                "分类": app_info.get("genre"),
                "图标": app_info.get("iconUrl"),
            })
        print(f"第 {page} 页爬取成功，获取 {len(app_list)} 条数据")
        return app_list

    except Exception as e:
        print(f"第 {page} 页爬取失败: {e}")
        return []


def main():
    all_apps = []
    for page in range(1, TOTAL_PAGE + 1):
        apps = crawl_one_page(page)
        all_apps.extend(apps)
        # 随机延时，降低被封风险
        time.sleep(random.uniform(1.5, 3))

    # 保存为CSV文件
    if all_apps:
        df = pd.DataFrame(all_apps)
        df.to_csv("七麦榜单前100.csv", index=False, encoding="utf-8-sig")
        print(f"\n爬取完成，共 {len(all_apps)} 条数据，已保存到 七麦榜单前100.csv")
    else:
        print("未获取到任何数据，请检查签名和接口是否正确")


if __name__ == "__main__":
    main()
var R=global
a=[
    3,
    "2026-06-26",
    "2026-06-26",
    "2026-06-26",
    "cn",
    "36",
    4,
    2
]

function p(t) {
                t = R["encodeURIComponent"](t)["replace"](/%([0-9A-F]{2})/g, function(n, t) {
                    return o("0x" + t)
                });
                try {
                    return R["btoa"](t)
                } catch (n) {
                    return R[W5][K5](t)[U5](Z5)
                }
            }
function o(n) {
                t = "",
                ['66', '72', '6f', '6d', '43', '68', '61', '72', '43', '6f', '64', '65']["forEach"](function(n) {
                    t += R["unescape"]("%u00" + n)
                });
                var t, e = t;
                return R["String"]["fromCharCode"](n)
            }
function h(n, t) {
                t = t || u();
                for (var e = (n = n["split"](""))["length"], r = t["length"], a = "charCodeAt", i = 0; i < e; i++)
                    n[i] = o(n[i][a](0) ^ t[(i + 10) % r][a](0));
                return n["join"]("")
            }

a = a["sort"]()["join"]("")
console.log(a)
a=p(a)
console.log(a)
r = +new R["Date"] - (1847 || 0) - 1661224081041
a = (a+= "@#" + "/rank/offline") + ("@#" + r) + ("@#" + 3)
console.log(a)
console.log(p(h(a, "xyz517cda96efgh")))



 function  getAnalysis(){
     console.log(p(h(a, "xyz517cda96efgh")))
     return p(h(a, "xyz517cda96efgh"))
 }
 getAnalysis()


























