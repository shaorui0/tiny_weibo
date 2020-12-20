from app.weibo_client import Blog
import unittest
import datetime


class BlogTesting(unittest.TestCase):
    def test_BlogBlog(self):
        ts = datetime.datetime.now().timestamp()
        blog = Blog(1, ts=ts)
        print(blog._blog_info)

if __name__ == '__main__':
    unittest.main()