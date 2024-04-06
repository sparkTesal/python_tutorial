import json

import openai
import pandas as pd

# 注意OPENAI_BASE_URL不能使用默认的
OPENAI_BASE_URL = 'https://api.chatanywhere.tech/v1'
# 注意这里需要替换成你自己的API_KEY
OPENAI_API_KEY = 'YOUR_API_KEY'

SINGLE_PROMPT_PROMPT_PREFIX = """
我现在正在做豆瓣电影短评的分类，我的输入会包含对应的电影名称以及用户具体的评论内容，输出是一个1-5分之间的整数分数。这个分数即是最终的分类

###案例1
电影：《复仇者联盟2》
评论内容：看毕，我激动地对友人说，等等奥创要来毁灭台北怎么办厚，她拍了拍我肩膀，没事，反正你买了两份旅行保险，惹......

分类：5


###案例1
电影：《复仇者联盟2》
评论内容：非常失望，剧本完全敷衍了事，主线剧情没突破大家可以理解，可所有的人物都缺乏动机，正邪之间、妇联内部都没什么火花。团结-分裂-团结的三段式虽然老套但其实也可以利用积攒下来的形象魅力搞出意思，但剧本写得...

分类：2

下面我会给出一个待分类的评论，
请输出对应的分类。要求输出结果仅包含一个分类结果，其他的不要输出，因为这样会影响到我后续的解析

待分类评论：
电影：《复仇者联盟2》
评论内容：粉丝向电影+全明星阵容，还是三部曲里的第1.5部续集，直接导致细节梗太多，每个角色都要照顾以至于顾不上故事节奏，叙事还要照顾到承上启下，结果整体都有点怪怪的。
"""

MULTI_PROMPT_PROMPT_PREFIX = """
我现在正在做豆瓣电影短评的分类，我的输入会包含对应的电影名称以及用户具体的评论内容，输出是一个1-5分之间的整数分数。这个分数即是最终的分类

###案例1
电影：《复仇者联盟2》
评论内容：看毕，我激动地对友人说，等等奥创要来毁灭台北怎么办厚，她拍了拍我肩膀，没事，反正你买了两份旅行保险，惹......

分类：5


###案例1
电影：《复仇者联盟2》
评论内容：非常失望，剧本完全敷衍了事，主线剧情没突破大家可以理解，可所有的人物都缺乏动机，正邪之间、妇联内部都没什么火花。团结-分裂-团结的三段式虽然老套但其实也可以利用积攒下来的形象魅力搞出意思，但剧本写得...

分类：2


以下会给出待分类的评论，会包含一个序号以及对应的电影名称和评论内容。

分类结果请按照json格式输出，输出是一个字典，key是评论序号，value是分类结果。
请直接输出json，不要输出其他任何文字，也不要输出```json这种markdowm代码标记，不然我无法解析你的输出


待分类评论：
"""


def load_csv_data(data_path: str, sample_num=20):
    """
    一条条的预测豆瓣电影短评的分数
    :param data_path: 数据路径
    :param sample_num: 抽样数量
    :return:
    """
    # 读取CSV文件
    df = pd.read_csv(data_path)

    # 随机抽取数据
    df = df.sample(sample_num)
    print(df.to_json(indent=4, force_ascii=False))


