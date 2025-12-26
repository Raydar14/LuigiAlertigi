import os
import re
from collections import defaultdict

image_dir = "shutterstock_images"
output_file = "index.html"

# Get list of images
images = [f for f in os.listdir(image_dir) if f.endswith(".jpg")]

# Data structure: { "Shoot Name": { "max_id": int, "images": [list of files] } }
groups = defaultdict(lambda: {"max_id": 0, "images": []})

for img in images:
    # Extract ID (numeric part at end)
    # Pattern: ...-440nw-16064503a.jpg -> ID 16064503
    # Pattern: ...-440nw-16064503.jpg
    # Pattern: image_12.jpg -> No ID, handle separately or put at bottom?
    
    match_id = re.search(r'[-_](\d+)[a-z]?\.jpg$', img)
    
    if match_id:
        img_id = int(match_id.group(1))
        
        # Extract Shoot Name
        # Split by -440nw- or -220nw- or just take everything before the ID
        # ...-defense-440nw-...
        if "-440nw-" in img:
            shoot_name = img.split("-440nw-")[0]
        elif "-220nw-" in img:
            shoot_name = img.split("-220nw-")[0]
        else:
            # Fallback regex split
            shoot_name = re.sub(r'[-_]\d+[a-z]?\.jpg$', '', img)
            
        # Clean shoot name
        shoot_name = shoot_name.replace("-", " ").title()
        
    else:
        # Fallback for "image_X.jpg" or others
        img_id = 0
        shoot_name = "Unsorted / Other"
        
    group = groups[shoot_name]
    group["images"].append(img)
    if img_id > group["max_id"]:
        group["max_id"] = img_id

# Sort groups by max_id descending (Newest First)
sorted_groups = sorted(groups.items(), key=lambda x: x[1]["max_id"], reverse=True)

