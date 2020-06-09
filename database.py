import psycopg2
from global_names import *


class FakeOrm:
    def __init__(self):
        self.tg_id = None
        self.inst_log=None 
        self.tg_log=None, 
        self.profile_type=None
        self.mean_likes=None, 
        self.rating=None
        self.ref_link=None
        self.verified=False, 
        self.bio=None
        self.hashtags=None
        self.followers=None, 
        self.pub_content=None
        self.category=None
        self.subcategory=None, 
        self.pub_info=None
        self.user_rating=None

        self.conn = psycopg2.connect(dbname=DATABASE, user=USER, 
                                    password=PASSWORD, 
                                    host=HOST,
                                    port=PORT)

    def telegram_insert(self):
        curs = self.conn.cursor()
        curs.execute("INSERT INTO tg_data(tg_id, inst_log, tg_log, profile_type, followers, mean_likes, rating, ref_link, verified, bio, hashtags) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s, %s)", (self.tg_id, self.inst_log, self.tg_log, self.profile_type, self.followers, self.mean_likes, self.rating, self.ref_link, self.verified, self.bio, self.hashtags))
        self.conn.commit()
        self.conn.close()


    def instagram_insert(self):
        curs = self.conn.cursor()
        curs.execute("INSERT INTO insta_info(inst_log, followers, pub_content, category, subcategory, pub_info) VALUES (%s, %s, %s, %s, %s, %s)", (self.inst_log, self.followers, self.pub_content, self.category, self.subcategory, self.pub_info))
        self.conn.commit()
        self.conn.close()

    def rating_insert(self):
        curs = self.conn.cursor()
        curs.execute("INSERT INTO rating(user_rating) VALUES (%s)", (self.user_rating))
        self.conn.commit()
        self.conn.close()