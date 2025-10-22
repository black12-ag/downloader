# M3U8 Video Downloader

A simple Python script to download videos from m3u8 streaming links.

## Prerequisites

You need **ffmpeg** installed on your system:

### macOS
```bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### Windows
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Usage

1. Navigate to the project directory:
```bash
cd /Users/munir011/CascadeProjects/m3u8_downloader
```

2. Run the script:
```bash
python3 download_video.py
```

The video will be downloaded as `movie.mp4` in the same directory.

## Customization

Edit `download_video.py` to change:
- **URL**: Modify the `video_url` variable
- **Output filename**: Change the `output_file` variable

## Notes

- The script uses ffmpeg's copy mode for faster downloads (no re-encoding)
- Download time depends on video size and your internet connection
- Make sure you have permission to download the content
