import niquests
import json
import feedgen.feed
import xml.etree.ElementTree as ET

imageCdn = 'https://images.weserv.nl/?n=-1&url='
faviconUrl = f'{ imageCdn }https://external-content.duckduckgo.com/ip3/www.taiwanplus.com.ico'
outputRssName = 'taiwanplus.rss'

# 從 TaiwanPlus 獲取 JSON 數據
response = niquests.get('https://www.taiwanplus.com/api/cms/latestnews')
data = response.json()

# 創建一個新的 rss feed
feed = feedgen.feed.FeedGenerator()
feed.id('https://www.taiwanplus.com')
feed.title('TaiwanPlus - Latest News')
feed.description('Your source of news, culture, and infotainment from Taiwan, a voice of freedom in Asia.')
feed.link(href='https://www.taiwanplus.com', rel='alternate')
feed.logo(faviconUrl)

# 遍歷 JSON 數據並將條目添加到 feed 中
# for item in data['items']:
for item in data:
    thumbnailUrl = f"{imageCdn}{item['image']}"
    feedDescription = f'<img src="{thumbnailUrl}" referrerpolicy="no-referrer"><br>{item["shortDescription"]}'
    fullUrl = f'https://www.taiwanplus.com/{item["encodedDefaultCategoryFullPath"]}/{item["vodId"]}'

    entry = feed.add_entry()
    entry.id(fullUrl)
    entry.title(item['title'])
    entry.description(feedDescription)
    entry.link(href=fullUrl)
    entry.published(item['publishTime'])

# 使用 feed.rss_str() 在內存中創建 RSS 字符串
rss_str = feed.rss_str(pretty=True)

# 使用 ET.fromstring() 從字符串解析 XML
root = ET.fromstring(rss_str)

# 找到<channel>標籤
channel = root.find('channel')

# 在<channel>內找到並刪除<lastBuildDate>標籤
last_build_date = channel.find('lastBuildDate')
if last_build_date is not None:
    channel.remove(last_build_date)

# 使用 tree.write() 將修改後的 XML 樹直接寫入文件
tree = ET.ElementTree(root)
tree.write(outputRssName, encoding='utf-8', xml_declaration=True)
