import scrapy
import re
from RegionSpider.items import RegionItem

class RegionSpider(scrapy.Spider):
    name = "region"

    def start_requests(self):
        urls = [
            'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/index.html',
        ]
        for url in urls:
            print(url)
            self.logger.info(url)
            yield scrapy.Request(url=url, callback=self.parseProvince,errback=self.parseProvinceError)

    def parseProvince(self, response):
        reg = r"<td><a href='(.*?).html'>(.*?)<br/></a></td>"
        reg = re.compile(reg, re.S)
        a = dict(re.findall(reg, response.text))
        #print(a)

        for x in range(0, len(a)):
            code = list(a.keys())[x]
            region_name = list(a.values())[x]
            pcode = "0"
            
            url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/{}.html'.format(
        code)
            print(url)
            yield scrapy.Request(url=url, callback=self.parseCity,cb_kwargs=dict(province = code),errback=self.parseCityError)

            code = str(int(code)*10000)
            yield RegionItem(code = code,name = region_name,pcode= pcode)

    def errorHandler(self,failure):
        # 日志记录所有的异常信息
        self.logger.error(repr(failure))

        # 假设我们需要对指定的异常类型做处理，
        # 我们需要判断异常的类型

        if failure.check(HttpError):
            # HttpError由HttpErrorMiddleware中间件抛出
            # 可以接收到非200 状态码的Response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # 此异常由请求Request抛出
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)

    def parseProvinceError(self, failure):
        self.errorHandler(failure)
    def parseCityError(self, failure):
        self.errorHandler(failure)                 
    def parseDistrictError(self, failure):
        self.errorHandler(failure)
    def parseTownError(self, failure):
        self.errorHandler(failure)
    def parseVillageError(self, failure):
        self.errorHandler(failure)

    def parseCity(self, response,province):
        reg = r"<tr class='citytr'><td><a href='.*?'>(.*?)</a></td><td><a href='.*?'>(.*?)</a></td></tr>"
        reg = re.compile(reg, re.S)
        i = dict(re.findall(reg, response.text))
        #print(i)

        for a in range(0, len(i)):
            code = list(i.keys())[a]
            region_name= list(i.values())[a]

            urlCode = code[:4]
            url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/{}/{}.html'.format(
        province, urlCode)
            print(url)
            request = scrapy.Request(url=url, callback=self.parseDistrict,cb_kwargs=dict(province = province),errback=self.parseDistrictError)
            request.cb_kwargs["city"] = code
            code = str(int(int(code) /1000000))
            pcode = str(int(int(province)*10000))
            yield RegionItem(code = code,name= region_name,pcode = pcode)
            yield request
           
    def parseDistrict(self, response,province,city):
        reg2_2 = r"<tr class='countytr'><td>(............)</td><td>(.*?)</td></tr>"
        reg2_2 = re.compile(reg2_2, re.S)
        reg2 = r"<tr class='countytr'><td><a href='.*?'>(.*?)</a></td><td><a href='.*?'>(.*?)</a></td></tr>"
        reg2 = re.compile(reg2, re.S)

        result2 = response.text
        j = dict(re.findall(reg2_2, result2))
        print('j:        ', j)
        j2 = dict(re.findall(reg2, result2))
        j.update(j2)

        for x in range(0, len(j)):
            code = list(j.keys())[x]
            param1 = code[0:2]
            param2 = code[2:4]
            param3 = code[0:6]

            region_name = list(j.values())[x]
            code = str(int(int(code) /1000000))
            pcode = str(int(int(city)/1000000))
            yield RegionItem(code = code,name= region_name,pcode=pcode)

            url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/{}/{}/{}.html'.format(
        param1, param2, parma3)
            request = scrapy.Request(url=url, callback=self.parseTown,cb_kwargs=dict(province = province),errback=self.parseTownError)
            request.cb_kwargs["city"] =city 
            request.cb_kwargs["district"] = code

            yield request

    def parseTown(self, response,province,city,district):
        reg = r"<tr class='towntr'><td><a href='.*?'>(.*?)</a></td><td><a href='.*?'>(.*?)</a></td></tr>"
        reg = re.compile(reg, re.S)
        i = dict(re.findall(reg, response.text))
        for c in range(0, len(i)):
            code = list(i.keys())[c]
            param1 = code[c][0:2]
            param2 = code[c][2:4]
            param3 = code[c][4:6]
            param4 = code[c][0:9]

            region_name = list(i.values())[x]

            yield RegionItem(code = code,name= region_name,pcode=pcode)

        url = 'http://www.stats.gov.cn/tjsj/tjbz/tjyqhdmhcxhfdm/2016/{}/{}/{}/{}.html'.format(
        param1, param2, param3, param4)
        
        request = scrapy.Request(url=url, callback=self.parseVillage,cb_kwargs=dict(province = province),errback=self.parseVillageError)
        request.cb_kwargs["city"] =city 
        request.cb_kwargs["district"] = district 
        request.cb_kwargs["town"] = code

        yield request


