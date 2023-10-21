import sqlite3
from newspaper import Article
import validators
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

# Function to check if a URL is valid
def is_url(url):
    return validators.url(url)

# Function to check if a URL is a YouTube URL
def is_youtube_url(url):
    return 'youtube.com' in url or 'youtu.be' in url

# Function to crawl a URL and extract data
def crawl(url):
    try:
        if not is_url(url):
            raise Exception('Invalid URL!')

        # Check if the URL is a YouTube URL and remove it from the SQLite database
        if is_youtube_url(url):
            print("URL is a YouTube link. Removing from the database:", url)
            conn = sqlite3.connect('news_data.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM news WHERE url=?', (url,))
            conn.commit()
            conn.close()
            return  # Stop processing and do not return any result for YouTube URLs

        article = Article(url)
        article.download()
        article.parse()
        
        if article is None:
            raise Exception('Failed to retrieve article content.')

        all_images = ', '.join(article.images)
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        seen_tags = set()
        seen_links = set()
        seen_images_src = set()  # Keep track of seen image srcs

        if domain == 'www.theverge.com':
            # Sử dụng BeautifulSoup để phân tích cú pháp HTML
            soup = BeautifulSoup(article.html, 'html.parser')

            # Tìm thẻ div cụ thể bạn muốn lấy bằng class
            specific_div = soup.find(
                'div', class_='duet--article--article-body-component-container clearfix sm:ml-auto md:ml-100 md:max-w-article-body lg:mx-100')

            # Khởi tạo danh sách để chứa các thẻ quan trọng
            important_tags = []

            seen_links = set()  # Tạo một set để lưu trữ các liên kết duy nhất
            
            seen_a_tag = False
            # Lấy danh sách các thẻ <p>, <a>, <img>, <li>, và các thẻ quan trọng khác
            if specific_div:
                for tag in specific_div.find_all(['p', 'a', 'img', 'li','h1','h2','h3']):
                    if tag.name == 'img':
                        img_src = tag.get('src', '')
                        if img_src not in seen_images_src:
                            seen_images_src.add(img_src)
                            del tag['decoding']
                            del tag['data-nimg']
                            del tag['style']
                            del tag['sizes']
                            del tag['srcset']
                            parent_a = tag.find_parent('a')
                            if parent_a and not seen_a_tag:
                                important_tags.append(str(tag))
                            else:
                                important_tags.append(str(tag))
                    elif tag.name == 'a' and 'href' in tag.attrs:
                        link_href = tag['href']
                        if link_href not in seen_links:
                            seen_links.add(link_href)
                            if not seen_a_tag:
                                important_tags.append(str(tag))
                                seen_a_tag = True
                    else:
                        for attr in ["class", "id"]:
                            del tag[attr]
                        tag_str = str(tag)
                        if tag_str not in seen_tags:
                            important_tags.append(tag_str)

                content_html = ''.join(important_tags)
       
        # Add handling for other domains here...
        elif domain == 'www.engadget.com':
            # Xử lý nội dung từ "https://www.engadget.com/"
            soup = BeautifulSoup(article.html, 'html.parser')

            # Tìm thẻ div cụ thể bạn muốn lấy (class 'article-content')
            specific_div = soup.find('div', class_='caas-body')

            # Khởi tạo danh sách để chứa các thẻ quan trọng
            important_tags = []

            seen_links = set()  # Tạo một set để lưu trữ các liên kết duy nhất
            
            seen_a_tag = False
            # Lấy danh sách các thẻ <p>, <a>, <img>, <li>, và các thẻ quan trọng khác
            if specific_div:
                for tag in specific_div.find_all(['p', 'a', 'img', 'li']):
                    if tag.name == 'img':
                        img_src = tag.get('src', '')
                        if img_src not in seen_images_src:
                            seen_images_src.add(img_src)
                            del tag['decoding']
                            del tag['data-nimg']
                            del tag['style']
                            del tag['sizes']
                            del tag['srcset']
                            parent_a = tag.find_parent('a')
                            if parent_a and not seen_a_tag:
                                important_tags.append(str(tag))
                            else:
                                important_tags.append(str(tag))
                    elif tag.name == 'a' and 'href' in tag.attrs:
                        link_href = tag['href']
                        if link_href not in seen_links:
                            seen_links.add(link_href)
                            if not seen_a_tag:
                                important_tags.append(str(tag))
                                seen_a_tag = True
                    else:
                        for attr in ["class", "id"]:
                            del tag[attr]
                        tag_str = str(tag)
                        if tag_str not in seen_tags:
                            important_tags.append(tag_str)


                content_html = ''.join(important_tags)

        elif domain == '9to5google.com':
            # Xử lý nội dung từ "https://9to5google.com/"
            soup = BeautifulSoup(article.html, 'html.parser')

            # Tìm thẻ div cụ thể bạn muốn lấy (class 'article-content')
            specific_div = soup.find(
                'div', class_='container med post-content')

            # Khởi tạo danh sách để chứa các thẻ quan trọng
            important_tags = []

            seen_links = set()  # Tạo một set để lưu trữ các liên kết duy nhất
            
            seen_a_tag = False
            # Lấy danh sách các thẻ <p>, <a>, <img>, <li>, và các thẻ quan trọng khác
            if specific_div:
                for tag in specific_div.find_all(['p', 'a', 'img', 'li']):
                    if tag.name == 'img':
                        img_src = tag.get('src', '')
                        if img_src not in seen_images_src:
                            seen_images_src.add(img_src)
                            del tag['decoding']
                            del tag['data-nimg']
                            del tag['style']
                            del tag['sizes']
                            del tag['srcset']
                            parent_a = tag.find_parent('a')
                            if parent_a and not seen_a_tag:
                                important_tags.append(str(tag))
                            else:
                                important_tags.append(str(tag))
                    elif tag.name == 'a' and 'href' in tag.attrs:
                        link_href = tag['href']
                        if link_href not in seen_links:
                            seen_links.add(link_href)
                            if not seen_a_tag:
                                important_tags.append(str(tag))
                                seen_a_tag = True
                    else:
                        for attr in ["class", "id"]:
                            del tag[attr]
                        tag_str = str(tag)
                        if tag_str not in seen_tags:
                            important_tags.append(tag_str)

                content_html = ''.join(important_tags)
            # ...
        elif domain == 'https://www.macrumors.com/':
            # Xử lý nội dung từ "https://www.macrumors.com/"
            soup = BeautifulSoup(article.html, 'html.parser')

            # Tìm thẻ div cụ thể bạn muốn lấy (class 'ugc--2nTu61bm minor--3O_9dH4U')
            specific_div = soup.find('div', class_='ugc--2nTu61bm minor--3O_9dH4U')

            # Khởi tạo danh sách để chứa các thẻ quan trọng
            important_tags = []
            seen_links = set()  # Tạo một set để lưu trữ các liên kết duy nhất
            
            seen_a_tag = False
            # Lấy danh sách các thẻ <p>, <a>, <img>, <li>, và các thẻ quan trọng khác
            if specific_div:
                for tag in specific_div.find_all(['p', 'a', 'img', 'li','h1','h2','h3']):
                    if tag.name == 'img':
                        img_src = tag.get('src', '')
                        if img_src not in seen_images_src:
                            seen_images_src.add(img_src)
                            del tag['decoding']
                            del tag['data-nimg']
                            del tag['style']
                            del tag['sizes']
                            del tag['srcset']
                            parent_a = tag.find_parent('a')
                            if parent_a and not seen_a_tag:
                                important_tags.append(str(tag))
                            else:
                                important_tags.append(str(tag))
                    elif tag.name == 'a' and 'href' in tag.attrs:
                        link_href = tag['href']
                        if link_href not in seen_links:
                            seen_links.add(link_href)
                            if not seen_a_tag:
                                important_tags.append(str(tag))
                                seen_a_tag = True
                    else:
                        for attr in ["class", "id"]:
                            del tag[attr]
                        tag_str = str(tag)
                        if tag_str not in seen_tags:
                            important_tags.append(tag_str)

                content_html = ''.join(important_tags)
        elif domain == 'https://techcrunch.com/':
            # Xử lý nội dung từ "https://techcrunch.com/"
            soup = BeautifulSoup(article.html, 'html.parser')

            # Tìm thẻ div cụ thể bạn muốn lấy (class 'ugc--2nTu61bm minor--3O_9dH4U')
            specific_div = soup.find('div', class_="article-content")

            # Khởi tạo danh sách để chứa các thẻ quan trọng
            important_tags = []

            seen_links = set()  # Tạo một set để lưu trữ các liên kết duy nhất
            
            seen_a_tag = False
            # Lấy danh sách các thẻ <p>, <a>, <img>, <li>, và các thẻ quan trọng khác
            if specific_div:
                for tag in specific_div.find_all(['p', 'a', 'img', 'li']):
                    if tag.name == 'img':
                        img_src = tag.get('src', '')
                        if img_src not in seen_images_src:
                            seen_images_src.add(img_src)
                            del tag['decoding']
                            del tag['data-nimg']
                            del tag['style']
                            del tag['sizes']
                            del tag['srcset']
                            parent_a = tag.find_parent('a')
                            if parent_a and not seen_a_tag:
                                important_tags.append(str(tag))
                            else:
                                important_tags.append(str(tag))
                    elif tag.name == 'a' and 'href' in tag.attrs:
                        link_href = tag['href']
                        if link_href not in seen_links:
                            seen_links.add(link_href)
                            if not seen_a_tag:
                                important_tags.append(str(tag))
                                seen_a_tag = True
                    else:
                        for attr in ["class", "id"]:
                            del tag[attr]
                        tag_str = str(tag)
                        if tag_str not in seen_tags:
                            important_tags.append(tag_str)

                content_html = ''.join(important_tags)
        elif domain == 'https://www.cnet.com/':
            # Xử lý nội dung từ "https://techcrunch.com/"
            soup = BeautifulSoup(article.html, 'html.parser')

            # Tìm thẻ div cụ thể bạn muốn lấy (class 'ugc--2nTu61bm minor--3O_9dH4U')
            specific_div = soup.find('div', class_="c-pageArticle_content")

            # Khởi tạo danh sách để chứa các thẻ quan trọng
            important_tags = []

            seen_links = set()  # Tạo một set để lưu trữ các liên kết duy nhất
            
            seen_a_tag = False
            # Lấy danh sách các thẻ <p>, <a>, <img>, <li>, và các thẻ quan trọng khác
            if specific_div:
                for tag in specific_div.find_all(['p', 'a', 'img', 'li']):
                    if tag.name == 'img':
                        img_src = tag.get('src', '')
                        if img_src not in seen_images_src:
                            seen_images_src.add(img_src)
                            del tag['decoding']
                            del tag['data-nimg']
                            del tag['style']
                            del tag['sizes']
                            del tag['srcset']
                            parent_a = tag.find_parent('a')
                            if parent_a and not seen_a_tag:
                                important_tags.append(str(tag))
                            else:
                                important_tags.append(str(tag))
                    elif tag.name == 'a' and 'href' in tag.attrs:
                        link_href = tag['href']
                        if link_href not in seen_links:
                            seen_links.add(link_href)
                            if not seen_a_tag:
                                important_tags.append(str(tag))
                                seen_a_tag = True
                    else:
                        for attr in ["class", "id"]:
                            del tag[attr]
                        tag_str = str(tag)
                        if tag_str not in seen_tags:
                            important_tags.append(tag_str)

                content_html = ''.join(important_tags)
        elif domain == 'https://9to5mac.com/':
            # Xử lý nội dung từ "https://techcrunch.com/"
            soup = BeautifulSoup(article.html, 'html.parser')

            # Tìm thẻ div cụ thể bạn muốn lấy (class 'container med post-content')
            specific_div = soup.find('div', class_="container med post-content")

            # Khởi tạo danh sách để chứa các thẻ quan trọng
            important_tags = []

            seen_links = set()  # Tạo một set để lưu trữ các liên kết duy nhất
            
            seen_a_tag = False
            # Lấy danh sách các thẻ <p>, <a>, <img>, <li>, và các thẻ quan trọng khác
            if specific_div:
                for tag in specific_div.find_all(['p', 'a', 'img', 'li','h1','h2']):
                    if tag.name == 'img':
                        img_src = tag.get('src', '')
                        if img_src not in seen_images_src:
                            seen_images_src.add(img_src)
                            del tag['decoding']
                            del tag['data-nimg']
                            del tag['style']
                            del tag['sizes']
                            del tag['srcset']
                            parent_a = tag.find_parent('a')
                            if parent_a and not seen_a_tag:
                                important_tags.append(str(tag))
                            else:
                                important_tags.append(str(tag))
                    elif tag.name == 'a' and 'href' in tag.attrs:
                        link_href = tag['href']
                        if link_href not in seen_links:
                            seen_links.add(link_href)
                            if not seen_a_tag:
                                important_tags.append(str(tag))
                                seen_a_tag = True
                    else:
                        for attr in ["class", "id"]:
                            del tag[attr]
                        tag_str = str(tag)
                        if tag_str not in seen_tags:
                            important_tags.append(tag_str)

                content_html = ''.join(important_tags)
        elif domain == 'https://www.windowscentral.com/':
            # Xử lý nội dung từ "https://techcrunch.com/"
            soup = BeautifulSoup(article.html, 'html.parser')

            # Tìm thẻ div cụ thể bạn muốn lấy (class 'container med post-content')
            specific_div = soup.find('div', class_="text-copy bodyCopy auto")

            # Khởi tạo danh sách để chứa các thẻ quan trọng
            important_tags = []

            seen_links = set()  # Tạo một set để lưu trữ các liên kết duy nhất
            
            seen_a_tag = False
            # Lấy danh sách các thẻ <p>, <a>, <img>, <li>, và các thẻ quan trọng khác
            if specific_div:
                for tag in specific_div.find_all(['p', 'a', 'img', 'li']):
                    if tag.name == 'img':
                        img_src = tag.get('src', '')
                        if img_src not in seen_images_src:
                            seen_images_src.add(img_src)
                            del tag['decoding']
                            del tag['data-nimg']
                            del tag['style']
                            del tag['sizes']
                            del tag['srcset']
                            parent_a = tag.find_parent('a')
                            if parent_a and not seen_a_tag:
                                important_tags.append(str(tag))
                            else:
                                important_tags.append(str(tag))
                    elif tag.name == 'a' and 'href' in tag.attrs:
                        link_href = tag['href']
                        if link_href not in seen_links:
                            seen_links.add(link_href)
                            if not seen_a_tag:
                                important_tags.append(str(tag))
                                seen_a_tag = True
                    else:
                        for attr in ["class", "id"]:
                            del tag[attr]
                        tag_str = str(tag)
                        if tag_str not in seen_tags:
                            important_tags.append(tag_str)

                content_html = ''.join(important_tags)
        elif domain == 'https://bgr.com/':
            # Xử lý nội dung từ "https://techcrunch.com/"
            soup = BeautifulSoup(article.html, 'html.parser')

            # Tìm thẻ div cụ thể bạn muốn lấy (class 'container med post-content')
            specific_div = soup.find('div', class_="entry-content no-dropcap")

            # Khởi tạo danh sách để chứa các thẻ quan trọng
            important_tags = []

            seen_links = set()  # Tạo một set để lưu trữ các liên kết duy nhất
            
            seen_a_tag = False
            # Lấy danh sách các thẻ <p>, <a>, <img>, <li>, và các thẻ quan trọng khác
            if specific_div:
                for tag in specific_div.find_all(['p', 'a', 'img', 'li']):
                    if tag.name == 'img':
                        img_src = tag.get('src', '')
                        if img_src not in seen_images_src:
                            seen_images_src.add(img_src)
                            del tag['decoding']
                            del tag['data-nimg']
                            del tag['style']
                            del tag['sizes']
                            del tag['srcset']
                            parent_a = tag.find_parent('a')
                            if parent_a and not seen_a_tag:
                                important_tags.append(str(tag))
                            else:
                                important_tags.append(str(tag))
                    elif tag.name == 'a' and 'href' in tag.attrs:
                        link_href = tag['href']
                        if link_href not in seen_links:
                            seen_links.add(link_href)
                            if not seen_a_tag:
                                important_tags.append(str(tag))
                                seen_a_tag = True
                    else:
                        for attr in ["class", "id"]:
                            del tag[attr]
                        tag_str = str(tag)
                        if tag_str not in seen_tags:
                            important_tags.append(tag_str)

                content_html = ''.join(important_tags)
        elif domain == 'https://gizmodo.com/':
            # Xử lý nội dung từ "https://techcrunch.com/"
            soup = BeautifulSoup(article.html, 'html.parser')

            # Tìm thẻ div cụ thể bạn muốn lấy (class 'container med post-content')
            specific_div = soup.find('div', class_="sc-r43lxo-1 cwnrYD")

            # Khởi tạo danh sách để chứa các thẻ quan trọng
            important_tags = []

            seen_links = set()  # Tạo một set để lưu trữ các liên kết duy nhất
            
            seen_a_tag = False
            # Lấy danh sách các thẻ <p>, <a>, <img>, <li>, và các thẻ quan trọng khác
            if specific_div:
                for tag in specific_div.find_all(['p', 'a', 'img', 'li']):
                    if tag.name == 'img':
                        img_src = tag.get('src', '')
                        if img_src not in seen_images_src:
                            seen_images_src.add(img_src)
                            del tag['decoding']
                            del tag['data-nimg']
                            del tag['style']
                            del tag['sizes']
                            del tag['srcset']
                            parent_a = tag.find_parent('a')
                            if parent_a and not seen_a_tag:
                                important_tags.append(str(tag))
                            else:
                                important_tags.append(str(tag))
                    elif tag.name == 'a' and 'href' in tag.attrs:
                        link_href = tag['href']
                        if link_href not in seen_links:
                            seen_links.add(link_href)
                            if not seen_a_tag:
                                important_tags.append(str(tag))
                                seen_a_tag = True
                    else:
                        for attr in ["class", "id"]:
                            del tag[attr]
                        tag_str = str(tag)
                        if tag_str not in seen_tags:
                            important_tags.append(tag_str)

                content_html = ''.join(important_tags)
        elif domain == 'https://www.androidpolice.com/':
            # Xử lý nội dung từ "https://techcrunch.com/"
            soup = BeautifulSoup(article.html, 'html.parser')

            # Tìm thẻ div cụ thể bạn muốn lấy (class 'class="content-block-regular"')
            specific_div = soup.find('div', class_="content-block-regular")

            # Khởi tạo danh sách để chứa các thẻ quan trọng
            important_tags = []

            seen_links = set()  # Tạo một set để lưu trữ các liên kết duy nhất
            
            seen_a_tag = False
            # Lấy danh sách các thẻ <p>, <a>, <img>, <li>, và các thẻ quan trọng khác
            if specific_div:
                for tag in specific_div.find_all(['p', 'a', 'img', 'li']):
                    if tag.name == 'img':
                        img_src = tag.get('src', '')
                        if img_src not in seen_images_src:
                            seen_images_src.add(img_src)
                            del tag['decoding']
                            del tag['data-nimg']
                            del tag['style']
                            del tag['sizes']
                            del tag['srcset']
                            parent_a = tag.find_parent('a')
                            if parent_a and not seen_a_tag:
                                important_tags.append(str(tag))
                            else:
                                important_tags.append(str(tag))
                    elif tag.name == 'a' and 'href' in tag.attrs:
                        link_href = tag['href']
                        if link_href not in seen_links:
                            seen_links.add(link_href)
                            if not seen_a_tag:
                                important_tags.append(str(tag))
                                seen_a_tag = True
                    else:
                        for attr in ["class", "id"]:
                            del tag[attr]
                        tag_str = str(tag)
                        if tag_str not in seen_tags:
                            important_tags.append(tag_str)

                content_html = ''.join(important_tags)
        elif domain == 'https://www.notebookcheck.net/':
            # Xử lý nội dung từ "https://techcrunch.com/"
            soup = BeautifulSoup(article.html, 'html.parser')
