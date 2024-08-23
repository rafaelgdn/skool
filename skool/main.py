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
    return read_queries(f"{queries_dir}/unique_general.csv")


async def get_urls(driver, query, content):
    soup = BeautifulSoup(content, "html.parser")
    discovery_cards = soup.css.select("div[class*='DiscoveryCards']")

    if not discovery_cards:
        invalid_tech_queries.append(query)
        print(f"No communities found for query: {query}")
        await driver.sleep(30)
        return []

    hrefs = discovery_cards[0].select("a[href]")

    if not hrefs:
        return []

    urls = [f"https://www.skool.com{a['href']}/about" for a in hrefs if "href" in a.attrs]

    return urls


async def get_communities(driver, query):
    print(f"Searching communities for query: {query}")
    url = f"https://www.skool.com/discovery?q={query}"
    await driver.get(url, wait_load=True)
    await driver.sleep(2)

    urls = []
    urls.extend(await get_urls(driver, query, await driver.page_source))

    while True:
        try:
            print(f"Navigating to next page for query: {query}")
            retries = 0

            next_button = await driver.find_element(By.XPATH, "//button[.//span[contains(text(), 'Next')]]")
            next_button_details = await get_element_details(driver, next_button)

            if "disabled" in next_button_details or next_button_details.get("disabled") == "":
                print(f"No more pages for query: {query}")
                break

            await driver.sleep(0.5)
            await next_button.click()
            await driver.sleep(5)

            while True:
                retries += 1
                cards = await driver.find_elements(By.CSS_SELECTOR, "div[class*='DiscoveryCards']")
                if cards or retries > 5:
                    break
                await driver.sleep(2)

            urls.extend(await get_urls(driver, query, await driver.page_source))
        except Exception as e:
            print(f"Erro ao navegar para a próxima página: {e}")
            break

    return urls


async def main():
    driver = await start_driver()
    queries = get_tech_queries()

    await driver.get("https://www.skool.com/", wait_load=True)
    await driver.sleep(5)

    for query in queries:
        try:
            urls = await get_communities(driver, query)
            if urls:
                with open(f"{queries_dir}/last_query_valid.csv", "w") as q:
                    q.write(query)
                valid_tech_queries.append(query)
                print(f"Found {len(urls)} communities for query: {query}")
                with open(f"{queries_dir}/urls.csv", "a") as f:
                    f.write("\n".join(urls))
        except Exception:
            continue

    await driver.quit()
    write_queries(f"{queries_dir}/valid.csv", valid_tech_queries)
    write_queries(f"{queries_dir}/invalid.csv", invalid_tech_queries)
    print(f"Arquivo tech.py atualizado. Queries removidas: {len(queries) - len(valid_tech_queries)}")


asyncio.run(main())
