from utils.scraper import start_driver
from selenium.webdriver.common.by import By
import asyncio
import time
import json
import csv
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir_abspath = os.path.abspath(current_dir)


def read_urls(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def write_urls(file_path, urls):
    with open(file_path, "w") as f:
        for url in urls:
            f.write(url + "\n")


async def main():
    driver = await start_driver()
    urls = read_urls(f"{current_dir_abspath}/unique_urls_formatted.csv")

    for url in urls:
        start_time = time.time()
        await driver.get(url, wait_load=True)
        await driver.sleep(2)

        data = await driver.find_element(By.ID, "__NEXT_DATA__")

        if data:
            data_text = await data.get_attribute("innerHTML")
            data_dict = json.loads(data_text)
            group_dict = data_dict.get("props", {}).get("pageProps", {}).get("currentGroup", {})

            if group_dict:
                group_name = group_dict.get("name", "")
                group_title = group_dict.get("metadata", {}).get("displayName", "")
                group_url = url
                group_support_email = group_dict.get("metadata", {}).get("gbSupportEmail", "")

                owner_text = group_dict.get("metadata", {}).get("owner")

                if owner_text:
                    owner_dict = json.loads(owner_text)
                    owner_name = f"{owner_dict.get('first_name', '')} {owner_dict.get('last_name', '')}"
                    owner_email = owner_dict.get("email", "")
                    link_instagram = owner_dict.get("metadata", {}).get("link_instagram", "")
                    link_facebook = owner_dict.get("metadata", {}).get("link_facebook", "")
                    link_linkedin = owner_dict.get("metadata", {}).get("link_linkedin", "")
                    link_twitter = owner_dict.get("metadata", {}).get("link_twitter", "")
                    link_youtube = owner_dict.get("metadata", {}).get("link_youtube", "")
                    link_website = owner_dict.get("metadata", {}).get("link_website", "")

                    if not link_instagram and link_website:
                        await driver.get(link_website, wait_load=True)
                        await driver.sleep(2)
                        try:
                            link_instagram = await driver.find_element(By.XPATH, "//a[contains(@href, 'instagram.com')]")
                            if link_instagram:
                                link_instagram = await link_instagram.get_attribute("href")
                        except Exception:
                            try:
                                about_button = await driver.find_element(By.XPATH, "//a[contains(@href, 'about')]")
                                if about_button:
                                    await about_button.click()
                                    await driver.sleep(2)
                                    link_instagram = await driver.find_element(By.XPATH, "//a[contains(@href, 'instagram.com')]")
                                    if link_instagram:
                                        link_instagram = await link_instagram.get_attribute("href")
                            except Exception:
                                try:
                                    contact_button = await driver.find_element(By.XPATH, "//a[contains(@href, 'contact')]")
                                    if contact_button:
                                        await contact_button.click()
                                        await driver.sleep(2)
                                        link_instagram = await driver.find_element(By.XPATH, "//a[contains(@href, 'instagram.com')]")
                                        if link_instagram:
                                            link_instagram = await link_instagram.get_attribute("href")
                                except Exception:
                                    pass

        creator_data = {
            "owner_name": owner_name,
            "owner_email": owner_email,
            "link_instagram": link_instagram,
            "link_facebook": link_facebook,
            "link_linkedin": link_linkedin,
            "link_twitter": link_twitter,
            "link_youtube": link_youtube,
            "link_website": link_website,
            "group_name": group_name,
            "group_title": group_title,
            "group_url": group_url,
            "group_support_email": group_support_email,
        }

        headers = [
            "owner_name",
            "owner_email",
            "link_instagram",
            "link_facebook",
            "link_linkedin",
            "link_twitter",
            "link_youtube",
            "link_website",
            "group_name",
            "group_title",
            "group_url",
            "group_support_email",
        ]

        creator_data_path = f"{current_dir_abspath}/creator_data.csv"
        creator_data_path_exists = os.path.exists(creator_data_path)
        creator_data_file_empty = creator_data_path_exists and os.path.getsize(creator_data_path) == 0

        with open(f"{current_dir_abspath}/creator_data.csv", "a+", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)

            if not creator_data_path_exists or creator_data_file_empty:
                writer.writeheader()

            writer.writerow(creator_data)

        print(f"Data saved for URL: {url}")

        elapsed_time = time.time() - start_time

        if elapsed_time < 5:
            await driver.sleep(5 - elapsed_time)

    await driver.quit()


asyncio.run(main())
