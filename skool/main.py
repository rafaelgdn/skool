from utils.scraper import start_driver, get_element_details
from selenium_driverless.types.by import By
from bs4 import BeautifulSoup
import os
import asyncio

current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir_abspath = os.path.abspath(current_dir)
queries_dir = os.path.join(current_dir_abspath, "utils/queries")

valid_tech_queries = []
invalid_tech_queries = []


def read_queries(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def write_queries(file_path, queries):
    with open(file_path, "w") as f:
        for query in queries:
            f.write(query + "\n")


def get_tech_queries():
    return read_queries(f"{queries_dir}/tech.csv")


async def get_urls(query, content):
    soup = BeautifulSoup(content, "html.parser")
    discovery_cards = soup.css.select("div[class*='DiscoveryCards']")

    if not discovery_cards:
        invalid_tech_queries.append(query)
        print(f"No communities found for query: {query}")
        return []

    hrefs = discovery_cards[0].select("a[href]")

    if not hrefs:
        return []

    urls = [f"https://www.skool.com{a['href']}/about" for a in hrefs if "href" in a.attrs]

    return urls


async def get_communities(driver, query):
    url = f"https://www.skool.com/discovery?q={query}"
    await driver.get(url, wait_load=True)
    await driver.sleep(0.5)
    await driver.wait_for_cdp("Page.domContentEventFired", timeout=15)

    urls = []
    urls.extend(await get_urls(query, await driver.page_source))

    while True:
        try:
            next_button = await driver.find_element(By.XPATH, "//button[.//span[contains(text(), 'Next')]]")
            next_button_details = await get_element_details(driver, next_button)

            if "disabled" in next_button_details or next_button_details.get("disabled") == "":
                print(f"No more pages for query: {query}")
                break

            await driver.sleep(0.5)
            await next_button.click()
            await driver.sleep(2)

            urls.extend(await get_urls(query, await driver.page_source))
        except Exception as e:
            print(f"Erro ao navegar para a próxima página: {e}")
            break

    return urls


async def main():
    driver = await start_driver()
    queries = get_tech_queries()

    for query in queries[0:3]:
        urls = await get_communities(driver, query)
        if urls:
            valid_tech_queries.append(query)
            print("urls: ", urls)
            with open("urls.txt", "a") as f:
                f.write("\n".join(urls))

    await driver.quit()
    write_queries(f"{queries_dir}/valid_tech.csv", valid_tech_queries)
    write_queries(f"{queries_dir}/invalid_tech.csv", invalid_tech_queries)
    print(f"Arquivo tech.py atualizado. Queries removidas: {len(queries) - len(valid_tech_queries)}")


asyncio.run(main())
