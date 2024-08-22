from utils.scraper import start_driver, get_element_details
from selenium_driverless.types.by import By
from bs4 import BeautifulSoup
import asyncio


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
    return read_queries("utils/queries/tech.csv")


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

    urls = [f"https://www.skool.com{href}/about" for href in hrefs]
    return urls


async def get_communities(driver, query):
    # url = f"https://www.skool.com/discovery?q={query}"
    url = "https://www.skool.com/discovery?p=34&q=business"
    await driver.get(url, wait_load=True)
    await driver.sleep(0.5)
    await driver.wait_for_cdp("Page.domContentEventFired", timeout=15)

    urls = []
    urls.extend(await get_urls(query, await driver.page_source))
    next_button = await driver.find_element(By.XPATH, "//button[.//span[contains(text(), 'Next')]]")
    next_button_details = await get_element_details(driver, next_button)

    while next_button and not next_button_details.get("disabled"):
        await driver.sleep(2)
        await next_button.click()
        await driver.sleep(0.5)
        await driver.wait_for_cdp("Page.domContentEventFired", timeout=15)
        urls.extend(await get_urls(query, await driver.page_source))
        next_button = await driver.find_element(By.XPATH, "//button[.//span[contains(text(), 'Next')]]")
        next_button_details = await get_element_details(driver, next_button)

    await driver.sleep(99999)
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
    write_queries("utils/queries/valid_tech.csv", valid_tech_queries)
    write_queries("utils/queries/invalid_tech.csv", invalid_tech_queries)
    print(f"Arquivo tech.py atualizado. Queries removidas: {len(queries) - len(valid_tech_queries)}")


asyncio.run(main())
