import requests
import os
import feedparser
from datetime import datetime
import pytz

# Tên file lưu trữ các link đã gửi (Trạng thái)
SENT_LINKS_FILE = 'sent_links.txt' 

# --- CẤU HÌNH ---
RSS_SOURCES = [
    # --- 4 Nguồn cũ ---
    "https://cafef.vn/thi-truong-chung-khoan.rss",
    "https://vietstock.vn/rss/chung-khoan.rss",
    "https://nguoiquansat.vn/thi-truong.rss",

    # --- 3 Nguồn mới bổ sung ---
    "https://vnexpress.net/rss/kinh-doanh.rss",                  # VnExpress
    "https://tinnhanhchungkhoan.vn/rss/tin-moi-nhat.rss",        # Đầu tư Chứng khoán
    "https://baodautu.vn/rss/chung-khoan-18.rss",                # Báo Đầu tư
    # --- 3 Nguồn MỚI BỔ SUNG LẦN NÀY ---
    "https://tapchitaichinh.vn/rss/chung-khoan.rss",             # Tạp chí Tài chính
    "https://congthuong.vn/rss/tai-chinh.rss",                   # Báo Công Thương
    "https://diendandoanhnghiep.vn/rss/tin-tuc-chung-khoan-27.rss", # Diễn đàn Doanh nghiệp
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

    # Keywords Tích cực (Bổ sung thêm từ khóa về mục tiêu, dòng tiền, hiệu quả)
    positive_keywords = [
        'tăng', 'lãi', 'vượt', 'đỉnh', 'khởi sắc', 'hồi phục', 
        'ổn định', 'mở cửa', 'thúc đẩy', 'hỗ trợ', 'tăng trưởng', 'đóng góp',
        'kỷ lục', 'giải ngân', 'thu hút', 'phục hồi', 'chính thức', 'động lực', 'mạnh mẽ',
        # --- BỔ SUNG MỚI ---
        'mục tiêu', 'dòng tiền', 'kích thích', 'thành công', 'hiệu quả', 'tiềm năng', 'chủ động', 
        'được phê duyệt', 'bứt phá', 'tăng tốc', 'tích cực', 'nới lỏng'
    ]

    # Keywords Tiêu cực (Bổ sung từ khóa về rủi ro, áp lực, trì trệ)
    negative_keywords = [
        'giảm', 'lỗ', 'thủng', 'đáy', 'bán tháo', 'lao dốc', 
        'siết chặt', 'kiểm tra', 'thanh tra', 'điều tra', 'phạt', 'khẩn cấp',
        'khó khăn', 'suy giảm', 'vỡ nợ', 'thách thức', 'đóng băng', 'thận trọng',
        # --- BỔ SUNG MỚI ---
        'bất ổn', 'nguy cơ', 'thiếu hụt', 'rào cản', 'áp lực', 'đình trệ', 'tê liệt', 
        'cảnh báo', 'thua lỗ', 'tụt dốc', 'phải trả', 'đổ vỡ'
    ]

    if any(w in title_lower for w in positive_keywords):
        return "🟢"
    elif any(w in title_lower for w in negative_keywords):
        return "🔴"
    else:
        return "🟡"

# --- HÀM XỬ LÝ TRẠNG THÁI MỚI ---

def load_sent_links():
    """Đọc file lưu trữ và trả về set chứa các link đã gửi (lấy 50 link gần nhất)."""
    if os.path.exists(SENT_LINKS_FILE):
        with open(SENT_LINKS_FILE, 'r') as f:
            # Giữ lại 50 link cuối cùng để tránh file quá lớn
            return set(f.read().splitlines()[-50:])
    return set()

def save_sent_links(new_links):
    """Ghi thêm các link mới vào file lưu trữ và giới hạn 100 link."""
    
    # 1. Lấy tất cả các link cũ
    current_links = []
    if os.path.exists(SENT_LINKS_FILE):
        with open(SENT_LINKS_FILE, 'r') as f:
            current_links = f.read().splitlines()
    
    # 2. Thêm các link mới vào cuối
    updated_links = current_links + list(new_links)

    # 3. Chỉ giữ lại 100 link gần nhất (giới hạn kích thước file)
    final_links = updated_links[-100:]

    # 4. Ghi file
    with open(SENT_LINKS_FILE, 'w') as f:
        f.write('\n'.join(final_links))


# --- HÀM LẤY TIN ĐÃ SỬA (Lọc tin cũ từ trạng thái) ---

def get_news():
    try:
        # Lấy danh sách link đã gửi từ lần chạy trước
        previously_sent_links = load_sent_links() 
        
        news_list = []
        # TẠO MỘT SET ĐỂ LƯU CÁC LINK ĐÃ THẤY (Lọc tin trùng trong lần chạy này)
        seen_links = set()
        
        for url in RSS_SOURCES:
            feed = feedparser.parse(url)
            # Lấy 5 tin mới nhất từ MỖI nguồn
            for entry in feed.entries[:5]:
                link = entry.link
                
                # BƯỚC LỌC KÉP: 
                # 1. Lọc tin trùng trong lần chạy hiện tại
                # 2. LỌC TIN ĐÃ GỬI TỪ LẦN TRƯỚC (chống lặp giữa các lần chạy)
                if link not in seen_links and link not in previously_sent_links:
                    seen_links.add(link)
                    date_info = entry.get('published_parsed') or entry.get('updated_parsed')
                    
                    news_list.append({
                        "title": entry.title,
                        "link": link,
                        "icon": get_icon(entry.title),
                        "date": date_info 
                    })
        
        # Sắp xếp theo ngày mới nhất
        news_list.sort(key=lambda x: x.get('date', 0), reverse=True)
        
        # Trả về tất cả tin mới, chưa từng được gửi
        return news_list
        
    except Exception as e:
        print(f"Lỗi lấy tin từ nhiều nguồn: {e}") 
        return []


# --- HÀM GỬI TIN (Giữ nguyên) ---

def send_telegram(news_items, time_str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return

    message = f"<b>🔔 CẬP NHẬT THÔNG TIN THỊ TRƯỜNG {time_str}</b>\n\n"
    
    for item in news_items:
        row = f"{item['icon']} {item['title']} - <a href='{item['link']}'>chi tiết</a>\n\n"
        if len(message) + len(row) + len(FOOTER_TEXT) < 4090:
            message += row
        else:
            break
    
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


# --- HÀM CHÍNH ĐÃ SỬA (Lưu trạng thái mới) ---

if __name__ == "__main__":
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now_str = datetime.now(vn_tz).strftime("%H:%M %d/%m")
    
    print("Đang lấy tin tức...")
    news_data = get_news()
    
    if news_data:
        # Lấy danh sách link của các tin sẽ gửi (chưa gửi bao giờ)
        links_to_save = [item['link'] for item in news_data]

        send_telegram(news_data, now_str)
        send_discord(news_data, now_str)
        
        # LƯU TRẠNG THÁI: Ghi các link vừa gửi vào file để lần sau không gửi lại
        save_sent_links(links_to_save) 
        
    else:
        print("Không có tin tức mới")