#class="content-body"
            specific_div = soup.find('id', id_="content")

            # Khởi tạo danh sách để chứa các thẻ quan trọng
            important_tags = []

            seen_links = set()  # Tạo một set để lưu trữ các liên kết duy nhất
            
            seen_a_tag = False
            # Lấy danh sách các thẻ <p>, <a>, <img>, <li>, và các thẻ quan trọng khác
            if specific_div:
                for tag in specific_div.find_all(['p', 'a', 'img', 'li']):
                    if tag.name == 'img':
                        img_src = tag.get('src', '')
                        if img_src not in seen_images_src:
                            seen_images_src.add(img_src)
                            del tag['decoding']
                            del tag['data-nimg']
                            del tag['style']
                            del tag['sizes']
                            del tag['srcset']
                            parent_a = tag.find_parent('a')
                            if parent_a and not seen_a_tag:
                                important_tags.append(str(tag))
                            else:
                                important_tags.append(str(tag))
                    elif tag.name == 'a' and 'href' in tag.attrs:
                        link_href = tag['href']
                        if link_href not in seen_links:
                            seen_links.add(link_href)
                            if not seen_a_tag:
                                important_tags.append(str(tag))
                                seen_a_tag = True
                    else:
                        for attr in ["class", "id"]:
                            del tag[attr]
                        tag_str = str(tag)
                        if tag_str not in seen_tags:
                            important_tags.append(tag_str)

                content_html = ''.join(important_tags)
        else:
            content_html = re.sub('\\n+', '</p><p>', '<p>' + article.text + '</p>')

        result = {
            'url': url,
            'content_html': content_html,
            'author': ', '.join(article.authors),
            'title': article.title,
            'keywords': ', '.join(article.keywords if article.keywords else (
                article.meta_keywords if article.meta_keywords else article.meta_data.get('keywords', []))),
            'published_date': article.publish_date if article.publish_date else article.meta_data.get('pubdate', ''),
            'top_img': article.top_image,
            'all_images': all_images,
        }
    except Exception as e:
        result = {
            'url': url,
            'content_html': '',
            'author': '',
            'title': '',
            'keywords': '',
            'published_date': '',
            'top_img': '',
            'all_images': '',
        }

    return result

