import hashlib
import time
import requests
import pandas as pd
import execjs













# ========== 请根据抓包结果修改以下配置 ==========
# ChainData榜单数据接口地址（浏览器F12抓包获取真实接口）
API_URL = "https://api.mytoken.info/ticker/currencyranklist"
# 请求头，模拟浏览器
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://mytokencap.com/en/",
    "Accept": "application/json, text/plain, */*"
}
# 抓取页数
TOTAL_PAGE = 10
# 每页条数（按站点实际值调整）
PAGE_SIZE = 50
# 分页参数名（抓包确认是page还是pageNum等）
PAGE_PARAM = "page"
PAGE_SIZE_PARAM = "pageSize"


# ==============================================

def generate_sign():
    """纯Python实现签名生成，对齐你的JS逻辑"""
    with open("my_token.js", encoding="utf-8") as f:
        js_code = f.read()
        js = execjs.compile(js_code)
        result = js.call("get_params")
    return result


def fetch_one_page(page_num):
    """抓取单页数据"""
    # 生成签名参数
    sign_params = generate_sign()
    # 构造完整请求参数
    params = {
        "pages": str(page_num)+'.1',
        "sizes": "100,100",
        "subject": "market_cap",
        "language": "en_US",
        "legal_currency": "USD",
        "code": str(sign_params['code']),
        "timestamp": str(sign_params['time']),
        "platform": "web_pc",
        "v": "0.1.0",
        "mytoken": ""
    }

    try:
        # 若接口是POST请求，改为 requests.post(API_URL, json=params, headers=HEADERS)
        resp = requests.post(API_URL, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        json_data = resp.json()

        # 【需根据实际返回结构调整】提取数据列表
        # 示例：返回格式为 {"code":0,"data":{"list":[...]}}
        data_list = json_data.get("data", {}).get("list", [])
        return data_list
    except Exception as e:
        print(f"第 {page_num} 页抓取失败: {e}")
        print(f"响应内容: {resp.text[:200]}")  # 打印前200字符方便排查
        return []


def main():
    all_data = []
    for page in range(1, TOTAL_PAGE + 1):
        print(f"正在抓取第 {page}/{TOTAL_PAGE} 页...")
        page_data = fetch_one_page(page)
        if page_data:
            all_data.extend(page_data)
            print(f"  本页获取 {len(page_data)} 条")
        # 控制请求频率，避免触发风控
        time.sleep(0.8)

    if not all_data:
        print("未抓取到任何数据，请检查接口地址、参数名和请求方式")
        return

    # 导出为Excel
    df = pd.DataFrame(all_data)
    output_file = "ChainData榜单前10页.xlsx"
    df.to_excel(output_file, index=False, engine="openpyxl")
    print(f"\n抓取完成！共获取 {len(all_data)} 条数据，已保存为 {output_file}")


if __name__ == "__main__":
    main()
