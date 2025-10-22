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
download_threads = {}  # Store thread objects

DOWNLOAD_DIR = Path("/tmp/downloads")  # Use /tmp on Render (writable)
DOWNLOAD_DIR.mkdir(exist_ok=True, parents=True)

def download_video(download_id, url, filename, quality='best'):
    """Background task to download video"""
    try:
        # For m3u8 URLs, we need to download to server first
        # (m3u8 streams can't be directly downloaded by browser)
        download_video_to_server(download_id, url, filename, quality)
            
    except Exception as e:
        downloads[download_id]['status'] = 'error'
        downloads[download_id]['progress'] = f'Error: {str(e)}'
    finally:
        # Clean up process reference
        if download_id in download_processes:
            del download_processes[download_id]

def download_video_to_server(download_id, url, filename, quality='best'):
    """Fallback: Download to server if direct download doesn't work"""
    try:
        output_path = DOWNLOAD_DIR / filename
        output_template = str(output_path.with_suffix(''))
        
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
            # Find the downloaded file - check multiple locations and extensions
            downloaded_file = None
            
            # First, try common extensions with exact filename
            for ext in ['.mp4', '.mkv', '.webm', '.avi', '.m4v', '.ts', '.flv']:
                test_path = output_path.with_suffix(ext)
                if test_path.exists():
                    downloaded_file = test_path
                    break
            
            # If not found, search entire directory for ANY video file (including files without extensions!)
            if not downloaded_file:
                all_files = list(DOWNLOAD_DIR.glob("*"))
                video_files = [f for f in all_files 
                              if f.is_file() 
                              and (f.suffix.lower() in ['.mp4', '.mkv', '.webm', '.avi', '.m4v', '.ts', '.flv', '.m4a', '']  # Include no extension!
                                   or f.suffix == '')  # Files without extension
                              and f.stat().st_size > 1024]  # At least 1KB
                
                if video_files:
                    # Get the most recently modified video file
                    downloaded_file = max(video_files, key=lambda f: f.stat().st_mtime)
                    print(f"Found file: {downloaded_file.name} ({downloaded_file.stat().st_size} bytes)")
            
            if downloaded_file:
                # Get file size and format
                file_size = downloaded_file.stat().st_size
                file_ext = downloaded_file.suffix.upper().replace('.', '') if downloaded_file.suffix else 'MP4'
                
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
                # List what files ARE in the directory for debugging
                files_in_dir = list(DOWNLOAD_DIR.glob('*'))
                file_names = [f.name for f in files_in_dir if f.is_file()]
                downloads[download_id]['progress'] = f'File not found. Expected: {output_path.stem}. Found files: {", ".join(file_names) if file_names else "none"}'
                print(f"ERROR: Expected {output_path.stem}, found: {file_names}")
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
def download():
    """Start a new download - streams directly to browser"""
    data = request.json
    url = data.get('url', '').strip()
    filename = data.get('filename', 'video').strip()
    quality = data.get('quality', 'best').strip()
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Ensure filename has .mp4 extension
    if not filename.endswith('.mp4'):
        filename += '.mp4'
    
    # Return the URL and filename - browser will call /stream endpoint
    return jsonify({
        'stream_url': f'/stream?url={url}&filename={filename}',
        'filename': filename
    })

@app.route('/stream')
def stream_video():
    """Stream video directly to browser - NO DOUBLE DOWNLOAD!"""
    url = request.args.get('url', '').strip()
    filename = request.args.get('filename', 'video.mp4').strip()
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    def generate():
        """Stream yt-dlp output directly to browser"""
        command = [
            'python3', '-m', 'yt_dlp',
            '--no-check-certificate',
            '-f', 'best',
            '--merge-output-format', 'mp4',
            '--concurrent-fragments', '16',
            '--buffer-size', '16K',
            '--http-chunk-size', '10M',
            '--retries', '10',
            '--fragment-retries', '10',
            '--write-sub',  # Download subtitles
            '--sub-lang', 'en',  # Only English subtitles
            '--embed-subs',  # Embed subtitles in video
            '--fixup', 'detect_or_warn',  # Fix issues automatically
            '-o', '-',  # Output to stdout!
            url
        ]
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        
        # Stream the output
        while True:
            chunk = process.stdout.read(8192)  # Read 8KB at a time
            if not chunk:
                break
            yield chunk
        
        process.wait()
    
    return app.response_class(
        generate(),
        mimetype='video/mp4',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Cache-Control': 'no-cache'
        }
    )

@app.route('/status/<download_id>')
def get_status(download_id):
    """Get download status"""
    if download_id not in downloads:
        return jsonify({'error': 'Download not found'}), 404
    
    return jsonify(downloads[download_id])

@app.route('/pause/<download_id>', methods=['POST'])
def pause_download(download_id):
    """Pause an active download"""
    if download_id not in downloads:
        return jsonify({'error': 'Download not found'}), 404
    
    # Pause the process if it's running
    if download_id in download_processes:
        try:
            import signal
            process = download_processes[download_id]
            process.send_signal(signal.SIGSTOP)  # Pause the process
            downloads[download_id]['status'] = 'paused'
            downloads[download_id]['progress'] = 'Download paused'
            return jsonify({'success': True, 'message': 'Download paused'})
        except Exception as e:
            return jsonify({'error': f'Failed to pause: {str(e)}'}), 500
    
    return jsonify({'error': 'No active process to pause'}), 400

@app.route('/resume/<download_id>', methods=['POST'])
def resume_download(download_id):
    """Resume a paused download"""
    if download_id not in downloads:
        return jsonify({'error': 'Download not found'}), 404
    
    # Resume the process if it's paused
    if download_id in download_processes:
        try:
            import signal
            process = download_processes[download_id]
            process.send_signal(signal.SIGCONT)  # Resume the process
            downloads[download_id]['status'] = 'downloading'
            downloads[download_id]['progress'] = 'Download resumed'
            return jsonify({'success': True, 'message': 'Download resumed'})
        except Exception as e:
            return jsonify({'error': f'Failed to resume: {str(e)}'}), 500
    
    return jsonify({'error': 'No paused process to resume'}), 400

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
