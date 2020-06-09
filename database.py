import psycopg2
from global_names import *


class FakeOrm:
    def __init__(self):
        default_attr = dict(tg_id=None, inst_log=None, tg_log=None, 
            profile_type=None, mean_likes=None, 
            rating=None, ref_link=None, verified=False, 
            bio=None, hashtags=None, followers=None, 
            pub_content=None, category=None, subcategory=None, 
            pub_info=None, user_rating=None)

        self.conn = psycopg2.connect(dbname=DATABASE, user=USER, 
                                    password=PASSWORD, 
                                    host=HOST,
                                    port=PORT)

    def telegram_insert(self):
        curs = self.conn.cursor()
        curs.execute("INSERT INTO tg_data(tg_id, inst_log, tg_log, profile_type, followers, mean_likes, rating, ref_link, verified, bio, hashtags) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s, %s)", (tg_id, inst_log, tg_log, profile_type, followers, mean_likes, rating, ref_link, verified, bio, hashtags))
        self.conn.commit()
        self.conn.close()


    def instagram_insert(self):
        curs = self.conn.cursor()
        curs.execute("INSERT INTO insta_info(inst_log, followers, pub_content, category, subcategory, pub_info) VALUES (%s, %s, %s, %s, %s, %s)", (inst_log, followers, pub_content, category, subcategory, pub_info))
        self.conn.commit()
        self.conn.close()

    def rating_insert(self):
        curs = self.conn.cursor()
        curs.execute("INSERT INTO rating(user_rating) VALUES (%s)", (user_rating))
        self.conn.commit()
        self.conn.close()