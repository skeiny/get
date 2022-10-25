### 这是一个帮助调研的工具
+ 它只会把论文的title记录下来

### 库依赖
+ pip install pandas
+ pip install bs4
+ pip install lxml

### 在main()函数中设置参数
+ key_words——需要筛选的关键词
+ conference_list——需要搜索的会议
+ journal_list——需要搜索的期刊，其中数字代表最新的刊号
+ loop_conference(...,a,b)——后两个参数填年份区间（闭区间）
+ loop_journal(...,x)——最后一个参数代表需要搜近x期
+ 根据需要，设置两个if语句中的Ture or False

上述参数设置完成后，运行get_paper_title.py，结果默认保存于result文件夹