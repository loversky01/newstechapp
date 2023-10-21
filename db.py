import sqlite3

# Kết nối đến cơ sở dữ liệu hoặc tạo nếu chưa tồn tại
conn = sqlite3.connect('news_data.db')

# Tạo một đối tượng cursor để thực hiện truy vấn SQL
cursor = conn.cursor()

# Tạo bảng với các cột đã chỉ định
cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        original_description TEXT,
        content_html TEXT,
        author TEXT,
        title TEXT,
        keywords TEXT,
        published_date TEXT,
        top_img TEXT,
        all_images TEXT
        
    )
''')

# Lưu các thay đổi vào cơ sở dữ liệu
conn.commit()

# Đóng kết nối đến cơ sở dữ liệu
conn.close()
