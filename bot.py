import requests
import json
import time

USER_AGENT = "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36"

# FIFA title -> custom ID mapping
FIFA_TITLE_MAP = {
    "FOX SPORTS ENG": "foxusa",
    "NTV ENGLISH - AQ": "ntv",
    "D SPORTS - AQ [ES]": "dsports",
    "TELEMUNDO - AQ": "telemundo",
    "TELEMUNDO SPANISH": "telemundo2",
    "M6 FRANCE - AQ [No delay]": "m6",
    "FOX SPORTS FHD": "foxusafhd",
    "FOX SPORTS 4k": "foxusa4k",
    "NOW SPORTS 4K": "nowsports4k",
    "TIPIK FR - AQ": "tipikfr",
    "CT SPORTS - AQ": "ctsports",
    "CTV SPORTS - AQ": "ctvsports",
    "Match Football": "matchfootball",
    "TVP POLISH FHD": "tvppolish",
    "ORF GERMAN HD": "orfgerman",
    "SPORZA SPORTS": "sporzasports",
    "CAZE TV - AQ [BR]": "cazetvprime",
    "SPORTV BR - AQ": "sportvbr",
    "ZDF GERMAN HD": "zdfgerman",
    "PEACOCK TV": "peacocktv",
    "UNITE8 ENG - IN": "unite8sports1hd",
    "UNITE8 HINDI - IN": "unite8sports2hd"
}

SOURCES = {
    "cricfusion": {
        "base_url": "https://newwwwapiiiiii.vercel.app/main?id=",
        "items": ["cazeamzn", "h", "u", "fs1"],
        "type": "individual_id",
        "headers": {
            "Referer": "https://newwwwapiiiiii.vercel.app",
            "Origin": "https://cricboost.pages.dev",
            "User-Agent": USER_AGENT
        }
    },

    "footapi_new": {
        "base_url": "https://footapi-psi.vercel.app/main",
        "items": [None],
        "type": "bulk_ids",
        "headers": {
            "Referer": "https://footapi-psi.vercel.app/",
            "Origin": "https://footsterss.pages.dev",
            "User-Agent": USER_AGENT
        }
    },

    "fifa26": {
        "base_url": "https://footballapi-delta.vercel.app/api/events?play=3",
        "items": [None],
        "type": "events_api",
        "headers": {
            "Origin": "https://fifa26-live.pages.dev",
            "User-Agent": USER_AGENT,
            "Accept": "*/*"
        }
    }
}

SECTION_MAP = {
    "cricfusion": "cric",
    "footapi_new": "foot",
    "fifa26": "fifa"
}


def fetch_all():
    master_list = {
        "cric": {},
        "foot": {},
        "fifa": {}
    }

    print("🔄 Automation Started...\n")

    for source_name, config in SOURCES.items():
        section = SECTION_MAP[source_name]

        print(f"📡 Processing [{section.upper()}]")

        for item in config["items"]:
            target_url = (
                config["base_url"]
                if item is None
                else f"{config['base_url']}{item}"
            )

            try:
                response = requests.get(
                    target_url,
                    headers=config["headers"],
                    timeout=15
                )

                if response.status_code != 200:
                    print(
                        f"  ❌ Failed ({response.status_code})"
                    )
                    continue

                data = response.json()

                # -------------------------------------------------
                # FOOT API (Bulk Channels)
                # -------------------------------------------------
                if config["type"] == "bulk_ids":

                    if isinstance(data, dict):
                        for channel_id, channel_data in data.items():
                            master_list[section][channel_id] = channel_data

                    elif isinstance(data, list):
                        for channel in data:
                            channel_id = (
                                channel.get("id")
                                or channel.get("name", "")
                                .lower()
                                .replace(" ", "")
                            )

                            master_list[section][channel_id] = channel

                    print(
                        f"  ✅ Added {len(master_list[section])} channels"
                    )

                # -------------------------------------------------
                # FIFA EVENTS API
                # -------------------------------------------------
                elif config["type"] == "events_api":

                    events = (
                        data.get("events", [])
                        if isinstance(data, dict)
                        else []
                    )

                    count = 0

                    for event in events:
                        for stream in event.get("streams", []):

                            title = stream.get("title", "").strip()

                            if not title:
                                continue

                            if title in FIFA_TITLE_MAP:
                                custom_id = FIFA_TITLE_MAP[title]
                            else:
                                custom_id = (
                                    title.lower()
                                    .replace(" ", "")
                                    .replace("-", "")
                                    .replace("[", "")
                                    .replace("]", "")
                                )

                            drm_data = stream.get("drm") or {}

                            master_list[section][custom_id] = {
                                "id": custom_id,
                                "name": title,
                                "Bearer": None,
                                "url": stream.get("url"),
                                "k1": drm_data.get("kid")
                                if isinstance(drm_data, dict)
                                else None,
                                "k2": drm_data.get("key")
                                if isinstance(drm_data, dict)
                                else None
                            }

                            count += 1

                    print(
                        f"  ✅ Added {count} FIFA streams"
                    )

                # -------------------------------------------------
                # CRIC Individual IDs
                # -------------------------------------------------
                else:

                    master_list[section][item] = data

                    print(
                        f"  ✅ Added channel: {item}"
                    )

            except Exception as e:
                print(f"  ⚠️ Error: {e}")

            time.sleep(1.5)

        print("-" * 50)

    with open("all_streams.json", "w", encoding="utf-8") as f:
        json.dump(
            master_list,
            f,
            indent=4,
            ensure_ascii=False
        )

    total_channels = (
        len(master_list["cric"])
        + len(master_list["foot"])
        + len(master_list["fifa"])
    )

    print("\n🎉 Done!")
    print(f"📦 Total Channels: {total_channels}")
    print("💾 Saved as: all_streams.json")


if __name__ == "__main__":
    fetch_all()
