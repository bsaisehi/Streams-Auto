import os
import glob
import time
import json
import re
import requests

USER_AGENT = "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36"

# 🟢 CONFIGURATION BLOCK FOR ALL 3 APIs
SOURCES = {
    "cricfusion": {
        "base_url": "https://newwwwapiiiiii.vercel.app/main?id=",
        # Aapke poorane aur naye IDs ka collection
        "items": ["cazeamzn", "h", "u", "fs1"],
        "type": "individual_id",
        "headers": {
            "Referer": "https://newwwwapiiiiii.vercel.app",
            "Origin": "https://cricboost.pages.dev",
            "User-Agent": USER_AGENT
        }
    },
    "footapi_new": {
        "base_url": "https://footapi-psi.vercel.app/main?id=",
        # Naye targets jo aapne bataye
        "items": ["cazeios", "unite8sports1hd", "unite8sports2hd"],
        "type": "individual_id",
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


def save_rolling_json(master_list):
    """JSON file ka naam badalne aur purani file ko mitaane ka unique protection logic"""
    print("\n🛡️ Securing Output: Rolling File Protection Active...")
    
    # 1. Current timestamp ke sath unique filename banana
    timestamp = int(time.time())
    new_filename = f"streams_{timestamp}.json"
    
    # 2. Nayi dynamic file mein updated data dump karna
    with open(new_filename, "w") as f:
        json.dump(master_list, f, indent=4)
    print(f"💾 Nayi live stream file saved: {new_filename}")
    
    # 3. Master 'manifest.json' file banana jo player ko dynamic file ka naam batayega
    manifest_data = {
        "live_file": new_filename,
        "updated_at": timestamp
    }
    with open("manifest.json", "w") as f:
        json.dump(manifest_data, f, indent=4)
    print("📋 Master manifest.json updated successfully!")
        
    # 4. Storage clean up: Purani saari streams_*.json files ko auto-delete karna
    all_json_files = glob.glob("streams_*.json")
    for file_path in all_json_files:
        if file_path != new_filename:
            try:
                os.remove(file_path)
                print(f"🗑️ Expired historical file deleted: {file_path}")
            except Exception as e:
                print(f"⚠️ Clean-up failure: {e}")

def fetch_all():
    master_list = {}
    print("🔄 Automation started... Fetching live streams data from 3 APIs...\n")
    
    for source_name, config in SOURCES.items():
        print(f"📡 Processing source: [{source_name.upper()}]")
        current_headers = config["headers"]
        
        for item in config["items"]:
            # Cache buster to permanently bypass "304 Not Modified" filters on target servers
            cache_buster = f"&_ts={int(time.time() * 1000)}"
            
            if item is None:
                target_url = f"{config['base_url']}{cache_buster}"
            else:
                # Agar base_url me already ? hai to use evaluate karo nahi to append karo
                sep = "&" if "?" in config['base_url'] else "?"
                target_url = f"{config['base_url']}{item}{sep}_ts={int(time.time() * 1000)}"
            
            try:
                res = requests.get(target_url, headers=current_headers, timeout=10)
                if res.status_code in [200, 304] and res.text.strip():
                    try:
                        data = res.json()
                        if config["type"] == "bulk_api":
                            master_list[source_name] = data
                            print(f"  ✅ Successfully fetched ALL bulk streams for {source_name}!")
                        else:
                            master_list[item] = data
                            print(f"  ✅ Successfully fetched ID: {item}")
                    except json.JSONDecodeError:
                        print(f"  ⚠️ Error: Got non-JSON response from {source_name} for item {item}.")
                else:
                    print(f"  ❌ Failed to fetch {source_name} | Status Code: {res.status_code}")
            except Exception as e:
                print(f"  ⚠️ Connection Error on {source_name}: {e}")
                
            time.sleep(1.5) # Modest sleep interval to protect api rate limit drops
        print("-" * 40)
        
    # CricXFootball JS data merge execution
    cricx_data = fetch_cricx_js()
    if cricx_data:
        master_list["cricxfootball_tokens"] = cricx_data
    print("-" * 40)
        
    # Rolling Module execution
    save_rolling_json(master_list)
    print("\n🎉 ALL DONE: Master data updated for all 3 engines smoothly!")

if __name__ == "__main__":
    fetch_all()
