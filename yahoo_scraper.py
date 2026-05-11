import requests
import csv
import os
from datetime import datetime, timezone, timedelta

# ========== 設定 ==========
RAKUTEN_APP_ID = "d634ff2c-683e-4977-844d-858728677083"
RAKUTEN_ACCESS_KEY = "pk_JItpWHG4EyXJ6Evay9tKEjtIoF0qTsV8eDhq2iN3ZEG"
AFFILIATE_ID = "53a343b6.2b506472.53a343b7.7360f1be"
KEYWORDS = [
    "ふるさと納税 ランキング",
    "ふるさと納税 肉",
    "ふるさと納税 米",
    "ふるさと納税 ビール",
    "ふるさと納税 家電"
]
OUTPUT_FILE = "affiliate_products.csv"
# =========================

def search_rakuten(keyword):
    url = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20220601"
    params = {
        "applicationId": RAKUTEN_APP_ID,
        "accessKey": RAKUTEN_ACCESS_KEY,
        "affiliateId": AFFILIATE_ID,
        "keyword": keyword,
        "hits": 5,
        "format": "json"
    }
    session = requests.Session()
    session.headers.update({
        "Referer": "https://www.rakuten.co.jp/",
        "Origin": "https://www.rakuten.co.jp/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    try:
        response = session.get(url, params=params, timeout=15)
        response.raise_for_status()
        print(f"APIレスポンス（{keyword}）: {response.status_code}")
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"ネットワークエラー（{keyword}）: {e}")
        return []
    except ValueError:
        print(f"JSONの解析に失敗しました（{keyword}）。レスポンス: {response.text}")
        return []

    if "error" in data:
        print(f"APIエラー（{keyword}）: {data['error']} - {data.get('error_description', '')}")
        return []

    products = []
    for item in data.get("Items", []):
        product = item["Item"]
        name = product["itemName"]
        price = product["itemPrice"]
        url_aff = product.get("affiliateUrl", "")
        products.append([name, price, url_aff])
    return products

def deploy_to_netlify(file_path):
    NETLIFY_TOKEN = "nfp_B4wYo2kEwAgFfkK95NXDF1mk6jhv2eA3349c"
    SITE_ID = "8692aea2-b5cf-45e0-885d-56f2097a6f98"
    
    print("Netlifyデプロイを開始します...")
    url = f"https://api.netlify.com/api/v1/sites/{SITE_ID}/deploys"
    headers = {"Authorization": f"Bearer {NETLIFY_TOKEN}"}
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "text/html")}
            response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            print("✅ デプロイに成功しました")
            deploy_id = response.json().get("id")
            if deploy_id:
                # ★ 自動公開の保険（キャッシュクリア＋公開確定）
                restore_url = f"https://api.netlify.com/api/v1/sites/{SITE_ID}/deploys/{deploy_id}/restore"
                requests.post(restore_url, headers=headers)
                print("✅ サイトを更新しました！ https://shibata-affiliate.netlify.app")
                print("🔄 ブラウザでCtrl+F5（スーパーリロード）で最新が表示されます")
            else:
                print("⚠️ デプロイIDが取得できませんでした")
        else:
            print(f"Netlifyデプロイ失敗 (ステータスコード: {response.status_code})")
            print(f"エラー詳細: {response.text}")
    except Exception as e:
        print(f"Netlifyデプロイ中に予期せぬエラー: {e}")

# ===== メイン処理 =====
print("===== アフィリエイト自動化スクリプト 開始 =====")
all_products = []

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["カテゴリ", "商品名", "価格", "アフィリエイトURL"])

for kw in KEYWORDS:
    print(f"\n🔍 「{kw}」を検索中...")
    results = search_rakuten(kw)
    
    if results:
        all_products.append((kw, results))
        with open(OUTPUT_FILE, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            for name, price, url_aff in results:
                writer.writerow([kw, name, price, url_aff])
        print(f"✅ {kw}: {len(results)}件追加")
    else:
        print(f"⚠️ {kw}: 商品が見つかりませんでした")

if all_products:
    print("\n📄 HTMLを生成しています...")
    html = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>毎日自動更新！おすすめ商品</title>
<style>
    body { font-family: 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f9f9f9; }
    h1 { color: #bf0000; border-bottom: 3px solid #bf0000; padding-bottom: 10px; }
    h2 { color: #333; background: #fff; padding: 10px; border-left: 5px solid #bf0000; }
    .product { background: white; border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .product h3 { margin: 0 0 10px 0; }
    .price { color: #e74c3c; font-weight: bold; font-size: 1.2em; }
    .btn { display: inline-block; background: #bf0000; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px; }
    .btn:hover { background: #a00000; }
    .footer { text-align: center; margin-top: 30px; padding: 20px; color: #777; font-size: 0.9em; }
</style>
</head>
<body>
<h1>🛒 【毎日自動更新】今日のおすすめ商品！</h1>
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
        <a href="{url_aff}" target="_blank" rel="nofollow" class="btn">👉 楽天で見てみる</a>
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
    
    # deploy_to_netlify(file_path)
else:
    print("\n⚠️ 商品が1件も取得できませんでした。")

print("\n===== スクリプト終了 =====")
