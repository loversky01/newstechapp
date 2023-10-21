import sqlite3
import pandas as pd
import google.generativeai as palm

# Kết nối vào cơ sở dữ liệu SQLite
conn = sqlite3.connect('news_data.db')
cursor = conn.cursor()

# Kiểm tra nếu cột 'summary' không tồn tại trong bảng 'news', hãy thêm nó
cursor.execute("PRAGMA table_info(news)")
columns = [column[1] for column in cursor.fetchall()]
if 'summary' not in columns:
    cursor.execute('ALTER TABLE news ADD COLUMN summary TEXT')
    conn.commit()

# Đọc dữ liệu từ cơ sở dữ liệu SQLite và tạo tóm tắt cho các bài viết chỉ khi cột "summary" chưa có giá trị
query = """
    SELECT *
    FROM news
"""
df = pd.read_sql_query(query, conn)

# Đặt kiểu dữ liệu của cột 'summary' thành chuỗi
df['summary'] = ''

# Lặp qua từng hàng trong DataFrame và tạo tóm tắt cho cột "content_html"
for index, row in df.iterrows():
    url = row['url']
    content = row['content_html']

    # Kiểm tra nếu domain không thuộc danh sách các domain được yêu cầu
    if not any(domain in url for domain in ['theverge.com', 'appleinsider.com', 'engadget.com', '9to5google.com', 'gizmodo.com', 'macrumors.com']):
        summary = "Bài viết này không có tóm tắt"
    else:
        text_to_summarize = "Summarize the following text into paragraphs, adding <li> at the beginning:" + content

        # Tạo tóm tắt văn bản bằng mã của bạn
        palm.configure(api_key='AIzaSyA587Mh3lxH3JOIw_5hseKvw5-KsIKhLNs')  # Thay YOUR_API_KEY bằng API key của bạn
        response = palm.generate_text(prompt=text_to_summarize)
        summary = response.result

    # Kiểm tra nếu summary không phải là None trước khi gán giá trị
    if summary is not None:
        # Chuyển đổi giá trị summary sang kiểu chuỗi (string)
        summary = str(summary)

        # Lưu tóm tắt vào cột 'summary' trong DataFrame
        df.at[index, 'summary'] = summary

# Cập nhật cơ sở dữ liệu SQLite với các giá trị đã tạo tóm tắt
df.to_sql('news', conn, if_exists='replace', index=False)

# Đóng kết nối đến cơ sở dữ liệu SQLite
conn.close()
