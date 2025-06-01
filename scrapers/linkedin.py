import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters

logging.basicConfig(level=logging.INFO)

def on_data(data: EventData):
    print("[ON DATA]", data.title, data.company_link, data.date, len(data.description))


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
    slow_mo=2,
    page_load_timeout=30,
)

scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

queries = [
    Query(
        options=QueryOptions(
            limit=5,
            locations=["Worldwide"],
            apply_link=False,
            filters=QueryFilters(
                relevance=RelevanceFilters.RECENT
            )
        )
    ),
    # Query(
    #     query="",
    #     options=QueryOptions(
    #         locations=["Nigeria"],
    #         apply_link=True,
    #         limit=5,
    #         filters=QueryFilters(
    #             relevance=RelevanceFilters.RECENT
    #         )
    #     )
    # )
]

try:
    scraper.run(queries)
except KeyboardInterrupt:
    print("scraper interrupted by user.")
