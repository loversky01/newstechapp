from datetime import datetime
from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# Kết nối tới cơ sở dữ liệu SQLite
def get_db_connection():
    conn = sqlite3.connect('news_data.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route để hiển thị danh sách các tin tức
@app.route('/')
def index():
    conn = get_db_connection()
    
    # Lấy danh sách các bài viết, sắp xếp theo published_date giảm dần
    current_time = datetime.now()
    news = conn.execute('SELECT * FROM news WHERE published_date <= ? ORDER BY published_date DESC', (current_time,)).fetchall()
    
    conn.close()
    return render_template('index.html', news=news)

@app.route('/detail/<int:news_id>')
def detail(news_id):
    conn = get_db_connection()
    news_item = conn.execute('SELECT * FROM news WHERE id = ?', (news_id,)).fetchone()
    conn.close()
    if news_item:
        return render_template('detail.html', news_item=news_item)
    else:
        return "Bài viết không tồn tại."

if __name__ == '__main__':
    app.run(debug=True)
