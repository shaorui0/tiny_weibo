import psycopg2
from datetime import datetime, timedelta
def run_sql(sql):
    logger.info("sql: ", sql)
    con = psycopg2.connect(database="weibo", user="postgres", password="", host="127.0.0.1", port="5432")
    cur = con.cursor()
    cur.execute(sql)
    rows = None
    
    # check SELECT sql
    if sql[:6].lower() == 'select':
        rows = cur.fetchall()

    con.commit()
    con.close()
    if rows is not None:
        return rows

import time
for i in range(100):
    user_name = 'user_name' + str(i)
    now = datetime.now().strftime("%Y-%m-%d")
    sql = "INSERT INTO UserTable(user_name,lastest_post_ts) VALUES('{}', '{}');".format(
        user_name,
        now
    )
    time.sleep(0.2)    
    run_sql(sql)

# 之前写了插入语句的，改改就行了
for i in range(10000):
    user_name = 'user_name' + str(i)
    now = datetime.now().strftime("%Y-%m-%d")
    sql = "INSERT INTO UserTable(user_name,lastest_post_ts) VALUES('{}', '{}');".format(
        user_name,
        now
    )
    time.sleep(0.2)    
    run_sql(sql)