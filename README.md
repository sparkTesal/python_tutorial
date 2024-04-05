# 介绍
项目主要包括两个文件
- 一个是`python_tutorial.ipynb`, 里面是python的基础语法。格式是jupyter notebook. 里面包括了python的基础语法，包括数据类型，循环，条件语句，函数，类等等。
- 另外一个是一个实战项目，是利用chatgpt对豆瓣电影的评论进行分类。也就是进行预测，然后和真实的用户打分进行比较，判断误差大小。
  - 主要是为了教学chatgpt的api调用方式以及如何进行文本分类。
  - 这是一种把非结构化数据转化为结构化数据的方法，可以用于很多场景。

# 环境准备
安装环境
本项目推荐pycharm作为IDE，使用anaconda作为python环境管理工具。Python版本推荐3.10. 具体安装步骤如下：
1. 下载安装pycharm，下载地址：https://www.jetbrains.com/pycharm/download/
2. 下载安装anaconda，下载地址：https://www.anaconda.com/products/distribution
3. 创建一个新的conda环境，命令如下：
```shell
conda create -n python_tutorial python=3.10
```
4. 打开pycharm，选择File->Open，打开本项目
5. 安装依赖包，命令如下：
```shell
pip install -r requirements.txt
```

# 使用
## python_tutorial.ipynb

在Pycharm中打开`python_tutorial.ipynb`，直接阅读即可开始学习python基础语法。当然也可以自己修改一下相关代码，然后运行看看效果。

## douban_comment_classifier.py

## 数据准备
项目中是没有把数据集上传的，因为有400多M，太大了，需要自己下载数据，下载地址：https://www.kaggle.com/datasets/utmhikari/doubanmovieshortcomments
下载完成之后解压缩，并把文件放在路径`data/DMSC.csv`下

## openai apikey准备
要调用chatgpt需要openai的apikey，官方的做法是去官网搞apikey，但是注册流程很复杂，需要非中国的号码。付费更复杂，需要海外开户的信用卡或者借记卡。
这里推荐去一个代理了openai的api的网站上去购买apikey: https://peiqishop.cn/buy/10

注意这个使用这个网站的apikey的话要修改对应的OPENAI_BASE_URL，不能使用默认的。具体修改代码中已经写了。

在Pycharm中打开`douban_comment_classifier.py`，要运行的代码都已经写在main函数中。默认会运行批量分类的函数。但是main函数中也包含了调用其他函数的代码，逐个打开注释即可运行。