def chat_with_sdk_in_stream(prompt, model="gpt-3.5-turbo"):
    """
    以流式的方式请求，因为访问api.chatanywhere.com.cn的时候，会出现超时的情况，所以需要以流式的方式请求,否则计费会出现问题
    :return:
    """
    openai.api_base = OPENAI_BASE_URL
    openai.api_key = OPENAI_API_KEY

    response = openai.ChatCompletion.create(
        model=model,
        stream=True,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # create variables to collect the stream of chunks
    collected_chunks = []
    collected_messages = []
    # iterate through the stream of events
    for chunk in response:
        collected_chunks.append(chunk)  # save the event response
        chunk_message = chunk['choices'][0]['delta']  # extract the message
        collected_messages.append(chunk_message)  # save the message

    # print the time delay and text received
    full_reply_content = ''.join([m.get('content', '') for m in collected_messages if 'content' in m])
    return full_reply_content


def classify_single_douban_comment(movie_name_cn: str, comment: str) -> int:
    """
    对豆瓣电影短评进行分类
    :param comment:
    :return:
    """
    prompt = f"{SINGLE_PROMPT_PROMPT_PREFIX}电影：《{movie_name_cn}》\n评论内容：{comment}"
    # 调用openai的sdk进行分类
    reply = chat_with_sdk_in_stream(prompt, "gpt-4-0125-preview")
    return int(reply.strip())


def classify_multi_douban_comment(comments: list):
    """
    对多条豆瓣电影短评进行分类
    :param comment:
    :return:
    """
    prompt = MULTI_PROMPT_PROMPT_PREFIX
    for index, (movie_name_cn, comment) in enumerate(comments):
        prompt += f"{index + 1}、电影：《{movie_name_cn}》\n评论内容：{comment}\n\n"
    # 调用openai的sdk进行分类
    reply = chat_with_sdk_in_stream(prompt, "gpt-4-0125-preview")
    try:
        replay_dict = json.loads(reply)
        return replay_dict
    except Exception as e:
        print(f"error:{reply}")
        return None


def predict_douban_comment_star_one_by_one(data_path: str, sample_num=20):
    """
    一条条的预测豆瓣电影短评的分数
    :param data_path: 数据路径
    :param sample_num: 抽样数量
    :return:
    """
    # 读取CSV文件
    df = pd.read_csv(data_path)

    # 随机抽取数据
    df = df.sample(sample_num)

    total_error = 0
    predict_cnt = 0
    for index, row in df.iterrows():
        movie_name_cn = row['Movie_Name_CN']
        comment = row['Comment']
        star = int(row['Star'])
        print(f"movie_name_cn:{movie_name_cn}, comment:{comment}")
        # 调用openai的sdk进行分类
        try:
            score = classify_single_douban_comment(movie_name_cn, comment)
        except Exception as e:
            print(f"error:{e}")
            continue

        predict_cnt += 1
        #计算误差
        error = abs(score - star)
        total_error+=error
        print(f"gpt预测:{score}, 真实分数:{star}, 误差:{error}")

    print(f"平均误差:{total_error/predict_cnt}")


def predict_douban_comment_star_batch(data_path: str, sample_num=20, batch_size=5):
    """
    一条条的预测豆瓣电影短评的分数
    :param data_path: 数据路径
    :param sample_num: 抽样数量
    :return:
    """
    # 读取CSV文件
    df = pd.read_csv(data_path)

    # 随机抽取数据
    df = df.sample(sample_num)

    total_error = 0
    predict_cnt = 0

    # 先对数据做分组处理，做成一组5个，然后调用classify_multi_douban_comment进行分类
    comments = []
    stars = []
    for index, row in df.iterrows():
        movie_name_cn = row['Movie_Name_CN']
        comment = row['Comment']
        star = int(row['Star'])
        comments.append((movie_name_cn, comment))
        stars.append(star)
        if len(comments) % batch_size == 0:
            # 调用openai的sdk进行分类
            try:
                result = classify_multi_douban_comment(comments)
                if result:
                    for result_index_str, score_str in result.items():
                        result_index = int(result_index_str)
                        score = int(score_str)

                        comment_info = comments[result_index - 1]
                        print(f"movie_name_cn:{comment_info[0]}, comment:{comment_info[1]}")

                        user_star = int(stars[result_index - 1])
                        error = abs(score - user_star)
                        total_error += error
                        print(f"gpt预测:{score}, 真实分数:{user_star}, 误差:{error}")
                        predict_cnt += 1
            except Exception as e:
                print(f"error:{e}")
            comments = []
            stars = []
    print(f"平均误差:{total_error / predict_cnt}")





if __name__ == '__main__':
    load_csv_data("data/DMSC.csv", 20)
    # print(chat_with_sdk_in_stream("hello", "gpt-3.5-turbo"))
    # print(classify_single_douban_comment("复仇者联盟2", "只有一颗彩蛋必须降一星。外加漫威的编剧是有心无力了吧。复仇者联盟只能永远着手与团队的和与不和。这种东西重复到第二次就是隔了三年，还是心有余而力不足吧。只好来三个新成员，但是认真地，有必要加一条家庭线么？妇联以后也是要走赛车帮的，we are familly 路线？？？"))
    # print(classify_multi_douban_comment([("复仇者联盟2", "粉丝向电影+全明星阵容，还是三部曲里的第1.5部续集，直接导致细节梗太多，每个角色都要照顾以至于顾不上故事节奏，叙事还要照顾到承上启下，结果整体都有点怪怪的。"),
    #                                     ("复仇者联盟2", "跪求乔斯·韦登回去弄“螢火蟲”，別再搞這些沒什麼營養的漫威大片。"),
    #                                      ("复仇者联盟2","刘大勇贾秀琰师徒真是狙击资本主义巨制界的先锋"),
    #                                      ("复仇者联盟2","好莱坞造梦境界依旧。值得表扬的是开头第一个镜头，其镜头运动设计的惊险流畅，大量低角度和超级特写的交代让人生理迅速发生反应，几乎马上进入情节。（那个慢速有点傻可是是给雷神的好吧）故事模式还是一样，反正...")]))
    # predict_douban_comment_star_one_by_one("data/DMSC.csv", 50)
    # predict_douban_comment_star_batch("data/DMSC.csv", 50, 5)