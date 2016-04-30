import requests
from bs4 import BeautifulSoup
import re
import csv
import time
import codecs
class weibo:
    url = 'http://weibo.cn/'
    userId = '2714280233'
    userName = 'xiaopapi'
    pageInfo = '?page='
    pageNumber = 1
    pageTotal = 0

    weiboCount = 0

    csvFile = codecs.open('weibo.csv', 'w', 'utf-8');
    writer = csv.writer(csvFile)
    writer.writerow(['userId', 'contentId', 'forwardFlag', 'content', 'originalLikeNum', 'originalForwardNum', 'originalRemarkNum',
                     'likeNum', 'forwardNum', 'RemarkNum', 'time', 'source', 'tag'])
    #此处请自行更改
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN',
        'Connection': 'keep-alive',
        'Host': 'weibo.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'
    }
    #此处请自行更改
    cook = {"Cookie": "SUHB=0cSnCNozKk-euy; _T_WM=c61e3979eebc0c590a9a845deb0cd533; SUB=_2A256Cn8FDeRxGeVP7lQW-SzJzz-IHXVZ9QFNrDV6PUJbstBeLVmjkW1LHesLXeK0FTi6uzasx-r_LJzIjhKpsg..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFT4E9cDTbFNB6gjZHDS-RJ5JpX5o2p; gsid_CTandWM=4ubgCpOz5iJAwSLfwh9b3dfe08L"}


    def __init__(self, userId):
        self.userId = userId

    def initWeb(self):
        html = requests.get(self.url + str(self.userId), cookies=self.cook, headers=self.header).text
        soup = BeautifulSoup(html, "html.parser")
        #初始化总页面数
        self.getPageTotal(soup)
        return soup

    def getUserId(self):
        return self.userId

    def setUserId(self, userId):
        self.userId = userId

    def getUserName(self):
        return self.userName

    def setUserName(self, userName):
        self.userName = userName

    def getPage(self, pageNum):
        html = requests.get(self.url + self.userId + self.pageInfo + str(pageNum), cookies=self.cook, headers=self.header).text
        soup = BeautifulSoup(html, "html.parser")
        return soup

    def getUserInfo(self, soup):
        user = soup.find('div', {'class': 'ut'})
        nPos = user.text.index(' ');
        print('用户名: ' + user.text[0:nPos])
        print('用户签名: ' + user.contents[4].text)
        print('用户Id: ' + re.search('\d+', user.contents[8]['href']).group())
        count = 0
        userRelateNum = soup.find('div', {'class': 'tip2'})
        for child in userRelateNum.children:
            count += 1
            if count == 1:
                print('微博数: ' + re.search('\d+', child.string).group())
            elif count == 3:
                print('关注人数: ' + re.search('\d+', child.string).group())
            elif count == 5:
                print('粉丝数: ' + re.search('\d+', child.string).group())

    def getPageTotal(self, soup):
        pageTotalNum = soup.find('div', {'class': 'pa'}).form.div.contents[2]['value']
        self.pageTotal = int(pageTotalNum)

    def getUserWeibo(self, soup):
        weiboContentHtml = soup.find_all('div', {'class': 'c'})
        lens = len(weiboContentHtml)
        #print('本页面微博数 '+str(lens-2))
        for i in range(0, lens-2):
            weiboInfoCsv = []
            tag = ''
            time = ''

            #微博主ID
            weiboInfoCsv.append(self.userId)

            # 'ctt'表示原创微博
            #微博ID
            weiboInfoCsv.append(weiboContentHtml[i]['id'])
            if weiboContentHtml[i].div.span['class'][0] == 'ctt':
                # 微博数目不断增加
                self.weiboCount += 1
                #是否转发标志
                weiboInfoCsv.append('false')
                #微博内容
                weiboContent = weiboContentHtml[i].div.span.text
                tagResult = re.search('#(.*)#', weiboContent)
                if tagResult is None:
                    tag = ''
                else:
                    #将微博内容中的标签信息去掉
                    beginPos = weiboContent.index('#')
                    endPos = weiboContent.index('#', beginPos+1, len(weiboContent))
                    tag = weiboContent[beginPos+1:endPos]
                    weiboContent = weiboContent[:beginPos] + weiboContent[endPos+1:]
                #去掉微博正文后http链接
                if 'http' in weiboContent:
                    posBegin = weiboContent.index('http')
                    if weiboContent.rfind(' ', posBegin, len(weiboContent)) == -1:
                        weiboContent = weiboContent[:posBegin]
                    else:
                        posEnd = weiboContent.rfind(' ', posBegin, len(weiboContent))
                        weiboContent = weiboContent[:posBegin] + weiboContent[posEnd:]
                weiboInfoCsv.append(weiboContent)
                #因为原创，故没有原文点赞、转发、评论数
                weiboInfoCsv.append(' ')
                weiboInfoCsv.append(' ')
                weiboInfoCsv.append(' ')
                #print('第' + str(self.weiboCount) + '条: ' + '原创: ' + weiboContent)
                # 原创微博有图
                if len(weiboContentHtml[i].contents) == 2:
                    contentInfos = weiboContentHtml[i].contents[1].contents
                    tempLen = len(contentInfos)
                    weiboInfoCsv.append(re.search('\d+', contentInfos[tempLen-10].string).group())
                    #print('点赞数: ' + re.search('\d+', contentInfos[tempLen-10].string).group())
                    weiboInfoCsv.append(
                        re.search('\d+', contentInfos[tempLen - 8].string).group())
                    #print('转发数: ' + re.search('\d+', contentInfos[tempLen-8].string).group())
                    weiboInfoCsv.append(
                        re.search('\d+', contentInfos[tempLen - 6].string).group())
                    #print('评论数: ' + re.search('\d+', contentInfos[tempLen-6].string).group())

                    timeAndSource = contentInfos[tempLen-1].string
                    if '来自' in timeAndSource:
                        posTimeEnd = timeAndSource.index('来自')
                        weiboInfoCsv.append(timeAndSource[:posTimeEnd - 1])
                        weiboInfoCsv.append(timeAndSource[posTimeEnd:])
                    else:
                        weiboInfoCsv.append(timeAndSource)
                        weiboInfoCsv.append(' ')
                    #print('发布时间: ' + contentInfos[tempLen-1].string)
                # 原创微博无图
                elif len(weiboContentHtml[i].contents) == 1:
                    contentInfos = weiboContentHtml[i].contents[0].contents
                    tempLen = len(contentInfos)
                    weiboInfoCsv.append(
                        re.search('\d+', contentInfos[tempLen - 10].string).group())
                    #print('点赞数: ' + re.search('\d+', contentInfos[tempLen-10].string).group())
                    weiboInfoCsv.append(
                        re.search('\d+', contentInfos[tempLen - 8].string).group())
                    #print('转发数: ' + re.search('\d+', contentInfos[tempLen-8].string).group())
                    weiboInfoCsv.append(
                        re.search('\d+', contentInfos[tempLen - 6].string).group())
                    #print('评论数: ' + re.search('\d+', contentInfos[tempLen-6].string).group())

                    timeAndSource = contentInfos[tempLen - 1].string
                    if '来自' in timeAndSource:
                        posTimeEnd = timeAndSource.index('来自')
                        weiboInfoCsv.append(timeAndSource[:posTimeEnd - 1])
                        weiboInfoCsv.append(timeAndSource[posTimeEnd:])
                    else:
                        weiboInfoCsv.append(timeAndSource)
                        weiboInfoCsv.append(' ')
                    #print('发布时间: ' + contentInfos[tempLen - 1].string)


            # 'cmt'表示转发微博
            elif weiboContentHtml[i].div.span['class'][0] == 'cmt':
                #表明原作者没有删除微博
                if len(weiboContentHtml[i].div.span.contents) > 1:
                    # 是否转发标志
                    weiboInfoCsv.append('true')
                    # 微博数目不断增加
                    self.weiboCount += 1
                    # 微博内容
                    weiboContent = weiboContentHtml[i].div.contents[1].text
                    tagResult = re.search('#(.*)#', weiboContent)
                    if tagResult is None:
                        tag = ''
                    else:
                        # 将微博内容中的标签信息去掉
                        beginPos = weiboContent.index('#')
                        endPos = weiboContent.index('#', beginPos + 1, len(weiboContent))
                        tag = weiboContent[beginPos+1:endPos]
                        weiboContent = weiboContent[:beginPos] + weiboContent[endPos + 1:]
                    # 去掉微博正文后http链接
                    if 'http' in weiboContent:
                        posBegin = weiboContent.index('http')
                        if weiboContent.rfind(' ', posBegin, len(weiboContent)) == -1:
                            weiboContent = weiboContent[:posBegin]
                        else:
                            posEnd = weiboContent.rfind(' ', posBegin, len(weiboContent))
                            weiboContent = weiboContent[:posBegin] + weiboContent[posEnd:]
                    weiboInfoCsv.append(weiboContent)
                    #print('第' + str(self.weiboCount) + '条: ' + '转发自: ' + weiboContentHtml[i].div.span.a.string+ ', 微博内容: ' + weiboContent)
                    # 转发微博有图
                    if len(weiboContentHtml[i].contents) == 3:
                        # 原文赞、评论、转发数
                        originContentInfos = weiboContentHtml[i].contents[1].contents
                        tempLenOringin = len(originContentInfos)
                        weiboInfoCsv.append(
                            re.search('\d+', originContentInfos[tempLenOringin - 6].string).group())
                        #print('原文点赞数: ' + re.search('\d+', originContentInfos[tempLenOringin-6].string).group())
                        weiboInfoCsv.append(
                            re.search('\d+', originContentInfos[tempLenOringin - 4].string).group())
                        #print('原文转发数: ' + re.search('\d+', originContentInfos[tempLenOringin-4].string).group())
                        weiboInfoCsv.append(
                            re.search('\d+', originContentInfos[tempLenOringin - 2].string).group())
                        #print('原文评论数: ' + re.search('\d+', originContentInfos[tempLenOringin-2].string).group())

                        # 转发后赞、评论、转发数
                        forwardContentInfos = weiboContentHtml[i].contents[2].contents
                        tempLenForward = len(forwardContentInfos)
                        weiboInfoCsv.append(
                            re.search('\d+', forwardContentInfos[tempLenForward - 10].string).group())
                        #print('转发后点赞数: ' + re.search('\d+', forwardContentInfos[tempLenForward-10].string).group())
                        weiboInfoCsv.append(
                            re.search('\d+', forwardContentInfos[tempLenForward - 8].string).group())
                        #print('转发后转发数: ' + re.search('\d+', forwardContentInfos[tempLenForward-8].string).group())
                        weiboInfoCsv.append(
                            re.search('\d+', forwardContentInfos[tempLenForward - 6].string).group())
                        #print('转发后评论数: ' + re.search('\d+', forwardContentInfos[tempLenForward-6].string).group())

                        timeAndSource = forwardContentInfos[tempLenForward - 1].string
                        if '来自' in timeAndSource:
                            posTimeEnd = timeAndSource.index('来自')
                            weiboInfoCsv.append(timeAndSource[:posTimeEnd-1])
                            weiboInfoCsv.append(timeAndSource[posTimeEnd:])
                        else:
                            weiboInfoCsv.append(timeAndSource)
                            weiboInfoCsv.append(' ')
                        #print('转发时间: ' + forwardContentInfos[tempLenForward - 1].string)
                    # 转发微博无图
                    elif len(weiboContentHtml[i].contents) == 2:

                        originContentInfos = weiboContentHtml[i].contents[0].contents
                        forwardContentInfos = weiboContentHtml[i].contents[1].contents
                        tempLenOringin = len(originContentInfos)
                        tempLenForward = len(forwardContentInfos)

                        weiboInfoCsv.append(re.search('\d+', originContentInfos[tempLenOringin - 6].string).group())
                        #print('原文点赞数: ' + re.search('\d+', originContentInfos[tempLenOringin - 6].string).group())
                        weiboInfoCsv.append(re.search('\d+', originContentInfos[tempLenOringin - 4].string).group())
                        #print('原文转发数: ' + re.search('\d+', originContentInfos[tempLenOringin - 4].string).group())
                        weiboInfoCsv.append(re.search('\d+', originContentInfos[tempLenOringin - 2].string).group())
                        #print('原文评论数: ' + re.search('\d+', originContentInfos[tempLenOringin - 2].string).group())

                        weiboInfoCsv.append(
                            re.search('\d+', forwardContentInfos[tempLenForward - 10].string).group())
                        #print('转发后点赞数: ' + re.search('\d+', forwardContentInfos[tempLenForward-10].string).group())
                        weiboInfoCsv.append(
                            re.search('\d+', forwardContentInfos[tempLenForward - 8].string).group())
                        #print('转发后转发数: ' + re.search('\d+', forwardContentInfos[tempLenForward-8].string).group())
                        weiboInfoCsv.append(
                            re.search('\d+', forwardContentInfos[tempLenForward - 6].string).group())
                        #print('转发后评论数: ' + re.search('\d+', forwardContentInfos[tempLenForward-6].string).group())

                        timeAndSource = forwardContentInfos[tempLenForward - 1].string
                        if '来自' in timeAndSource:
                            posTimeEnd = timeAndSource.index('来自')
                            weiboInfoCsv.append(timeAndSource[:posTimeEnd - 1])
                            weiboInfoCsv.append(timeAndSource[posTimeEnd:])
                        else:
                            weiboInfoCsv.append(timeAndSource)
                            weiboInfoCsv.append(' ')
                        #print('转发时间: ' + forwardContentInfos[tempLenForward - 1].string)
            weiboInfoCsv.append(tag)
            self.writer.writerow(weiboInfoCsv)

    def getInfo(self, pageNum):
        soup = self.getPage(pageNum)
        self.getUserWeibo(soup)

    def deal(self):
        #解析异常页面数
        errorPage = 0
        scheduleNum = 0
        soup = self.initWeb()
        #self.getUserInfo(soup)
        for i in range(1, self.pageTotal):
            try:
                self.getInfo(i)
                #sleep 5 minutes after requesting per 20 pages
                scheduleNum += 1
                if scheduleNum == 20:
                    time.sleep(300)
                    scheduleNum = 0
            except:
                errorPage += 1
                print('第'+str(i)+'页面解析异常')
                time.sleep(300)
                #如果累积有20个页面解析异常，函数结束
                if errorPage == 20:
                    return
                break
        self.csvFile.close()
#请自行添加微博博主ID
wb = weibo('')
wb.deal()