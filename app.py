#!/usr/bin/env python3
"""
Web-based Video Downloader
A Flask web application to download videos from any URL
"""

from flask import Flask, render_template, request, jsonify, send_file
import subprocess
import os
import uuid
from pathlib import Path
import threading
import time

app = Flask(__name__)

# Store download status and processes
downloads = {}
download_processes = {}  # Store subprocess objects for cancellation

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

def download_video(download_id, url, filename, quality='best'):
    """Background task to download video"""
    try:
        downloads[download_id]['status'] = 'downloading'
        downloads[download_id]['progress'] = 'Starting download...'
        
        output_path = DOWNLOAD_DIR / filename
        output_template = str(output_path.with_suffix(''))
        
        # For direct m3u8 streams, just use 'best' - the quality is in the URL itself
        # The user already selected the quality when they got the m3u8 URL (360, 720, 1080, etc.)
        format_string = 'best'
        
        # Use yt-dlp to download with MAXIMUM SPEED settings
        command = [
            'python3', '-m', 'yt_dlp',
            '--no-check-certificate',
            '--newline',  # Print progress on new lines
            '-f', format_string,
            '-o', output_template,
            '--merge-output-format', 'mp4',
            '--concurrent-fragments', '16',  # Download 16 fragments at once (FAST!)
            '--buffer-size', '16K',  # Larger buffer for faster download
            '--http-chunk-size', '10M',  # Download in 10MB chunks
            '--retries', '10',  # Retry failed chunks
            '--fragment-retries', '10',  # Retry failed fragments
            '--no-part',  # Don't use .part files (faster)
            '--no-mtime',  # Don't set file modification time (faster)
            url
        ]
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=str(Path.cwd())
        )
        
        # Store process for cancellation
        download_processes[download_id] = process
        
        # Read output line by line
        error_messages = []
        for line in process.stdout:
            line = line.strip()
            if line:
                downloads[download_id]['progress'] = line
                # Capture error messages
                if 'ERROR' in line or 'error' in line.lower():
                    error_messages.append(line)
                if '[download]' in line and '%' in line:
                    # Extract percentage
                    try:
                        percent = line.split('%')[0].split()[-1]
                        downloads[download_id]['percent'] = float(percent)
                    except:
                        pass
        
        process.wait()
        
        if process.returncode == 0:
            # Find the downloaded file
            downloaded_file = None
            for ext in ['.mp4', '.mkv', '.webm', '.avi']:
                test_path = output_path.with_suffix(ext)
                if test_path.exists():
                    downloaded_file = test_path
                    break
            
            if downloaded_file:
                # Get file size and format
                file_size = downloaded_file.stat().st_size
                file_ext = downloaded_file.suffix.upper().replace('.', '')
                
                # Format file size
                if file_size < 1024 * 1024:  # Less than 1 MB
                    size_str = f"{file_size / 1024:.2f} KB"
                elif file_size < 1024 * 1024 * 1024:  # Less than 1 GB
                    size_str = f"{file_size / (1024 * 1024):.2f} MB"
                else:  # GB or larger
                    size_str = f"{file_size / (1024 * 1024 * 1024):.2f} GB"
                
                downloads[download_id]['status'] = 'completed'
                downloads[download_id]['file'] = str(downloaded_file)
                downloads[download_id]['file_size'] = size_str
                downloads[download_id]['file_format'] = file_ext
                downloads[download_id]['progress'] = f'Download completed! ({size_str}, {file_ext})'
            else:
                downloads[download_id]['status'] = 'error'
                downloads[download_id]['progress'] = 'File not found after download'
        else:
            downloads[download_id]['status'] = 'error'
            error_detail = error_messages[-1] if error_messages else 'Download failed'
            downloads[download_id]['progress'] = f'Failed: {error_detail}'
            
    except Exception as e:
        downloads[download_id]['status'] = 'error'
        downloads[download_id]['progress'] = f'Error: {str(e)}'
    finally:
        # Clean up process reference
        if download_id in download_processes:
            del download_processes[download_id]

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/check-formats', methods=['POST'])
def check_formats():
    """Check available formats for a URL"""
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        # Use yt-dlp to list formats with playlist extraction
        command = [
            'python3', '-m', 'yt_dlp',
            '--no-check-certificate',
            '-J',  # Output JSON
            '--flat-playlist',  # Extract all videos from playlist/page
            '--no-warnings',
            url
        ]
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            import json
            info = json.loads(result.stdout)
            
            formats = []
            for fmt in info.get('formats', []):
                # Only include video formats with reasonable quality
                if fmt.get('vcodec') != 'none' and fmt.get('height'):
                    filesize = fmt.get('filesize') or fmt.get('filesize_approx') or 0
                    
                    # Format file size
                    if filesize > 0:
                        if filesize < 1024 * 1024:
                            size_str = f"{filesize / 1024:.1f} KB"
                        elif filesize < 1024 * 1024 * 1024:
                            size_str = f"{filesize / (1024 * 1024):.1f} MB"
                        else:
                            size_str = f"{filesize / (1024 * 1024 * 1024):.2f} GB"
                    else:
                        size_str = "Unknown"
                    
                    formats.append({
                        'format_id': fmt.get('format_id'),
                        'resolution': f"{fmt.get('width')}x{fmt.get('height')}",
                        'height': fmt.get('height'),
                        'ext': fmt.get('ext'),
                        'filesize': filesize,
                        'filesize_str': size_str,
                        'fps': fmt.get('fps'),
                        'vcodec': fmt.get('vcodec', '').split('.')[0],
                        'acodec': fmt.get('acodec', 'none').split('.')[0]
                    })
            
            # Sort by height (quality)
            formats.sort(key=lambda x: x['height'], reverse=True)
            
            # Remove duplicates, keep best quality for each resolution
            seen_heights = set()
            unique_formats = []
            for fmt in formats:
                if fmt['height'] not in seen_heights:
                    seen_heights.add(fmt['height'])
                    unique_formats.append(fmt)
            
            return jsonify({
                'title': info.get('title', 'Video'),
                'duration': info.get('duration'),
                'formats': unique_formats[:10]  # Limit to top 10
            })
        else:
            return jsonify({'error': 'Could not fetch video information'}), 400
            
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Request timeout'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def start_download():
    """Start a new download"""
    data = request.json
    url = data.get('url', '').strip()
    filename = data.get('filename', 'video').strip()
    quality = data.get('quality', 'best').strip()
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Ensure filename has .mp4 extension
    if not filename.endswith('.mp4'):
        filename += '.mp4'
    
    # Generate unique download ID
    download_id = str(uuid.uuid4())
    
    # Initialize download status
    downloads[download_id] = {
        'status': 'queued',
        'progress': 'Queued...',
        'percent': 0,
        'url': url,
        'filename': filename,
        'quality': quality
    }
    
    # Start download in background thread
    thread = threading.Thread(target=download_video, args=(download_id, url, filename, quality))
    thread.daemon = True
    thread.start()
    
    return jsonify({'download_id': download_id})

