import niquests
import json
import feedgen.feed

imageCdn = 'https://images.weserv.nl/?n=-1&url='
faviconUrl = f'{ imageCdn }https://external-content.duckduckgo.com/ip3/www.taiwanplus.com.ico'

# 從 TaiwanPlus 獲取 JSON 數據
response = niquests.get( 'https://www.taiwanplus.com/api/cms/latestnews' )
data = response.json()

# 創建一個新的 rss feed
feed = feedgen.feed.FeedGenerator()
feed.id( 'https://www.taiwanplus.com' )
feed.title( 'TaiwanPlus - Latest News' )
feed.description( f'Your source of news, culture, and infotainment from Taiwan, a voice of freedom in Asia.' )
feed.link( href='https://www.taiwanplus.com' )
feed.logo( faviconUrl )

# 遍歷 JSON 數據並將條目添加到 feed 中
for item in data:
    thumbnailUrl = f"{ imageCdn }{ item['image'] }"
    feedDescription = f'<img src={ thumbnailUrl } referrerpolicy=no-referrer><br><br>{ item[ "shortDescription" ] }'
    fullUrl = f'https://www.taiwanplus.com/{ item[ "encodedDefaultCategoryFullPath" ] }/{ item[ "vodId" ] }'

    entry = feed.add_entry()
    entry.id( fullUrl )
    entry.title( item[ 'title' ] )
    entry.description( feedDescription )
    entry.link( href = fullUrl )
    entry.published( item[ 'publishTime' ] )

# 將 feed 輸出為 .rss 文件
feed.rss_file( 'taiwanplus.rss', pretty=True )
