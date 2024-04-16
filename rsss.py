import niquests
from bs4 import BeautifulSoup, CData
import urllib.parse
import html

# 創建一個 niquests 會話
session = niquests.Session(happy_eyeballs=True)
# 設置請求頭部，禁用緩存以獲取最新內容
session.headers['Cache-Control'] = 'no-cache'
session.headers['Pragma'] = 'no-cache'

urls = [
    'https://rsshub.app/pts',
    'https://rsshub.app/8world',
    'http://localhost:1200/pts',
    'http://localhost:1200/8world'
]

# 遍歷列表中的每個 RSS 源地址
for url in urls:
    # 使用 niquests 發送 HTTP GET 請求到 RSS 源地址
    response = session.get(url)
    # 獲取響應中的 XML 內容
    xml_content = response.text

    # 使用 BeautifulSoup 解析 XML 內容
    root = BeautifulSoup(xml_content, 'xml')
    # 找到 XML 中的 <channel> 標籤
    channel = root.find('channel')

    # 從 <channel> 標籤中提取 feed domain
    feed_domain = urllib.parse.urlparse(channel.find('link').text).hostname
    # 對 feed domain 進行 URL 編碼
    encoded_feed_domain = urllib.parse.quote_plus(feed_domain)

    # 檢查 <channel> 標籤下是否存在 <image> 標籤
    image_tag = channel.find('image')
    if image_tag is not None:
        # 如果存在，則替換 <image> 標籤下的 <url> 標籤內容
        image_tag.find('url').string = f"https://images.weserv.nl/?n=-1&url={urllib.parse.quote_plus('https://external-content.duckduckgo.com/ip3/' + encoded_feed_domain + '.ico')}"
    else:
        # 如果不存在 <image> 標籤，則添加一個新的 <image> 標籤
        image_tag = root.new_tag('image')
        url_tag = root.new_tag('url')
        # 設置 <url> 標籤的內容
        url_tag.string = f"https://images.weserv.nl/?n=-1&url={urllib.parse.quote_plus('https://external-content.duckduckgo.com/ip3/' + encoded_feed_domain + '.ico')}"
        image_tag.append(url_tag)
        # 添加 <title> 和 <link> 標籤
        title_tag = root.new_tag('title')
        title_tag.string = channel.find('title').text
        image_tag.append(title_tag)
        link_tag = root.new_tag('link')
        link_tag.string = channel.find('link').text
        image_tag.append(link_tag)
        # 將 <image> 標籤添加到 <channel> 標籤下
        channel.append(image_tag)

    # 遍歷 <channel> 標籤下的所有 <item> 標籤
    for item in root.find_all('item'):
        # 獲取每個 <item> 標籤下的 <description> 標籤
        description = item.find('description')
        if description is not None:
            # 對 <description> 標籤的內容進行 HTML 實體解碼
            description_text = html.unescape(description.text)
            # 使用 BeautifulSoup 找到所有的 <img> 標籤
            img_tags = [img['src'] for img in BeautifulSoup(description_text, 'html.parser').find_all('img')]
            # 遍歷所有的圖片 URL
            for src in img_tags:
                # 對圖片 URL 進行 URL 編碼
                encoded_image_url = urllib.parse.quote_plus(src)
                # 替換原始的圖片 URL 為使用 images.weserv.nl 服務的 URL
                new_src = f"https://images.weserv.nl/?n=-1&url={encoded_image_url}"
                description_text = description_text.replace(src, new_src)
            # 清空原始的 <description> 標籤內容
            description.string = ''
            # 使用 CDATA 包裹更新後的描述內容，以保持 HTML 標籤不被解析
            description.append(CData(description_text))

    # 將修改後的 XML 內容寫入到對應的 RSS 文件中
    with open(f'{urllib.parse.urlparse(url).hostname}.rss', 'w', encoding='utf-8') as file:
        file.write(root.prettify())

# 輸出完成信息
print('所有 RSS 源已經輸出到對應的文件中。')
