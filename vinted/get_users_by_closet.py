import aiohttp
import asyncio
import json

base_url = "https://www.vinted.fr/"
promoted_closet = f"https://www.vinted.fr/api/v2/promoted_closets?per_page=50"
# ["promoted_closets"][i]["user"]["id"]


async def getPromotedCloset(session):
    async with session.get(f"{promoted_closet}") as response:
        if response.status == 200:
            json_response = await response.json()
            return json_response


async def getCloset(session):
    tasks = []
    task = asyncio.create_task(getPromotedCloset(session))
    tasks.append(task)

    responses = await asyncio.gather(*tasks)
    return responses


async def main():
    pages = range(1, 3)  # max 200 page, get error 500 after
    async with aiohttp.ClientSession() as session:
        await session.get(base_url)
        closets = await getCloset(session)
        with open("closet.json", "w", encoding="utf-8") as f:
            json.dump(closets, f)
        return closets


def getNewUsers():
    "return a dict {user_id: item_count} of users from closet"

    users_dict = {}
    # ["promoted_closets"][i]["user"]["id"]
    with open("closet.json", "r", encoding="utf-8") as f:
        json_closet = json.load(f)
    for promoted_closets in json_closet:
        closets = promoted_closets["promoted_closets"]
        for closet in closets:
            user = closet["user"]
            user_id = user["id"]
            user_item_count = user["item_count"]
            users_dict[user_id] = user_item_count
    return users_dict


def addUsers(users_dict):

    json_users = getUsers()
    with open("users_list.json", "w+") as f:
        users_dict.update(json_users)
        json.dump(users_dict, f)


def getUsers():
    try:
        f = open("users_list.json", "r")
        json_users = json.load(f)
    except Exception as e:  # file doesn't exist
        print(repr(e))
        json_users = {}
    return json_users


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    users = asyncio.run(main())
    users_dict = getNewUsers()
    addUsers(users_dict)
