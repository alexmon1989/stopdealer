"""Форматирование номеров телефонов для дальнейшего поиска их с сайта."""
import pymongo

connection = pymongo.MongoClient()
collection = connection.e1_automobiles.automobiles

for x in collection.find():
    if x['seller']['phone']:
        phone = x['seller']['phone']\
            .replace('+7', '')\
            .replace('-', '')\
            .replace('(', '')\
            .replace(')', '')\
            .replace(' ', '')
        if phone[0] in ['7', '8']:
            phone = phone[1:]
        collection.update({'_id': x['_id']}, {'$set': {'seller.phone': phone}})
