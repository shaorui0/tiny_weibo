from app.weibo_client import Weibo, User
import unittest



class WeiboTesting(unittest.TestCase):
    def test_WeiboUser(self):
        weibo = Weibo()
        user = User(1)
        user2 = User(2)
        user3 = User(3)
        user4 = User(4)
        weibo.add_user(user)
        weibo.add_user(user2)
        weibo.add_user(user3)
        weibo.add_user(user4)
        weibo.follow(1,2)
        print(weibo.users)
        print(user.following)
        weibo.unfollow(1,2)
        print(weibo.users)
        print(user.following)
        # weibo.follow(1,5) TODO raise
        print(weibo.users)
        print(user.following)
        
    def test_postBlog(self):
        weibo = Weibo()
        user = User(1)
        user2 = User(2)
        weibo.add_user(user)
        weibo.add_user(user2)
        weibo.postBlog(1, 3)
        weibo.postBlog(1, 4)
        print(user.posted_blogs)
        
    # TODO 测试feed相关功能