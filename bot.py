import requests
import json
import time
import base64

USER_AGENT = "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36"
SECRET_KEY = "ChaudharyPlayerPremiumKey_2026!@#"

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
        "type": "bulk_api",
        "headers": {
            "Referer": "https://footapi-psi.vercel.app/",
            "Origin": "https://footsterss.pages.dev",
            "User-Agent": USER_AGENT
        }
    },
    "fifa26": {
        "base_url": "https://footballapi-delta.vercel.app/api/events?play=1",
        "items": [None],
        "type": "bulk_api",
        "headers": {
            "Origin": "https://fifa26-live.pages.dev",
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
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
    # Sahi backend layout structure initialize kiya hai
    structured_master = {
        "footapi_new": [],
        "events": [],
        "success": "true",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total": "0"
    }
    
    total_channels_count = 0
    print("🔄 Automation started... Fetching live streams data according to new structure...\n")

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

                        # 1. Footapi New processing
                        if source_name == "footapi_new":
                            if isinstance(data, list):
                                structured_master["footapi_new"] = data
                                total_channels_count += len(data)
                            elif isinstance(data, dict):
                                # Agar map format me hai toh usko flat list bana denge backend compatibility ke liye
                                channel_list = list(data.values()) if not data.get("id") else [data]
                                structured_master["footapi_new"] = channel_list
                                total_channels_count += len(channel_list)
                            print(f"  ✅ Loaded {len(structured_master['footapi_new'])} channels into [footapi_new]")

                        # 2. Fifa26 Events processing
                        elif source_name == "fifa26":
                            # Response chahe object ho ya array, isko direct events list me bhejenge
                            if isinstance(data, list):
                                structured_master["events"] = data
                                total_channels_count += len(data)
                            elif isinstance(data, dict):
                                # Agar root dict me koi specific key array hai toh use extract karenge, nahi toh direct wrapper array me wrap karenge
                                events_data = data.get("events", data)
                                structured_master["events"] = events_data if isinstance(events_data, list) else [events_data]
                                total_channels_count += 1
                            print(f"  ✅ Loaded events data successfully into [events]")

                        # 3. Cricfusion Individual IDs processing (Root level par save honge)
                        else:
                            structured_master[item] = data
                            total_channels_count += 1
                            print(f"  ✅ Successfully loaded Root ID: {item}")

                    except json.JSONDecodeError:
                        print("  ⚠️ Error: Got non-JSON response from server.")
                else:
                    print(f"  ❌ Failed to fetch | Status Code: {res.status_code}")

            except Exception as e:
                print(f"  ⚠️ Connection Error: {e}")

            time.sleep(1.5)

        print("-" * 45)
        
    # Total channels metric update karenge
    structured_master["total"] = str(total_channels_count)
        
    # Ab final JSON ko encrypt karenge naye backend algorithm ke hisab se
    final_secure_response = {}
    
    for key, val in structured_master.items():
        # Jo metadata keys pehle se fixed strings hain unhe bina encryption ke bhejenge (ya as-is copy karenge)
        if key in ["success", "generated_at", "total"]:
            final_secure_response[key] = val
        else:
            # Baaki saare arrays aur heavy channels data individual encrypt hokar base64 banenge
            final_secure_response[key] = encode_to_custom_string(val)
        
    # Final production ready file dumping
    with open("all_streams.json", "w") as f:
        json.dump(final_secure_response, f, indent=4)
        
    print(f"\n🎉 Process finished! GitHub payload is fully sync with Backend Vercel Scheme inside 'all_streams.json'.")

if __name__ == "__main__":
    fetch_all()
