import requests
import json
import time

# Configurations
USER_AGENT = "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36"
EVENTS_LIST_URL = "https://footballapi-delta.vercel.app/api/events"
STREAMS_BASE_URL = "https://footballapi-delta.vercel.app/api/events?play=" 

HEADERS = {
    "Origin": "https://fifa26-live.pages.dev",
    "User-Agent": USER_AGENT,
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8"
}

def fetch_all_events_and_streams():
    optimized_master = {}
    print("🔄 Automation started... Fetching overall events list...\n")

    try:
        # Step 1: Sabhi active events ki list fetch karein
        res = requests.get(EVENTS_LIST_URL, headers=HEADERS, timeout=12)
        if res.status_code != 200 or not res.text.strip():
            print(f"❌ Failed to fetch events list. Status Code: {res.status_code}")
            return

        list_data = res.json()
        if not list_data.get("success") or "events" not in list_data:
            print("❌ Invalid response format from Events List API.")
            return

        events = list_data["events"]
        total_events = len(events)
        print(f"📡 Total {total_events} events found. Starting stream details extraction...\n")

        # Step 2: Loop chala kar HAR ek Event ID ke data ko fetch karna
        for index, event in enumerate(events, 1):
            event_id = str(event.get("event_id"))
            event_title = event.get("event_title")
            category = event.get("category")
            event_time = event.get("event_time")

            print(f"[{index}/{total_events}] 🔄 Fetching channels for Event ID {event_id}: {event_title}")

            # Dynamic URL Generation (Jaise ?play=1, ?play=3)
            target_detail_url = f"{STREAMS_BASE_URL}{event_id}" 
            
            # Base structure initialize kar rahe hain
            optimized_master[event_id] = {
                "title": event_title,
                "time": event_time,
                "category": category,
                "streams": []
            }

            try:
                # Detail API request
                detail_res = requests.get(target_detail_url, headers=HEADERS, timeout=10)
                
                if detail_res.status_code == 200 and detail_res.text.strip():
                    detail_data = detail_res.json()
                    
                    if detail_data.get("success") and "events" in detail_data:
                        for ev_detail in detail_data["events"]:
                            # Confirm kar rahe hain ki sahi event ka response parse ho raha hai
                            if str(ev_detail.get("event_id")) == event_id:
                                raw_streams = ev_detail.get("streams", [])
                                
                                # Loop chala kar channels ko structured numeric IDs ("1", "2"...) dena
                                for ch_index, stream in enumerate(raw_streams, 1):
                                    optimized_master[event_id]["streams"].append({
                                        "channel_id": str(ch_index),  # Pure string numbers ("1", "2", "3")
                                        "title": stream.get("title"),
                                        "url": stream.get("url"),
                                        "drm": stream.get("drm", {})
                                    })
                                
                print(f"  ✅ Loaded {len(optimized_master[event_id]['streams'])} channels successfully.")
            
            except Exception as e:
                print(f"  ⚠️ Error fetching streams for event {event_id}: {e}")

            # Safe Side Delay: Server block ya rate limit se bachne ke liye 1 second ka gap
            time.sleep(1)

        # Step 3: Pure merged data ko compressed/optimized single JSON file me save karna
        # separators=(',', ':') use karne se JSON ka size ekdum chota ho jata hai (Low-Network Friendly)
        with open("all_streams.json", "w", encoding="utf-8") as f:
            json.dump(optimized_master, f, separators=(',', ':'))

        print(f"\n🎉 Process Finished! All {total_events} events perfectly merged into 'live_data.json'.")

    except Exception as main_err:
        print(f"❌ Main automation process failed: {main_err}")

if __name__ == "__main__":
    fetch_all_events_and_streams()
