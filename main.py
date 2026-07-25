import requests
import os
import feedparser
from datetime import datetime
import pytz
from datetime import datetime, timedelta # Cần phải import thêm timedelta ở đầu file
import time # Nhớ thêm import này ở đầu file nếu chưa có
#Update6/13/2026
# Track log 25/7/2026
SENT_LINKS_FILE = 'sent_links.txt' 

# --- CẤU HÌNH ---------------------------------------------------
# Giới hạn độ tuổi tối đa của bài viết được phép gửi (tính theo giờ)
# Nếu bài báo cũ hơn 12 tiếng, bot sẽ bỏ qua
MAX_AGE_HOURS = 24

# THÊM DÒNG NÀY: Giới hạn số lượng tin gửi mỗi lần
MAX_ITEMS_PER_SEND = 5

RSS_SOURCES = [
    # --- NGUỒN CŨ VÀ HIỆN CÓ ---
    # XÓA NGUỒN LỖI https://baodautu.vn/tai-chinh-chung-khoan.rss
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

    #Nguoiquansat
    "https://nguoiquansat.vn/rss/chung-khoan",
    "https://nguoiquansat.vn/rss/chung-khoan/chuyen-dong-thi-truong",
    "https://nguoiquansat.vn/rss/chung-khoan/doanh-nghiep-az",
    "https://nguoiquansat.vn/rss/chung-khoan/cau-chuyen-dau-tu",
    "https://nguoiquansat.vn/rss/bat-dong-san",
    "https://nguoiquansat.vn/rss/bat-dong-san/thi-truong-doanh-nghiep",
    "https://nguoiquansat.vn/rss/bat-dong-san/ha-tang-chinh-sach",
    "https://nguoiquansat.vn/rss/tai-chinh-ngan-hang",
    "https://nguoiquansat.vn/rss/tai-chinh-ngan-hang/ngan-hang",
    "https://nguoiquansat.vn/rss/tai-chinh-ngan-hang/vang-ty-gia",
    "https://nguoiquansat.vn/rss/tai-chinh-ngan-hang/tai-san-so",
    "https://nguoiquansat.vn/rss/doanh-nghiep",
    "https://nguoiquansat.vn/rss/doanh-nghiep/doanh-nhan",
    "https://nguoiquansat.vn/rss/the-gioi",
    "https://nguoiquansat.vn/rss/the-gioi/tai-chinh-quoc-te",
    "https://nguoiquansat.vn/rss/thi-truong",
    "https://nguoiquansat.vn/rss/vi-mo",

     # --- NGUỒN TỪ VIETSTOCK ---
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
    "https://vietstock.vn/4220//bat-dong-san/thi-truong-nha-dat.rss",
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
    "https://vietstock.vn/585/nhan-dinh-phan-tich/phan-tich-ky-thuat.rss",
    "https://vietstock.vn/rss/chung-khoan.rss",
    
    # --- Nguồn bổ sung ---
    "https://vnexpress.net/rss/kinh-doanh.rss",                  # VnExpress
    #"https://tinnhanhchungkhoan.vn/rss/tin-moi-nhat.rss",        # Đầu tư Chứng khoán
    
    # --- Nguồn VnEconomy ---
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
    "https://vneconomy.vn/dau-tu.rss",

    # --- NGUỒN TỪ NHỊP SỐNG KINH DOANH ---
    "https://nhipsongkinhdoanh.vn/rss/vang-bac-kim-loai-quy-14711.rss",
    "https://nhipsongkinhdoanh.vn/rss/tai-san-so-14191.rss",
    "https://nhipsongkinhdoanh.vn/rss/tai-chinh-6.rss", # Chỉ giữ lại 1 lần
    "https://nhipsongkinhdoanh.vn/rss/doanh-nghiep-7182.rss",
    "https://nhipsongkinhdoanh.vn/rss/kinh-doanh-11.rss",
    #Investing.com
    "https://vn.investing.com/rss/commodities_Metals.rss",
    "https://vn.investing.com/rss/commodities_Energy.rss",
    "https://vn.investing.com/rss/commodities_Agriculture.rss",
    "https://vn.investing.com/rss/market_overview_investing_ideas.rss",
    "https://vn.investing.com/rss/stock_Stocks.rss",
    "https://vn.investing.com/rss/stock_Indices.rss",
    "https://vn.investing.com/rss/market_overview_Fundamental.rss",
    "https://vn.investing.com/rss/market_overview_Technical.rss",
    "https://vn.investing.com/rss/market_overview_Opinion.rss",
    "https://vn.investing.com/rss/news_14.rss",
    "https://vn.investing.com/rss/news_287.rss", 
    "https://vn.investing.com/rss/news_25.rss",
    "https://vn.investing.com/rss/news_11.rss",
    #MarketTimes
    "https://markettimes.vn/rss/kinh-doanh",
    "https://markettimes.vn/rss/tai-chinh",
    "https://markettimes.vn/rss/bat-dong-san",
    "https://markettimes.vn/rss/cong-nghe",
    "https://markettimes.vn/rss/nganh-hang",
    "https://markettimes.vn/rss/the-gioi",
    # --- NGUỒN MỚI TỪ DÂN TRÍ ---
    "https://dantri.com.vn/rss/gia-vang.rss",
    "https://dantri.com.vn/rss/tam-diem.rss",
    "https://dantri.com.vn/rss/kinh-doanh.rss"
]
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# --- CHỮ KÝ MUỐN THÊM CHO DISCORD (CÓ LINK) ---
FOOTER_TEXT_DISCORD = """
[#bietdoi](https://t.me/bietdoinews)
===============================
📊 Phân tích cảm xúc bài viết từ Hệ thống AI của Biệt Đội Tài Chén
🟢 Tích cực       🟡 Trung lập       🔴 Tiêu cực
"""

