import requests
import os
import feedparser
from datetime import datetime
import pytz

# --- CẤU HÌNH ---
# Dùng RSS của CafeF hoặc Vietstock (Ví dụ này dùng CafeF mục Chứng khoán)
RSS_URL = "https://cafef.vn/thi-truong-chung-khoan.rss" 
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Hàm xác định màu icon dựa trên từ khóa trong tiêu đề
def get_icon(title):
    title_lower = title.lower()
    # Các từ khóa tích cực
    if any(w in title_lower for w in ['tăng', 'lãi', 'vượt', 'đỉnh', 'khởi sắc', 'hồi phục']):
        return "🟢"
    # Các từ khóa tiêu cực
    elif any(w in title_lower for w in ['giảm', 'lỗ', 'thủng', 'đáy', 'bán tháo', 'lao dốc']):
        return "🔴"
    # Còn lại (tin trung lập hoặc thông báo)
    else:
        return "🟡"

def get_news():
    try:
        # Đọc RSS Feed
        feed = feedparser.parse(RSS_URL)
        news_list = []
        
        # Lấy 10 tin mới nhất
        for entry in feed.entries[:10]:
            news_list.append({
                "title": entry.title,
                "link": entry.link,
                "icon": get_icon(entry.title)
            })
        return news_list
    except Exception as e:
        print(f"Lỗi lấy tin: {e}")
        return []

def send_telegram(news_items, time_str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return

    # Tạo nội dung tin nhắn dạng HTML
    # Format: 🟢 Tiêu đề bài báo - <a href="link">chi tiết</a>
    message = f"<b>🔔 CẬP NHẬT THÔNG TIN THỊ TRƯỜNG {time_str}</b>\n\n"
    
    for item in news_items:
        # Telegram dùng thẻ <a> để tạo link ẩn
        row = f"{item['icon']} {item['title']} - <a href='{item['link']}'>chi tiết</a>\n\n"
        
        # Telegram giới hạn 4096 ký tự, nếu dài quá thì cắt bớt để tránh lỗi
        if len(message) + len(row) < 4000:
            message += row
        else:
            break

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML", # Bắt buộc để hiển thị link ẩn
        "disable_web_page_preview": True # Tắt preview ảnh để tin nhắn gọn gàng
    }
    requests.post(url, json=payload)
    print("Đã gửi Telegram")

def send_discord(news_items, time_str):
    if not DISCORD_WEBHOOK:
        return

    # Tạo nội dung cho Discord (Dùng Markdown)
    description = ""
    for item in news_items:
        # Format: 🟢 Tiêu đề - [chi tiết](link)
        row = f"{item['icon']} {item['title']} - [chi tiết]({item['link']})\n\n"
        if len(description) + len(row) < 4000:
            description += row
        else:
            break

    payload = {
        "embeds": [{
            "title": f"🔔 CẬP NHẬT THÔNG TIN THỊ TRƯỜNG {time_str}",
            "description": description,
            "color": 16776960, # Màu vàng
            "footer": {
                "text": "Nguồn: CafeF"
            }
        }]
    }
    requests.post(DISCORD_WEBHOOK, json=payload)
    print("Đã gửi Discord")

if __name__ == "__main__":
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now_str = datetime.now(vn_tz).strftime("%H:%M %d/%m")
    
    print("Đang lấy tin tức...")
    news_data = get_news()
    
    if news_data:
        send_telegram(news_data, now_str)
        send_discord(news_data, now_str)
    else:
        print("Không có tin tức mới")
