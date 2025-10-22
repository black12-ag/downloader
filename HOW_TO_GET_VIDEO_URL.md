# How to Get the Real Video URL

Some websites don't provide direct video links. Here's how to get the actual video URL:

## Method 1: Use Browser Developer Tools (Recommended)

1. **Open the video page** in your browser
2. **Right-click** on the page and select **"Inspect"** or press **F12**
3. Go to the **"Network"** tab
4. **Filter by "m3u8"** or "media"
5. **Play the video**
6. Look for requests ending in `.m3u8` or containing video data
7. **Right-click** on the request → **Copy** → **Copy URL**
8. **Paste that URL** into the downloader

## Method 2: Use the URL Extractor Script

Run this command with the webpage URL:

```bash
cd /Users/munir011/CascadeProjects/m3u8_downloader
python3 extract_video_url.py "YOUR_WEBPAGE_URL_HERE"
```

This will show you all available video formats and their direct URLs.

## Method 3: Browser Extensions

Install a browser extension like:
- **Video DownloadHelper** (Firefox/Chrome)
- **Stream Detector** (Chrome)
- **Video Downloader Professional** (Chrome)

These can detect and show video URLs on the page.

## For freemoviesfull.cc specifically:

The site embeds videos from other sources. You need to:
1. Click on the quality you want (360p, 720p, 1080p)
2. Use Method 1 above to capture the actual m3u8 URL
3. Use that URL in the downloader

## Example:

If you find a URL like:
```
https://example.com/hls/video123/index.m3u8
```

Use that in the Video Downloader app instead of the webpage URL.
