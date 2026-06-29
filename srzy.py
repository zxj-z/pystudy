import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import re
from urllib.parse import urljoin

# ========== 配置 ==========
BASE_DOMAIN = "https://www.srzy.cn"
LIST_URL_TPL = "https://www.srzy.cn/news-list-tzgg-{page}.html"
OUTPUT_CSV = "上饶职业技术学院_通知公告全量.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://www.srzy.cn/",
    "Accept-Language": "zh-CN,zh;q=0.9"
}
MAX_RETRY = 3
DELAY = (1, 2.5)


def fetch(url: str):
    """带重试的通用请求"""
    for i in range(MAX_RETRY):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.encoding = "utf-8"
            if resp.status_code == 200:
                return resp.text
            print(f"状态码 {resp.status_code}，第{i + 1}次重试: {url}")
        except Exception as e:
            print(f"请求异常，第{i + 1}次重试: {url} | {str(e)[:50]}")
        time.sleep(random.uniform(*DELAY))
    print(f"请求最终失败: {url}")
    return None


def get_total_page(html: str) -> int:
    """提取总页数，兼容无空格、全角字符等格式"""
    # 宽松匹配：共XX条新闻 ... X页
    match = re.search(r"共\d+条新闻.*?(\d+)\s*页", html)
    if match:
        return int(match.group(1))
    # 兜底匹配：1/4页 格式
    match2 = re.search(r"\d+/(\d+)\s*页", html)
    if match2:
        return int(match2.group(1))
    print("⚠️ 未识别到总页数，默认爬取前5页")
    return 5


def parse_list_links(html: str) -> list:
    """从列表页提取所有新闻详情链接，兼容动态+静态路径"""
    soup = BeautifulSoup(html, "html.parser")
    result = []

    # 匹配规则1：动态详情页 c=show 格式（官网实际采用格式）
    # 匹配规则2：静态 news-detail / news-show 格式（兼容伪静态）
    selectors = [
        'a[href*="c=show"]',
        'a[href*="news-detail"]',
        'a[href*="news-show"]'
    ]

    for sel in selectors:
        for a in soup.select(sel):
            href = a["href"].strip()
            title = a.get_text(strip=True)
            # 过滤空标题、过短标题、分页/导航链接
            if not title or len(title) < 6:
                continue
            # 排除分页相关链接
            if any(key in title for key in ["首页", "上一页", "下一页", "末页", "跳转到"]):
                continue
            detail_url = urljoin(BASE_DOMAIN, href)
            result.append({
                "标题": title,
                "详情链接": detail_url,
                "发布日期": "",
                "正文内容": ""
            })

    # 去重（按链接去重）
    unique = []
    seen = set()
    for item in result:
        if item["详情链接"] not in seen:
            seen.add(item["详情链接"])
            unique.append(item)
    return unique


def parse_detail(html: str) -> dict:
    """解析详情页：提取发布日期和正文"""
    if not html:
        return {"date": "", "content": ""}
    soup = BeautifulSoup(html, "html.parser")

    # 提取发布日期
    date_text = ""
    date_pattern = re.compile(r"发布时间[：:]\s*(\d{4}-\d{2}-\d{2})")
    page_text = soup.get_text()
    date_match = date_pattern.search(page_text)
    if date_match:
        date_text = date_match.group(1)
    else:
        # 兜底：匹配 20xx-xx-xx 格式日期
        date_match2 = re.search(r"(\d{4}-\d{2}-\d{2})", page_text)
        if date_match2:
            date_text = date_match2.group(1)

    # 提取正文：依次尝试常见正文容器
    content = ""
    for selector in [
        ".news-content", ".article-content",
        ".content", ".detail", "article",
        ".show-content", ".news-detail"
    ]:
        node = soup.select_one(selector)
        if node and len(node.get_text(strip=True)) > 50:
            content = node.get_text(strip=True, separator="\n")
            break

    # 终极兜底：移除多余标签后提取主体文本
    if not content:
        for tag in soup.select("script, style, nav, footer, header, .menu, .page, .pagination"):
            tag.decompose()
        content = soup.get_text(strip=True, separator="\n")

    return {"date": date_text, "content": content}


def main():
    print("=" * 50)
    print("上饶职业技术学院 - 通知公告全量爬取（适配修复版）")
    print("=" * 50)

    # 1. 获取总页数
    first_html = fetch(LIST_URL_TPL.format(page=1))
    if not first_html:
        print("❌ 首页请求失败，请检查网络或URL是否正确")
        return
    total_page = get_total_page(first_html)
    print(f"✅ 识别到总页数：{total_page} 页")

    # 调试：打印第一页匹配到的链接数
    first_items = parse_list_links(first_html)
    print(f"✅ 第一页匹配到 {len(first_items)} 条新闻链接\n")
    if len(first_items) == 0:
        print("❌ 第一页未匹配到任何链接，程序退出")
        return

    # 2. 爬取所有列表页
    all_items = first_items
    print(f"第 1 / {total_page} 页完成，累计 {len(all_items)} 条")

    for page in range(2, total_page + 1):
        html = fetch(LIST_URL_TPL.format(page=page))
        if not html:
            continue
        page_items = parse_list_links(html)
        all_items.extend(page_items)
        print(f"第 {page} / {total_page} 页完成，累计 {len(all_items)} 条")
        time.sleep(random.uniform(*DELAY))

    # 全局去重
    all_items = list({item["详情链接"]: item for item in all_items}.values())
    print(f"\n📌 去重后共 {len(all_items)} 条新闻，开始爬取详情正文...\n")

    # 3. 批量爬取详情页
    for idx, item in enumerate(all_items, 1):
        if idx % 10 == 0:
            print(f"详情进度：{idx} / {len(all_items)}")
        detail_html = fetch(item["详情链接"])
        detail_info = parse_detail(detail_html)
        item["发布日期"] = detail_info["date"]
        item["正文内容"] = detail_info["content"]
        time.sleep(random.uniform(*DELAY))

    # 4. 保存CSV
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["发布日期", "标题", "详情链接", "正文内容"])
        writer.writeheader()
        writer.writerows(all_items)

    print("\n" + "=" * 50)
    print(f"🎉 爬取完成，共获取 {len(all_items)} 条数据")
    print(f"文件已保存为：{OUTPUT_CSV}")
    print("=" * 50)


if __name__ == "__main__":
    main()