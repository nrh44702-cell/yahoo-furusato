import requests
import csv
import os
from datetime import datetime, timezone, timedelta

# ========== Yahoo!ショッピング設定 ==========
# 後で取得するキー（今はダミー）
YAHOO_CLIENT_ID = "dmVyPTIwMjUwNyZpZD11akdBSk1GWVFzJmhhc2g9WlRabVlUVm1NV0UzTkRGaE5EVmpNZw"
AFFILIATE_ID = "3770335_892610495"

KEYWORDS = [
    "ふるさと納税 肉",
    "ふるさと納税 米",
    "ふるさと納税 ビール",
    "ふるさと納税 家電",
    "ふるさと納税 フルーツ"
]
OUTPUT_FILE = "affiliate_products.csv"
# ==========================================

def search_yahoo(keyword):
    url = "https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch"
    params = {
        "appid": YAHOO_CLIENT_ID,
        "affiliate_type": "vc",
        "affiliate_id": AFFILIATE_ID,
        "query": keyword,
        "hits": 5
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        print(f"APIレスポンス（{keyword}）: {response.status_code}")
        data = response.json()
    except Exception as e:
        print(f"エラー（{keyword}）: {e}")
        return []

    products = []
    for item in data.get("hits", []):
        name = item.get("name", "")
        price = item.get("price", 0)
        url_aff = item.get("url", "")
        products.append([name, price, url_aff])
    return products

# ===== メイン処理 =====
print("===== Yahoo!ショッピング アフィリエイト自動化 開始 =====")
all_products = []

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["カテゴリ", "商品名", "価格", "アフィリエイトURL"])

for kw in KEYWORDS:
    print(f"\n🔍 「{kw}」を検索中...")
    results = search_yahoo(kw)

    if results:
        all_products.append((kw, results))
        with open(OUTPUT_FILE, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            for name, price, url_aff in results:
                writer.writerow([kw, name, price, url_aff])
        print(f"✅ {kw}: {len(results)}件追加")
    else:
        print(f"⚠️ {kw}: 商品が見つかりませんでした")

# HTML生成（楽天のサイトとほぼ同じデザイン）
if all_products:
    print("\n📄 HTMLを生成しています...")
    html = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>毎日自動更新！Yahoo!おすすめふるさと納税</title>
<style>
    body { font-family: 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f9f9f9; }
    h1 { color: #ff6600; border-bottom: 3px solid #ff6600; padding-bottom: 10px; }
    h2 { color: #333; background: #fff; padding: 10px; border-left: 5px solid #ff6600; }
    .product { background: white; border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .product h3 { margin: 0 0 10px 0; }
    .price { color: #e74c3c; font-weight: bold; font-size: 1.2em; }
    .btn { display: inline-block; background: #ff6600; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px; }
    .btn:hover { background: #cc5500; }
    .footer { text-align: center; margin-top: 30px; padding: 20px; color: #777; font-size: 0.9em; }
</style>
</head>
<body>
<h1>🛒 【毎日自動更新】Yahoo!ふるさと納税のおすすめ返礼品！</h1>
<p>最終更新: <span id="update-time"></span></p>
<script>document.getElementById('update-time').textContent = new Date().toLocaleString('ja-JP');</script>
"""
    for kw, products in all_products:
        html += f"<h2>📌 {kw}のおすすめ</h2>"
        for name, price, url_aff in products:
            html += f"""
    <div class="product">
        <h3>{name}</h3>
        <p class="price">💰 {price}円</p>
        <a href="{url_aff}" target="_blank" rel="nofollow" class="btn">👉 Yahoo!で見てみる</a>
    </div>"""

    html += """
<div class="footer">
    <p>※ このページはPythonによって24時間ごとに自動更新されています。</p>
    <p>※ 価格や在庫は変動する可能性があります。最新情報はリンク先でご確認ください。</p>
</div>
</body>
</html>"""

    file_path = "index.html"
    with open(file_path, "w", encoding="utf-8-sig") as f:
        f.write(html)
    print(f"✅ HTMLを更新しました！（{len(KEYWORDS)}カテゴリ）")
else:
    print("\n⚠️ 商品が1件も取得できませんでした。")

print("\n===== スクリプト終了 =====")
