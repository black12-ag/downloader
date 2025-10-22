#!/usr/bin/env python3
"""
M3U8 Video Downloader
Downloads video from m3u8 streaming links using ffmpeg
"""

import subprocess
import sys
from pathlib import Path

def download_m3u8(url, output_filename="downloaded_video.mp4"):
    """
    Download video from m3u8 URL using ffmpeg
    
    Args:
        url: The m3u8 stream URL
        output_filename: Name for the output file (default: downloaded_video.mp4)
    """
    output_path = Path(output_filename)
    
    print(f"Downloading video from: {url}")
    print(f"Output file: {output_path.absolute()}")
    print("\nStarting download...\n")
    
    try:
        # Use ffmpeg to download and convert the m3u8 stream
        # Added options to handle problematic streams
        command = [
            'ffmpeg',
            '-allowed_extensions', 'ALL',  # Allow all segment extensions
            '-protocol_whitelist', 'file,http,https,tcp,tls,crypto',  # Allow necessary protocols
            '-i', url,
            '-c', 'copy',  # Copy streams without re-encoding (faster)
            '-bsf:a', 'aac_adtstoasc',  # Fix audio stream if needed
            '-y',  # Overwrite output file if exists
            str(output_path)
        ]
        
        print("Running ffmpeg with enhanced compatibility options...\n")
        
        # Run ffmpeg
        result = subprocess.run(
            command,
            check=True,
            capture_output=False
        )
        
        print(f"\n✓ Download completed successfully!")
        print(f"Video saved to: {output_path.absolute()}")
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error during download: {e}")
        print("\nTrying alternative method with re-encoding...")
        
        # Fallback: try with re-encoding instead of copy
        try:
            command_fallback = [
                'ffmpeg',
                '-allowed_extensions', 'ALL',
                '-protocol_whitelist', 'file,http,https,tcp,tls,crypto',
                '-i', url,
                '-c:v', 'libx264',  # Re-encode video
                '-c:a', 'aac',  # Re-encode audio
                '-y',
                str(output_path)
            ]
            
            subprocess.run(command_fallback, check=True, capture_output=False)
            print(f"\n✓ Download completed with re-encoding!")
            print(f"Video saved to: {output_path.absolute()}")
        except subprocess.CalledProcessError as e2:
            print(f"\n✗ Fallback method also failed: {e2}")
            sys.exit(1)
    except FileNotFoundError:
        print("\n✗ Error: ffmpeg not found!")
        print("Please install ffmpeg:")
        print("  macOS: brew install ffmpeg")
        print("  Linux: sudo apt-get install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        sys.exit(1)

if __name__ == "__main__":
    # The m3u8 URL to download
    video_url = "https://akmzed.cloud/_v1_akmzed/MM3IaYxunxzXLZjjjJrkqDMrJwGxDN4UMYFE~MKfAk8=/aW5kZXgubTN1OA==.m3u8"
    
    # You can change the output filename here
    output_file = "movie.mp4"
    
    download_m3u8(video_url, output_file)
