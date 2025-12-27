#!/usr/bin/env python3
import sys
import os
import shutil
import signal
import socket
import subprocess
import concurrent.futures
import urllib3
import http.server
import socketserver
from urllib.parse import urlparse, quote

# --- Config & Setup ---
VERSION = "RLS25.12.27"
MAX_CONCURRENT = 4
HOME_DIR = os.path.expanduser("~")
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")
SHARED_DIR = os.path.expanduser("~/Oque_Shared")

# Global list to track active files for cleanup on Ctrl+C
ACTIVE_FILES = []

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Dependency Check
try:
    import requests
    from tqdm import tqdm
except ImportError:
    print("Error: Missing dependencies. Please run the installer again.")
    sys.exit(1)

# --- Signal Handling (Ctrl+C) ---

def signal_handler(sig, frame):
    print("\n\n[!] Cancellation detected (Ctrl+C).")
    print("Cleaning up temporary files...")
    
    # Remove incomplete files
    for filepath in ACTIVE_FILES:
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f" - Deleted incomplete: {os.path.basename(filepath)}")
            except OSError:
                pass
    
    print("Oque stopped.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# --- Helper Functions ---

def get_local_ip():
    """Finds the local network IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't actually connect, just determines route
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def start_share_server(directory, specific_file=None):
    if not os.path.exists(directory):
        print(f"Error: Directory {directory} does not exist.")
        return

    os.chdir(directory)
    port = 8000
    ip = get_local_ip()
    
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("", port))
            break
        except OSError:
            port += 1

    print("\n" + "="*40)
    print(f" SHARED SERVER STARTED")
    print("="*40)
    print(f" Root Folder: {directory}")
    
    base_link = f"http://{ip}:{port}/"
    print(f" Folder Link: {base_link}")
    
    if specific_file:
        # Generate a direct clickable link for the specific file (handles spaces/%20)
        safe_name = quote(specific_file)
        print(f" Direct File: {base_link}{safe_name}")
        
    print(" Press CTRL+C to stop sharing.")
    print("="*40 + "\n")

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args): pass

    try:
        with socketserver.TCPServer(("", port), QuietHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")

def clean_filename(url, is_git=False):
    try:
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if is_git:
            repo_name = path.split("/")[-1]
            if not repo_name.endswith(".zip"): return f"{repo_name}.zip"
            return repo_name
        name = os.path.basename(path)
        return name if name else "downloaded_file"
    except:
        return "unknown_file"

def download_task(url, position, dest_folder, is_git=False):
    if is_git and not url.endswith(".zip"):
        if "github.com" in url and "/archive/" not in url:
            # FIX: Remove .git suffix if present
            if url.endswith(".git"):
                url = url[:-4]
            url = f"{url.rstrip('/')}/archive/HEAD.zip"

    filename = clean_filename(url, is_git)
    dest_path = os.path.join(dest_folder, filename)
    
    # Track file for Ctrl+C cleanup
    ACTIVE_FILES.append(dest_path)

    try:
        response = requests.get(url, stream=True, timeout=20, verify=False)
        response.raise_for_status()
        total = int(response.headers.get('content-length', 0))
        
        bar_fmt = '{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{rate_fmt} < {remaining}]'
        
        with tqdm(total=total, unit='B', unit_scale=True, 
                  desc=f"Downloading {filename}", position=position, leave=True, 
                  bar_format=bar_fmt) as pbar:
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(8192):
                    if chunk:
                        pbar.update(len(chunk))
                        f.write(chunk)
        
        # Download success, remove from active cleanup list
        if dest_path in ACTIVE_FILES:
            ACTIVE_FILES.remove(dest_path)
            
        return True, dest_path, None
    except Exception as e:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        if dest_path in ACTIVE_FILES:
            ACTIVE_FILES.remove(dest_path)
        return False, filename, str(e)

# --- Commands ---

def cmd_url(args):
    is_shared = False
    urls = []
    
    for arg in args:
        if arg.lower() == "shared":
            is_shared = True
        else:
            urls.append(arg)
            
    if not urls:
        print("Usage: oque url <link> [shared]")
        return

    # If shared, save to dedicated folder, otherwise Home
    dest_dir = SHARED_DIR if is_shared else HOME_DIR
    if is_shared and not os.path.exists(SHARED_DIR):
        os.makedirs(SHARED_DIR)

    print(f"Queueing {len(urls)} file(s)...")
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as ex:
        futures = [ex.submit(download_task, u, i, dest_dir) for i, u in enumerate(urls)]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    print("\n" * len(urls) + "-"*40)
    print(f"Saved to: {dest_dir}")
    for success, path, err in results:
        print(f" [OK] {os.path.basename(path)}" if success else f" [X] {path}: {err}")
    
    if is_shared:
        start_share_server(dest_dir)

def cmd_ytdlp(args):
    if not args: return
    
    link = args[0]
    is_shared = "shared" in args
    
    dest_dir = SHARED_DIR if is_shared else DOWNLOADS_DIR
    if is_shared and not os.path.exists(SHARED_DIR):
        os.makedirs(SHARED_DIR)

    print(f"Fetching via yt-dlp...")
    if shutil.which("yt-dlp") is None:
        print("Error: yt-dlp missing.")
        return

    try:
        cmd = ["yt-dlp", "-P", dest_dir, link]
        subprocess.run(cmd, check=True)
        print("-" * 30)
        print(f" [OK] Media saved to: {dest_dir}")
        
        if is_shared:
            start_share_server(dest_dir)
            
    except subprocess.CalledProcessError:
        print(" [X] FAILED: yt-dlp error.")

def cmd_share(args):
    target = args[0] if args else "."
    target_path = os.path.abspath(target)
    
    if os.path.isfile(target_path):
        # User provided a file -> Share the parent folder + Highlight the file
        folder = os.path.dirname(target_path)
        filename = os.path.basename(target_path)
        start_share_server(folder, specific_file=filename)
    else:
        # User provided a folder
        start_share_server(target_path)

def cmd_git(args):
    if not args: return
    link = args[0]
    print("Processing Git Repo...")
    s, p, e = download_task(link, 0, HOME_DIR, is_git=True)
    print("\n" + "-"*30)
    print(f" [OK] {p}" if s else f" [X] {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: oque <url|ytdlp|git|share|restart|uninstall|version>")
        return

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd == "url": cmd_url(args)
    elif cmd == "ytdlp": cmd_ytdlp(args)
    elif cmd == "git": cmd_git(args)
    elif cmd == "share": cmd_share(args)
    elif cmd == "version": print(VERSION)
    elif cmd == "restart": print("oque restarted.")
    elif cmd == "uninstall":
        if input("Type 'oque' to confirm uninstall: ") == "oque":
            try: os.remove("/usr/local/bin/oque")
            except: print("Use sudo.")
            else: print("Uninstalled.")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
