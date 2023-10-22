import sqlite3
import pandas as pd
import google.generativeai as palm

# Kết nối vào cơ sở dữ liệu SQLite
conn = sqlite3.connect('news_data.db')
cursor = conn.cursor()

# Đọc dữ liệu từ cơ sở dữ liệu SQLite
query = """
    SELECT *
    FROM news
"""
df = pd.read_sql_query(query, conn)

# Lặp qua từng hàng trong DataFrame và tạo tóm tắt cho cột "content_html" nếu summary là trống
for index, row in df.iterrows():
    if not row['summary']:  # Chỉ tạo tóm tắt nếu summary là trống
        url = row['url']
        content = row['content_html']

        text_to_summarize = "Summarize the following text into paragraphs, adding <li> at the beginning:" + content

        # Tạo tóm tắt văn bản bằng mã của bạn
        palm.configure(api_key='')  # Thay YOUR_API_KEY bằng API key của bạn
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
