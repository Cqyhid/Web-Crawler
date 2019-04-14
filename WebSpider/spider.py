import requests
import copy
import re


class Spider():

    root_pattern = '<div class="CategoryTreeItem">([\s\S]*?)</div>'
    href_pattern = 'href="([^"]+)"'
    subcategory_pattern = '<a.*?href="[^"]*".*?>([\S\s]*?)</a>'
    title_pattern = re.compile('Category:([\s\S]*)')
    count = 0


    def __fetch_content(self,url = 'https://en.wikipedia.org/wiki/Category:Lists_of_television_channels'):
        r = requests.get(url)
        return r.text
        #str bytes

    def __analysis(self,htmls):
        root_html = re.findall(Spider.root_pattern,htmls)

        #find href
        href = []
        for html in root_html:
            href.append(re.findall(Spider.href_pattern,html))
        
        for i in range(len(href)):
            href[i] = 'https://en.wikipedia.org'+ href[i][0]

        #find subcategory name
        subcategory = []
        for html in root_html:
            subcategory.append(re.findall(Spider.subcategory_pattern,html)[0])

        return href,subcategory

    #save html
    
    def __savehtml(self,file_name, file_content):
        #注意windows文件命名的禁用符，比如 /
        with open(file_name.replace('/', '_') + ".txt", "w") as f:
            #写文件用bytes而不是str，所以要转码
            f.write(file_content.encode("utf8").decode("cp950", "ignore"))
            f.close()
  
    #start go crawling
    def go(self,search_mode):
        subcategory = {}
        temp_subcategory = []
        href = []
        temp_href = []
        
        #分析root网页获取subcategories
        htmls = self.__fetch_content()
        self.__savehtml('Lists_of_television_channels',htmls)
        href,subcategory['Lists_of_television_channels'] = self.__analysis(htmls)

        #判断是否存在子网页
        while len(href)>0:
            if search_mode == 'DFS':
                node = href.pop()
                #获取对应链接的文本
                category_name = re.search(Spider.title_pattern,node)

            elif search_mode == 'BFS':
                node = href.pop(0)
                #获取对应链接的文本
                category_name = re.search(Spider.title_pattern,node)
            else:
                print('system error! please reboot')
                break
            #test if there is a dead loop
            if category_name.group(1) in subcategory.keys():
                continue
            #分析网页获取subcategory
            htmls = self.__fetch_content(str(node))
            self.__savehtml(category_name.group(1),htmls)
            temp_href,temp_subcategory = self.__analysis(htmls)

            if len(temp_subcategory)>0:
                #将存在的subcategory的字符串写入对于key为其父类的名下
                subcategory[category_name.group(1)] = copy.deepcopy(temp_subcategory)
                for item in temp_href:
                    #将链接从后写入list
                    href.append(item)

                #清空字典列表以备下次使用
                temp_subcategory.clear()
                temp_href.clear()
        #断点
        # print(subcategory)
        return subcategory

    def check_content(self,key,result_dict):
        Spider.count += 1
        temp = key.replace(' ','_')
        if temp in result_dict.keys():
            i = 1
            while(i<=Spider.count):
                print('\t',end='')
                i += 1
            print(temp)
            temp_dict = result_dict.pop(temp)
            for keys in temp_dict:
                self.check_content(keys,result_dict)
        else:
            while(Spider.count > 0):
                print('\t',end='')
                Spider.count -= 1
            print(temp)

    #show the result with indention
    def result_sorting(self,result):
        print('Lists_of_television_channels')
        for keys in result['Lists_of_television_channels']:
            self.check_content(keys,result)
        print('finished')
            


spider = Spider()
search_mode = input(str('Please identify your search mode(input BFS or DFS) : '))
if search_mode == 'BFS' or 'DFS':
    result = spider.go(search_mode)
    spider.result_sorting(result)
else:
    print('Incorrect mode chosen,please reboot the system')