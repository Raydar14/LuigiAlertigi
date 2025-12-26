import os
import re
from collections import Counter

directory = "shutterstock_images"

if not os.path.exists(directory):
    print("Directory not found.")
    exit()

files = [f for f in os.listdir(directory) if f.endswith(".jpg")]
total_images = len(files)

shoots = []

for f in files:
    # Regex to strip the ID and size suffix
    # Looking for pattern: -[digits]nw-[digits][char]?.jpg OR -[digits][char]?.jpg
    # Example: ...-defense-440nw-16064503a.jpg
    # We want "...-defense"
    
    # Strategy: split by last occurrence of pattern or just use simple string manipulation
    # Most seem to have "-440nw-" or "-220nw-"
    
    parts = f.split("-440nw-")
    if len(parts) > 1:
        shoot_name = parts[0]
    else:
        parts = f.split("-220nw-")
        if len(parts) > 1:
            shoot_name = parts[0]
        else:
            # Fallback if no size marker, just strip last dash-part
            # But wait, looking at file list: 
            # september-16-2025---new-york-ny-440nw-15489084d.jpg
            # luigi-mangione-pleaded-not-guilty-federal-court-440nw-15270743a.jpg
            shoot_name = f.rsplit('-', 1)[0] # Very rough fallback
            
    shoots.append(shoot_name)

print(f"Debug: First 5 extracted names: {shoots[:5]}")


shoot_counts = Counter(shoots)

output = []
output.append(f"Total Photos: {total_images}")
output.append(f"Total Unique Shoots/Events: {len(shoot_counts)}")
output.append("-" * 30)
output.append("Top 20 Shoots:")
for shoot, count in shoot_counts.most_common(20):
    output.append(f"{count:3d} : {shoot}")
output.append("-" * 30)

with open("report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print("Report saved to report.txt")
