import json
import re

try:
    with open('debug_page_2.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if match:
        print("MATCH FOUND")
        data = json.loads(match.group(1))
        
        # Traverse to find assets
        # Common paths: props.pageProps.assets
        assets = data.get('props', {}).get('pageProps', {}).get('assets', [])
        print(f"Direct assets found: {len(assets)}")
        
        if not assets:
            print("Digging deeper...")
            # Dump keys to debug
            print(data.get('props', {}).get('pageProps', {}).keys())

    else:
        print("NO NEXT DATA FOUND")
        
except Exception as e:
    print(f"Error: {e}")
