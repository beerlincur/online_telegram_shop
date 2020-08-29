import json

async def add_user(chat_id):
    with open("users.json", "r+", encoding="utf-8") as file:
        data = json.load(file)
        ch = str(chat_id)
        if ch not in data["users"]:
            data["users"].append(ch)
            file.seek(0)
            file.write(json.dumps(data, ensure_ascii=False, indent=4))
            file.truncate()
        
        return chat_id

async def get_all_users():
    with open("users.json", "r+", encoding="utf-8") as file:
        data = json.load(file)
        return data["users"]

async def get_count_users():
    with open("users.json", "r+", encoding="utf-8") as file:
        data = json.load(file)
        return len(data["users"])