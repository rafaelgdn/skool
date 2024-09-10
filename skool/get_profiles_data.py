from utils.scraper import start_driver, get_element_details
from selenium_driverless.types.by import By
import os
import csv
import json
import time
import random
import asyncio

current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir_abspath = os.path.abspath(current_dir)


def clean_for_csv(text):
    if isinstance(text, str):
        return text.replace("\n", " ").replace("\r", "").replace('"', '""')
    return text


def save_users_in_file(users):
    creator_data_path = f"{current_dir_abspath}/timyoon_members_followers.csv"
    creator_data_path_exists = os.path.exists(creator_data_path)
    creator_data_file_empty = creator_data_path_exists and os.path.getsize(creator_data_path) == 0

    with open(creator_data_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=users[0].keys(), quoting=csv.QUOTE_ALL)
        if not creator_data_path_exists or creator_data_file_empty:
            writer.writeheader()
        cleaned_users = [{k: clean_for_csv(v) for k, v in user.items()} for user in users]
        writer.writerows(cleaned_users)


async def get_users_data(driver):
    data = await driver.find_element(By.ID, "__NEXT_DATA__")
    data_text = await data.get_attribute("innerHTML")
    data_dict = json.loads(data_text)
    items_list = data_dict.get("props", {}).get("pageProps", {}).get("items") or data_dict.get("props", {}).get("pageProps", {}).get("users", [])
    users = []
    for item in items_list:
        item_data = item.get("src", item)
        user = {
            "instagram": item_data.get("metadata", {}).get("linkInstagram", ""),
            "name": f"{item_data.get('firstName', '')} {item_data.get('lastName', '')}".strip(),
            "skool_username": item_data.get("name", ""),
            "email": item_data.get("email", ""),
            "facebook": item_data.get("metadata", {}).get("linkFacebook", ""),
            "linkedin": item_data.get("metadata", {}).get("linkLinkedin", ""),
            "twitter": item_data.get("metadata", {}).get("linkTwitter", ""),
            "website": item_data.get("metadata", {}).get("linkWebsite", ""),
            "youtube": item_data.get("metadata", {}).get("linkYoutube", ""),
            "location": item_data.get("metadata", {}).get("location", ""),
            "bio": item_data.get("metadata", {}).get("bio", ""),
        }
        users.append(user)
    save_users_in_file(users)
    return users


async def get_profiles_data(driver):
    start_time = time.time()

    while True:
        try:
            retries = 0

            # Waiting for Members list to load
            while True:
                retries += 1
                cards = await driver.find_elements(By.ID, "__NEXT_DATA__")
                if cards or retries > 5:
                    break
                await driver.sleep(2)

            await get_users_data(driver)

            next_button = await driver.find_element(By.XPATH, "//button[.//span[contains(text(), 'Next')]]")
            next_button_details = await get_element_details(driver, next_button)

            if "disabled" in next_button_details or next_button_details.get("disabled") == "":
                print("No more members pages")
                break

            await driver.sleep(0.5)
            await next_button.click()
            await driver.sleep(2)
            await driver.refresh()
            await driver.sleep(5)
        except Exception as e:
            print(f"Error navigating to the next page: {e}")
            break

    elapsed_time = time.time() - start_time
    if elapsed_time < 5:
        remaining_time = 5 - elapsed_time
        random_additional_time = random.uniform(0, 5)
        total_sleep_time = remaining_time + random_additional_time
        print(f"Tempo total de execução: {elapsed_time:.2f} segundos")
        print(f"Adicionando sleep de {total_sleep_time:.2f} segundos")
        await driver.sleep(remaining_time)


# communities members url or followers url
# https://www.skool.com/timyoon/-/members?t=member
# https://www.skool.com/@timyoon?t=followers
async def main():
    driver = await start_driver()
    await driver.get("https://www.skool.com/@timyoon?t=followers", wait_load=True)
    await driver.sleep(5)
    await get_profiles_data(driver)
    await driver.quit()


asyncio.run(main())
