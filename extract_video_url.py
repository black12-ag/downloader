#!/usr/bin/env python3
"""
Extract video URL from a webpage
Helps find the actual video stream URL from streaming sites
"""

import subprocess
import sys

def extract_video_url(page_url):
    """Extract video URLs from a webpage using yt-dlp"""
    print(f"\n🔍 Extracting video URLs from: {page_url}\n")
    
    try:
        # Use yt-dlp to list all available formats
        command = [
            'python3', '-m', 'yt_dlp',
            '--no-check-certificate',
            '-F',  # List all available formats
            '--no-warnings',
            page_url
        ]
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Available formats:\n")
            print(result.stdout)
            
            # Also try to get the direct URL
            print("\n" + "="*60)
            print("🔗 Extracting direct video URL...")
            print("="*60 + "\n")
            
            command_url = [
                'python3', '-m', 'yt_dlp',
                '--no-check-certificate',
                '-g',  # Get direct URL
                '--no-warnings',
                page_url
            ]
            
            result_url = subprocess.run(
                command_url,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result_url.returncode == 0 and result_url.stdout.strip():
                urls = result_url.stdout.strip().split('\n')
                print("📺 Direct video URL(s):")
                for i, url in enumerate(urls, 1):
                    print(f"\n{i}. {url}")
                print("\n✅ Copy one of these URLs to use in the downloader!")
            else:
                print("⚠️  Could not extract direct URL")
                print(f"Error: {result_url.stderr}")
        else:
            print("❌ Failed to extract video information")
            print(f"\nError output:\n{result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout: The extraction took too long")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract_video_url.py <webpage_url>")
        print("\nExample:")
        print("  python3 extract_video_url.py 'https://example.com/watch/video'")
        sys.exit(1)
    
    url = sys.argv[1]
    extract_video_url(url)
