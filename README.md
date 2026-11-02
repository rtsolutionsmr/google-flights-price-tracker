# Google Flights price tracker in Python (no API key)

Track Google Flights fares for many routes and dates, save the cheapest flight per day to CSV, and run it daily. Uses the Google Flights Scraper on Apify — no Google account or API key.

▶️ **Actor:** [rt-solutions/google-flights-scraper](https://apify.com/rt-solutions/google-flights-scraper) · runs on Apify's free plan

Google Flights has no public API. If you want to watch fares for a route every day, compare dozens of dates, or feed flight prices into a spreadsheet, you need a scraper. In this tutorial we'll collect Google Flights prices for many routes and dates in one run, export them to CSV, and schedule a daily price check.


## What you get

For every flight shown by Google Flights:

- total price and currency, rank on the results page
- airlines, departure / arrival time, duration, number of stops and layovers
- every leg: flight number, aircraft, legroom, codeshares
- CO2 emissions vs. the typical value for the route
- a direct Google Flights link

## 1. Try it without code

1. Open [Google Flights Scraper](https://apify.com/rt-solutions/google-flights-scraper) and click **Try for free**.
2. Fill in origins, destinations and dates:

```json
{ "origins": ["JFK"], "destinations": ["LHR"], "departureDates": ["2026-12-03"] }
```

3. Click **Start**. After a few seconds you can export the results as CSV, Excel or JSON.

## 2. Many routes × many dates in one run

You can give several airports and a **date range** (`start..end`). Every origin × destination × date becomes a search:

```json
{
  "origins": ["JFK", "EWR"],
  "destinations": ["LHR", "CDG"],
  "departureDates": ["2026-12-01..2026-12-14"],
  "tripLengthDays": 7,
  "cabinClass": "economy",
  "stops": "nonstop",
  "currency": "USD"
}
```

`tripLengthDays: 7` turns every search into a round trip returning 7 days later. Use `returnDate` instead for a fixed return day.

## 3. Run it from Python

```bash
pip install -r requirements.txt
export APIFY_TOKEN=your_token   # free account: https://apify.com
python track_prices.py
```

```python
import os
from apify_client import ApifyClient
import csv

client = ApifyClient(os.environ["APIFY_TOKEN"])

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
```

A flight item looks like this (shortened):

```json
{
  "origin": "JFK", "destination": "LHR", "departureDate": "2026-12-03",
  "price": 711, "currency": "EUR", "airlines": ["American"],
  "departure": "2026-12-03T18:25", "arrival": "2026-12-04T06:20",
  "durationMinutes": 415, "stops": 0, "co2Kg": 421,
  "legs": [{ "flightNumber": "AA 100", "aircraft": "Boeing 777", "legroom": "31 inches" }]
}
```

## 4. Track fares every day

In Apify Console open the Actor → **Schedules** → run it daily with the same input. Each run is a new dataset, so you can append the cheapest price per date to a Google Sheet (Apify has a Google Sheets integration) or to your database and watch prices move.

## Cost

- $0.20 per 1,000 flights on the free plan ($0.08–0.10 on paid plans)
- searches that return no flights are not charged
- a 7-day × 1-route check (~150 flights) costs about $0.03

## Notes

- `price` is the total for all passengers; for round trips it is the round-trip price shown with the outbound flight, as on Google Flights.
- No Google account or API key is needed.

That's it — a few lines of Python and you have a daily fare tracker. Questions or a missing field? Open an issue on the [Actor page](https://apify.com/rt-solutions/google-flights-scraper).

## License

MIT — the example code is free to use. The data comes from the [google-flights-scraper](https://apify.com/rt-solutions/google-flights-scraper) Actor (pay per result on Apify).
