from app.weibo_client import User
import unittest
import datetime


class UserTesting(unittest.TestCase):
    def test_UserUser(self):
        user = User(1)
        ts = datetime.datetime.now().timestamp()
        user.post_blog(ts, 1)
        print(user.posted_blogs)
        user.post_blog(ts, 2)
        print(user.posted_blogs) # 因为post的id是线性增长的，怎么可能post多个？但是需不需要防这一手呢？这一手是要在代码上
        user.post_blog(ts, 3)
        print(user.posted_blogs) # 典型的没写单侧的问题，连简单的重复添加都不能识别
        user.delete_blog(2)
        print(user.posted_blogs) 
        user.delete_blog(2)
        print(user.posted_blogs) 

    def test_follow(self):
        user = User(1)
        user.follow_user(2)
        print(user.following) 
        user.unfollow_user(2)
        print(user.following) 
        
    def test_get_lastest_posted(self):
        user = User(1)
        ts = datetime.datetime.now().timestamp()
        user.post_blog(ts, 1)
        user.post_blog(ts, 2)
        user.post_blog(ts, 3)
        
        print(user.get_lastest_posted(3))
        
if __name__ == '__main__':
    unittest.main()