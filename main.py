from imdb import IMDb
from googletrans import Translator
import vk_api
import random
import sqlite3
import time
import threading
import wikipedia


def rung(s):
    # так как imdb не работает с рускоязычными запросами, то необходима функция переводящая их
    translator = Translator()
    translation = translator.translate(s, src='ru', dest='en')
    return translation.text


def search(s):
    # функция, которая посылает запросы на imdb
    ia = IMDb()
    series = ia.search_movie(s)
    if len(series) == 0:
        return []
    return series


lang_kodes = {'Абхазия': 'AB', 'Алжир': 'DZ', 'Армения': 'AM', 'Бельгия': 'BE', 'Бермуды': 'BM', 'Болгария': 'BG',
              'Бразилия': 'BR', 'Вьетнам': 'VN', 'Дания': 'DK', 'Египет': 'EG', 'Израиль': 'IL', 'Ирландия': 'IE',
              'Испания': 'ES', 'Италия': 'IT', 'Казахстан': 'KZ', 'Канада': 'KA', 'Киргизия': 'KG', 'Китай': 'CN',
              'Куба': 'CU', 'Латвия': 'LV', 'Мальта': 'MT', 'Мексика': 'MX', 'Молдова': 'MD', 'Монголия': 'MN',
              'Нигер': 'NV', 'Норвегия': 'NO', 'Объединенные Арабские Эмираты': 'AE', 'Польша': 'PL',
              'Португалия': 'PT', 'Россия': 'RU', 'Сент-Люсия': 'LC', 'Сингапур': 'SG',
              'Соединенные Штаты Америки': 'US', 'Таиланд': 'TH', 'Уганда': 'UG', 'Украина': 'UA', 'Франция': 'FR',
              'Хорватия': 'HR', 'Чад': 'TD'}

wikipedia.set_lang("ru")
# устанавливаем русский язык для апи википедии
f = open('ids.txt', 'r+')
c = f.readlines()
token = "ecbde2a84cae25f0504f3ae8454220b8fdc91eaab9f3873118afc2195310bcd693dc667c1882240b988c6"
# здесь неоходимо задать уникальный токен группы вк
vk = vk_api.VkApi(token=token)
vk._auth_token()
conn = sqlite3.connect('fdb.db')
# подключаемся к базе данных с клиентами и фильмами
cur = conn.cursor()
while True:
    # основной функциональный код бота
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
                          {"peer_id": id, "message": "Этого нет в вашем списке",
                           "random_id": random.randint(1, 2147483647)})
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
                vk.method("messages.send",
                          {"peer_id": id, "message": 'Ваш список пуст', "random_id": random.randint(1, 2147483647)})
            else:
                for x in res:
                    w4 += f'{k}) {x[0]} \n'
                    k += 1
                k = 1
                vk.method("messages.send", {"peer_id": id, "message": w4, "random_id": random.randint(1, 2147483647)})
        elif '/справка' in body.lower():
            vk.method("messages.send", {"peer_id": id, "message": f'{wikipedia.summary(body.lower().split()[1:])} \n',
                                        "random_id": random.randint(1, 2147483647)})
            wiki_material = wikipedia.page(body.lower().split()[1:]).images[0]
            vk.method("messages.send", {"peer_id": id,
                                        "message": f'Материал по теме: \n {wiki_material}',
                                        "random_id": random.randint(1, 2147483647)})
        elif '/перевод' in body.lower():
            translator = Translator()
            translation = translator.translate(body[8:])
            if not (1040 <= ord(body[8:][0]) <= 1103):
                translation = translator.translate(body[8:], dest='ru')
            else:
                translation = translator.translate(body[8:], dest='en')
            vk.method("messages.send", {"peer_id": id, "message": {translation.text},
                                        "random_id": random.randint(1, 2147483647)})
        elif '/код' in body.lower():
            j = 0
            for k, v in lang_kodes.items():
                if body.lower()[3:].strip() in k.lower():
                    vk.method("messages.send", {"peer_id": id, "message": f'{v}',
                                                "random_id": random.randint(1, 2147483647)})
                    j += 1
            if j == 0:
                vk.method("messages.send", {"peer_id": id, "message": 'нет идей',
                                            "random_id": random.randint(1, 2147483647)})
        elif body.lower() == '/игра':
            vk.method("messages.send", {"peer_id": id, "message": f'Выберите \n 1 - камень, 2 - ножницы, 3 - бумага',
                                        "random_id": random.randint(1, 2147483647)})
        elif body.lower() == '1' or body.lower() == '2' or body.lower() == '3':
            player = int(body)
            comp = random.randint(1, 3)
            if comp == 1:
                vk.method("messages.send", {"peer_id": id, "message": 'Компьютер выбрал камень.',
                                            "random_id": random.randint(1, 2147483647)})
            elif comp == 2:
                vk.method("messages.send", {"peer_id": id, "message": 'Компьютер выбрал ножницы.',
                                            "random_id": random.randint(1, 2147483647)})
            elif comp == 3:
                vk.method("messages.send", {"peer_id": id, "message": 'Компьютер выбрал бумагу.',
                                            "random_id": random.randint(1, 2147483647)})
            if player == comp:
                win = 0
            elif player == 1 and comp == 2:
                win = 1
            elif player == 1 and comp == 3:
                win = 2
            elif player == 2 and comp == 1:
                win = 2
            elif player == 2 and comp == 3:
                win = 1
            elif player == 3 and comp == 1:
                win = 1
            elif player == 3 and comp == 2:
                win = 2
            elif win == 0:
                vk.method("messages.send", {"peer_id": id, "message": "Ничья!",
                                            "random_id": random.randint(1, 2147483647)})
            elif win == 1:
                vk.method("messages.send", {"peer_id": id, "message": "Победил игрок!",
                                            "random_id": random.randint(1, 2147483647)})
            elif win == 2:
                vk.method("messages.send", {"peer_id": id, "message": "Победил компьютер!",
                                            "random_id": random.randint(1, 2147483647)})
        else:
            vk.method("messages.send", {"peer_id": id, "message": 'Видимо я чего то не понимаю',
                                        "random_id": random.randint(1, 2147483647)})