count = len(images)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Luigi Mangione Timeline</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script>
    <style>
        :root {{
            --bg-color: #001f17; 
            --card-bg: #033024;  
            --accent: #00ff9d;   
            --text-main: #e8f7f2;
            --text-secondary: #8ab0a2;
        }}
        
        body {{
            margin: 0;
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            background-image: radial-gradient(circle at 10% 20%, #003628 0%, transparent 20%),
                              radial-gradient(circle at 90% 80%, #00291f 0%, transparent 20%);
            color: var(--text-main);
            overflow-x: hidden;
            padding-bottom: 100px; /* Space for action bar */
        }}

        header {{
            padding: 40px 20px;
            text-align: center;
            background: linear-gradient(to bottom, #002b21, var(--bg-color));
            border-bottom: 1px solid #004d40;
        }}

        h1 {{
            font-size: 2.5rem;
            margin: 0;
            background: linear-gradient(to right, #ffffff, #00ff9d);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(0, 255, 157, 0.3);
        }}
        
        .timeline {{
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}

        .event-section {{
            margin-bottom: 60px;
            position: relative;
        }}
        
        .event-title {{
            font-size: 1.5rem;
            margin-bottom: 20px;
            padding-left: 20px;
            border-left: 4px solid var(--accent);
            color: var(--text-main);
            text-transform: capitalize;
            text-shadow: 0 0 10px rgba(0, 255, 157, 0.2);
        }}

        /* Horizontal Swipe Container */
        .carousel {{
            display: flex;
            gap: 20px;
            overflow-x: auto;
            padding: 10px 20px 40px 20px; 
            scroll-snap-type: x mandatory;
            scrollbar-width: none; 
            -ms-overflow-style: none;
        }}
        
        .carousel::-webkit-scrollbar {{
            display: none;
        }}

        .card {{
            flex: 0 0 auto;
            width: 300px;
            scroll-snap-align: start;
            background: var(--card-bg);
            border: 1px solid #004d40;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 10px 25px -5px rgba(0, 20, 15, 0.5);
            transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
            position: relative;
            cursor: pointer;
        }}
        
        .card:hover {{
            transform: scale(1.02) translateY(-5px);
            box-shadow: 0 20px 30px -10px rgba(0, 255, 157, 0.15);
            border-color: var(--accent);
            z-index: 10;
        }}
        
        .card.selected {{
            border: 2px solid var(--accent);
            box-shadow: 0 0 15px var(--accent);
        }}

        .card img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            display: block;
            pointer-events: none; /* Let click pass to card */
        }}
        
        /* Overlays */
        .select-overlay {{
            position: absolute;
            top: 10px;
            left: 10px;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: 2px solid rgba(255,255,255,0.7);
            background: rgba(0,0,0,0.4);
            transition: all 0.2s;
            z-index: 20;
            cursor: pointer;
        }}
        
        .select-overlay:hover {{
            background: rgba(255,255,255,0.2);
            border-color: #fff;
        }}

        .card.selected .select-overlay {{
            background: var(--accent);
            border-color: var(--accent);
            box-shadow: 0 0 8px var(--accent);
             /* Add checkmark svg maybe? */
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23000' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='20 6 9 17 4 12'%3E%3C/polyline%3E%3C/svg%3E");
            background-size: 16px;
            background-position: center;
            background-repeat: no-repeat;
        }}
        
        .card-actions {{
            position: absolute;
            bottom: 10px;
            right: 10px;
            display: flex;
            gap: 8px;
            z-index: 30;
        }}

        .action-icon-btn {{
            background: rgba(0,0,0,0.6);
            color: #fff;
            border: none;
            border-radius: 50%;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 1.2rem;
        }}
        
        .action-icon-btn:hover {{
            background: var(--accent);
            color: #000;
            transform: scale(1.1);
        }}

        /* Meme Editor CSS */
        #meme-editor {{
            display: none;
            position: fixed;
            z-index: 2500;
            left: 0; top: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.9);
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        #meme-editor.active {{ display: flex; }}
        
        .editor-container {{
            background: var(--card-bg);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--accent);
            text-align: center;
            max-width: 90%;
        }}
        
        canvas {{
            max-width: 100%;
            max-height: 60vh;
            border: 1px solid #333;
            margin-bottom: 20px;
        }}
        
        .meme-controls {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        
        .meme-controls input {{
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #555;
            background: #001f17;
            color: #fff;
            font-family: 'Impact', 'Outfit', sans-serif;
            text-transform: uppercase;
        }}
        
        .meme-buttons {{ display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }}
        
        .open-link {{
             position: absolute;
             top: 0; left: 0; width: 100%; height: 100%;
             z-index: 5; /* Below overlays */
        }}

        .card-dummy {{
             flex: 0 0 1px;
        }}
        
        .hint-scroll {{
            text-align: right;
            font-size: 0.8rem;
            color: var(--text-secondary);
            margin-top: -10px;
            padding-right: 20px;
            opacity: 0.6;
        }}
        
        /* Action Bar */
        #action-bar {{
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%) translateY(150px);
            background: rgba(3, 48, 36, 0.95);
            backdrop-filter: blur(10px);
            padding: 15px 30px;
            border-radius: 50px;
            border: 1px solid var(--accent);
            display: flex;
            gap: 20px;
            align-items: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            z-index: 1000;
        }}
        
        #action-bar.visible {{
            transform: translateX(-50%) translateY(0);
        }}
        
        .action-btn {{
            background: transparent;
            border: 1px solid var(--accent);
            color: var(--accent);
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-family: inherit;
            font-weight: 500;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.8rem;
        }}
        
        .action-btn:hover {{
            background: var(--accent);
            color: #001f17;
        }}
        
        .action-btn.primary {{
            background: var(--accent);
            color: #001f17;
        }}
        
        .selection-count {{
            color: #fff;
            margin-right: 10px;
            font-weight: bold;
        }}

        /* LIGHTBOX STYLES */
        #lightbox {{
            display: none;
            position: fixed;
            z-index: 2000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: rgba(0,0,0,0.95);
            backdrop-filter: blur(5px);
        }}
        
        #lightbox.active {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}

        .lb-content {{
            max-width: 90%;
            max-height: 85vh;
            border-radius: 4px;
            box-shadow: 0 0 50px rgba(0,255,157,0.1);
            user-select: none;
        }}

        .lb-close {{
            position: absolute;
            top: 20px;
            right: 30px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
            z-index: 2001;
            transition: 0.3s;
        }}
        
        .lb-close:hover {{ color: var(--accent); }}

        .lb-nav {{
            cursor: pointer;
            position: absolute;
            top: 50%;
            width: auto;
            padding: 16px;
            margin-top: -50px;
            color: white;
            font-weight: bold;
            font-size: 40px;
            transition: 0.3s ease;
            border-radius: 0 3px 3px 0;
            user-select: none;
            z-index: 2001;
        }}
        
        .lb-next {{ right: 0; border-radius: 3px 0 0 3px; }}
        .lb-prev {{ left: 0; border-radius: 0 3px 3px 0; }}
        .lb-nav:hover {{ background-color: rgba(0,255,157,0.2); color: var(--accent); }}

        #lb-caption {{
            position: absolute;
            bottom: 20px;
            color: #ccc;
            text-align: center;
            width: 100%;
            font-size: 0.9rem;
        }}

    </style>
