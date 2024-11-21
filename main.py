import time
import requests
import json
import time
import random
import pandas as pd
from xs_encrypt import encrypt_xs

# 文章id
page_id = '6735812d000000001a0368e2'

# 请求头
h1 = {
	'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36 Edg/130.0.0.0',
    # 注意更新
	'Cookie': "abRequestId=b768f963-7631-5b4c-ad07-a3d871487f9f; xsecappid=xhs-pc-web; a1=191cf53dc6fl5souas27vyn5kou6lpcc1g2nrmsmt50000950592; webId=e5380b72530f43006cd3cf0171c03796; gid=yjySi2jj0jy0yjySi2qfSk6MKi12Ml70MJWhJ69vI2Tl7I28K1USSF888j282jJ840yjyj2J; webBuild=4.43.0; _ga=GA1.2.360623178.1731688744; _gid=GA1.2.2146588166.1731688744; _ga_K4YXYBHT33=GS1.1.1731688744.1.1.1731688763.0.0.0; web_session=0400698c232ad357fdb6c83602354b0f06d5a4; acw_tc=0a5088c817316925677951850e3bee29657bf29a87d207a6a3d58b9a8a282d; websectiga=2845367ec3848418062e761c09db7caf0e8b79d132ccdd1a4f8e64a11d0cac0d; sec_poison_id=f6f2a37b-885a-400c-9d89-f9273a8ee763; unread={%22ub%22:%226736e7a4000000001b013c91%22%2C%22ue%22:%2267373d8e000000003c01a770%22%2C%22uc%22:10}", # .replace('%', '%%'),
    'a1': "191cf53dc6fl5souas27vyn5kou6lpcc1g2nrmsmt50000950592"
}

def crawer(note_id, root_comment_id=None, cursor=None):
    comments = []
    if root_comment_id is None:
        base_url = 'https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id={}&top_comment_id=&image_formats=jpg,webp,avif'.format(
            note_id)
    else:
        base_url = 'https://edith.xiaohongshu.com/api/sns/web/v2/comment/sub/page?note_id={}&root_comment_id={}&top_comment_id=&num=10&image_formats=jpg,webp,avif'.format(
            note_id, root_comment_id)
    
    next_cursor = cursor
    while True:
        if next_cursor is None:
            url = base_url
        else:
            url = '{}&cursor={}'.format(base_url, next_cursor)

        h1["x-s"] = encrypt_xs(url.replace("https://edith.xiaohongshu.com", ""), h1['a1'], int(round(time.time() * 1000)) )

        # 发送请求
        time.sleep(random.random()*2)
        r = requests.get(url, headers=h1)
        print('.', end='')
        # 解析数据
        json_data = r.json()
        if json_data['code'] != 0:
            raise Exception("获取评论失败，请检查笔记id或cookie: "+ json.dumps(json_data,ensure_ascii=False))
        comments.extend(json_data['data']['comments'])

        # 最后一页，停止
        if json_data['data']['has_more'] == False:
            break

        # 得到下一页的游标
        next_cursor = json_data['data']['cursor']
    return comments
	
def main(note_id):
    df = pd.DataFrame({})
    comments = crawer(note_id=note_id)
    
    # 保存数据到DF
    for comment in comments:
        sub_comments = comment['sub_comments']
        df = df._append({
            '笔记链接': 'https://www.xiaohongshu.com/explore/' + note_id,
            '评论id': comment['id'],
            '评论者昵称': comment['user_info']['nickname'],
            '评论者id': comment['user_info']['user_id'],
            '评论时间': comment['create_time'],
            '评论IP属地': comment['ip_location'],
            '评论点赞数': comment['like_count'],
            '评论内容': comment['content'],
            '评论级别': 0,
            '评论目标id': ""
        }, ignore_index=True)

        if comment['sub_comment_has_more']:
            sub_comments.extend(crawer(note_id=note_id, root_comment_id=comment['id'], cursor=comment['sub_comment_cursor']))
        
        for sub_comment in sub_comments:
            df = df._append({
                '笔记链接': 'https://www.xiaohongshu.com/explore/' + note_id,
                '评论id': sub_comment['id'],
                '评论者昵称': sub_comment['user_info']['nickname'],
                '评论者id': sub_comment['user_info']['user_id'],
                '评论时间': sub_comment['create_time'],
                '评论IP属地': sub_comment['ip_location'],
                '评论点赞数': sub_comment['like_count'],
                '评论内容': sub_comment['content'],
                '评论级别': 1,
                '评论目标id': sub_comment['target_comment']['id']
            }, ignore_index=True)

    # 保存到csv
    df.to_csv('{}.csv'.format(note_id), mode='w', header=True, index=False, encoding='utf_8_sig')

main(page_id)