import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, OnSiteOrRemoteFilters
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
import os

# logging.basicConfig(level=logging.INFO)

load_dotenv(override=True)
LI_AT = os.getenv("LI_AT_COOKIE")

def get_linkedin_jobs():
    """
    get linked jobs (seen or unseen, 40)
    """

    job_list = []
    current_job_list = []
    final_list = []

    def on_data(data: EventData):
        nonlocal job_list
        job_list.append([
            data.title,
            data.company,
            data.skills,
            data.description,
            data.date,
            data.apply_link,
            data.job_id,
            data.link.split("?")[0],
        ])
        # print("[ON DATA]", data.title, data.link.split("?")[0], data.date, len(data.description))
        # print(job_list)


    def on_metrics(metrics: EventMetrics):
        print("[ON METRICS]", str(metrics))

    def on_error(error):
        print("[ON ERROR]", error)

    def on_end():
        nonlocal job_list, current_job_list
        current_job_list.append(job_list)
        job_list = []
        print("[ON END]")

    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--proxy-server=http://102.23.228.240:8080")

    scraper = LinkedinScraper(
        chrome_executable_path=None,
        chrome_binary_location="/usr/bin/chromium-browser",
        chrome_options=chrome_options,
        headless=True,
        max_workers=1,
        slow_mo=3,
        page_load_timeout=30,
    )

    scraper.on(Events.DATA, on_data)
    scraper.on(Events.ERROR, on_error)
    scraper.on(Events.END, on_end)

    queries = [
        Query(
            options=QueryOptions(
                limit=30,
                locations=["Worldwide"],
                apply_link=False,
                filters=QueryFilters(
                    relevance=RelevanceFilters.RECENT,
                    on_site_or_remote=OnSiteOrRemoteFilters.REMOTE
                )
            )
        ),
        Query(
            options=QueryOptions(
                limit=10,
                locations=["Nigeria"],
                apply_link=False,
                filters=QueryFilters(
                    relevance=RelevanceFilters.RECENT
                )
            )
        )
    ]

    scraper.run(queries)
    final_list = current_job_list[:]

    return final_list
