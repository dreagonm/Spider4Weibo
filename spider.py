import requests
import json
import datetime
import time

Headers = { # Cookie使用登录后生成的Cookie，否则会有微博无法查看
    'Cookie' : '*',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32'
}

info_url = 'https://weibo.com/ajax/profile/info'
list_url = 'https://weibo.com/ajax/statuses/mymblog'
detail_url = 'https://weibo.com/ajax/statuses/longtext'

end_time_year = 2021
output_dataname = 'test.txt'
page_delay = 1
wait_delay = 5

def GetBlogContent(uid,page,blog_name):
    content2write = []
    print('获取uid为%d的<%s>的第%d页微博'%(uid,blog_name,page))
    res = requests.get(url=list_url,headers=Headers,params={
        'uid' : uid,
        'page' : page,
        'feature': 0
    })
    if res.status_code != 200:
        raise('获取失败，可能是网络或者对方服务器短时间禁止了爬虫访问')
    res.encoding = 'utf-8'
    try:
        data = json.loads(res.text)
    except:
        print('获取出错，检查cookie设置')
        raise Exception('获取出错，检查cookie设置')
    
    blog_list = data['data']['list']
    for blog in blog_list:
        post_time = time.strptime(blog['created_at'],'%a %b %d %H:%M:%S %z %Y')
        if(post_time.tm_year < end_time_year):
            return True
        if blog['isLongText']:
            blogid = blog['mblogid']
            detail_res = requests.get(url = detail_url,headers=Headers,params={
                'id' : blogid
            })
            if detail_res.status_code != 200:
                raise('获取失败，可能是网络或者对方服务器短时间禁止了爬虫访问')
            detail_data = json.loads(detail_res.text)
            try:
                content = detail_data['data']['longTextContent']
            except: #存在刚好卡在长文本和短文本之间的情况，特殊处理
                content = blog['text_raw']
        else:
            content = blog['text_raw']
        timestr = time.strftime('%Y %b %d %H:%M:%S',post_time)
        content2write.append(timestr+','+content+'\n')
    with open(output_dataname,'a',encoding = 'utf-8') as f:
        f.writelines(content2write)
    print('获取完成，等待%ds后获取下一页' % page_delay)
    time.sleep(page_delay)
    return False

def GetBlogInfo(uid):
    info_res = requests.get(url = info_url,headers=Headers,params={
        'custom':uid
    })
    try:
        info_data = json.loads(info_res.text)
    except:
        print('获取出错，检查cookie设置')
        raise Exception('获取出错，检查cookie设置')
    blog_name = info_data['data']['user']['screen_name']
    return blog_name

def Blog(start_page,uid,first = False):
    print('开始获取，结果将保存至%s中' % output_dataname)
    page = start_page
    blog_name = GetBlogInfo(uid)
    if first and start_page == 1:
        with open(output_dataname,'w',encoding = 'utf-8') as f:
            f.write(blog_name+'\n')
    while True:
        try:
            if GetBlogContent(uid,page,blog_name):
                print('到达限制时间，获取全部完成')
                break
            if not first:
                return None
            page += 1
        except:
            print('等待%ds后重试获取操作' % wait_delay)
            time.sleep(wait_delay)
            if Blog(page,uid) == None:
                if not first:
                    return None
            page += 1
    print('获取结果保存完毕')
    return page
    
if __name__ == '__main__':
    Blog(1,2803301701,True)
    # GetBlogContent(2803301701,629,'test')
