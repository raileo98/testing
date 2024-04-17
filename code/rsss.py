import niquests
from bs4 import BeautifulSoup, CData
import urllib.parse
import html

# 創建一個 niquests 會話
session = niquests.Session(happy_eyeballs=True)
# 設置請求頭部，禁用緩存以獲取最新內容
session.headers['Cache-Control'] = 'no-cache'
session.headers['Pragma'] = 'no-cache'

# 將 urls 列表轉換為字典
feeds = {
    'tw_pts': 'http://localhost:1200/pts',
    'tw_cts': 'http://localhost:1200/cts/real',
    'sg_8world': 'http://localhost:1200/8world',
    'jp_nhk_zt': 'http://localhost:1200/nhk/news/zt',
    'jp_nhk_zh': 'http://localhost:1200/nhk/news/zh',
    'mn_vom': 'http://localhost:1200/vom/featured/zh',
    'hk_rthk_local_ch': 'https://rthk.hk/rthk/news/rss/c_expressnews_clocal.xml',
    'hk_rthk_greaterchina_ch': 'https://rthk.hk/rthk/news/rss/c_expressnews_greaterchina.xml',
    'hk_rthk_international_ch': 'https://rthk.hk/rthk/news/rss/c_expressnews_cinternational.xml',
    'hk_rthk_finance_ch': 'https://rthk.hk/rthk/news/rss/c_expressnews_cfinance.xml',
    'hk_rthk_sport_ch': 'https://rthk.hk/rthk/news/rss/c_expressnews_csport.xml',
    'hk_rthk_local_en': 'https://rthk.hk/rthk/news/rss/e_expressnews_elocal.xml',
    'hk_rthk_greaterchina_en': 'https://rthk.hk/rthk/news/rss/e_expressnews_egreaterchina.xml',
    'hk_rthk_international_en': 'https://rthk.hk/rthk/news/rss/e_expressnews_einternational.xml',
    'hk_rthk_finance_en': 'https://rthk.hk/rthk/news/rss/e_expressnews_efinance.xml',
    'hk_rthk_sport_en': 'https://rthk.hk/rthk/news/rss/e_expressnews_esport.xml',
}

# 遍歷字典中的每個 RSS 源地址
for name, url in feeds.items():
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
        image_url = f"https://external-content.duckduckgo.com/ip3/{encoded_feed_domain}.ico"
        image_tag.find('url').replace_with(root.new_string(CData(image_url)))
    else:
        # 如果不存在 <image> 標籤，則添加一個新的 <image> 標籤
        image_tag = root.new_tag('image')
        url_tag = root.new_tag('url')
        # 設置 <url> 標籤的內容
        image_url = f"https://external-content.duckduckgo.com/ip3/{encoded_feed_domain}.ico"
        url_tag.string = CData(image_url)
        image_tag.append(url_tag)
        # 添加 <title> 和 <link> 標籤
        title_tag = root.new_tag('title')
        title_tag.string = channel.find('title').text
        image_tag.append(title_tag)
        link_tag = root.new_tag('link')
        link_tag.string = channel.find('link').text
        image_tag.append(link_tag)
        # 將 <image> 標籤添加到 <channel> 標籤下
        channel.insert(0, image_tag)

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
                # 替換原始的圖片 URL 為使用 images.weserv.nl 服務的 URL
                new_src = f"https://images.weserv.nl/?n=-1&url={urllib.parse.quote_plus(src)}"
                description_text = description_text.replace(src, new_src)
            # 清空原始的 <description> 標籤內容
            description.string = ''
            # 使用 CDATA 包裹更新後的描述內容，以保持 HTML 標籤不被解析
            description.append(CData(description_text))

    # 將修改後的 XML 內容寫入到對應的 RSS 文件中
    with open(f'{name}.rss', 'w', encoding='utf-8') as file:
        file.write(root.prettify())

# 輸出完成信息
print('所有 RSS 源已經輸出到對應的文件中。')
