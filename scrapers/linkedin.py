import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, OnSiteOrRemoteFilters
from dotenv import load_dotenv

# logging.basicConfig(level=logging.INFO)

load_dotenv(override=True)

def on_data(data: EventData):
    print("[ON DATA]", data.title, data.link.split("?")[0], data.date, len(data.description))


def on_metrics(metrics: EventMetrics):
    print("[ON METRICS]", str(metrics))

def on_error(error):
    print("[ON ERROR]", error)

def on_end():
    print("[ON END]")


scraper = LinkedinScraper(
    chrome_executable_path=None,
    chrome_binary_location=None,
    chrome_options=None,
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

try:
    scraper.run(queries)
except KeyboardInterrupt:
    print("scraper interrupted by user.")
