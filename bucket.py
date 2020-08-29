import json
from aiogram import types

async def add_product_by_name(chat_id, product_name, one_product_price, amount):

    with open('buckets.json', 'r+', encoding='utf-8') as file:
        
        product_is_found = False
        data = json.load(file)
        try:
            goods = data[f"{chat_id}"]['goods']
            total_bucket_price = data[f"{chat_id}"]['total_bucket_price']

            for good in goods:
                if good['product_name'] == product_name:
                    product_is_found = True
                    good['amount'] += amount
                    good['total_product_price'] += (good['one_product_price'] * amount)
                    data[f"{chat_id}"]['total_bucket_price'] += (good['one_product_price'] * amount)
                    break
        except:
            data[f"{chat_id}"] = {"goods": [], "total_bucket_price": 0, "amount_of_products": 0}

        if not product_is_found:
            new_product = { "product_name": product_name, "one_product_price": int(one_product_price), "amount": int(amount), "total_product_price": one_product_price * amount }
            data[f"{chat_id}"]['goods'].append(new_product)
            data[f"{chat_id}"]['total_bucket_price'] += (one_product_price * amount)
            data[f"{chat_id}"]['amount_of_products'] += 1

        file.seek(0)
        file.write(json.dumps(data, ensure_ascii=False, indent=4))
        file.truncate()

#add_to_bucket("352290160", "suit", 100, 10)
#add_to_bucket("352290160", "gloves", 100, 10)

def add_product_by_number(chat_id, product_number, amount):
    
    with open('buckets.json', 'r+', encoding='utf-8') as file:
        
        product_is_found = False
        data = json.load(file)
        try:
            goods = data[f"{chat_id}"]['goods']
            total_bucket_price = data[f"{chat_id}"]['total_bucket_price']

            i = 1
            for good in goods:

                if i == product_number:
                    product_is_found = True
                    good['amount'] += amount
                    good['total_product_price'] += (good['one_product_price'] * amount)
                    data[f"{chat_id}"]['total_bucket_price'] += (good['one_product_price'] * amount)
                    break
                i += 1

            file.seek(0)
            file.write(json.dumps(data, ensure_ascii=False, indent=4))
            file.truncate()
            
            return True

        except:
            return False

def get_bucket_string(chat_id):

    with open('buckets.json', 'r+', encoding='utf-8') as file:
        
        data = json.load(file)
        try:
            goods = data[f"{chat_id}"]['goods']
            total_bucket_price = data[f"{chat_id}"]['total_bucket_price']
            amount_of_products = data[f"{chat_id}"]['amount_of_products']
            
            if amount_of_products == 0:
                return None

            result = "Ваша корзина:\n"
            i = 1
            for good in goods:

                name = good["product_name"]
                am = good['amount']
                total_product = good['total_product_price']
                result += f"{i}. {name} в количестве: {am}, в сумме: {total_product}₽\n\n"
                i += 1
            
            result += f"----------------------------------\nИтого: {total_bucket_price}₽"
            
            return result
        except:
            return None

def get_bucket_for_checkout(chat_id):
    with open('buckets.json', 'r+', encoding='utf-8') as file:
        
        data = json.load(file)
        try:
            goods = data[f"{chat_id}"]['goods']
            total_bucket_price = data[f"{chat_id}"]['total_bucket_price']
            amount_of_products = data[f"{chat_id}"]['amount_of_products']
            
            if amount_of_products == 0:
                return None

            description = ""
            prices = []

            i = 1
            for good in goods:
                name = good['product_name']
                am = good['amount']
                total_product = good['total_product_price']
                description += f"{i}. {name} в количестве: {am}, в сумме: {total_product}₽\n"
                prices.append(types.LabeledPrice(label=name, amount=(total_product*100)))
                i += 1

            return description, prices
            
        except:
            return None

def remove_bucket(chat_id):
    
    with open('buckets.json', 'r+', encoding='utf-8') as file:
        
        data = json.load(file)
        try:
            del data[f"{chat_id}"]
            file.seek(0)
            file.write(json.dumps(data, ensure_ascii=False, indent=4))
            file.truncate()
            return True

        except:
            return False

def get_product_by_number(chat_id, num_of_product):
    with open('buckets.json', 'r+', encoding='utf-8') as file:
        
        data = json.load(file)
        try:
            goods = data[f"{chat_id}"]['goods']
            result = "Продукт для редактирования:\n"
            i = 1
            for good in goods:
                if i == num_of_product:
                    name = good["product_name"]
                    am = good['amount']
                    total_product = good['total_product_price']
                    result += f"{i}. {name} в количестве: {am}, в сумме: {total_product}₽\n\n"
                    break

                i += 1

            return result

        except:
            return None


def remove_from_bucket(chat_id, product_number, amount, delete_all):

    with open('buckets.json', 'r+', encoding='utf-8') as file:
        product_is_found = False
        data = json.load(file)
        try:
            goods = data[f"{chat_id}"]['goods']
            i = 1
            for good in goods:
                if i == product_number:
                    product_is_found = True
                    if delete_all:
                        data[f"{chat_id}"]['total_bucket_price'] -= (good['one_product_price'] * good['amount'])
                        good['amount'] = 0
                    else:
                        if amount >= good['amount']:
                            amount = good['amount']

                        good['amount'] -= amount
                        good['total_product_price'] -= (good['one_product_price'] * amount)
                        data[f"{chat_id}"]['total_bucket_price'] -= (good['one_product_price'] * amount)

                    if good['amount'] <= 0:
                        goods.remove(good)
                        data[f"{chat_id}"]['amount_of_products'] -= 1
                    break
                i += 1

            if data[f"{chat_id}"]['amount_of_products'] == 0:
                del data[f"{chat_id}"]

            file.seek(0)
            file.write(json.dumps(data, ensure_ascii=False, indent=4))
            file.truncate()

            if product_is_found:
                return True
            else:
                return False   

        except:
            return False 

#print(remove_from_bucket("352290160", 1, 1, False))

def get_amount_of_products(chat_id):
    with open('buckets.json', 'r+', encoding='utf-8') as file:
        
        data = json.load(file)
        try:
            am = data[f"{chat_id}"]['amount_of_products']
            return am
        except:
            return 0

#remove_from_bucket("352290160", "suit", 100, 10)

#print(remove_bucket("352290160"))

