import datetime
import time
import heapq
import random

NEW_FEED_NUMBER = 10

class User():
    def __init__(self, uid):
        self._id = uid
        self.posted_blogs = list()
        self.following = set()
    
    def add_blog(self, ts, blog_id):
        # big root heap, order by timestamp
        heapq.heappush(self.posted_blogs, (-1 * ts, blog_id))

    def delete_blog(self, blog_id):
        pass

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
        
        tmp_total_blogs = self.posted_blogs[:]
        tmp = list()
        for i in range(0, top_k):
            tmp.append(heapq.heappop(tmp_total_blogs))
        return tmp


class Weibo():
    def __init__(self):
        # all of user in Weibo
        self.users = dict() # map: id => User_id

    def follow(self, follower, followee):
        # check follwer and followee in weibo
        if follower not in self.users:
            self.users[follower] = User(follower)
            #raise Exception("follower {} not in Weibo".format(follower))
        if followee not in self.users:
            self.users[followee] = User(followee)
            #raise Exception("followee {} not in Weibo".format(followee))

        cur_follower = self.get_user(follower)
        cur_follower.follow_user(followee)

    def unfollow(self, follower, followee):
        # check follwer and followee in weibo
        if follower not in self.users:
            self.users[follower] = User(follower)
            #raise Exception("follower {} not in Weibo".format(follower))
        if followee not in self.users:
            self.users[followee] = User(followee)
            #raise Exception("followee {} not in Weibo".format(followee))

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
            self.users.update({user_id: User(user_id)})
        ts = datetime.datetime.now().timestamp()
        self.get_user(user_id).add_blog(ts, blog_id)
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
    test()