<div align="center">

# ⚡ Oque
### The Modern, Concurrent Terminal Downloader for Linux

![Version](https://img.shields.io/badge/version-Beta_7.12.25-blue?style=for-the-badge&logo=linux)
![Python](https://img.shields.io/badge/Made_with-Python_3-yellow?style=for-the-badge&logo=python)
![Safety](https://img.shields.io/badge/Virus_Free-100%25-success?style=for-the-badge&logo=security)

</div>

---

## 📖 About
**Oque** is a lightweight, powerful CLI tool designed to replace boring file downloads. It brings modern features to your terminal:
* **Visuals:** Beautiful, real-time progress bars with speed and ETA.
* **Concurrency:** Automatically downloads up to **4 files at once**.
* **Smart Handling:** Auto-detects GitHub repositories and video links.
* **Zero Config:** Installs in seconds, works immediately.

---

## 🚀 Installation
Install Oque with a single command. This will download the latest version from GitHub, install dependencies (`tqdm`, `requests`, `yt-dlp`), and set up the `oque` command.

```bash
curl -sL https://raw.githubusercontent.com/SunSolsticeByte/oque/main/install.sh | sudo bash install.sh

```

> **Note:** Oque installs to `/usr/local/bin`. You may be asked for your password to allow the installation.

---

## 🛠️ Usage Guide

### 0. BASIC SHORTCUT:

Shortcuts that you should know (use keyboard pls🙏)

```bash
CTRL + C > STOP THE CURRENT OQUE TERMINAL (the left over files will be deleted)

```

### 1. Download Files (Parallel)

Download multiple files simultaneously. Oque manages the queue and shows individual progress bars.

```bash
oque url <Download link> <Download link 2 optional> <etc>

```

* **Saves to:** `~` (Home Directory)

### 2. Download GitHub Repositories

Paste any GitHub repository link. Oque automatically detects it, adds the correct archive suffix, and downloads the source code as a ZIP.

```bash
oque git <Github HTTPS Repo link>

```

* **Saves to:** `~/<RepoName>.zip`

### 3. Download Video/Audio

Uses the power of `yt-dlp` to download high-quality media from YouTube and other sites.

```bash
oque ytdlp <link>

```

* **Saves to:** `~/Downloads`

### 4. Instant Sharing

Uses the power of `HTTP` to 'Share any files with no limit!'

```bash
oque share <Path>
oque url <Link> shared
oque ytdlp <link> shared
```

* **Sharing to:** `LOCAL NETWORK e.g: 192.168.1.13:8000 (based on your ip in LAN)`
* **WARN:** `SHARING WILL ONLY WORK IF THE TERMINAL IS OPEN! (Ctrl + C to close)`



### 5. System Commands

```bash
# Check installed version
oque version

# Restart the tool (simulated refresh)
oque restart

```

---

## 🗑️ Uninstallation

If you want to remove Oque from your system, you can do so cleanly using the built-in command:

```bash
oque uninstall

```

*Follow the prompt (type `oque` to confirm) and it will self-destruct.*

---

## 🛡️ Trust & Safety

**Is Oque safe?**
Yes. We prioritize transparency:

1. **Open Source:** You are reading this on GitHub. The code in `oque.py` is exactly what runs on your machine.
2. **No Hidden Telemetry:** We do not track your downloads, IP, or usage data.
3. **Non-Destructive:** The installer adds files but does not alter your critical system configurations or force a full system update.

---

## 🧰 Built With

* **Python 3** - Core Logic
* **TQDM** - Visual Progress Bars
* **Requests** - HTTP Handling
* **yt-dlp** - Media Extraction

<div align="center">
<sub>Made with ❤️ by SunSolsticeByte</sub>
</div>
