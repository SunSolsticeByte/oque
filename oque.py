cat << 'EOF' > oque.py
#!/usr/bin/env python3
import sys
import os
import subprocess
import concurrent.futures
import urllib3
from urllib.parse import urlparse

# --- Config & Setup ---
VERSION = "Version Beta 7.12.25"
MAX_CONCURRENT = 4
HOME_DIR = os.path.expanduser("~")
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")

# Disable SSL warnings for cleaner output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Try importing dependencies, or exit cleanly if missing
try:
    import requests
    from tqdm import tqdm
except ImportError:
    print("Error: Missing dependencies (requests, tqdm). Please run the installer again.")
    sys.exit(1)

# --- Helper Functions ---

def clean_filename(url, is_git=False):
    """Derives a filename from the URL."""
    try:
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if is_git:
            # If it's a github repo, name it repo_name.zip
            repo_name = path.split("/")[-1]
            if repo_name.endswith(".zip"):
                return repo_name
            return f"{repo_name}.zip"
        
        name = os.path.basename(path)
        return name if name else "downloaded_file"
    except:
        return "unknown_file"

def download_task(url, position, dest_folder, is_git=False):
    """Handles a single download with a progress bar."""
    
    # Git Handling: Append archive link if it looks like a raw repo URL
    if is_git and not url.endswith(".zip"):
        if "github.com" in url and "/archive/" not in url:
            url = f"{url.rstrip('/')}/archive/HEAD.zip"

    filename = clean_filename(url, is_git)
    dest_path = os.path.join(dest_folder, filename)

    try:
        # verify=False fixes the SSL/Certificate errors
        response = requests.get(url, stream=True, timeout=20, verify=False)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        
        # Custom Bar Format: Filename | 45% | [====] | 2MB/5MB [ 500KB/s < 00:02 ]
        bar_fmt = '{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{rate_fmt} < {remaining}]'
        
        with tqdm(total=total_size, unit='B', unit_scale=True, 
                  desc=f"Downloading {filename}", position=position, leave=True, 
                  bar_format=bar_fmt) as pbar:
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        pbar.update(len(chunk))
                        f.write(chunk)
        
        return True, dest_path, None
    except Exception as e:
        return False, filename, str(e)

# --- Command Handlers ---

def cmd_url(urls):
    if not urls:
        print("Usage: oque url <link1> <link2> ...")
        return

    print(f"Queueing {len(urls)} file(s)...")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
        futures = [executor.submit(download_task, url, i, HOME_DIR) for i, url in enumerate(urls)]
        
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    # Summary
    print("\n" * len(urls)) # Spacing to clear bars
    print("-" * 40)
    print("DOWNLOAD SUMMARY (~/):")
    for success, name_or_path, error in results:
        if success:
            print(f" [OK] Saved: {name_or_path}")
        else:
            print(f" [X] FAILED {name_or_path}: {error}")

def cmd_git(link):
    if not link:
        print("Usage: oque git <github_url>")
        return
    print("Processing Git Repository...")
    success, path, err = download_task(link, 0, HOME_DIR, is_git=True)
    print("\n" + "-" * 30)
    if success:
        print(f" [OK] Repo saved as: {path}")
    else:
        print(f" [X] Git Download Failed: {err}")

def cmd_ytdlp(link):
    if not link:
        print("Usage: oque ytdlp <link>")
        return
    
    print(f"Fetching via yt-dlp: {link}")
    # Check if yt-dlp exists
    if shutil.which("yt-dlp") is None:
        print("Error: yt-dlp is not installed/found in PATH.")
        return

    try:
        # Run yt-dlp silently, only showing its own progress
        cmd = ["yt-dlp", "-P", DOWNLOADS_DIR, link]
        subprocess.run(cmd, check=True)
        print("-" * 30)
        print(f" [OK] Media saved to: {DOWNLOADS_DIR}")
    except subprocess.CalledProcessError:
        print(f" [X] FAILED: yt-dlp could not download the link.")

def cmd_restart():
    # In a script context, we just echo. 
    # Real service restart would require systemctl access.
    print("oque restarted.")

def cmd_uninstall():
    print(f"Uninstalling {VERSION}...")
    confirm = input("Are you sure? Type 'oque' to confirm: ")
    if confirm.strip() == "oque":
        try:
            target = "/usr/local/bin/oque"
            if os.path.exists(target):
                os.remove(target)
                print("Oque has been uninstalled.")
            else:
                print("Oque is not installed in /usr/local/bin.")
        except PermissionError:
            print("Error: Permission denied. Try: sudo oque uninstall")
    else:
        print("Cancelled.")

# --- Main ---

def main():
    if len(sys.argv) < 2:
        print("Usage: oque <url|git|ytdlp|restart|uninstall|version>")
        return

    command = sys.argv[1].lower()
    import shutil # Lazy import

    if command == "url":
        cmd_url(sys.argv[2:])
    elif command == "git":
        cmd_git(sys.argv[2] if len(sys.argv) > 2 else None)
    elif command == "ytdlp":
        cmd_ytdlp(sys.argv[2] if len(sys.argv) > 2 else None)
    elif command == "restart":
        cmd_restart()
    elif command == "uninstall":
        cmd_uninstall()
    elif command == "version":
        print(VERSION)
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
EOF
