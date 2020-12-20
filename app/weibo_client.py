import datetime
import time
import heapq
import random

NEW_FEED_NUMBER = 10
class Blog():
    # TODO 分布式应该考虑哪些东西？blog id 应该是自动增长的
    def __init__(self, blog_id, **kargs):
        self._blog_id = blog_id
        self._blog_info = dict()
        self._blog_info.update(kargs)
    
    def _update_attr(self, key, value):
        self._blog_info.update({key: value})
    
    def _get_info(self, key):
        try:
            self._blog_info[key]
        except:
            raise KeyError(f"The attribute does not exist in the blog[{key}]")
    
    # TODO 属性函数
    def blog_id(self):
        return self._blog_id


from collections import deque
import itertools
class User():
    # user id 应该是自动增长的
    def __init__(self, uid):
        self._id = uid
        self.posted_blogs = deque()
        self.blogs = dict() # TODO 持久化
        self.following = set()
    
    def post_blog(self, ts, blog_id):
        # big root heap, order by timestamp
        # heapq.heappush(self.posted_blogs, (-1 * ts, blog_id))
        self.posted_blogs.append(blog_id)
        self.blogs[blog_id] = Blog(blog_id, ts=-1 * ts)
        #self.posted_blogs.
        # TODO 没必要，本来就是按时间插入进去的
        # 什么样的数据结构？本质就是数据结构的组织
        # 关于这种无非就是一直append、一直delete
        # 每个blog_id会有一些评论，然后。。。做一个这样的东西，总是会考虑很多东西，比如weibo里面

    def delete_blog(self, blog_id):
        if blog_id not in self.blogs:
            raise KeyError(f"blog_id[{blog_id}] not in this user[{self._id}]")
        
        index_blog_id = self.posted_blogs.index(blog_id)
        del self.posted_blogs[index_blog_id]
        
        del self.blogs[blog_id]

    def follow_user(self, uid):
        if self._id == uid:
            raise Exception("Can't follow yourself.")
        self.following.add(uid) # user may not exist, lazy check for user existence
        print("{} has followed {}, current following".format(self._id, uid), self.following)

    def unfollow_user(self, uid):
        if self._id == uid:
            raise Exception("Can't unfollow yourself.")
        if uid not in self.following:
            raise Exception("You are not following this person")            
        self.following.remove(uid)
        print("{} has unfollowed {}, current following".format(self._id, uid), self.following)
    
    def get_lastest_posted(self, top_k=NEW_FEED_NUMBER):
        if top_k < 0:
            raise Exception("top_k must be greater than 0.")

        if len(self.posted_blogs) <= top_k:
            return self.posted_blogs
        return deque(itertools.islice(self.posted_blogs, 0, top_k))

    def uid(self):
        return self._id