# --- CHỮ KÝ MUỐN THÊM CHO TELEGRAM (KHÔNG LINK) ---
FOOTER_TEXT_TELEGRAM = """
#bietdoi
===============================
📊 Phân tích cảm xúc bài viết từ Hệ thống AI của Biệt Đội Tài Chén
🟢 Tích cực       🟡 Trung lập       🔴 Tiêu cực
"""

# Hàm xác định màu icon nâng cấp toàn diện
def get_icon(title):
    title_lower = title.lower()

    # =========================================================================
    # KỊCH BẢN TÍCH CỰC (🟢): Thị trường uptrend, phục hồi, giải cứu, làm ăn tốt
    # =========================================================================
    positive_keywords = [
        # 1. Cụm từ "hóa giải" tin xấu / Hành động giải cứu của Chính phủ
        'tháo gỡ khó khăn', 'tháo gỡ vướng mắc', 'xử lý vướng mắc', 'giải cứu', 
        'vượt khó', 'khơi thông dòng vốn', 'khơi thông dòng tiền', 'nới lỏng tiền tệ',
        'hạ lãi suất', 'giảm lãi suất', 'hoãn nợ', 'giãn nợ', 'gia hạn nợ',
        'cứu vớt', 'hồi sinh', 'vực dậy', 'tiếp sức', 'tiếp máu', 'bơm thêm vốn',

        # 2. Thuật ngữ Chứng khoán & Dòng tiền (Uptrend)
        'đón sóng', 'gom ròng', 'mua ròng', 'hút tiền', 'bơm tiền', 'dòng tiền vào',
        'khối ngoại mua', 'đại gia ngoại', 'cá mập gom', 'tự doanh mua', 'nâng hạng',
        'nới room', 'nới trần', 'xanh sàn', 'giá trần', 'tăng trần', 'kịch trần',
        'uptrend', 'bứt tốc', 'bứt phá', 'tăng tốc', 'bùng nổ', 'tạo đáy xong',
        'đảo chiều tăng', 'vượt đỉnh', 'lội ngược dòng', 'phá kỷ lục', 'đạt đỉnh mới',
        'sóng lớn', 'con sóng', 'dẫn dắt thị trường', 'trụ vững', 'giữ vững sắc xanh',

        # 3. Kết quả kinh doanh & Doanh nghiệp (Tin tốt)
        'lãi đậm', 'lãi khủng', 'lãi kỷ lục', 'lãi vượt', 'vượt mong đợi', 'vượt dự báo',
        'vượt kế hoạch', 'tin tích cực', 'tin vui', 'khởi sắc', 'hồi phục', 'phục hồi',
        'thắng lớn', 'thặng dư', 'hưởng lợi', 'về đích', 'sáng cửa', 'được phê duyệt',
        'ký hợp tác', 'ký kết', 'khởi công', 'muốn xây', 'đổ bộ', 'mở rộng quy mô',
        'chia cổ tức', 'thâu tóm thành công', 'm&a thành công', 'rót vốn',

        # 4. Vĩ mô tốt & Động lực phát triển
        'ổn định', 'mở cửa', 'thúc đẩy', 'hỗ trợ', 'tăng trưởng', 'đóng góp', 'phát triển',
        'giải ngân', 'thu hút', 'động lực', 'mạnh mẽ', 'mục tiêu', 'kích thích', 'thành công',
        'hiệu quả', 'tiềm năng', 'chủ động', 'tích cực', 'đầu tư', 'vươn lên', 'kỷ lục',
        
        # 5. Từ đơn tích cực (Quét sau cùng)
        'tăng', 'lãi', 'vượt', 'đỉnh', 'bơm', 'trần', 'xanh'
    ]

    # =========================================================================
    # KỊCH BẢN TIÊU CỰC (🔴): Khủng hoảng, sập sàn, pháp lý, chiến tranh, nợ nần
    # =========================================================================
    negative_keywords = [
        # 1. Rủi ro Hệ thống / Kỹ thuật Chứng khoán (Downtrend)
        'áp lực bán', 'bán tháo', 'lao dốc', 'giảm sâu', 'giảm mạnh', 'sụt giảm',
        'cắm đầu', 'bốc hơi', 'bay màu', 'bốc hơi nghìn tỷ', 'tháo chạy', 'hụt hơi',
        'gánh nặng', 'u ám', 'kém sắc', 'đỏ sàn', 'lau sàn', 'nằm sàn', 'giảm sàn',
        'trắng bên mua', 'mất thanh khoản', 'downtrend', 'margin call', 'giải chấp',
        'bị bán ròng', 'khối ngoại bán', 'rút vốn', 'rút ròng', 'di tản dòng tiền',
        'hủy niêm yết', 'vỡ trận', 'sập sàn', 'thủng đáy', 'phá đáy',

        # 2. Rủi ro Doanh nghiệp & Nợ nần
        'nợ xấu', 'vỡ nợ', 'thua lỗ', 'lỗ nặng', 'lỗ kỷ lục', 'lỗ ròng', 'âm vốn',
        'hụt thu', 'kiệt quệ', 'khổ trăm bề', 'thoái vốn', 'thoái sạch', 'kẹt dòng tiền',
        'đóng băng', 'tê liệt', 'đình trệ', 'rào cản', 'vướng mắc', 'khó khăn', 'thách thức',
        'đình chỉ', 'cưỡng chế', 'bị phạt', 'xử phạt', 'nộp phạt', 'phạt tiền',

        # 3. Rủi ro Pháp lý / Thanh tra (Tin cực độc cho chứng khoán)
        'khởi tố', 'bắt giam', 'tạm giam', 'sai phạm', 'bê bối', 'scandal', 'điều tra',
        'thanh tra', 'kiểm tra', 'siết chặt', 'thắt chặt', 'thao túng', 'gian lận',
        'lừa đảo', 'chiếm đoạt', 'bị cáo', 'hầu tòa', 'kỷ luật', 'truy thu',

        # 4. Địa chính trị / Thiên tai / Chiến tranh (Vĩ mô xấu)
        'tấn công', 'trả đũa', 'xung đột', 'chiến tranh', 'leo thang', 'bắn phá',
        'giao tranh', 'trừng phạt', 'cấm vận', 'không kích', 'tên lửa', 'nổ súng',
        'khiêu khích', 'đe dọa', 'bất ổn chính trị', 'bạo loạn', 'khủng bố', 'đảo chính',
        'nguy cơ', 'bất ổn', 'thiếu hụt', 'khẩn cấp', 'thận trọng', 'cảnh báo', 'đổ vỡ',
        'ngõ cụt', 'thu giữ', 'biến động', 'phải trả', 'tụt dốc',

        # 5. Từ đơn tiêu cực (Quét sau cùng)
        'giảm', 'lỗ', 'thủng', 'đáy', 'phạt', 'đỏ', 'sập', 'bắt'
    ]

    # =========================================================================
    # LOGIC QUET THÔNG MINH
    # =========================================================================
    # Bước 1: Quét Tích cực trước vì các CỤM TỪ GHÉP dài giải cứu nằm ở đây (ví dụ: "tháo gỡ khó khăn")
    if any(w in title_lower for w in positive_keywords):
        # Mẹo phụ: Check lại xem có từ phủ định biến tốt thành xấu không (ví dụ: "lãi kỷ lục bị từ chối")
        # Nhưng với RSS đa số cụm từ ghép ở trên đã đủ an toàn.
        return "🟢"
        
    # Bước 2: Quét Tiêu cực sau khi đã loại trừ các cụm từ giải cứu
    elif any(w in title_lower for w in negative_keywords):
        return "🔴"
        
    # Bước 3: Không dính chữ nào ở trên => Trung lập
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
            # Áp dụng Spoofing User-Agent để vượt qua rào cản 403 (Không phải tất cả)
            headers = {'User-Agent': 'Mozilla/5.0'}
            # Thử parse feed với headers
            try:
                # Sử dụng requests để tải nội dung thô trước khi parse (tùy chọn)
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status() # Báo lỗi nếu HTTP code là 4xx hoặc 5xx
                feed = feedparser.parse(response.content)
            except requests.exceptions.HTTPError as errh:
                print(f"LỖI HTTP {errh.response.status_code}: {url}")
                continue
            except requests.exceptions.RequestException as err:
                print(f"LỖI KẾT NỐI {url}: {err}")
                continue
            except Exception:
                # Nếu feedparser không xử lý được (như lỗi XML), bỏ qua
                print(f"LỖI PARSE FEED: {url}")
                continue
            
            for entry in feed.entries[:5]: # Chỉ xem xét 5 tin mới nhất từ mỗi nguồn
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
        
   
          

