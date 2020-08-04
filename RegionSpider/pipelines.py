# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
import time

userName = "book"
password = "book"
ipAddress = "39.102.44.200"
port = 3306
dbName = "sq_web_tp5021"
charset = "utf8"

class RegionSpiderPipeline:
    mydb = None
    mycursor = None 

     # 开启爬虫时执行，只执行一次
    def open_spider(self, spider):
        # spider.hello = "world"  # 为spider对象动态添加属性，可以在spider模块中获取该属性值
        # 可以开启数据库等

        self.mydb = pymysql.connect(host=ipAddress, port=port, user=userName,
                     password=password, db=dbName, charset=charset)
        self.mycursor = self.mydb.cursor()
        pass

    # 关闭爬虫时执行，只执行一次。 (如果爬虫中间发生异常导致崩溃，close_spider可能也不会执行)
    def close_spider(self, spider):
        if self.mycursor :
            self.mycursor.close()
        if self.mydb:
            self.mydb.close()


     # 处理提取的数据(保存数据)
    def process_item(self, item, spider):
        print(item)
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        sql = "insert into t_regions(RegionCode, RegionName,Pid,CreateTime) values('{}','{}','{}','{}')".format(item["code"],item["name"],item["pcode"],now)
        print(sql)
        try:
            if self.mycursor:
                self.mycursor.execute(sql)
        except Exception as ex:
            print(ex)
        self.mydb.commit()

        