import niquests
from bs4 import BeautifulSoup, CData
import urllib.parse
import html

# 創建一個 niquests 會話
session = niquests.Session(happy_eyeballs=True)
session.headers['Cache-Control'] = 'no-cache'
session.headers['Pragma'] = 'no-cache'

# 使用 niquests 獲取 RSS 源 URL
url = 'https://rsshub.app/pts'
response = session.get(url)
xml_content = response.text

# 解析 XML 內容
root = BeautifulSoup(xml_content, 'xml')

# 遍歷所有的 <channel> 標籤
channel = root.find('channel')

# 提取 feed domain
feed_domain = urllib.parse.urlparse(channel.find('link').text).hostname
# 對 feed domain 進行 URL 編碼
encoded_feed_domain = urllib.parse.quote_plus(feed_domain)

# 檢查是否存在 <image> 標籤，如果存在則替換
image_tag = channel.find('image')
if image_tag is not None:
    # 替換 <image> 標籤下的 <url> 標籤內容
    image_tag.find('url').string = f"https://images.weserv.nl/?n=-1&url={urllib.parse.quote_plus('https://external-content.duckduckgo.com/ip3/' + encoded_feed_domain + '.ico')}"
else:
    # 如果不存在 <image> 標籤，則添加
    image_tag = root.new_tag('image')
    url_tag = root.new_tag('url')
    url_tag.string = f"https://images.weserv.nl/?n=-1&url={urllib.parse.quote_plus('https://external-content.duckduckgo.com/ip3/' + encoded_feed_domain + '.ico')}"
    image_tag.append(url_tag)
    title_tag = root.new_tag('title')
    title_tag.string = channel.find('title').text
    image_tag.append(title_tag)
    link_tag = root.new_tag('link')
    link_tag.string = channel.find('link').text
    image_tag.append(link_tag)
    channel.append(image_tag)

# 遍歷所有的 <item> 標籤
for item in root.find_all('item'):
    # 獲取 <description> 標籤
    description = item.find('description')
    if description is not None:
        # 處理 HTML 實體
        description_text = html.unescape(description.text)
        
        # 使用 Beautiful Soup 找到所有的 <img> 標籤
        img_tags = [img['src'] for img in BeautifulSoup(description_text, 'html.parser').find_all('img')]
        
        # 為每個圖片 URL 添加前綴
        for src in img_tags:
            # 對圖片 URL 進行編碼
            encoded_image_url = urllib.parse.quote_plus(src)
            # 添加圖片服務器前綴
            new_src = f"https://images.weserv.nl/?n=-1&url={encoded_image_url}"
            # 替換原始的圖片 URL
            description_text = description_text.replace(src, new_src)
        
        # 使用 CDATA 包裹更新後的描述內容
        description.string = ''
        description.append(CData(description_text))

# 將修改後的 XML 內容寫入到 pts.rss 文件
with open('pts.rss', 'w', encoding='utf-8') as file:
    file.write(root.prettify())

# 文件寫入完成
print('RSS 源已經輸出到 pts.rss 文件中。')
