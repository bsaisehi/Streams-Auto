import requests
import json
import time

USER_AGENT = "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36"

# FIFA ke titles ko aapki player play-IDs se match karne ke liye mapping dictionary
# Inke aage hum script ke andar loop me auto 'f' prefix laga denge
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
        "base_url": "https://footballapi-delta.vercel.app/api/events?play=1",
        "items": [None],
        "type": "events_api",
        "headers": {
            "Origin": "https://fifa26-live.pages.dev",
            "User-Agent": USER_AGENT,
            "Accept": "*/*"
        }
    }
}

def fetch_all():
    master_list = {}
    print("🔄 Automation started... Generating Flat JSON Output with 'f' Prefix for FIFA...\n")

    for source_name, config in SOURCES.items():
        print(f"📡 Processing source: [{source_name.upper()}]")
        current_headers = config["headers"]

        for item in config["items"]:
            target_url = config["base_url"] if item is None else f"{config['base_url']}{item}"

            try:
                res = requests.get(target_url, headers=current_headers, timeout=10)

                if res.status_code == 200 and res.text.strip():
                    try:
                        data = res.json()

                        # Case 1: Bulk APIs (footapi_new) - Normal Root Level Flat IDs
                        if config["type"] == "bulk_ids":
                            if isinstance(data, dict):
                                for channel_id, channel_data in data.items():
                                    master_list[channel_id] = channel_data
                            elif isinstance(data, list):
                                for channel in data:
                                    c_id = channel.get("id") or channel.get("name", "").lower().replace(" ", "")
                                    master_list[c_id] = channel
                            print(f"  ✅ Flattened normal channels from {source_name}")

                        # Case 2: FIFA Complex Events - Inke aage automatic 'f' prefix lagega
                        elif config["type"] == "events_api":
                            events = data.get("events", []) if isinstance(data, dict) else []
                            extracted_count = 0
                            
                            for event in events:
                                for stream in event.get("streams", []):
                                    title = stream.get("title", "")
                                    
                                    # Agar map me title hai toh uske aage 'f' lagao, nahi toh dynamic title ke aage 'f' jod do
                                    if title in FIFA_TITLE_MAP:
                                        custom_id = f"f{FIFA_TITLE_MAP[title]}"
                                    else:
                                        clean_title = title.lower().replace(" ", "").replace("-", "")
                                        custom_id = f"f{clean_title}"
                                    
                                    drm_data = stream.get("drm") or {}
                                    master_list[custom_id] = {
                                        "id": custom_id,
                                        "name": title,
                                        "Bearer": None,
                                        "url": stream.get("url"),
                                        "k1": drm_data.get("kid") if isinstance(drm_data, dict) else None,
                                        "k2": drm_data.get("key") if isinstance(drm_data, dict) else None
                                    }
                                    extracted_count += 1
                            print(f"  ✅ Extracted & Flattened {extracted_count} FIFA streams with 'f' prefix!")

                        # Case 3: Individual IDs (cricfusion)
                        else:
                            master_list[item] = data
                            print(f"  ✅ Flattened individual ID: {item}")

                    except json.JSONDecodeError:
                        print("  ⚠️ Error: Got non-JSON response from server.")
                else:
                    print(f"  ❌ Failed to fetch | Status Code: {res.status_code}")

            except Exception as e:
                print(f"  ⚠️ Connection Error: {e}")

            time.sleep(1.5)

        print("-" * 40)
        
    # Final consolidated data dump
    with open("all_streams.json", "w") as f:
        json.dump(master_list, f, indent=4)
        
    print(f"\n🎉 Success! All items saved cleanly. FIFA channels are now safely prefixed with 'f'.")

if __name__ == "__main__":
    fetch_all()
