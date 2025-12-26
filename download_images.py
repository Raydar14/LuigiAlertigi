import os
import time
import re
import random
import json

try:
    import requests
except ImportError:
    print("Error: 'requests' module not found. Please run: pip install requests")
    exit(1)

image_urls = []
MAX_IMAGES = 2000
MAX_PAGES = 40
save_dir = "shutterstock_images"

# 1. Pre-scan existing images to avoid re-downloading or re-counting them
existing_ids = set()
if os.path.exists(save_dir):
    for f in os.listdir(save_dir):
        if f.endswith(".jpg"):
            # Extract ID from filename. Usually "....-440nw-[id].jpg" or just "[id].jpg"
            # We'll assume the ID is the sequence of digits/chars before the extension
            # or try to match known patterns.
            # Filename from URL logic was: url.split("/")[-1]
            match = re.search(r'[-_]([a-zA-Z0-9]+)\.jpg$', f)
            if match:
                existing_ids.add(match.group(1))
            else:
                # Fallback: use whole filename as ID equivalent
                existing_ids.add(f)

print(f"Index contains {len(existing_ids)} existing images.")

# Cookies and headers from browser session
cookie_string = "stck_anonymous_id=43557a08-8767-4900-8349-397b445335d4; sstk_anonymous_id=43557a08-8767-4900-8349-397b445335d4; visit_id=17660311027148526; visitor_id=17660311027148526; htjs_anonymous_id=43557a08-8767-4900-8349-397b445335d4; gtm_monitoring_roll=16; _ga=GA1.1.1993302843.1766031104; FPLC=owQpTN5zG0%2BGhM%2BDqLEop0PcmGCkF8TTvaGraoZ5UZGb%2FwqS7YAN3omaTaTw75IhsVVoJ6rO3U3sy0iMIeldfLosHNARdBuxGLkE5or7WxP%2FGJ6OC%2F%2FigVvMMJ874g%3D%3D; FPAU=1.2.380044759.1766031105; slireg=https://scout.us1.salesloft.com; __ssid=ce29824ef012dfb12675a097041407f; sliguid=64ad36a1-e93d-4276-9f49-7c35b42d11a7; slirequested=true; _fbp=fb.1.1766031104786.1472349564; OptanonAlertBoxClosed=2025-12-18T04:11:50.411Z; go_lihp=editorial; search-term-cookie=luigi%20mangione; usi_launched=11608538575932066604968; search-component-cookie=; sstk_session_start=2025-12-18T19%3A12%3A02.570Z; stck_session_id=a9ff0af8-9a31-4c75-aff9-8f6cbfdc4ca5; sstk_session_id=a9ff0af8-9a31-4c75-aff9-8f6cbfdc4ca5; n_v=7f11b1c2704; x-client-app=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXBsb3llZEF0IjoxNzY2MDg0NDMxMDAwLCJ2ZXJzaW9uIjoiN2YxMWIxYzI3MDQiLCJuYW1lIjoibmV4dC13ZWIiLCJpYXQiOjE3NjYwODQ3NTcsImV4cCI6MTc5NzYyMDc1N30.iWJEryLAHyhR8vGYY36kBQM-9HN9dfDVNIk-JONro0w; tracking_id=q8biMBVWmsG_uXTZ6fp9vg; footage_search_tracking_id=q8biMBVWmsG_uXTZ6fp9vg; downlink=low; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Dec+18+2025+13%3A38%3A06+GMT-0600+(Central+Standard+Time)&version=202403.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=a65e48eb-39f2-4a81-ad84-dc3c9b6a46db&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0005%3A1%2CC0004%3A1%2CC0007%3A1&intType=1&geolocation=CR%3BSJ&AwaitingReconsent=false; datadome=rh84~kJ1aD98NFitau1U5S16i1UC73gXuomF56a6UhtLE7Tzy1j6c4NVt1NBbpxLVhU33PfiLEyIM_EiCQL4iF2ZaDksCGBcu1R1wxmorRnXS34T7xwBPkwTWvYHoITE; _uetsid=aa4251b0dbc711f09596bf447aeef067|wxqu57|2|g1y|0|2178; _ga_VEW1GCS46P=GS2.1.s1766084900$o5$g1$t1766086688$j60$l0$h0; _uetvid=aa47f8c0dbc711f0aa8a17b1bede4422|146klvg|1766086689263|9|1|bat.bing.com/p/insights/c/l; _ga_SSGTMSSTK=GS2.1.s1766084900$o5$g1$t1766086689$j58$l0$h1333401599"

cookies = {}
for chunk in cookie_string.split(';'):
    if '=' in chunk:
        name, value = chunk.strip().split('=', 1)
        cookies[name] = value

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    # Additional headers found in typical browser requests to mimic real traffic
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

import re

print(f"Scraping up to {MAX_IMAGES} images from top {MAX_PAGES} pages...")

