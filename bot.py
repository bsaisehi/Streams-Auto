import requests
import json
import time
import base64

USER_AGENT = "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36"
SECRET_KEY = "ChaudharyPlayerPremiumKey_2026!@#"

# FIFA ke titles ko aapki player play-IDs se match karne ke liye mapping dictionary
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

def xor_encrypt_decrypt(input_str, key):
    output = []
    for i in range(len(input_str)):
        output.append(chr(ord(input_str[i]) ^ ord(key[i % len(key)])))
    return "".join(output)

def encode_to_custom_string(obj):
    # Compact JSON format generate karne ke liye separators use kiye hain
    json_str = json.dumps(obj, separators=(',', ':'))
    xor_str = xor_encrypt_decrypt(json_str, SECRET_KEY)
    
    # Python 3 compatibility handle karne ke liye bytes conversion
    binary_bytes = xor_str.encode('utf-8', errors='surrogateescape')
    base64_bytes = base64.b64encode(binary_bytes)
    return base64_bytes.decode('utf-8')

def fetch_all():
    # Saare data ko flat karke rakhne ke liye temporary master dictionary
    raw_master_list = {}
    
    # Base structure jisme metadata hooks pehle se predefined hain
    structured_master = {
        "success": "true",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total": "0"
    }
    
    total_channels_count = 0
    print("🔄 Automation started... Fetching live streams & processing flat IDs with 'f' prefix...\n")

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
                            items_added = 0
                            if isinstance(data, dict):
                                for channel_id, channel_data in data.items():
                                    raw_master_list[channel_id] = channel_data
                                    items_added += 1
                            elif isinstance(data, list):
                                for channel in data:
                                    c_id = channel.get("id") or channel.get("name", "").lower().replace(" ", "")
                                    raw_master_list[c_id] = channel
                                    items_added += 1
                            total_channels_count += items_added
                            print(f"  ✅ Flattened {items_added} normal channels from {source_name}")

                        # Case 2: FIFA Complex Events - Inke aage automatic 'f' prefix lagega aur root par aayenge
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
                                    raw_master_list[custom_id] = {
                                        "id": custom_id,
                                        "name": title,
                                        "Bearer": None,
                                        "url": stream.get("url"),
                                        "k1": drm_data.get("kid") if isinstance(drm_data, dict) else None,
                                        "k2": drm_data.get("key") if isinstance(drm_data, dict) else None
                                    }
                                    extracted_count += 1
                                    
                            total_channels_count += extracted_count
                            print(f"  ✅ Extracted & Flattened {extracted_count} FIFA streams with 'f' prefix!")

                        # Case 3: Individual IDs (cricfusion)
                        else:
                            raw_master_list[item] = data
                            total_channels_count += 1
                            print(f"  ✅ Flattened individual ID: {item}")

                    except json.JSONDecodeError:
                        print("  ⚠️ Error: Got non-JSON response from server.")
                else:
                    print(f"  ❌ Failed to fetch | Status Code: {res.status_code}")

            except Exception as e:
                print(f"  ⚠️ Connection Error: {e}")

            time.sleep(1.5)

        print("-" * 45)
        
    # Total count ko metadata ke andar feed karna
    structured_master["total"] = str(total_channels_count)
    
    # Final output taiyar karne ke liye loop jisme metadata normal rahega aur channels secure honge
    final_secure_response = {}
    
    # 1. Sabse pehle metadata parameters copy karo bina encrypt kiye
    for meta_key in ["success", "generated_at", "total"]:
        final_secure_response[meta_key] = structured_master[meta_key]
        
    # 2. Saare dynamic channel IDs ko individually XOR aur Base64 encrypt karke feed karo
    print("🔐 Encrypting payload IDs using ChaudharyPlayer Premium Key...")
    for channel_key, channel_val in raw_master_list.items():
        final_secure_response[channel_key] = encode_to_custom_string(channel_val)
        
    # Final production ready secure file output write-up
    with open("all_streams.json", "w") as f:
        json.dump(final_secure_response, f, indent=4)
        
    print(f"\n🎉 Process finished! Encrypted Flat JSON Sync with Backend Scheme inside 'all_streams.json'.")

if __name__ == "__main__":
    fetch_all()
