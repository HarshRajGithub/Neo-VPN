# Free VPN Application

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

A privacy-focused desktop application that provides free proxy-based VPN functionality with a built-in web browser. Fetch, test, and connect to free proxies from multiple sources, with all traffic routed through the selected proxy.

![VPN App Screenshot](screenshot.png)

## Features

### Core Features
- **Free Proxy Sources**: Fetches proxies from 4 different free proxy APIs
- **Proxy Testing**: Tests proxy connectivity and measures latency
- **Auto-Connect**: Automatically connects to the fastest available proxy
- **Manual Selection**: Choose specific proxies from the list
- **Real-time Status**: Visual indicators for connection status
- **Connection Logs**: Detailed logs of all VPN activities

### Browser Features
- **Built-in Browser**: Separate browser window with full navigation controls
- **Proxy Routing**: All browser traffic routes through the selected proxy
- **Back/Forward Navigation**: Full browser history support
- **URL Bar**: Direct URL entry with protocol detection
- **Real-time Proxy Status**: Clear indication of proxy usage in browser

### Security Features
- **DNS Protection**: Prevents DNS leaks
- **No Logging**: Application doesn't store any browsing history
- **Open Source**: Fully transparent codebase

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/free-vpn-app.git
cd free-vpn-app

# Install dependencies
pip install -r requirements.txt

# Run the application
python vpn_app.py