for page in range(1, MAX_PAGES + 1):
    if len(image_urls) >= MAX_IMAGES:
        break
        
    search_url = f"https://www.shutterstock.com/editorial/search/luigi-mangione?sort=-date&page={page}"
    print(f"Fetching page {page}: {search_url} ...")
    
    try:
        response = requests.get(search_url, headers=headers, cookies=cookies)
        page_links = []  # Initialize to empty list
        
        if response.status_code == 200:
            new_links = 0  # Initialize counter for this page
            
            # Method 1: Try parsing __NEXT_DATA__ (Reliable for Next.js)
            try:
                 json_match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', response.text)
                 if json_match:
                     data = json.loads(json_match.group(1))
                     assets = data.get('props', {}).get('pageProps', {}).get('assets', [])
                     print(f"  [JSON] Found {len(assets)} assets in metadata.")
                     
                     skipped_existing = 0
                     skipped_keywords = 0
                     
                     for asset in assets:
                         asset_id = asset.get('id')
                         title = asset.get('title', '')
                         
                         if asset_id:
                             # 1. Deduplication: Check against existing files
                             if str(asset_id) in existing_ids:
                                 skipped_existing += 1
                                 continue
                            
                             # 2. Filtering: Exclude fans/signs/tents/supporters based on Title
                             if re.search(r'\b(fan|fans|sign|signs|placard|tent|tents|supporter|supporters)\b', title, re.IGNORECASE):
                                 skipped_keywords += 1
                                 # print(f"  [DEBUG] Skipped title: {title}")
                                 continue

                             safe_title = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
                             if not safe_title:
                                 safe_title = "editorial-image"
                                 
                             # PRIORITIZE 'src' which is the direct image link
                             full_url = asset.get('src')
                             
                             if not full_url:
                                 # Fallback to page URL or manual construction (though these might be HTML pages)
                                 # We prefer NOT to download pages as images.
                                 # If we only have 'url' (page), we can't download the image easily without visiting it.
                                 # So we stick to 'src'.
                                 # Only fallback if standard pattern applies?
                                 pass
                             
                             # If still no full_url, maybe valid image is not available in metadata. switch to next.
                             if not full_url:
                                  continue

                             # 3. Filtering: Check URL for keywords (slugified)
                             if re.search(r'[-/](fan|fans|sign|signs|placard|tent|tents|supporter|supporters)[-/.]', full_url, re.IGNORECASE):
                                 skipped_keywords += 1
                                 continue

                             if full_url and full_url not in image_urls:
                                 image_urls.append(full_url)
                                 new_links += 1
                                 if len(image_urls) >= MAX_IMAGES:
                                     break
                     
                     print(f"  STATS p{page}: Assets={len(assets)} Exist={skipped_existing} Keys={skipped_keywords} New={new_links}")

            except Exception as e:
                print(f"  [JSON Error] {e}")

            # Improved regex as generic fallback
            if new_links == 0 and skipped_existing == 0 and skipped_keywords == 0:
                # Capture strictly editorial image links
                page_links = re.findall(r'href=["\']((?:https://www\.shutterstock\.com)?/editorial/image-editorial/[^"\'\?]+)', response.text)
                
                if not page_links:
                     page_links = re.findall(r'(/editorial/image-editorial/[a-zA-Z0-9-]+)', response.text)

                for link in page_links:
                    link = link.strip()
                    if link.startswith("https"):
                        full_url = link
                    else:
                        full_url = "https://www.shutterstock.com" + link if link.startswith("/") else "https://www.shutterstock.com/" + link
                    
                    # Deduplication check
                    try:
                        url_id = full_url.split("/")[-1].split("-")[-1]
                        if url_id in existing_ids:
                            continue
                    except:
                        pass
                    
                    # Filtering: Check URL for keywords (slugified)
                    if re.search(r'[-/](fan|fans|sign|signs|placard|tent|tents|supporter|supporters)[-/.]', full_url, re.IGNORECASE):
                        continue

                    if "/editorial/image-editorial/" in full_url:    
                        if full_url not in image_urls:
                            image_urls.append(full_url)
                            new_links += 1
                            if len(image_urls) >= MAX_IMAGES:
                                break
            
            print(f"  Found {new_links} NEW images on page {page}. Total queued: {len(image_urls)}")
            
            if new_links == 0 and len(image_urls) > 0:
                 print("  DEBUG: No new images found on this page.")

            # Random delay to avoid detection
            import random
            time.sleep(random.uniform(2, 5)) 
        else:
            print(f"  Failed to fetch page {page}: Status {response.status_code}")
            if response.status_code == 403:
                print("  403 Forbidden - Bot protection triggered. Stopping scrape.")
                break
    except Exception as e:
        print(f"  Error fetching page {page}: {e}")

if not image_urls:
    print("Warning: No images found. Your cookies might have expired or the site structure changed.")
    print("Try updating the 'cookie_string' variable with fresh cookies from your browser.")

save_dir = "shutterstock_images"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

print(f"Downloading {len(image_urls)} images...")

# Prepare headers for image downloads
img_headers = headers.copy()
img_headers["Accept"] = "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
img_headers["Sec-Fetch-Dest"] = "image"
img_headers["Sec-Fetch-Mode"] = "no-cors" # Images are often no-cors
img_headers["Referer"] = "https://www.shutterstock.com/"

for i, url in enumerate(image_urls):
    try:
        # Extract filename from URL or just use index
        filename = url.split("/")[-1]
        if not filename.endswith(".jpg"):
            filename = f"image_{i}.jpg"
        
        filepath = os.path.join(save_dir, filename)
        
        # Don't redownload if exists
        if os.path.exists(filepath):
             print(f"Skipping {filename}, already exists.")
             continue
             
        # Add random delay
        time.sleep(random.uniform(0.5, 1.5))
        
        response = requests.get(url, headers=img_headers, cookies=cookies, stream=True)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download {url}: Status {response.status_code}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

print("Download complete.")
