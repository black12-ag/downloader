#!/usr/bin/env python3
"""
Interactive M3U8 Video Downloader
Prompts user for URL and downloads the video
"""

import subprocess
import sys
from pathlib import Path

def download_m3u8(url, output_filename):
    """
    Download video from m3u8 URL using yt-dlp
    
    Args:
        url: The m3u8 stream URL
        output_filename: Name for the output file
    """
    output_path = Path(output_filename)
    output_template = str(output_path.with_suffix(''))  # Remove extension, yt-dlp will add it
    
    print(f"\n{'='*60}")
    print(f"Downloading video from: {url}")
    print(f"Output file: {output_path.absolute()}")
    print(f"{'='*60}\n")
    
    try:
        # Use yt-dlp to download the m3u8 stream (run as Python module)
        command = [
            'python3', '-m', 'yt_dlp',
            '--no-check-certificate',
            '--allow-unplayable-formats',
            '--fixup', 'never',
            '-o', output_template,
            '--merge-output-format', 'mp4',
            url
        ]
        
        # Run yt-dlp
        result = subprocess.run(
            command,
            check=True,
            capture_output=False
        )
        
        print(f"\n{'='*60}")
        print(f"✓ Download completed successfully!")
        print(f"Video saved to: {output_path.absolute()}")
        print(f"{'='*60}\n")
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error during download: {e}")
        print("\nThe stream may be protected, expired, or invalid.")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease install yt-dlp:")
        print("  pip3 install yt-dlp")
        return False
    
    return True

def main():
    """Main interactive loop"""
    print("\n" + "="*60)
    print("M3U8 Video Downloader")
    print("="*60)
    
    while True:
        # Get URL from user
        print("\nEnter the m3u8 URL (or 'quit' to exit):")
        url = input("> ").strip()
        
        if url.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not url:
            print("Error: URL cannot be empty!")
            continue
        
        # Get output filename
        print("\nEnter output filename (default: video.mp4):")
        filename = input("> ").strip()
        
        if not filename:
            filename = "video.mp4"
        
        # Ensure .mp4 extension
        if not filename.endswith('.mp4'):
            filename += '.mp4'
        
        # Download the video
        success = download_m3u8(url, filename)
        
        # Ask if user wants to download another
        if success:
            print("\nDownload another video? (yes/no):")
            response = input("> ").strip().lower()
            if response not in ['yes', 'y']:
                print("\nGoodbye!")
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user. Goodbye!")
        sys.exit(0)