def send_telegram(news_items, time_str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID or not news_items:
        print("Thiếu cấu hình hoặc không có tin tức!")
        return

    # Chuẩn bị nội dung tin nhắn
    message = f"<b>🔔 CẬP NHẬT THÔNG TIN THỊ TRƯỜNG {time_str}</b>\n\n"
    for item in news_items:
        row = f"{item['icon']} {item['title']} - <a href='{item['link']}'>chi tiết</a>\n\n"
        if len(message) + len(row) + len(FOOTER_TEXT_TELEGRAM) < 4000:
            message += row
        else:
            break
            
    message += FOOTER_TEXT_TELEGRAM

    # MẸO: Lấy link của bài viết đầu tiên chèn vào cuối tin nhắn dưới dạng một dấu chấm ẩn
    # Điều này bắt ép Telegram phải lấy ảnh của bài đầu tiên để làm preview ở dưới cùng
    first_item_link = news_items[0]['link']
    message += f"<a href='{first_item_link}'>&#8205;</a>" # Khung trắng ẩn không gây xấu tin nhắn

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        # --- CẤU HÌNH ĐỂ HIỆN DƯỚI CÙNG VÀ ẢNH TO ---
        "link_preview_options": {
            "is_disabled": False,             # Bật xem trước liên kết
            "prefer_large_media": True,       # Giữ ảnh to đẹp
            "show_above_text": False          # KHÔNG đưa lên đầu nữa, mặc định nằm dưới cùng
        }
    }

    # --- CƠ CHẾ THỬ LẠI (RETRY) ---
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            print("✅ Đã gửi Telegram thành công!")
            return 
        except Exception as e:
            print(f"⚠️ Lần thử {attempt + 1} thất bại: {e}")
            if attempt < max_retries - 1:
                time.sleep(10)
            else:
                print("❌ Đã thử 3 lần nhưng vẫn không thể gửi Telegram.")