</head>
<body>

    <header>
        <h1>Luigi's Timeline</h1>
        <p style="color: var(--text-secondary); margin-top: 10px;">{count} Moments Captured</p>
    </header>

    <div class="timeline">
"""

global_index = 0
for shoot_name, data in sorted_groups:
    images_list = data["images"]
    if not images_list:
        continue
        
    html_content += f"""
        <div class="event-section">
            <div class="event-title">{shoot_name}</div>
            <div class="carousel">
    """
    
    for img in images_list:
        full_path = f"{image_dir}/{img}"
        
        # Click on CARD opens Lightbox (passing global_index)
        # Click on OVERLAY toggles selection
        
        html_content += f"""
                <div class="card" onclick="openLightbox({global_index})">
                    <div class="select-overlay" onclick="event.stopPropagation(); toggleSelection('{img}', this.parentElement)"></div>
                    
                    <div class="card-actions">
                        <button class="action-icon-btn meme-btn" onclick="event.stopPropagation(); openMemeEditor('{full_path}')" title="Meme Maker">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19l7-7 3 3-7 7-3-3z"></path><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"></path><path d="M2 2l7.586 7.586"></path><circle cx="11" cy="11" r="2"></circle></svg>
                        </button>
                        <button class="action-icon-btn share-btn" onclick="event.stopPropagation(); shareSingle('{full_path}', '{img}')" title="Share">
                             <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>
                        </button>
                        <button class="action-icon-btn download-btn" onclick="event.stopPropagation(); downloadSingle('{full_path}', '{img}')" title="Download">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                        </button>
                    </div>

                    <img src="{full_path}" loading="lazy" alt="Photo" id="img-{global_index}" data-info="{shoot_name}">
                </div>
        """
        global_index += 1
        
    html_content += """
                <div class="card-dummy"></div>
            </div>
            <div class="hint-scroll">Swipe for more &rarr;</div>
        </div>
    """

html_content += f"""
    </div>
    
    <div id="action-bar">
        <span class="selection-count"><span id="count-display">0</span> Selected</span>
        <button class="action-btn primary" onclick="downloadZip()">Download ZIP</button>
        <button class="action-btn" onclick="emailList()">Email List</button>
        <button class="action-btn" onclick="shareSelection()">Share</button>
        <button class="action-btn" onclick="clearSelection()" style="border-color: #ff6b6b; color: #ff6b6b;">Clear</button>
    </div>

    <!-- Meme Editor Modal -->
    <div id="meme-editor">
        <div class="editor-container">
            <canvas id="meme-canvas"></canvas>
                <div class="meme-controls">
                <input type="text" id="top-text" placeholder="TOP TEXT" oninput="drawMeme()">
                <input type="text" id="middle-text" placeholder="MIDDLE TEXT" oninput="drawMeme()">
                <input type="text" id="bottom-text" placeholder="BOTTOM TEXT" oninput="drawMeme()">
                <div class="meme-buttons">
                     <button class="action-btn" onclick="luigiLogic()">Luigi Logic 🎲</button>
                     <button class="action-btn primary" onclick="downloadMeme()">Download Meme</button>
                     <button class="action-btn" onclick="shareMeme()">Share</button>
                     <button class="action-btn" onclick="closeMemeEditor()" style="border-color: #ff6b6b; color: #ff6b6b;">Close</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Lightbox Modal -->
    <div id="lightbox">
        <span class="lb-close" onclick="closeLightbox()">&times;</span>
        <a class="lb-nav lb-prev" onclick="changeSlide(-1)">&#10094;</a>
        <a class="lb-nav lb-next" onclick="changeSlide(1)">&#10095;</a>
        <img class="lb-content" id="lb-img">
        <div id="lb-caption"></div>
    </div>
    
    <footer style="text-align: center; padding: 50px; color: #555;">
        End of Timeline
    </footer>

    <script>
        // --- Selection Logic ---
        let selectedImages = new Set();
        const imageDir = "shutterstock_images/";

        function toggleSelection(filename, card) {{
            if (selectedImages.has(filename)) {{
                selectedImages.delete(filename);
                card.classList.remove('selected');
            }} else {{
                selectedImages.add(filename);
                card.classList.add('selected');
            }}
            updateActionBar();
        }}
        
        function clearSelection() {{
            selectedImages.clear();
            document.querySelectorAll('.card.selected').forEach(c => c.classList.remove('selected'));
            updateActionBar();
        }}

        function updateActionBar() {{
            const bar = document.getElementById('action-bar');
            const countDisplay = document.getElementById('count-display');
            
            countDisplay.innerText = selectedImages.size;
            
            if (selectedImages.size > 0) {{
                bar.classList.add('visible');
            }} else {{
                bar.classList.remove('visible');
            }}
        }}

         // --- Download / Share Logic ---
        function downloadSingle(url, filename) {{
             fetch(url)
                .then(resp => resp.blob())
                .then(blob => {{
                    saveAs(blob, filename);
                }})
                .catch(err => alert("Download failed: " + err));
        }}

        async function shareSingle(url, filename) {{
            if (navigator.share) {{
                try {{
                    const response = await fetch(url);
                    const blob = await response.blob();
                    const file = new File([blob], filename, {{ type: blob.type }});
                    
                    if (navigator.canShare && navigator.canShare({{ files: [file] }})) {{
                        await navigator.share({{
                            files: [file],
                            title: 'Luigi Photo',
                            text: 'Check out this photo of Luigi Mangione'
                        }});
                    }} else {{
                         throw new Error("File sharing not supported");
                    }}
                }} catch (err) {{
                    console.log('Share failed', err);
                    copyToClipboard(url);
                }}
            }} else {{
                copyToClipboard(url);
            }}
        }}

        function copyToClipboard(text) {{
             navigator.clipboard.writeText(text).then(() => alert("Sharing not supported in this mode. Link copied to clipboard!"));
        }}

        async function downloadZip() {{
            if (selectedImages.size === 0) return;
            const zip = new JSZip();
            const btn = document.querySelector('.action-btn.primary');
            const originalText = btn.innerText;
            btn.innerText = "Zipping...";
            try {{
                const limit = selectedImages.size;
                let processed = 0;
                const promises = Array.from(selectedImages).map(async (filename) => {{
                    const response = await fetch(imageDir + filename);
                    if (response.ok) {{
                        const blob = await response.blob();
                        zip.file(filename, blob);
                    }}
                    processed++;
                    btn.innerText = `Zipping ${{Math.round((processed/limit)*100)}}%`;
                }});
                await Promise.all(promises);
                const content = await zip.generateAsync({{type:"blob"}});
                saveAs(content, "luigi_archive_selection.zip");
            }} catch (err) {{
                alert("Error: " + err.message);
            }} finally {{
                btn.innerText = originalText;
            }}
        }}

        function emailList() {{
            if (selectedImages.size === 0) return;
            const fileList = Array.from(selectedImages).join('%0D%0A'); 
            window.location.href = `mailto:?subject=Luigi Photos&body=Files:%0D%0A%0D%0A${{fileList}}`;
        }}

        async function shareSelection() {{
            if (selectedImages.size === 0) return;
            const text = "Checking out these photos:\\n" + Array.from(selectedImages).join('\\n');
            if (navigator.share) {{
                try {{ await navigator.share({{ title: 'Luigi Photos', text: text }}); }} 
                catch (err) {{ }}
            }} else {{
                navigator.clipboard.writeText(text).then(() => alert("Copied list!"));
            }}
        }}

        // --- Lightbox Logic ---
        const totalImages = {global_index}; // Python injected count
        let currentIndex = 0;
        const lightbox = document.getElementById('lightbox');
        const lbImg = document.getElementById('lb-img');
        const lbCaption = document.getElementById('lb-caption');

        function openLightbox(index) {{
            currentIndex = index;
            updateLightbox();
            lightbox.classList.add('active');
            document.body.style.overflow = 'hidden'; // Stop background scroll
        }}

        function closeLightbox() {{
            lightbox.classList.remove('active');
            document.body.style.overflow = 'auto'; 
        }}

        function changeSlide(n) {{
            currentIndex += n;
            if (currentIndex >= totalImages) currentIndex = 0;
            if (currentIndex < 0) currentIndex = totalImages - 1;
            updateLightbox();
        }}

        function updateLightbox() {{
            // Find the image in the DOM by its ID `img-index`
            const srcImg = document.getElementById(`img-${{currentIndex}}`);
            if (srcImg) {{
                lbImg.src = srcImg.src;
                lbCaption.innerText = srcImg.getAttribute('data-info') + ` (${{currentIndex + 1}} / ${{totalImages}})`;
            }}
        }}

        // Gestures & Keyboard
        document.addEventListener('keydown', function(event) {{
            if (!lightbox.classList.contains('active')) return;
            if (event.key === "ArrowLeft") changeSlide(-1);
            if (event.key === "ArrowRight") changeSlide(1);
            if (event.key === "Escape") closeLightbox();
        }});

        // Touch Swipe
        let touchStartX = 0;
        let touchEndX = 0;
        
        lightbox.addEventListener('touchstart', e => {{
            touchStartX = e.changedTouches[0].screenX;
        }});
        
        lightbox.addEventListener('touchend', e => {{
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }});

        function handleSwipe() {{
            if (touchEndX < touchStartX - 50) changeSlide(1); // Swipe Left -> Next
            if (touchEndX > touchStartX + 50) changeSlide(-1); // Swipe Right -> Prev
        }}

        // Click outside closes
        lightbox.addEventListener('click', e => {{
            if (e.target === lightbox) closeLightbox();
        }});

        // --- Meme Editor Logic ---
        const memeEditor = document.getElementById('meme-editor');
        const canvas = document.getElementById('meme-canvas');
        const ctx = canvas.getContext('2d');
        let currentMemeImg = new Image();

        const luigiQuotes = [
            "The system isn't broken, it's fixed.",
            "Health is a right, not a privilege.",
            "Profit over people is the real sickness.",
            "Disrupt the status quo.",
            "Silence is compliance.",
            "We need a cure for greed.",
            "The waiting room is full of injustice.",
            "Diagnosis: Corruption.",
            "Prescription: Revolution.",
            "Transparency is the best medicine."
        ];

        function openMemeEditor(imgUrl) {{
            memeEditor.classList.add('active');
            // Removed crossOrigin for local file support
            currentMemeImg.src = imgUrl;
            currentMemeImg.onload = () => {{
                drawMeme();
            }};
            document.getElementById('top-text').value = "";
            document.getElementById('middle-text').value = "";
            document.getElementById('bottom-text').value = "";
        }}
        
        function closeMemeEditor() {{
            memeEditor.classList.remove('active');
        }}
        
        // Restore arrows when closing lightbox (if modified)
        function closeLightbox() {{
            lightbox.classList.remove('active');
            document.body.style.overflow = 'auto'; 
            document.querySelectorAll('.lb-nav').forEach(el => el.style.display = '');
        }}
        
        function drawMeme() {{
            const width = window.innerWidth > 800 ? 800 : window.innerWidth - 40;
            const scale = width / currentMemeImg.naturalWidth;
            const height = currentMemeImg.naturalHeight * scale;
            
            canvas.width = width;
            canvas.height = height;
            
            ctx.drawImage(currentMemeImg, 0, 0, width, height);
            
            const topText = document.getElementById('top-text').value;
            const middleText = document.getElementById('middle-text').value;
            const bottomText = document.getElementById('bottom-text').value;
            
            ctx.font = `bold ${{width/10}}px Impact`;
            ctx.fillStyle = 'white';
            ctx.strokeStyle = 'black';
            ctx.lineWidth = width/150;
            ctx.textAlign = 'center';
            
            if (topText) {{
                ctx.textBaseline = 'top';
                ctx.strokeText(topText.toUpperCase(), width/2, 10);
                ctx.fillText(topText.toUpperCase(), width/2, 10);
            }}
            
            if (middleText) {{
                ctx.textBaseline = 'middle';
                ctx.strokeText(middleText.toUpperCase(), width/2, height/2);
                ctx.fillText(middleText.toUpperCase(), width/2, height/2);
            }}
            
            if (bottomText) {{
                ctx.textBaseline = 'bottom';
                ctx.strokeText(bottomText.toUpperCase(), width/2, height - 10);
                ctx.fillText(bottomText.toUpperCase(), width/2, height - 10);
            }}
        }}
        
        function luigiLogic() {{
             let quote = luigiQuotes[Math.floor(Math.random() * luigiQuotes.length)];
             
             // Remove trailing punctuation first
             quote = quote.replace(/[.,;?!]+$/, '');

             // Split by punctuation (comma, period, etc in middle)
             // This consumes the punctuation so it doesn't appear in text
             let parts = quote.split(/[.,;?!]+/).map(p => p.trim()).filter(p => p.length > 0);
             
             // Fallback: If 1 part is too long (>24 chars), split by space
             if (parts.length === 1 && parts[0].length > 24) {{
                 const mid = Math.floor(parts[0].length / 2);
                 const splitIdx = parts[0].lastIndexOf(' ', mid);
                 if (splitIdx !== -1) {{
                    parts = [parts[0].substring(0, splitIdx), parts[0].substring(splitIdx + 1)];
                 }}
             }}

             // Assign to fields
             let t = "", m = "", b = "";
             
             if (parts.length === 1) {{
                 b = parts[0];
             }} else if (parts.length === 2) {{
                 t = parts[0];
                 b = parts[1];
             }} else {{
                 t = parts[0];
                 m = parts[1];
                 b = parts.slice(2).join(" ");
             }}
             
             document.getElementById('top-text').value = t;
             document.getElementById('middle-text').value = m;
             document.getElementById('bottom-text').value = b;
             
             drawMeme();
        }}
        
        function downloadMeme() {{
            canvas.toBlob(function(blob) {{
                if (window.saveAs) {{
                    saveAs(blob, "Luigi_Logic_Meme.jpg");
                }} else {{
                    const link = document.createElement('a');
                    link.download = 'Luigi_Logic_Meme.jpg';
                    link.href = URL.createObjectURL(blob);
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }}
            }}, 'image/jpeg');
        }}
        
        async function shareMeme() {{
            canvas.toBlob(async function(blob) {{
                const file = new File([blob], "Luigi_Logic_Meme.jpg", {{ type: "image/jpeg" }});
                if (navigator.share && navigator.canShare({{ files: [file] }})) {{
                    try {{
                        await navigator.share({{
                            files: [file],
                            title: 'Luigi Meme',
                            text: 'Luigi Logic'
                        }});
                    }} catch (err) {{ 
                        console.log(err);
                        downloadMeme(); // Fallback
                    }}
                }} else {{
                    alert("Sharing not supported completely. Downloading instead...");
                    downloadMeme();
                }}
            }}, 'image/jpeg');
        }}

    </script>
</body>
</html>
"""

with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated timeline {output_file} with {count} images in {len(sorted_groups)} events.")

