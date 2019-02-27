import requests
import lxml.html
import time
import pandas as pd
import re
from bs4 import BeautifulSoup


headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }


def run(searchkeyword):
    urldict = get_all_keyword_news_url(searchkeyword)
    contentall = []
    for pageurl in urldict.keys():
        #data是否有多个值？
        time.sleep(1)
        print('parsing comment:', pageurl)
        data = form_data(pageurl)
        while 1:
            commentpagenum = requests.post('https://dyn.ithome.com/ithome/getajaxdata.aspx',data=data)
            time.sleep(1)
            print(len(commentpagenum.text))
            if len(commentpagenum.text) == 0:
                break
            pagesoup = get_comment_page(data)
            title = urldict[pageurl]
            df = parse_comment(pagesoup,title)
            contentall.append(df)
            data['page'] += 1
    final_df = pd.concat(contentall, ignore_index=True)
    final_df = final_df.drop_duplicates()
    final_df.to_csv('C:/Users/Administrator/Desktop/test123.csv',encoding='utf-8-sig',index=False)


def get_all_keyword_news_url(searchkeyword):
    searchkeywordtoutf8 = str(searchkeyword.encode("utf-8"))[1:].replace('\\x','%').replace('\'','')
    searchurl = 'https://dyn.ithome.com/search/adt_all_' + searchkeywordtoutf8 +'_0.html'
    rsurl = requests.get(searchurl,headers=headers)
    html = lxml.html.fromstring(rsurl.text)
    if html.xpath('//div[@class="pagenew"]'):
        page = html.xpath('//div[@class="pagenew"]/input[@type="button"]/@onclick')[0]
        pageregex =  re.compile("'Pager_input',(.*?),'页索")
        pagenum = re.search(pageregex,page).group(1)
        pagenum = int(pagenum)
    else:
        pagenum = 1
    urldict = {}
    for i in range(1,pagenum+1):
        time.sleep(1)
        searchpageurl = 'https://dyn.ithome.com/search/adt_all_' + searchkeywordtoutf8 + '_0_' + str(i) + '.html'
        print('getting all keyword news url:',searchpageurl)
        rssearchpageurl = requests.get(searchpageurl, headers=headers)
        rssearchpageurlsoup =  BeautifulSoup(rssearchpageurl.text, 'lxml')
        listlist = rssearchpageurlsoup.find_all('a',class_='list_thumbnail')
        for infor in listlist:
            hrefurl = infor.attrs['href']
            title = infor.img.attrs['alt']
            urldict[hrefurl] = title
    return urldict


def form_data(pageurl):
    pageurl = pageurl
    pagecataflag = True if '0' in pageurl.split('/') else 0
    if pagecataflag:
        newsid = ''.join(pageurl.split('/')[-2:]).replace('.htm','')
    else:
        newsid = ''.join(pageurl.split('/')[-1]).replace('.htm', '')
    hashurl = 'http://dyn.ithome.com/comment/'+newsid
    rs = requests.get(hashurl, headers=headers)
    regex = re.compile('var ch11 =(.*?);')
    if re.search(regex,rs.text):
        hashcode = re.search(regex, rs.text).group(1).replace('\'','').replace(' ','')
    data = {
        'newsID': newsid,
        'hash': hashcode,
        'type': 'commentpage',
        'page': 1,
        'order': 'false',
    }
    return data


def get_comment_page(data):
    rs = requests.post('https://dyn.ithome.com/ithome/getajaxdata.aspx',data=data)
    soup = BeautifulSoup(rs.text, 'lxml')
    return soup


def parse_comment(soup,title):
    contentall = []
    li_list = soup.find_all('li', class_='entry')
    reli_list = soup.find_all('li', class_='gh')
    for li in li_list:
        nickname = li.find('span', class_='nick').text
        comment = li.find('p').text
        like = li.find('a', class_='s').text
        like = re.search('\d+',like).group()
        dislike = li.find('a', class_='a').text
        dislike = re.search('\d+', dislike).group()
        phone = li.find('a', attrs={'href':'//m.ithome.com/ithome/download/'}).text if li.find('a', attrs={'href':'//m.ithome.com/ithome/download/'}) else 0
        positiontime = li.find('span', class_='posandtime').text
        position = re.search('\w+',positiontime).group()
        time = re.search('\d+-\d+-\d+ \d+:\d+:\d+',positiontime).group()
        contentall.append([title,nickname,comment,like,dislike,phone,position,time])
    for li in reli_list:
        nickname = li.find('span', class_='nick').text
        comment = li.find('p').text
        like = li.find('a', class_='s').text
        like = re.search('\d+',like).group()
        dislike = li.find('a', class_='a').text
        dislike = re.search('\d+', dislike).group()
        phone = li.find('a', attrs={'href':'//m.ithome.com/ithome/download/'}).text if li.find('a', attrs={'href':'//m.ithome.com/ithome/download/'}) else 0
        positiontime = li.find('span', class_='posandtime').text
        position = re.search('\w+',positiontime).group()
        time = re.search('\d+-\d+-\d+ \d+:\d+:\d+',positiontime).group()
        contentall.append([title,nickname,comment,like,dislike,phone,position,time])
    df = pd.DataFrame(contentall,columns=['title','nickname','comment','like','dislike','phone','position','time'])
    return df

searchkeyword = 'nubia α'
run(searchkeyword)

