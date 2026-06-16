import requests
import json
import time
import base64

USER_AGENT = "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36"
SECRET_KEY = "ChaudharyPlayerPremiumKey_2026!@#"

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

def xor_encrypt_decrypt(input_str, key):
    output = []
    for i in range(len(input_str)):
        output.append(chr(ord(input_str[i]) ^ ord(key[i % len(key)])))
    return "".join(output)

def encode_to_custom_string(obj):
    json_str = json.dumps(obj, separators=(',', ':'))
    xor_str = xor_encrypt_decrypt(json_str, SECRET_KEY)
    binary_bytes = xor_str.encode('utf-8', errors='surrogateescape')
    base64_bytes = base64.b64encode(binary_bytes)
    return base64_bytes.decode('utf-8')

def fetch_all():
    master_list = {}
    print("🔄 Automation started... Fetching live streams data...\n")
    
    for source_name, config in SOURCES.items():
        print(f"📡 Processing source: [{source_name.upper()}]")
        current_headers = config["headers"]
        
        for item in config["items"]:
            # URL banana (bulk api ke liye item None hoga isliye direct url use hoga)
            target_url = config["base_url"] if item is None else f"{config['base_url']}{item}"
            
            try:
                res = requests.get(target_url, headers=current_headers, timeout=10)
                
                if res.status_code == 200 and res.text.strip():
                    try:
                        data = res.json()
                        
                        # Agar bulk list dene wali API hai (jaise FIFA26)
                        if config["type"] == "bulk_api":
                            master_list[source_name] = data
                            print(f"  ✅ Successfully fetched ALL streams at once for {source_name}!")
                        
                        # Agar ek ek karke ID fetch karne wali API hai (jaise Cricfusion)
                        else:
                            master_list[item] = data
                            print(f"  ✅ Successfully fetched ID: {item}")
                            
                    except json.JSONDecodeError:
                        print(f"  ⚠️ Error: Got non-JSON response from server.")
                else:
                    print(f"  ❌ Failed to fetch | Status Code: {res.status_code}")
                    
            except Exception as e:
                print(f"  ⚠️ Connection Error: {e}")
                
            # Rate limit se bachne ke liye chhota sa pause
            time.sleep(1.5)
            
        print("-" * 40)
        
    final_secure_response = {}
    for key, val in master_list.items():
        final_secure_response[key] = encode_to_custom_string(val)
        
    with open("all_streams.json", "w") as f:
        json.dump(final_secure_response, f, indent=4)
        
    print(f"\n🎉 Process finished! Data successfully encrypted and saved in 'all_streams.json'.")

if __name__ == "__main__":
    fetch_all()
