import requests
import os
import feedparser
from datetime import datetime
import pytz

# --- CẤU HÌNH ---
RSS_SOURCES = [
    # --- 4 Nguồn cũ ---
    "https://cafef.vn/thi-truong-chung-khoan.rss",
    "https://vietstock.vn/rss/chung-khoan.rss",
    "https://nguoiquansat.vn/thi-truong.rss",
  
    
    # --- 12 Nguồn VnEconomy mới ---
    "https://vneconomy.vn/tin-moi.rss",
    "https://vneconomy.vn/tieu-diem.rss",
    "https://vneconomy.vn/chung-khoan.rss",
    "https://vneconomy.vn/thi-truong.rss",
    "https://vneconomy.vn/nhip-cau-doanh-nghiep.rss",
    "https://vneconomy.vn/tieu-dung.rss",
    "https://vneconomy.vn/kinh-te-xanh.rss",
    "https://vneconomy.vn/tai-chinh.rss",
    "https://vneconomy.vn/kinh-te-so.rss",
    "https://vneconomy.vn/dia-oc.rss",
    "https://vneconomy.vn/kinh-te-the-gioi.rss",
    "https://vneconomy.vn/dau-tu.rss"
]
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# --- CHỮ KÝ MUỐN THÊM ---
FOOTER_TEXT = """
#bietdoi
===============================
📊 Phân tích cảm xúc bài viết từ Hệ thống AI của Biệt Đội Tài Chén
🟢 Tích cực       🟡 Trung lập       🔴 Tiêu cực
"""

# Hàm xác định màu icon
def get_icon(title):
    title_lower = title.lower()

    # Keywords Tích cực (Bao gồm Thị trường, Chính sách, Kinh tế Vĩ mô)
    positive_keywords = [
        'tăng', 'lãi', 'vượt', 'đỉnh', 'khởi sắc', 'hồi phục', 
        'ổn định', 'mở cửa', 'thúc đẩy', 'hỗ trợ', 'tăng trưởng', 
        'kỷ lục', 'giải ngân', 'thu hút', 'phục hồi', 'chính thức'
    ]

    # Keywords Tiêu cực (Bao gồm Rủi ro, Thanh tra, Giảm điểm/lỗ)
    negative_keywords = [
        'giảm', 'lỗ', 'thủng', 'đáy', 'bán tháo', 'lao dốc', 
        'siết chặt', 'kiểm tra', 'thanh tra', 'điều tra', 'phạt', 
        'khó khăn', 'suy giảm', 'vỡ nợ', 'thách thức', 'đóng băng', 'thận trọng'
    ]

    if any(w in title_lower for w in positive_keywords):
        return "🟢"
    elif any(w in title_lower for w in negative_keywords):
        return "🔴"
    else:
        return "🟡"

def get_news():
    try:
        news_list = []
        # TẠO MỘT SET ĐỂ LƯU CÁC LINK ĐÃ THẤY
        seen_links = set()
        
        # Bắt đầu vòng lặp qua danh sách RSS_SOURCES
        for url in RSS_SOURCES:
            feed = feedparser.parse(url)
            # Lấy 5 tin mới nhất từ MỖI nguồn
            for entry in feed.entries[:5]:
                link = entry.link
                
                # 1. KIỂM TRA TRÙNG LẶP
                if link not in seen_links:
                    seen_links.add(link)
                    
                    # 2. BỔ SUNG TRƯỜNG DATE
                    date_info = entry.get('published_parsed') or entry.get('updated_parsed')
                    
                    news_list.append({
                        "title": entry.title,
                        "link": link,
                        "icon": get_icon(entry.title),
                        "date": date_info 
                    })
        
        # 3. SẮP XẾP: Sắp xếp danh sách tin theo thời gian/ngày đăng (mới nhất lên đầu)
        news_list.sort(key=lambda x: x.get('date', 0), reverse=True)
        
        # 4. TRẢ VỀ TOÀN BỘ TIN TỨC: Đã bỏ giới hạn [:10]
        return news_list 
        
    except Exception as e:
        print(f"Lỗi lấy tin từ nhiều nguồn: {e}") 
        return []
            
        
    except Exception as e:
        # Thay thế print(f"Lỗi lấy tin: {e}") cũ bằng thông báo mới
        print(f"Lỗi lấy tin từ nhiều nguồn: {e}") 
        return []

def send_telegram(news_items, time_str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return

    message = f"<b>🔔 CẬP NHẬT THÔNG TIN THỊ TRƯỜNG {time_str}</b>\n\n"
    
    for item in news_items:
        row = f"{item['icon']} {item['title']} - <a href='{item['link']}'>chi tiết</a>\n\n"
        # Trừa chỗ trống để chèn footer (khoảng 50 ký tự)
        if len(message) + len(row) + len(FOOTER_TEXT) < 4090:
            message += row
        else:
            break
    
    # --- THÊM CHỮ KÝ VÀO CUỐI ---
    message += FOOTER_TEXT

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload)
    print("Đã gửi Telegram")

def send_discord(news_items, time_str):
    if not DISCORD_WEBHOOK:
        return

    description = ""
    for item in news_items:
        row = f"{item['icon']} {item['title']} - [chi tiết]({item['link']})\n\n"
        if len(description) + len(row) + len(FOOTER_TEXT) < 4000:
            description += row
        else:
            break
            
    # --- THÊM CHỮ KÝ VÀO CUỐI ---
    description += FOOTER_TEXT

    payload = {
        "embeds": [{
            "title": f"🔔 CẬP NHẬT THÔNG TIN THỊ TRƯỜNG {time_str}",
            "description": description,
            "color": 16776960,
            "footer": {
                "text": "Nguồn: Tổng hợp bởi Biệt_Đội_News"
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
