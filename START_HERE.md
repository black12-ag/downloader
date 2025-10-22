# 🎬 Video Downloader - Complete Project

## 📁 Project Location
**Desktop/downloader/**

All project files are now in this folder on your Desktop!

---

## 🚀 Quick Start

### Run the Web App Locally:

```bash
cd ~/Desktop/downloader
python3 app.py
```

Then open your browser to: **http://localhost:8080**

---

## 📦 What's Included:

### Main Files:
- **app.py** - Main Flask web application (the one you use!)
- **templates/index.html** - Web interface
- **requirements.txt** - Python dependencies

### Helper Scripts:
- **download_video.py** - Simple command-line downloader
- **download_interactive.py** - Interactive CLI version
- **extract_video_url.py** - Extract video URLs from webpages
- **standalone.html** - Standalone HTML version (no server needed)

### Documentation:
- **README.md** - Basic project info
- **README_DEPLOYMENT.md** - How to deploy to public website
- **HOW_TO_GET_VIDEO_URL.md** - How to find video URLs

### Deployment Files:
- **Procfile** - For Heroku/Render deployment
- **runtime.txt** - Python version
- **vercel.json** - For Vercel deployment

---

## 🎯 How to Use:

### Method 1: Web App (Recommended)
1. Run: `cd ~/Desktop/downloader && python3 app.py`
2. Open: http://localhost:8080
3. Paste your m3u8 URL
4. Select quality
5. Click "Download Video"

### Method 2: Command Line
```bash
cd ~/Desktop/downloader
python3 download_interactive.py
```

### Method 3: Standalone HTML
Just open `standalone.html` in your browser - no server needed!

---

## 🌐 Deploy to Public Website:

### Option 1: Render (Free & Easy)
1. Go to https://render.com
2. Create new Web Service
3. Upload this folder
4. Done!

### Option 2: Railway (Free & Fast)
1. Go to https://railway.app
2. New Project → Deploy from folder
3. Upload this folder
4. Done!

See **README_DEPLOYMENT.md** for detailed instructions.

---

## 📝 Features:

✅ Download videos from m3u8 URLs  
✅ Multiple quality options (1080p, 720p, 480p, 360p, 240p)  
✅ Check available formats and file sizes  
✅ Real-time download progress  
✅ Automatic video/audio merging  
✅ Shows file size and format after download  

---

## 🔧 Requirements:

- Python 3.x
- Flask
- yt-dlp
- ffmpeg (for video processing)

Install dependencies:
```bash
cd ~/Desktop/downloader
pip3 install -r requirements.txt
```

---

## 💡 Tips:

### Finding Video URLs:
1. Open video page in browser
2. Press **F12** (Developer Tools)
3. Go to **Network** tab
4. Filter by "m3u8"
5. Play the video
6. Copy the m3u8 URL that appears
7. Use it in the downloader!

### Quality Selection:
- **Best Available** - Automatically selects highest quality
- **1080p** - Full HD (200-400 MB for movies)
- **720p** - HD (100-200 MB)
- **480p** - SD (50-100 MB)
- **360p** - Low (20-50 MB)
- **240p** - Lowest (10-20 MB)

---

## 📞 Need Help?

Check these files:
- **HOW_TO_GET_VIDEO_URL.md** - How to find video URLs
- **README_DEPLOYMENT.md** - How to deploy online

---

**Enjoy your video downloader! 🎉**
