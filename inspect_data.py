import json
import re

try:
    with open('debug_page_30.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if match:
        data = json.loads(match.group(1))
        # Traverse to find assets
        assets = data.get('props', {}).get('pageProps', {}).get('assets', [])
        if assets:
            first = assets[0]
            print("Keys:", list(first.keys()))
            
            # Look for specific url fields
            for key in ['url', 'src', 'thumbnail', 'preview', 'display_url', 'uri', 'thumb', 'huge_thumb']:
                if key in first:
                    print(f"{key}: {first[key]}")
            
            if 'urls' in first:
                print("urls object:", first['urls'])

        else:
            print("No assets found in JSON.")

except Exception as e:
    print(f"Error: {e}")