class Weibo():
    def __init__(self):
        # all of user in Weibo
        self.users = dict() # map: id => User_id
        
    # 创建用户
    def add_user(self, user):
        if user.uid() in self.users:
            raise Exception(f"user {uid} already in Weibo")
        self.users[user.uid()] = user

    def follow(self, follower, followee):
        # check follwer and followee in weibo
        if follower not in self.users:
            # TODO 你不能关注一个不存在的人，直接报错比较好，不能创建一个僵尸
            raise Exception(f"follower {follower} not in Weibo")
        if followee not in self.users:
            raise Exception(f"followee {followee} not in Weibo")

        cur_follower = self.get_user(follower)
        cur_follower.follow_user(followee)

    def unfollow(self, follower, followee):
        if follower not in self.users:
            raise Exception(f"follower {follower} not in Weibo")
        if followee not in self.users:
            raise Exception(f"followee {followee} not in Weibo")

        cur_follower = self.get_user(follower)
        cur_follower.unfollow_user(followee)

    def getNewsFeed(self, user_id):
        """
        get new feed
        """
        if user_id not in self.users:
            raise Exception("user [{}] not in Weibo".format(user_id))

        # Find all the people who follow
        # total_following = self.get_user(user_id).following 
        
        # Optimized! According to the last Weibo of all followee, determine the source of the feed that needs to be obtained
        total_following = self.get_top_k_followee_latest_posted(user_id, NEW_FEED_NUMBER)
        total_following.append(user_id) # include herself

        total_user_lastest_posted = list()
        for signal_following in total_following:
            # Find the most recent post (top 10) of the current person
            cur_lastest_posted = self.get_user(signal_following).get_lastest_posted(NEW_FEED_NUMBER)
            total_user_lastest_posted.extend(cur_lastest_posted)
        
        # format of element in total_user_lastest_posted: (-1 * ts, user_id)
        return [x[1] for x in heapq.nsmallest(NEW_FEED_NUMBER, total_user_lastest_posted)]

    def postBlog(self, user_id, blog_id):
        """
        post blog, add current timestamp and blog id to watch list of current user
        """
        if user_id not in self.users:
            raise Exception(f"user {user_id} not in Weibo")
        ts = datetime.datetime.now().timestamp()
        
        self.get_user(user_id).post_blog(ts, blog_id)
        print("user [{}] has posted a blog [{}] at [{}]".format(user_id, blog_id, ts))
    
    def get_top_k_followee_latest_posted(self, user_id, top_k):
        """
        According to the last Weibo of all followee, determine the source of the feed that needs to be obtained
        Args:
            user_id: follower user id
            top_k: max number of followee who posted the latest feed in the current user's watch list
        Return:
            a list of followee id who posted the latest feed in the current user's watch list
        """
        if top_k > len(self.get_user(user_id).following):
            return list(self.get_user(user_id).following)
        
        result = list()
        unfilter = self.get_user(user_id).following
        for followee_id in unfilter:
            ts, blog_id = self.get_user(followee_id).get_lastest_posted(1)[0]
            ts *= -1
            # the heap order by timestamp, keep info of followee who posted the latest news
            if len(result) < top_k:
                heapq.heappush(result, (ts, blog_id, followee_id))
            else:
                # keep max length of heap is top_k
                heapq.heappush(result, (ts, blog_id, followee_id))
                heapq.heappop(result)

        return [x[2] for x in result] # user_ids

    def get_user(self, user_id):
        """
        user may not exist in Weibo or has been deleted.
        """
        if user_id not in self.users:
            raise Exception("user: [{}] not exist in Weibo".format(user_id))
        return self.users[user_id]


weibo = Weibo()

def test_simple():
    global weibo
    weibo.postBlog(1, 5)
    print(weibo.getNewsFeed(1))
    weibo.follow(1, 2)
    weibo.postBlog(2, 6)
    print(weibo.getNewsFeed(1))
    weibo.unfollow(1, 2)
    print(weibo.getNewsFeed(1))

def test():
    global weibo
    print("start to test post feed")
    blog_id = 1
    for i in range(50):
        user_id = random.randint(0, 9)
        weibo.postBlog(user_id, blog_id)
        
        blog_id += 1
        time.sleep(0.1)

    print("start to test posted_blogs / get_lastest_posted")
    for uid, cur_user in weibo.users.items():
        print(uid, cur_user.posted_blogs)
        print(uid, cur_user.get_lastest_posted())
        print(">> cur_user.following", cur_user.following)

    print("start to test following")
    for i in range(100):
        follower = random.randint(0, 9)
        followee = random.randint(0, 9)
        if follower == followee:
            followee += 1
            followee %= 10
        weibo.get_user(follower).follow_user(followee)


    print("start to test get_top_k_followee_latest_posted")
    for i in range(10):
        print(weibo.get_user(i).following)
        print(weibo.get_top_k_followee_latest_posted(i, 3))


    print("start to test getNewsFeed")
    for i in range(100):
        user_id = random.randint(0, 9)
        print(weibo.getNewsFeed(user_id))
        time.sleep(1)

if __name__ == "__main__":
    test_simple()
    #test()