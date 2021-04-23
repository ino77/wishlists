from imdb import IMDb
from googletrans import Translator
from requests import *
import vk_api
import random
import sqlite3
import time


def rung(s):
    translator = Translator()
    translation = translator.translate(s, src='ru', dest='en')
    return translation.text


def search(s):
    ia = IMDb()
    series = ia.search_movie(s)
    if len(series) == 0:
        return []
    return series

f = open('ids.txt', 'r+')
c = f.readlines()
token = "ecbde2a84cae25f0504f3ae8454220b8fdc91eaab9f3873118afc2195310bcd693dc667c1882240b988c6"
vk = vk_api.VkApi(token=token)
vk._auth_token()
conn = sqlite3.connect('fdb.db')
cur = conn.cursor()
while True:
    print('Бот запущен')
    messages = vk.method("messages.getConversations", {"offset": 0, "count": 20, "filter": "unanswered"})
    if messages["count"] >= 1:
        id = messages["items"][0]["last_message"]["from_id"]
        body = messages["items"][0]["last_message"]["text"]
        print(c)
        if not f'{str(id)}\n' in c:
            f.writelines(f'{id}\n')
            w = f"""CREATE TABLE u{int(id)} (
                       fname TEXT,
                       fimdb TEXT,
                       izbr INT);"""
            print(w)
            cur.execute(w)
            conn.commit()
        if "/удалить" in body.lower():
            s = body[8:].strip()
            print(s)
            cur.execute(f'''SELECT fname FROM u{id} WHERE fname='{s}';''')
            t = len(cur.fetchall())
            if t != 0:
                cur.execute(f"DELETE FROM u{id} WHERE fname='{s}';")
                conn.commit()
                vk.method("messages.send",
                        {"peer_id": id, "message": "сделано.", "random_id": random.randint(1, 2147483647)})
            else:
                vk.method("messages.send",
                          {"peer_id": id, "message": "Этого нет в вашем списке", "random_id": random.randint(1, 2147483647)})
        if "/добавить" in body.lower():
            s = body[8:].strip()
            if 1040 <= ord(s[0]) <= 1103:
                s = rung(s)
            z = search(s)
            if len(search(s)) == 0:
                vk.method("messages.send",
                          {"peer_id": id, "message": "Ничего не найдено", "random_id": random.randint(1, 2147483647)})
            else:
                vk.method("messages.send",
                          {"peer_id": id, "message": f"{z[0]} \n https://www.imdb.com/title/tt{z[0].getID()}",
                           "random_id": random.randint(1, 2147483647)})
                vk.method("messages.send", {"peer_id": id, "message": "Это то, что вы искали?",
                                            "random_id": random.randint(1, 2147483647)})
        elif body.lower() == 'да':
            w2 = f'''select * from u{id}'''
            cur.execute(w2)
            res = len(cur.fetchall())
            print(res)
            ww = f'''SELECT fimdb FROM u{id}'''
            cur.execute(ww)
            re = cur.fetchall()
            h = []
            for x in re:
                h.append(x[0])
            if not f'https://www.imdb.com/title/tt{z[0].getID()}' in h:
                w1 = f'''INSERT INTO u{id}(fname, fimdb, izbr) 
                    VALUES('{z[0]}', 'https://www.imdb.com/title/tt{z[0].getID()}', {res + 1});'''
                cur.execute(w1)
                conn.commit()
            vk.method("messages.send",
                      {"peer_id": id, "message": "Добавлено", "random_id": random.randint(1, 2147483647)})
        elif body.lower() == 'нет':
            z.remove(z[0])
            vk.method("messages.send",
                      {"peer_id": id, "message": f"{z[0]} \n https://www.imdb.com/title/tt{z[0].getID()}",
                       "random_id": random.randint(1, 2147483647)})
            vk.method("messages.send",
                      {"peer_id": id, "message": f"Это то, что вы искали?", "random_id": random.randint(1, 2147483647)})
        elif body.lower() == '/список':
            k = 1
            w2, w4 = f'''select * from u{id}''', ''
            cur.execute(w2)
            res = cur.fetchall()
            if len(res) == 0:
                vk.method("messages.send", {"peer_id": id, "message": 'Ваш список пуст', "random_id": random.randint(1, 2147483647)})
            else:
                for x in res:
                    w4 += f'{k}) {x[0]} \n'
                    k += 1
                k = 1
                vk.method("messages.send", {"peer_id": id, "message": w4, "random_id": random.randint(1, 2147483647)})

