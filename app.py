from flask import Flask, jsonify
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

app = Flask(__name__)

URL = "https://developer.android.com/build/releases/gradle-plugin"

def parse_tables_from_html(html):
    """
    使用 BeautifulSoup 解析 HTML，
    返回一个列表，每个元素代表一个表格数据(二维数组).
    """
    soup = BeautifulSoup(html, "html.parser")
    table_wrappers = soup.find_all("div", class_="devsite-table-wrapper")
    results = []
    for div in table_wrappers:
        table_tag = div.find("table")
        if not table_tag:
            continue
        all_rows = []
        for tr in table_tag.find_all("tr"):
            row_data = []
            cells = tr.find_all(["th", "td"])
            for c in cells:
                row_data.append(c.get_text(strip=True))
            if row_data:
                all_rows.append(row_data)
        if all_rows:
            results.append(all_rows)
    return results

async def fetch_html():
    """
    使用 Playwright 抓取页面，并等待表格加载完成。
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL)
        # 等待页面中包含表格的 div 加载完毕
        await page.wait_for_selector("div.devsite-table-wrapper", timeout=10000)
        html = await page.content()
        await browser.close()
    return html

async def fetch_and_parse():
    html = await fetch_html()
    tables = parse_tables_from_html(html)
    return tables

# 全局缓存，防止每次请求都重新抓取
TABLES_CACHE = None

@app.route("/")
def index():
    return "Playwright + Flask Demo: /count 或 /table/<idx>"

@app.route("/count")
def get_count():
    global TABLES_CACHE
    if TABLES_CACHE is None:
        TABLES_CACHE = asyncio.run(fetch_and_parse())
    return jsonify({
        "table_count": len(TABLES_CACHE)
    })

@app.route("/table/<int:idx>")
def get_table(idx):
    global TABLES_CACHE
    if TABLES_CACHE is None:
        TABLES_CACHE = asyncio.run(fetch_and_parse())
    if idx < 0 or idx >= len(TABLES_CACHE):
        return jsonify({
            "error": f"invalid table index {idx}, total {len(TABLES_CACHE)}"
        }), 404
    return jsonify({
        "table_index": idx,
        "rows": TABLES_CACHE[idx]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)