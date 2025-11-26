import requests
import os
import feedparser
from datetime import datetime
import pytz

from datetime import datetime, timedelta # Cần phải import thêm timedelta ở đầu file
# Tên file lưu trữ các link đã gửi (Trạng thái)
SENT_LINKS_FILE = 'sent_links.txt' 

# --- CẤU HÌNH ---
# Giới hạn độ tuổi tối đa của bài viết được phép gửi (tính theo giờ)
# Nếu bài báo cũ hơn 12 tiếng, bot sẽ bỏ qua
MAX_AGE_HOURS = 12
RSS_SOURCES = [
    # --- 4 Nguồn cũ ---
    # --- NGUỒN CAFEF MỚI VÀ HIỆN CÓ ---
    "https://cafef.vn/thi-truong-chung-khoan.rss", # Giữ lại nguồn chính
    "https://cafef.vn/bat-dong-san.rss",
    "https://cafef.vn/doanh-nghiep.rss",
    "https://cafef.vn/tai-chinh-ngan-hang.rss",
    "https://cafef.vn/tai-chinh-quoc-te.rss",
    "https://cafef.vn/smart-money.rss",
    "https://cafef.vn/vi-mo-dau-tu.rss",
    "https://cafef.vn/kinh-te-so.rss",
    "https://cafef.vn/thi-truong.rss",
    "https://cafef.vn/tin-tuc-du-an.rss",
    "https://vietstock.vn/rss/chung-khoan.rss",

    # --- 15 NGUỒN MỚI TỪ NGƯỜI QUAN SÁT (BỎ ĐUÔI .RSS) ---
    # 1. Chứng Khoán (4 nguồn)
    "https://nguoiquansat.vn/rss/chung-khoan.rss", 
    "https://nguoiquansat.vn/rss/chung-khoan/chuyen-dong-thi-truong.rss", 
    "https://nguoiquansat.vn/rss/chung-khoan/doanh-nghiep-az.rss", 
    "https://nguoiquansat.vn/rss/chung-khoan/cau-chuyen-dau-tu.rss",

    # 2. Bất Động Sản (3 nguồn)
    "https://nguoiquansat.vn/rss/bat-dong-san.rss", 
    "https://nguoiquansat.vn/rss/bat-dong-san/thi-truong-doanh-nghiep.rss", 
    "https://nguoiquansat.vn/rss/bat-dong-san/ha-tang-chinh-sach.rss",

    # 3. Tài Chính & Ngân Hàng (1 nguồn)
    "https://nguoiquansat.vn/rss/tai-chinh-ngan-hang.rss",

    # 4. Doanh Nghiệp (3 nguồn)
    "https://nguoiquansat.vn/rss/doanh-nghiep.rss", 
    "https://nguoiquansat.vn/rss/doanh-nghiep/chuyen-dong-doanh-nghiep.rss", 
    "https://nguoiquansat.vn/rss/doanh-nghiep/co-hoi-dau-tu.rss",

    # 5. Khác (4 nguồn)
    "https://nguoiquansat.vn/rss/the-gioi/tai-chinh-quoc-te.rss", 
    "https://nguoiquansat.vn/rss/thi-truong.rss", 
    "https://nguoiquansat.vn/rss/thi-truong/hang-hoa-tieu-dung.rss", 
    "https://nguoiquansat.vn/rss/vi-mo.rss",
    

    # --- 3 Nguồn mới bổ sung ---
    "https://vnexpress.net/rss/kinh-doanh.rss",                  # VnExpress
    "https://tinnhanhchungkhoan.vn/rss/tin-moi-nhat.rss",        # Đầu tư Chứng khoán
    
    # --- 12 NGUỒN MỚI TỪ BÁO ĐẦU TƯ ---
    "https://baodautu.vn/thoi-su.rss",
    "https://baodautu.vn/dau-tu.rss",
    "https://baodautu.vn/doanh-nghiep.rss",
    "https://baodautu.vn/ngan-hang--bao-hiem.rss",
    "https://baodautu.vn/tai-chinh-chung-khoan.rss",
    "https://baodautu.vn/bat-dong-san.rss",
    "https://baodautu.vn/tieu-dung.rss",
    "https://baodautu.vn/dau-tu-va-cuoc-song.rss",
    "https://baodautu.vn/dau-tu-phat-trien-ben-vung.rss",
    "https://baodautu.vn/kinh-te-so.rss",
    "https://baodautu.vn/quoc-te.rss",
    "https://baodautu.vn/diem-tin-noi-bat.rss",
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

    # --- 36 NGUỒN MỚI TỪ VIETSTOCK (BỔ SUNG) ---

    # 1. Chứng Khoán (9 nguồn)
    "https://vietstock.vn/739/chung-khoan/giao-dich-noi-bo.rss",
    "https://vietstock.vn/830/chung-khoan/co-phieu.rss",
    "https://vietstock.vn/3358/chung-khoan/etf-va-cac-quy.rss",
    "https://vietstock.vn/4186/chung-khoan/chung-khoan-phai-sinh.rss",
    "https://vietstock.vn/4308/chung-khoan/chung-quyen.rss",
    "https://vietstock.vn/3355/chung-khoan/cau-chuyen-dau-tu.rss",
    "https://vietstock.vn/143/chung-khoan/chinh-sach.rss",
    "https://vietstock.vn/785/chung-khoan/thi-truong-trai-phieu.rss",
    "https://vietstock.vn/145/chung-khoan/y-kien-chuyen-gia.rss",

    # 2. Doanh Nghiệp (5 nguồn)
    "https://vietstock.vn/737/doanh-nghiep/hoat-dong-kinh-doanh.rss",
    "https://vietstock.vn/738/doanh-nghiep/co-tuc.rss",
    "https://vietstock.vn/764/doanh-nghiep/tang-von-m-a.rss",
    "https://vietstock.vn/746/doanh-nghiep/ipo-co-phan-hoa.rss",
    "https://vietstock.vn/214/doanh-nghiep/nhan-vat.rss",
    "https://vietstock.vn/3118/doanh-nghiep/trai-phieu-doanh-nghiep.rss",

    # 3. Bất Động Sản (2 nguồn)
    "https://vietstock.vn/42221/bat-dong-san/quy-hoach-ha-tang.rss",
    "https://vietstock.vn/4220//bat-dong-san/thi-truong-nha-dat.rss", # Link này có vẻ bị thừa '/', tôi đã giữ nguyên

    # 4. Tài Chính (4 nguồn)
    "https://vietstock.vn/757/tai-chinh/ngan-hang.rss",
    "https://vietstock.vn/3113/tai-chinh/bao-hiem.rss",
    "https://vietstock.vn/758/tai-chinh/thue-va-ngan-sach.rss",
    "https://vietstock.vn/16312/tai-chinh/tai-san-so.rss",

    # 5. Hàng Hóa (3 nguồn)
    "https://vietstock.vn/759/hang-hoa/vang-va-kim-loai-quy.rss",
    "https://vietstock.vn/34/hang-hoa/nhien-lieu.rss",
    "https://vietstock.vn/118/hang-hoa/nong-san-thuc-pham.rss",

    # 6. Kinh Tế & Vi Mô (2 nguồn)
    "https://vietstock.vn/761/kinh-te/vi-mo.rss",
    "https://vietstock.vn/768/kinh-te/kinh-te-dau-tu.rss",

    # 7. Thế Giới (3 nguồn)
    "https://vietstock.vn/773/the-gioi/chung-khoan-the-gioi.rss",
    "https://vietstock.vn/772/the-gioi/tai-chinh-quoc-te.rss",
    "https://vietstock.vn/775/the-gioi/kinh-te-nganh.rss",

    # 8. Đông Dương (3 nguồn)
    "https://vietstock.vn/1326/dong-duong/vi-mo-dau-tu.rss",
    "https://vietstock.vn/1327/dong-duong/tai-chinh-ngan-hang.rss",
    "https://vietstock.vn/1328/dong-duong/thi-truong-chung-khoan.rss",

    # 9. Nhận Định/Phân Tích (3 nguồn)
    "https://vietstock.vn/1636/nhan-dinh-phan-tich/nhan-dinh-thi-truong.rss",
    "https://vietstock.vn/582/nhan-dinh-phan-tich/phan-tich-co-ban.rss",
    "https://vietstock.vn/585/nhan-dinh-phan-tich/phan-tich-ky-thuat.rss"
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




# --- HÀM LẤY TIN (ĐÃ THÊM LỌC THEO THỜI GIAN) ---

def get_news():
    try:
        previously_sent_links = load_sent_links() 
        news_list = []
        seen_links = set()
        
        # Thiết lập ngưỡng thời gian tối đa cho bài viết
        age_limit = datetime.now(pytz.utc) - timedelta(hours=MAX_AGE_HOURS)
        
        for url in RSS_SOURCES:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                link = entry.link
                date_info = entry.get('published_parsed') or entry.get('updated_parsed')
                
                # BƯỚC LỌC 1: Lọc bài viết quá cũ (Age Filter)
                if date_info:
                    try:
                        # Chuyển đổi thời gian bài viết sang UTC để so sánh
                        article_dt_utc = datetime(*date_info[:6], tzinfo=pytz.utc)
                        if article_dt_utc < age_limit:
                            continue # Bỏ qua bài báo quá cũ
                    except Exception as e:
                        # Bỏ qua nếu không thể phân tích ngày tháng
                        print(f"Không thể phân tích ngày đăng của link {link}: {e}")
                        continue
                else:
                    # Bỏ qua nếu không có thông tin ngày đăng
                    continue

                # BƯỚC LỌC 2 & 3: Lọc link trùng trong lần chạy hiện tại và link đã gửi từ trước
                if link not in seen_links and link not in previously_sent_links:
                    seen_links.add(link)
                    
                    news_list.append({
                        "title": entry.title,
                        "link": link,
                        "icon": get_icon(entry.title),
                        "date": date_info 
                    })
        
        # Sắp xếp và trả về tất cả tin mới, chưa quá cũ
        news_list.sort(key=lambda x: x.get('date', 0), reverse=True)
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
