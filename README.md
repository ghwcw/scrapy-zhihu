# scrapy-zhihu（release v1.0）
采用scrapy框架和递归思想，爬取知乎用户信息及其关注人列表和粉丝列表信息。

pipeline管道输出到MongoDB和MySQL数据库中。其中MySQL采用了SQL方法和sqlalchemy ORM方法。
# 使用重要说明
1.本仓库所有文件应放在项目根目录下；

2.须自行安装python3及其虚拟环境；

3.运行“pip install -r requirement.txt”安装所需库；

4.直接run运行spiders下的run.py文件即可进行爬虫。
