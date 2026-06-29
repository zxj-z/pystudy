import requests

import json
import os
import time
from urllib.parse import unquote

# ========== 配置 ==========
BASE_URL = "https://apps.game.qq.com/cgi-bin/ams/module/ishow/V1.0/query/workList_inc.cgi"
ACTIVITY_ID = 2735
PAGE_SIZE = 20  # 每页数量
SAVE_DIR = "wangzhe_skins"  # 保存目录
DOWNLOAD_IMAGES = True  # 是否下载图片

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://apps.game.qq.com/",
}

# 基础参数
BASE_PARAMS = {
    "activityId": ACTIVITY_ID,
    "sVerifyCode": "ABCD",
    "sDataType": "JSON",
    "iListNum": PAGE_SIZE,
    "totalpage": 0,
    "iOrder": 0,
    "iSortNumClose": 1,
    "iAMSActivityId": 51991,
    "_everyRead": "true",
    "iTypeId": 2,
    "iFlowId": 267733,
    "iActId": ACTIVITY_ID,
    "iModuleId": ACTIVITY_ID,
}


def get_page(page_num):
    """获取单页数据"""
    params = BASE_PARAMS.copy()
    params["page"] = page_num

    try:
        response = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"请求第 {page_num} 页失败: {e}")
        return None


def decode_item(item):
    """解码商品数据中的URL编码字段"""
    decoded = {}
    for key, value in item.items():
        if isinstance(value, str) and ("%" in value):
            try:
                decoded[key] = unquote(value)
            except:
                decoded[key] = value
        else:
            decoded[key] = value
    return decoded


def download_image(url, save_path):
    """下载单张图片"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return False


def main():
    # 创建保存目录
    os.makedirs(SAVE_DIR, exist_ok=True)
    if DOWNLOAD_IMAGES:
        os.makedirs(os.path.join(SAVE_DIR, "images"), exist_ok=True)

    all_skins = []

    # 先获取第一页，拿到总页数
    print("正在获取第一页数据...")
    first_page = get_page(0)
    if not first_page:
        print("获取第一页失败，退出")
        return

    total_pages = int(first_page["iTotalPages"])
    total_lines = int(first_page["iTotalLines"])
    print(f"总共 {total_lines} 个皮肤，{total_pages} 页")

    # 处理第一页
    for item in first_page["List"]:
        decoded = decode_item(item)
        all_skins.append(decoded)

    print(f"第 1 页完成，已获取 {len(all_skins)} 个")

    # 爬取剩余页面
    for page in range(11, total_pages):
        print(f"正在爬取第 {page + 1}/{total_pages} 页...")
        data = get_page(page)

        if not data or "List" not in data:
            print(f"第 {page + 1} 页数据为空，跳过")
            time.sleep(1)
            continue

        for item in data["List"]:
            decoded = decode_item(item)
            all_skins.append(decoded)

        print(f"第 {page + 1} 页完成，已获取 {len(all_skins)} 个")

        # 延时，避免请求太快被封
        time.sleep(0.5)

    # 保存数据到JSON
    json_path = os.path.join(SAVE_DIR, "skins_list.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_skins, f, ensure_ascii=False, indent=2)
    print(f"\n数据已保存到 {json_path}")

    # 下载图片
    if DOWNLOAD_IMAGES:
        print("\n开始下载图片...")
        for i, skin in enumerate(all_skins):
            skin_name = skin.get("sProdName", f"skin_{skin.get('iProdId', i)}")
            prod_id = skin.get("iProdId", str(i))

            # 创建皮肤目录
            skin_dir = os.path.join(SAVE_DIR, "images", f"{prod_id}_{skin_name}")
            os.makedirs(skin_dir, exist_ok=True)

            # 下载8张图
            for img_num in range(1, 9):
                img_key = f"sProdImgNo_{img_num}"
                if img_key in skin:
                    img_url = skin[img_key]
                    # 把缩略图地址换成原图
                    img_url = img_url.replace("/200", "/0")

                    img_name = f"{img_num}.jpg"
                    img_path = os.path.join(skin_dir, img_name)

                    if not os.path.exists(img_path):
                        download_image(img_url, img_path)
                        time.sleep(0.2)

            if (i + 1) % 10 == 0:
                print(f"已下载 {i + 1}/{len(all_skins)} 个皮肤的图片")

    print(f"\n全部完成！共爬取 {len(all_skins)} 个皮肤")


if __name__ == "__main__":
    main()