@app.route('/status/<download_id>')
def get_status(download_id):
    """Get download status"""
    if download_id not in downloads:
        return jsonify({'error': 'Download not found'}), 404
    
    return jsonify(downloads[download_id])

@app.route('/cancel/<download_id>', methods=['POST'])
def cancel_download(download_id):
    """Cancel an active download"""
    if download_id not in downloads:
        return jsonify({'error': 'Download not found'}), 404
    
    # Kill the process if it's running
    if download_id in download_processes:
        try:
            process = download_processes[download_id]
            process.terminate()  # Try graceful termination first
            time.sleep(0.5)
            if process.poll() is None:  # If still running
                process.kill()  # Force kill
            del download_processes[download_id]
        except:
            pass
    
    # Update status
    downloads[download_id]['status'] = 'cancelled'
    downloads[download_id]['progress'] = 'Download cancelled by user'
    
    return jsonify({'success': True, 'message': 'Download cancelled'})

@app.route('/download-file/<download_id>')
def download_file(download_id):
    """Download the completed file"""
    if download_id not in downloads:
        return jsonify({'error': 'Download not found'}), 404
    
    download_info = downloads[download_id]
    
    if download_info['status'] != 'completed':
        return jsonify({'error': 'Download not completed'}), 400
    
    file_path = download_info['file']
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Video Downloader Web App")
    print("="*60)
    print("\nStarting server...")
    print("Open your browser and go to: http://localhost:8080")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8080)
