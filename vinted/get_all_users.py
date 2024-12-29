import aiohttp
import asyncio
import json

base_url = "https://www.vinted.fr/"
users_url = f"https://www.vinted.fr/api/v2/users?page="
search_users = f"https://www.vinted.fr/api/v2/users?page=200&search_text=l"
perpage = f"https://www.vinted.fr/api/v2/users?page=200&search_text=l&per_page=90"
propoted_closet = f"https://www.vinted.fr/api/v2/promoted_closets?per_page=50"
# ["promoted_closets"][i]["user"]["id"]


async def getUsersPage(session, page):
    async with session.get(f"{users_url}{page}") as response:
        if response.status == 200:
            json_response = await response.json()
            return json_response


async def getUsers(session, pages):
    tasks = []
    for page in pages:
        task = asyncio.create_task(getUsersPage(session, page))
        tasks.append(task)

    responses = await asyncio.gather(*tasks)
    return responses


async def main():
    pages = range(1, 201)  # max 200 page, get error 500 after
    async with aiohttp.ClientSession() as session:
        await session.get(base_url)
        users = await getUsers(session, pages)
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f)
        return users


def getUsersWithItems():
    "return list with user_id, item_count of users with items"
    formated_users_list = []
    with open("users.json", "r", encoding="utf-8") as f:
        json_users = json.load(f)
    for users_page in json_users:
        # users: id, item_count
        users_list = users_page["users"]
        for user in users_list:
            user_id = user["id"]
            user_item_count = user["item_count"]
            formated_users_list.append([user_id, user_item_count])
    users_with_items = [user for user in formated_users_list if user[1] > 0]
    return users_with_items


if __name__ == "__main__":
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # users = asyncio.run(main())
    users_list = getUsersWithItems()