def send_discord(news_items, time_str):
    if not DISCORD_WEBHOOK:
        return

    description = ""
    for item in news_items:
        row = f"{item['icon']} {item['title']} - [chi tiết]({item['link']})\n\n"
        if len(description) + len(row) + len(FOOTER_TEXT_DISCORD) < 4000:
            description += row
        else:
            break
            
    description += FOOTER_TEXT_DISCORD

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


# --- HÀM CHÍNH ĐÃ SỬA (GIỚI HẠN SỐ LƯỢNG VÀ LƯU TRẠNG THÁI) ---

if __name__ == "__main__":
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now_str = datetime.now(vn_tz).strftime("%H:%M %d/%m")
    
    print("Đang lấy tin tức...")
    news_data = get_news()
    
    if news_data:
        # GIỚI HẠN: Chỉ lấy MAX_ITEMS_PER_SEND (5) tin mới nhất để gửi
        items_to_send = news_data[:MAX_ITEMS_PER_SEND]
        
        if not items_to_send:
            print("Không có tin tức mới (sau khi lọc/giới hạn)")
            exit()
            
        # Lấy danh sách link của các tin đã được gửi
        links_to_save = [item['link'] for item in items_to_send]

        send_telegram(items_to_send, now_str) 
        send_discord(items_to_send, now_str)   
        
        # LƯU TRẠNG THÁI: Ghi các link vừa gửi vào file để lần sau không gửi lại
        save_sent_links(links_to_save) 
        
    else:
        print("Không có tin tức mới")
