#!/usr/bin/env python3
"""
M3U8 Video Downloader using yt-dlp
More robust alternative to ffmpeg for downloading m3u8 streams
"""

import subprocess
import sys
from pathlib import Path

def download_m3u8(url, output_filename="movie.mp4"):
    """
    Download video from m3u8 URL using yt-dlp
    
    Args:
        url: The m3u8 stream URL
        output_filename: Name for the output file (default: movie.mp4)
    """
    output_path = Path(output_filename)
    output_template = str(output_path.with_suffix(''))  # Remove extension, yt-dlp will add it
    
    print(f"Downloading video from: {url}")
    print(f"Output file: {output_path.absolute()}")
    print("\nStarting download with yt-dlp...\n")
    
    try:
        # Use yt-dlp to download the m3u8 stream (run as Python module)
        command = [
            'python3', '-m', 'yt_dlp',
            '--no-check-certificate',  # Skip SSL certificate verification if needed
            '--allow-unplayable-formats',  # Allow downloading unplayable formats
            '--fixup', 'never',  # Don't try to fix file formats
            '-o', output_template,  # Output template
            '--merge-output-format', 'mp4',  # Merge to mp4
            url
        ]
        
        # Run yt-dlp
        result = subprocess.run(
            command,
            check=True,
            capture_output=False
        )
        
        print(f"\n✓ Download completed successfully!")
        print(f"Video saved to: {output_path.absolute()}")
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error during download: {e}")
        print("\nThe stream may be protected, expired, or invalid.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease install yt-dlp:")
        print("  pip3 install yt-dlp")
        sys.exit(1)

if __name__ == "__main__":
    # The m3u8 URL to download
    video_url = "https://akmzed.cloud/_v1_akmzed/MM3IaYxunxzXLZjjjJrkqDMrJwGxDN4UMYFE~MKfAk8=/aW5kZXgubTN1OA==.m3u8"
    
    # You can change the output filename here
    output_file = "movie.mp4"
    
    download_m3u8(video_url, output_file)
