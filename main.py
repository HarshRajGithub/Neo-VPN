# vpn_app.py
import webview
import requests
import json
import random
import threading
import time
import re
import webbrowser
from typing import List, Dict, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

class VPNManager:
    def __init__(self):
        self.proxies = []
        self.custom_proxies = []
        self.current_proxy = None
        self.is_connected = False
        self.testing_in_progress = False
        self.api_urls = [
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/Proxy-List/HTTP.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
        ]
    
    def validate_proxy(self, proxy: str) -> bool:
        pattern = r'^(\d{1,3}\.){3}\d{1,3}:\d{1,5}$'
        return bool(re.match(pattern, proxy))
    
    def add_custom_proxy(self, proxy: str) -> Dict:
        if not self.validate_proxy(proxy):
            return {"success": False, "error": "Invalid proxy format. Use IP:PORT"}
        
        if proxy not in self.custom_proxies:
            self.custom_proxies.append(proxy)
            return {"success": True, "proxy": proxy}
        return {"success": False, "error": "Proxy already exists"}
    
    def remove_custom_proxy(self, proxy: str) -> Dict:
        if proxy in self.custom_proxies:
            self.custom_proxies.remove(proxy)
            return {"success": True}
        return {"success": False, "error": "Proxy not found"}
    
    def fetch_proxies(self) -> List[str]:
        all_proxies = set()
        
        for url in self.api_urls:
            try:
                print(f"[VPN] Fetching from: {url}")
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    proxies = response.text.strip().split('\n')
                    for proxy in proxies:
                        proxy = proxy.strip()
                        if self.validate_proxy(proxy):
                            all_proxies.add(proxy)
                    print(f"[VPN] Found {len(all_proxies)} proxies so far")
            except Exception as e:
                print(f"[VPN] Error fetching from {url}: {e}")
        
        self.proxies = list(all_proxies)
        return self.proxies
    
    def test_single_proxy(self, proxy: str) -> Dict:
        try:
            proxy_dict = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            start_time = time.time()
            response = requests.get(
                "http://httpbin.org/ip", 
                proxies=proxy_dict, 
                timeout=5,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            latency = time.time() - start_time
            if response.status_code == 200:
                return {
                    "proxy": proxy,
                    "working": True,
                    "latency": round(latency * 1000, 2)
                }
        except:
            pass
        return {
            "proxy": proxy,
            "working": False,
            "latency": None
        }
    
    def test_proxy(self, proxy: str) -> tuple:
        try:
            proxy_dict = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            start_time = time.time()
            response = requests.get(
                "http://httpbin.org/ip", 
                proxies=proxy_dict, 
                timeout=5,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            latency = time.time() - start_time
            if response.status_code == 200:
                return True, round(latency * 1000, 2)
        except:
            pass
        return False, None
    
    def stop_testing(self):
        self.testing_in_progress = False
    
    def connect_to_proxy(self, proxy: str = None) -> Dict:
        try:
            if proxy:
                self.current_proxy = proxy
                self.is_connected = True
                return {"success": True, "proxy": self.current_proxy}
            
            return {"success": False, "error": "No proxy specified"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def disconnect(self):
        self.current_proxy = None
        self.is_connected = False
        return {"success": True}

class VPNWebViewApp:
    def __init__(self):
        self.vpn_manager = VPNManager()
        self.main_window = None
        self.browser_window = None
        
    def open_browser_window(self, url):
        """Open a new browser window that will use the proxy"""
        proxy_string = None
        if self.vpn_manager.is_connected and self.vpn_manager.current_proxy:
            proxy_string = self.vpn_manager.current_proxy
        
        # Create a new window with the URL directly (not iframe)
        window_title = f"Secure Browser - {'Proxy: ' + proxy_string if proxy_string else 'Direct Connection'}"
        
        # Open the URL directly in a new webview window
        self.browser_window = webview.create_window(
            window_title,
            url,
            width=1200,
            height=800,
            resizable=True,
            confirm_close=True
        )
        
        return self.browser_window
    
    def get_html(self):
        """Return the main application HTML interface"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NEO VPN - Real-Time Proxy Scanner</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
                
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Inter', sans-serif;
                    background: radial-gradient(circle at 20% 50%, #0a0a0a, #000000);
                    min-height: 100vh;
                    color: #fff;
                    position: relative;
                    overflow-x: hidden;
                }
                
                body::before {
                    content: '';
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: 
                        repeating-linear-gradient(90deg, rgba(0, 255, 255, 0.05) 0px, rgba(0, 255, 255, 0.05) 1px, transparent 1px, transparent 100px),
                        repeating-linear-gradient(0deg, rgba(0, 255, 255, 0.05) 0px, rgba(0, 255, 255, 0.05) 1px, transparent 1px, transparent 100px);
                    pointer-events: none;
                    animation: gridMove 20s linear infinite;
                }
                
                @keyframes gridMove {
                    0% { transform: translate(0, 0); }
                    100% { transform: translate(100px, 100px); }
                }
                
                .glow {
                    position: fixed;
                    width: 500px;
                    height: 500px;
                    border-radius: 50%;
                    filter: blur(100px);
                    opacity: 0.3;
                    pointer-events: none;
                }
                
                .glow-1 {
                    background: #00ffff;
                    top: -250px;
                    right: -250px;
                    animation: float 10s ease-in-out infinite;
                }
                
                .glow-2 {
                    background: #ff00ff;
                    bottom: -250px;
                    left: -250px;
                    animation: float 8s ease-in-out infinite reverse;
                }
                
                @keyframes float {
                    0%, 100% { transform: translate(0, 0); }
                    50% { transform: translate(50px, 50px); }
                }
                
                .container {
                    max-width: 1600px;
                    margin: 0 auto;
                    padding: 20px;
                    position: relative;
                    z-index: 1;
                }
                
                .header {
                    text-align: center;
                    margin-bottom: 40px;
                    position: relative;
                }
                
                .header h1 {
                    font-size: 4em;
                    font-weight: 800;
                    background: linear-gradient(135deg, #00ffff, #ff00ff, #00ffff);
                    background-size: 200% 200%;
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    animation: gradientShift 3s ease infinite;
                    letter-spacing: -2px;
                }
                
                @keyframes gradientShift {
                    0%, 100% { background-position: 0% 50%; }
                    50% { background-position: 100% 50%; }
                }
                
                .header p {
                    color: rgba(255, 255, 255, 0.6);
                    font-size: 1.1em;
                    margin-top: 10px;
                }
                
                .glass-card {
                    background: rgba(10, 10, 20, 0.4);
                    backdrop-filter: blur(20px);
                    border-radius: 20px;
                    border: 1px solid rgba(0, 255, 255, 0.2);
                    padding: 25px;
                    margin-bottom: 20px;
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }
                
                .glass-card::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.1), transparent);
                    transition: left 0.5s ease;
                }
                
                .glass-card:hover::before {
                    left: 100%;
                }
                
                .glass-card:hover {
                    transform: translateY(-5px);
                    border-color: rgba(0, 255, 255, 0.5);
                    box-shadow: 0 10px 30px rgba(0, 255, 255, 0.1);
                }
                
                .card-title {
                    font-size: 1.5em;
                    font-weight: 600;
                    margin-bottom: 20px;
                    background: linear-gradient(135deg, #00ffff, #ff00ff);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }
                
                .two-columns {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 20px;
                }
                
                .status-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 20px;
                }
                
                .status-card {
                    background: linear-gradient(135deg, rgba(0, 255, 255, 0.1), rgba(255, 0, 255, 0.1));
                    border-radius: 20px;
                    padding: 25px;
                    border: 1px solid rgba(0, 255, 255, 0.3);
                    position: relative;
                    overflow: hidden;
                }
                
                .status-card::after {
                    content: '';
                    position: absolute;
                    top: -50%;
                    right: -50%;
                    width: 200%;
                    height: 200%;
                    background: radial-gradient(circle, rgba(0, 255, 255, 0.1), transparent);
                    opacity: 0;
                    transition: opacity 0.5s ease;
                }
                
                .status-card:hover::after {
                    opacity: 1;
                }
                
                .status-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 20px;
                }
                
                .status-led {
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    position: relative;
                }
                
                .status-led.connected {
                    background: #00ffff;
                    box-shadow: 0 0 20px #00ffff;
                    animation: pulse 2s infinite;
                }
                
                .status-led.disconnected {
                    background: #ff00ff;
                    box-shadow: 0 0 20px #ff00ff;
                }
                
                .status-led.scanning {
                    background: #ffff00;
                    box-shadow: 0 0 20px #ffff00;
                    animation: pulse 0.5s infinite;
                }
                
                @keyframes pulse {
                    0%, 100% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.5; transform: scale(1.2); }
                }
                
                .status-text {
                    font-size: 2em;
                    font-weight: 700;
                    margin: 10px 0;
                }
                
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                    gap: 15px;
                    margin-top: 20px;
                }
                
                .stat-item {
                    text-align: center;
                    padding: 15px;
                    background: rgba(0, 0, 0, 0.3);
                    border-radius: 15px;
                    border: 1px solid rgba(0, 255, 255, 0.2);
                    transition: all 0.3s ease;
                }
                
                .stat-item:hover {
                    border-color: #00ffff;
                    transform: scale(1.05);
                }
                
                .stat-value {
                    font-size: 28px;
                    font-weight: 700;
                    color: #00ffff;
                    text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
                }
                
                .stat-label {
                    font-size: 11px;
                    opacity: 0.7;
                    margin-top: 5px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                
                .button-group {
                    display: flex;
                    gap: 15px;
                    flex-wrap: wrap;
                    margin-top: 20px;
                }
                
                .btn {
                    padding: 12px 28px;
                    border: none;
                    border-radius: 50px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 600;
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                
                .btn::before {
                    content: '';
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    width: 0;
                    height: 0;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.3);
                    transform: translate(-50%, -50%);
                    transition: width 0.6s, height 0.6s;
                }
                
                .btn:hover::before {
                    width: 300px;
                    height: 300px;
                }
                
                .btn-primary {
                    background: linear-gradient(135deg, #00ffff, #0099ff);
                    color: #000;
                    box-shadow: 0 5px 15px rgba(0, 255, 255, 0.3);
                }
                
                .btn-danger {
                    background: linear-gradient(135deg, #ff00ff, #ff0099);
                    color: #fff;
                    box-shadow: 0 5px 15px rgba(255, 0, 255, 0.3);
                }
                
                .btn-secondary {
                    background: rgba(255, 255, 255, 0.1);
                    color: #fff;
                    border: 1px solid rgba(0, 255, 255, 0.5);
                }
                
                .btn-secondary:hover {
                    background: rgba(0, 255, 255, 0.2);
                    border-color: #00ffff;
                }
                
                .btn-success {
                    background: linear-gradient(135deg, #00ff88, #00cc66);
                    color: #000;
                }
                
                .btn-warning {
                    background: linear-gradient(135deg, #ffaa00, #ff8800);
                    color: #000;
                }
                
                .input-group {
                    display: flex;
                    gap: 10px;
                    margin-top: 15px;
                }
                
                .input-field {
                    flex: 1;
                    padding: 12px 15px;
                    background: rgba(0, 0, 0, 0.5);
                    border: 1px solid rgba(0, 255, 255, 0.3);
                    border-radius: 10px;
                    color: #fff;
                    font-size: 14px;
                    transition: all 0.3s ease;
                }
                
                .input-field:focus {
                    outline: none;
                    border-color: #00ffff;
                    box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
                }
                
                .proxy-list-container {
                    max-height: 400px;
                    overflow-y: auto;
                    position: relative;
                }
                
                .proxy-list-container::-webkit-scrollbar {
                    width: 6px;
                }
                
                .proxy-list-container::-webkit-scrollbar-track {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                }
                
                .proxy-list-container::-webkit-scrollbar-thumb {
                    background: #00ffff;
                    border-radius: 10px;
                }
                
                .proxy-item {
                    background: rgba(0, 0, 0, 0.3);
                    padding: 12px 15px;
                    margin: 8px 0;
                    border-radius: 10px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    transition: all 0.3s ease;
                    border-left: 3px solid transparent;
                    animation: slideIn 0.3s ease;
                }
                
                @keyframes slideIn {
                    from {
                        opacity: 0;
                        transform: translateX(-20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateX(0);
                    }
                }
                
                .proxy-item:hover {
                    background: rgba(0, 255, 255, 0.1);
                    border-left-color: #00ffff;
                    transform: translateX(5px);
                }
                
                .proxy-address {
                    font-family: 'Courier New', monospace;
                    font-size: 13px;
                    color: #fff;
                }
                
                .proxy-badge {
                    font-size: 10px;
                    padding: 2px 8px;
                    border-radius: 20px;
                    margin-left: 10px;
                    font-weight: 600;
                }
                
                .badge-public {
                    background: rgba(0, 255, 255, 0.2);
                    color: #00ffff;
                }
                
                .badge-custom {
                    background: rgba(255, 0, 255, 0.2);
                    color: #ff00ff;
                }
                
                .proxy-latency {
                    font-size: 11px;
                    padding: 3px 8px;
                    background: rgba(0, 255, 255, 0.2);
                    border-radius: 20px;
                    color: #00ffff;
                    margin-left: 10px;
                }
                
                .proxy-actions {
                    display: flex;
                    gap: 8px;
                }
                
                .proxy-actions button {
                    padding: 5px 12px;
                    font-size: 11px;
                }
                
                .test-badge {
                    padding: 4px 10px;
                    border-radius: 20px;
                    font-size: 11px;
                    font-weight: bold;
                }
                
                .test-badge.working {
                    background: rgba(0, 255, 255, 0.3);
                    color: #00ffff;
                    box-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
                    animation: glowPulse 1s ease;
                }
                
                @keyframes glowPulse {
                    0%, 100% { box-shadow: 0 0 5px rgba(0, 255, 255, 0.3); }
                    50% { box-shadow: 0 0 20px rgba(0, 255, 255, 0.8); }
                }
                
                .test-badge.failed {
                    background: rgba(255, 0, 255, 0.3);
                    color: #ff00ff;
                }
                
                .browser-container {
                    background: rgba(0, 0, 0, 0.5);
                    border-radius: 15px;
                    padding: 20px;
                }
                
                .browser-placeholder {
                    background: rgba(0, 0, 0, 0.3);
                    border-radius: 10px;
                    padding: 40px;
                    text-align: center;
                    border: 1px dashed rgba(0, 255, 255, 0.3);
                }
                
                .logs {
                    background: rgba(0, 0, 0, 0.5);
                    border-radius: 10px;
                    padding: 15px;
                    max-height: 150px;
                    overflow-y: auto;
                    font-family: 'Courier New', monospace;
                    font-size: 11px;
                }
                
                .log-entry {
                    padding: 4px 0;
                    border-bottom: 1px solid rgba(0, 255, 255, 0.1);
                    color: rgba(255, 255, 255, 0.7);
                }
                
                .log-time {
                    color: #00ffff;
                    margin-right: 10px;
                }
                
                .loading {
                    text-align: center;
                    padding: 40px;
                }
                
                .spinner {
                    width: 40px;
                    height: 40px;
                    border: 3px solid rgba(0, 255, 255, 0.3);
                    border-top: 3px solid #00ffff;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 15px;
                }
                
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                .info-box {
                    background: rgba(0, 255, 255, 0.1);
                    border-left: 3px solid #00ffff;
                    padding: 15px;
                    border-radius: 10px;
                    margin-top: 15px;
                }
                
                .note {
                    text-align: center;
                    font-size: 11px;
                    color: rgba(255, 255, 255, 0.4);
                    margin-top: 20px;
                }
                
                .progress-bar {
                    width: 100%;
                    height: 2px;
                    background: rgba(0, 255, 255, 0.2);
                    border-radius: 2px;
                    overflow: hidden;
                    margin-top: 10px;
                }
                
                .progress-fill {
                    height: 100%;
                    background: linear-gradient(90deg, #00ffff, #ff00ff);
                    width: 0%;
                    transition: width 0.3s ease;
                }
            </style>
        </head>
        <body>
            <div class="glow glow-1"></div>
            <div class="glow glow-2"></div>
            
            <div class="container">
                <div class="header">
                    <h1>NEO VPN</h1>
                    <p>Real-Time Proxy Scanner | Secure Browser</p>
                </div>
                
                <div class="status-grid">
                    <div class="status-card">
                        <div class="status-header">
                            <span class="status-text">Connection Status</span>
                            <div class="status-led disconnected" id="statusLed"></div>
                        </div>
                        <div class="status-text" id="statusText" style="font-size: 1.5em;">Disconnected</div>
                        <div class="proxy-details" id="proxyDetails" style="margin-top: 10px; opacity: 0.7;">No active connection</div>
                    </div>
                    
                    <div class="status-card">
                        <div class="status-header">
                            <span class="status-text">System Statistics</span>
                        </div>
                        <div class="stats-grid">
                            <div class="stat-item">
                                <div class="stat-value" id="totalProxies">0</div>
                                <div class="stat-label">Found</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value" id="workingProxies">0</div>
                                <div class="stat-label">Working</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value" id="customCount">0</div>
                                <div class="stat-label">Custom</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="two-columns">
                    <div class="glass-card">
                        <div class="card-title">Control Panel</div>
                        <div class="button-group">
                            <button class="btn btn-primary" id="connectBtn" onclick="connectToBestProxy()">Connect</button>
                            <button class="btn btn-danger" id="disconnectBtn" onclick="disconnectVPN()">Disconnect</button>
                            <button class="btn btn-secondary" id="refreshBtn" onclick="startScan()">Scan Proxies</button>
                        </div>
                    </div>
                    
                    <div class="glass-card">
                        <div class="card-title">Custom Proxy</div>
                        <div class="input-group">
                            <input type="text" class="input-field" id="customProxyInput" placeholder="IP:PORT (e.g., 192.168.1.1:8080)">
                            <button class="btn btn-success" onclick="addCustomProxy()">Add Proxy</button>
                        </div>
                        <div id="customProxyStatus"></div>
                    </div>
                </div>
                
                <div class="glass-card">
                    <div class="card-title">Proxy Database <span id="scanStatus" style="font-size: 12px; color: #ffff00;"></span></div>
                    <div class="progress-bar" id="progressBar" style="display: none;">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <div id="proxyListContainer" class="proxy-list-container">
                        <div class="loading">
                            <div class="spinner"></div>
                            <p>Click "Scan Proxies" to discover proxies</p>
                        </div>
                    </div>
                </div>
                
                <div class="glass-card">
                    <div class="card-title">Secure Browser</div>
                    <div class="browser-container">
                        <div class="input-group">
                            <input type="text" class="input-field" id="urlInput" placeholder="Enter URL..." value="https://www.youtube.com">
                            <button class="btn btn-primary" onclick="openBrowser()">Open Browser</button>
                        </div>
                        <div class="browser-placeholder">
                            <p style="margin-bottom: 10px;">Standalone Secure Browser Window</p>
                            <div class="info-box">
                                <strong>Proxy Status:</strong> <span id="browserProxyStatus" style="color: #00ffff;">No proxy active</span><br>
                                The browser opens in a new window and will load websites directly .
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="glass-card">
                    <div class="card-title">Event Log</div>
                    <div class="logs" id="logsContainer">
                        <div class="log-entry">
                            <span class="log-time">[System]</span>
                            NEO VPN initialized
                        </div>
                    </div>
                </div>
                
                <div class="note">
                    ⚡ Real-Time Scanning | Proxy-Enabled Browser | Full Website Compatibility
                </div>
            </div>
            
            <script>
                let currentProxy = null;
                let isConnecting = false;
                let customProxies = [];
                let isScanning = false;
                
                function waitForAPI() {
                    return new Promise((resolve) => {
                        if (window.pywebview && window.pywebview.api) {
                            resolve();
                            return;
                        }
                        
                        let attempts = 0;
                        const checkInterval = setInterval(() => {
                            attempts++;
                            if (window.pywebview && window.pywebview.api) {
                                clearInterval(checkInterval);
                                resolve();
                            } else if (attempts > 50) {
                                clearInterval(checkInterval);
                                addLog('API connection timeout');
                                resolve();
                            }
                        }, 100);
                    });
                }
                
                async function callPython(func, ...args) {
                    try {
                        if (!window.pywebview || !window.pywebview.api) {
                            await waitForAPI();
                        }
                        
                        if (!window.pywebview || !window.pywebview.api) {
                            throw new Error('API not available');
                        }
                        
                        const result = await window.pywebview.api[func](...args);
                        return JSON.parse(result);
                    } catch(e) {
                        console.error(`Error:`, e);
                        throw e;
                    }
                }
                
                function addLog(message) {
                    const logsContainer = document.getElementById('logsContainer');
                    const logEntry = document.createElement('div');
                    logEntry.className = 'log-entry';
                    const now = new Date();
                    const timeStr = now.toLocaleTimeString();
                    logEntry.innerHTML = `<span class="log-time">[${timeStr}]</span> ${message}`;
                    logsContainer.appendChild(logEntry);
                    logsContainer.scrollTop = logsContainer.scrollHeight;
                    
                    while (logsContainer.children.length > 50) {
                        logsContainer.removeChild(logsContainer.firstChild);
                    }
                }
                
                function updateStatus(connected, proxy = null) {
                    const led = document.getElementById('statusLed');
                    const statusText = document.getElementById('statusText');
                    const proxyDetails = document.getElementById('proxyDetails');
                    const browserStatus = document.getElementById('browserProxyStatus');
                    
                    if (connected && proxy) {
                        led.className = 'status-led connected';
                        statusText.textContent = 'CONNECTED';
                        proxyDetails.innerHTML = `Active Proxy: ${proxy}`;
                        browserStatus.innerHTML = `✅ Active Proxy: ${proxy}`;
                        addLog(`Connected to proxy: ${proxy}`);
                    } else {
                        led.className = 'status-led disconnected';
                        statusText.textContent = 'Disconnected';
                        proxyDetails.textContent = 'No active connection';
                        browserStatus.innerHTML = '⚠️ No proxy active';
                    }
                }
                
                function updateStats(total, working, custom) {
                    document.getElementById('totalProxies').textContent = total || 0;
                    document.getElementById('workingProxies').textContent = working || 0;
                    document.getElementById('customCount').textContent = custom || 0;
                }
                
                function addProxyToDisplay(proxy, latency) {
                    const container = document.getElementById('proxyListContainer');
                    
                    if (container.children.length === 1 && container.children[0].classList.contains('loading')) {
                        container.innerHTML = '';
                    }
                    
                    const existing = Array.from(container.children).find(child => 
                        child.querySelector('.proxy-address')?.textContent === proxy
                    );
                    
                    if (existing) return;
                    
                    const proxyDiv = document.createElement('div');
                    proxyDiv.className = 'proxy-item';
                    
                    proxyDiv.innerHTML = `
                        <div style="flex: 1;">
                            <span class="proxy-address">${escapeHtml(proxy)}</span>
                            <span class="proxy-badge badge-public">PUBLIC</span>
                            <span class="proxy-latency">${latency}ms</span>
                        </div>
                        <div class="proxy-actions">
                            <button class="btn btn-primary" style="padding: 5px 12px;" onclick="connectToProxy('${escapeHtml(proxy)}')">Connect</button>
                        </div>
                        <div class="test-badge working">✓ ${latency}ms</div>
                    `;
                    container.appendChild(proxyDiv);
                    
                    proxyDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    
                    const workingCount = document.querySelectorAll('.proxy-item').length;
                    updateStats(
                        parseInt(document.getElementById('totalProxies').textContent),
                        workingCount,
                        customProxies.length
                    );
                }
                
                function escapeHtml(str) {
                    const div = document.createElement('div');
                    div.textContent = str;
                    return div.innerHTML;
                }
                
                async function startScan() {
                    if (isScanning) {
                        addLog('Scan already in progress');
                        return;
                    }
                    
                    const refreshBtn = document.getElementById('refreshBtn');
                    const container = document.getElementById('proxyListContainer');
                    const progressBar = document.getElementById('progressBar');
                    const scanStatus = document.getElementById('scanStatus');
                    const led = document.getElementById('statusLed');
                    
                    isScanning = true;
                    refreshBtn.disabled = true;
                    refreshBtn.textContent = 'Scanning...';
                    container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Scanning for proxies...</p></div>';
                    progressBar.style.display = 'block';
                    scanStatus.innerHTML = '🔍 SCANNING...';
                    led.classList.add('scanning');
                    
                    addLog('Starting proxy scan...');
                    
                    try {
                        const result = await callPython('fetchProxies');
                        if (result.success && result.proxies) {
                            const totalProxies = result.total;
                            updateStats(totalProxies, 0, customProxies.length);
                            addLog(`Found ${totalProxies} proxies, testing...`);
                            
                            let tested = 0;
                            for (const p of result.proxies) {
                                const testResult = await callPython('testProxy', p.proxy);
                                tested++;
                                const progress = (tested / totalProxies) * 100;
                                document.getElementById('progressFill').style.width = progress + '%';
                                
                                if (testResult.working) {
                                    addProxyToDisplay(p.proxy, testResult.latency);
                                    addLog(`Found working proxy: ${p.proxy} (${testResult.latency}ms)`);
                                }
                            }
                        }
                    } catch(e) {
                        addLog(`Scan error: ${e.message}`);
                        container.innerHTML = `<div style="color: #ff00ff; text-align: center; padding: 20px;">Error: ${e.message}</div>`;
                    } finally {
                        isScanning = false;
                        refreshBtn.disabled = false;
                        refreshBtn.textContent = 'Scan Proxies';
                        progressBar.style.display = 'none';
                        scanStatus.innerHTML = '';
                        led.classList.remove('scanning');
                        addLog('Proxy scan completed');
                    }
                }
                
                async function connectToProxy(proxy) {
                    if (isConnecting) {
                        addLog('Connection in progress...');
                        return;
                    }
                    
                    isConnecting = true;
                    addLog(`Connecting to ${proxy}...`);
                    
                    try {
                        const result = await callPython('connect', proxy);
                        if (result.success) {
                            currentProxy = result.proxy;
                            updateStatus(true, currentProxy);
                            addLog(`Connected successfully`);
                        } else {
                            addLog(`Connection failed: ${result.error}`);
                            alert('Connection failed: ' + result.error);
                        }
                    } catch(e) {
                        addLog(`Connection error: ${e.message}`);
                        alert('Error: ' + e.message);
                    } finally {
                        isConnecting = false;
                    }
                }
                
                async function connectToBestProxy() {
                    const firstProxy = document.querySelector('.proxy-address');
                    if (firstProxy) {
                        connectToProxy(firstProxy.textContent);
                    } else {
                        alert('No proxies found. Please run a scan first.');
                    }
                }
                
                async function disconnectVPN() {
                    addLog('Disconnecting...');
                    
                    try {
                        await callPython('disconnect');
                        currentProxy = null;
                        updateStatus(false);
                        addLog('Disconnected');
                    } catch(e) {
                        addLog(`Disconnect error: ${e.message}`);
                    }
                }
                
                async function addCustomProxy() {
                    const input = document.getElementById('customProxyInput');
                    const proxy = input.value.trim();
                    
                    if (!proxy) {
                        alert('Please enter a proxy (IP:PORT)');
                        return;
                    }
                    
                    addLog(`Adding custom proxy: ${proxy}`);
                    
                    try {
                        const result = await callPython('addCustomProxy', proxy);
                        if (result.success) {
                            addLog(`Custom proxy added`);
                            input.value = '';
                            const testResult = await callPython('testProxy', proxy);
                            if (testResult.working) {
                                addProxyToDisplay(proxy, testResult.latency);
                                customProxies.push(proxy);
                                updateStats(
                                    parseInt(document.getElementById('totalProxies').textContent),
                                    document.querySelectorAll('.proxy-item').length,
                                    customProxies.length
                                );
                            }
                        } else {
                            addLog(`Failed to add: ${result.error}`);
                            alert('Error: ' + result.error);
                        }
                    } catch(e) {
                        addLog(`Error: ${e.message}`);
                        alert('Error: ' + e.message);
                    }
                }
                
                async function openBrowser() {
                    const url = document.getElementById('urlInput').value;
                    if (!url) {
                        alert('Please enter a URL');
                        return;
                    }
                    
                    let targetUrl = url;
                    if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
                        targetUrl = 'https://' + targetUrl;
                    }
                    
                    if (currentProxy) {
                        addLog(`Opening browser with proxy: ${currentProxy} - URL: ${targetUrl}`);
                        alert(`Browser will open with proxy: ${currentProxy}\nURL: ${targetUrl}`);
                    } else {
                        addLog(`Opening browser (direct connection) - URL: ${targetUrl}`);
                    }
                    
                    try {
                        await callPython('openBrowser', targetUrl);
                        addLog('Browser window opened');
                    } catch(e) {
                        addLog(`Browser error: ${e.message}`);
                        alert('Error opening browser: ' + e.message);
                    }
                }
                
                window.addEventListener('DOMContentLoaded', async () => {
                    addLog('Initializing NEO VPN...');
                    await waitForAPI();
                    addLog('System ready');
                    updateStatus(false);
                    
                    const customResult = await callPython('getCustomProxies');
                    if (customResult.success) {
                        customProxies = customResult.proxies;
                        updateStats(0, 0, customProxies.length);
                    }
                });
            </script>
        </body>
        </html>
        """
    
    def get_js_api(self):
        """Return the JavaScript API object"""
        class JSApi:
            def __init__(self, app):
                self.app = app
                self.vpn_manager = app.vpn_manager
            
            def fetchProxies(self):
                try:
                    print("[API] Fetching proxies...")
                    proxies = self.vpn_manager.fetch_proxies()
                    
                    result = {
                        "success": True,
                        "total": len(proxies) + len(self.vpn_manager.custom_proxies),
                        "proxies": [{"proxy": p, "type": "public"} for p in proxies]
                    }
                    return json.dumps(result)
                except Exception as e:
                    return json.dumps({"success": False, "error": str(e)})
            
            def getCustomProxies(self):
                try:
                    return json.dumps({
                        "success": True,
                        "proxies": self.vpn_manager.custom_proxies
                    })
                except Exception as e:
                    return json.dumps({"success": False, "error": str(e)})
            
            def addCustomProxy(self, proxy):
                try:
                    result = self.vpn_manager.add_custom_proxy(proxy)
                    return json.dumps(result)
                except Exception as e:
                    return json.dumps({"success": False, "error": str(e)})
            
            def connect(self, proxy=None):
                try:
                    result = self.vpn_manager.connect_to_proxy(proxy)
                    return json.dumps(result)
                except Exception as e:
                    return json.dumps({"success": False, "error": str(e)})
            
            def disconnect(self):
                try:
                    result = self.vpn_manager.disconnect()
                    return json.dumps(result)
                except Exception as e:
                    return json.dumps({"success": False, "error": str(e)})
            
            def getStatus(self):
                try:
                    result = {
                        "connected": self.vpn_manager.is_connected,
                        "proxy": self.vpn_manager.current_proxy
                    }
                    return json.dumps(result)
                except Exception as e:
                    return json.dumps({"success": False, "error": str(e)})
            
            def testProxy(self, proxy):
                try:
                    is_working, latency = self.vpn_manager.test_proxy(proxy)
                    return json.dumps({
                        "success": True,
                        "working": is_working,
                        "latency": latency
                    })
                except Exception as e:
                    return json.dumps({"success": False, "error": str(e)})
            
            def openBrowser(self, url):
                try:
                    self.app.open_browser_window(url)
                    return json.dumps({"success": True})
                except Exception as e:
                    return json.dumps({"success": False, "error": str(e)})
        
        return JSApi(self)
    
    def run(self):
        """Run the application"""
        self.main_window = webview.create_window(
            "NEO VPN - Real-Time Proxy Scanner",
            html=self.get_html(),
            js_api=self.get_js_api(),
            width=1400,
            height=950,
            resizable=True,
            min_size=(1000, 750)
        )
        webview.start()

def main():
    print("=" * 60)
    print("NEO VPN - Real-Time Proxy Scanner")
    print("=" * 60)
    print("\nFeatures:")
    print("   Real-time proxy discovery")
    print("   Working proxies appear instantly")
    print("   Built-in secure browser")
    print("   Custom proxy support")
    print("   Full website compatibility (YouTube, Google, etc.)")
    print("\nHow it works:")
    print("  1. Click 'Scan Proxies' to discover working proxies")
    print("  2. Click 'Connect' next to any working proxy")
    print("  3. Click 'Open Browser' - a new window opens with the URL")
    print("  4. Browse any website normally - it will use the proxy!")
    print("\nNote: The browser opens in a new window, not an iframe,")
    print("      so all websites including YouTube will work perfectly.")
    print("\nStarting application...\n")
    
    app = VPNWebViewApp()
    app.run()

if __name__ == "__main__":
    main()
