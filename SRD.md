# weibo



## schema


### schema 设计


User:
- user_id, bigint
    - 【sharding】ts + shard_id (RR（不管是按 RR（加个基本的原子操作就可以了） ，还是按user_id，这应该属于代码层的工作，比如`insta5`，就是`shard_id = 5`的数据） % Sharding_NUM) + auto_incre，表示一个时刻，一个shardor上面能创建多少个用户
- user_name, char(10)
- user_posted(暂定方案1): 
    1. 直接在 blog 表中 sql 查，然后放缓存（**redis-list**）
    2. json/map (id: is_delete)
    3. string(list)
    4. 不用这个字段，通过blog表进行获取【y】
- following, text
    - json {user_id: is_unfollowed} # 一致性
- fans, text
    - json {user_id: is_unfollowed}
- lastest_post_ts, timestamp


Blog:
- blog_id
    - 【sharding】
        - ts + shard_id(user_id % Sharding_NUM) + auto_incre（某个时刻，一个用户能创建多少个post）
- user_id, bigint(for now)
- content, text
- is_deleted, char(1)
- post_date, timestamp


Following
- user_id
- following_user_id


我感觉这种 networking ，用 DB 不太好，感觉可以用 table。
- 目前用DB
- TODO 后面改进为 Table


#### 设计意图


User:
- user_id
    - sharding里面考虑了什么？TODO 后面分布式再考虑
    【sharding】ts + shard_id(RR % NUM) + auto_incre，表示一个时刻，一个shardor上面能创建多少个用户

- user_posted: 一个人其实发不了多少微博，直接用一个list，保持他们的时间的先后顺序即可，我倾向于『头插』
    - 这里是否需要is_delete这样的逻辑标注？（因为blog表里面已经标注了，到时候联结？）
    - 我觉得这里还是用list string，到时候『联结』即可。
        1. 因为需要时间的先后顺序, "2,1", "3,2,1" ...
        2. 当你插入一条blog的时候，你能返回blog_id然后更新到User里面吗？
        3. blog_id如何做sharding？【结论，目前不做sharding】
            - 跟着用户
            - 如果某个用户非常hot，就...，那么blog_id也得转移？

- fans, text
    - pre: 不管怎么做，信息肯定是这么多信息，没办法去压缩的（也可以压缩一下 TODO ）。要么直接存放在一个表单里面，那么就数据量过大了（目前先存在这里）
    - 当有人取消关注我时...（我的关注者里面有4000w个人，其中某个人取消关注了我，我需要立即响应吗？其实不需要，只要保证他看不到我就行了）
    - 我发微博的时候，不是我主动推给粉丝，而是粉丝上线以后，主动获取时间线
    - 【业务上】这一部分，做为一个异步的操作，也是完全ok的，不需要无缝响应
    - 【技术上】必须实时相应呢？做一个逻辑删除？因为加一个flag，并没有使得space有数量级的增加
    - 但是，我需要获取4000w的数据时候，还是会很大吧？需要拆分吗？我觉得不能。必须使用堆，你才能知道某个用户是否关注了我，不然list就太麻烦了。json to map是一个基本的操作
    【对比】
    - 所以最终：- json {user_id: is_unfollowed}

Blog:
- blog_id, 自增？
    - 需要sharding吗？安放到一个地方，作为一个blog
    - 如果要sharding，你要么就不从属与一个user
    - 要么从属user， pre_user_id + post_blog_id，那样就太长了；同时，统一的读也不太方便？
    - 【业务上】一个用户发不了数量级非常高的微博，数据没有那么巨大
    - 到时可以考虑一下，**一致性**的问题
    - 也需要sharding ==== > 考虑这样几个问题，Sharding 最终的目的是为了什么？为了更快的性能
        - 如果是一张大表，那么多人同时发微博，不得挤爆？
        1. 分库分表（逻辑、物理）
        2. 至少某个user的所有blog都放在一个block里面吧
    - 【sharding】
        - ts + shard_id(user_id % NUM) + auto_incre
        - 某个时刻，一个用户能创建多少个post

#### TODO


1. 需要知道schema 等 Instagram blog里面的那些语法
    - https://instagram-engineering.com/sharding-ids-at-instagram-1cf5a71e5a5c
    ```
    CREATE OR REPLACE FUNCTION insta5.next_id(OUT result bigint) AS $$
    DECLARE
        our_epoch bigint := 1314220021721;
        seq_id bigint;
        now_millis bigint;
        shard_id int := 5;
    BEGIN
        SELECT nextval('insta5.table_id_seq') %% 1024 INTO seq_id;
        SELECT FLOOR(EXTRACT(EPOCH FROM clock_timestamp()) * 1000) INTO now_millis;
        result := (now_millis - our_epoch) << 23;
        result := result | (shard_id <<10);
        result := result | (seq_id);
    END;
        $$ LANGUAGE PLPGSQL;


    CREATE TABLE insta5.our_table (
        "id" bigint NOT NULL DEFAULT insta5.next_id(),
        ...rest of table schema...
    )
    ```
2. 需要知道怎么使用逻辑分区
    - https://pgdash.io/blog/postgres-11-sharding.html
    - https://about.gitlab.com/handbook/engineering/development/enablement/database/doc/fdw-sharding.html
    - 同一个物理机 / 分物理机（docker）
    - cluster 怎么配置，google docker 配置一个 postgres cluster

搞清以上两点，
- 对于postgres，就比较熟悉了（sql语法什么的）
- 对于分布式系统，就敢说涉及过了


## 时间线设计


### （sql 需求）
sql: 找到follow里面，lastest_post_ts 的十个人


follow_str => follow_list => '(1,2,3,4)'
我关注的人，按照 lastest_post_ts 排序

"select * from User where user_id in {} order by lastest_post_ts;".format(follow_list_str)


sql：for userid in tok_10_user: 找到每个人最近的十条微博，except is_deleted

每个人发的微博（Blog表里面，按照user_id加索引）

select * from Blog where user_id in {} group by user_id HAVING COUNT(user_id) <= 10 order by post_date desc; # TEST，肯定需要用到group by

找到每个用户的前10个，而不是一个用户的前是个


于是乎，目前就有了一百个（可以加到cache里面进行增量） TODO 后面再说（并且对比性能）
- blog_id
- user_id
- post_ts
- content


##### diff

【重要】有了数据之后进行测试
直接sql获取这些用户的前十（整体前十）
sql获取每个人的前十，然后「代码」对比数据
    - 一次获取一百条
    - 代码for循环 10 * 10

- 尝试直接用 sql
- 尝试 sql + 代码
- 看看效果

### 关于读写问题

是否需要在代码层面设置 锁 一类的东西？在哪里设置？


### 验证

0. 创建一个脚本，大量的创建用户和发微博，看看数据能不能对上号？（多用几个process，进行高并发的创建。模拟那个生产环境）
    - 创建用户，可以提出来用 restful （TODO 这里就要加 Django 了）
    - 创建了 restful 以后，就可以进行 benchmark 了
1. 先加缓存
2. 然后看看能不能负载均衡
3. 然后看看能不能加消息队列，怎么加消息队列（用一下kafka）

