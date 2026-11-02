"""Google Flights price tracker in Python (no API key)

Track Google Flights fares for many routes and dates, save the cheapest flight per day to CSV, and run it daily. Uses the Google Flights Scraper on Apify — no Google account or API key.
Actor: https://apify.com/rt-solutions/google-flights-scraper
"""
import os
from apify_client import ApifyClient
import csv

client = ApifyClient(os.environ["APIFY_TOKEN"])  # Apify Console → Settings → API & Integrations

run = client.actor("rt-solutions/google-flights-scraper").call(run_input={
    "origins": ["JFK"],
    "destinations": ["LHR"],
    "departureDates": ["2026-12-01..2026-12-07"],
    "stops": "nonstop",
})

rows = list(client.dataset(run.default_dataset_id).iterate_items())

# Cheapest flight per departure date
best = {}
for f in rows:
    d = f["departureDate"]
    if f.get("price") and (d not in best or f["price"] < best[d]["price"]):
        best[d] = f

with open("cheapest_jfk_lhr.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["date", "price", "currency", "airlines", "departure", "durationMinutes"])
    for d, f in sorted(best.items()):
        w.writerow([d, f["price"], f["currency"], "/".join(f["airlines"]), f["departure"], f["durationMinutes"]])

print(f"{len(rows)} flights, cheapest per day saved to cheapest_jfk_lhr.csv")