def save_to_database(data):
    try:
        conn = sqlite3.connect('news_data.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM news WHERE url=?', (data['url'],))
        existing_record = cursor.fetchone()

        if existing_record:
            cursor.execute('''
                UPDATE news
                SET content_html=?, author=?, title=?, keywords=?, published_date=?, top_img=?, all_images=?
                WHERE url=?
            ''', (
                data['content_html'], data['author'], data['title'], data['keywords'],
                data['published_date'], data['top_img'], data['all_images'], data['url']
            ))
        else:
            cursor.execute('''
                INSERT INTO news (url, content_html, author, title, keywords, published_date, top_img, all_images)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['url'], data['content_html'], data['author'], data['title'], data['keywords'],
                data['published_date'], data['top_img'], data['all_images']
            ))

        conn.commit()

    except sqlite3.Error as err:
        print("SQLite Error:", err)
    finally:
        conn.close()

if __name__ == '__main__':
    try:
        conn = sqlite3.connect('news_data.db')
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(news)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'content_html' not in columns:
            cursor.execute('ALTER TABLE news ADD COLUMN content_html TEXT')
            conn.commit()

        cursor.execute('SELECT url FROM news')
        urls = [row[0] for row in cursor.fetchall()]

        for url in urls:
            if is_youtube_url(url):
                print("URL is a YouTube link. Removing from the database:", url)
                cursor.execute('DELETE FROM news WHERE url=?', (url,))
                conn.commit()
                continue

            result = crawl(url)
            save_to_database(result)

    except sqlite3.Error as err:
        print("SQLite Error:", err)
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()
