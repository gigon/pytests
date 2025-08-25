import os
import sys
import datetime
import pandas as pd
import json
from seleniumbase import SB
from selenium_stealth import stealth
from seleniumbase import BaseCase

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print('Loaded .env file')
except ImportError:
    print('python-dotenv not installed, using system environment variables only')

BaseCase.main(__name__, __file__)

class BaseTestCase(BaseCase):
    def setUp(self):
        super().setUp()
        
        # Apply stealth to the current driver for better bot protection
        # Note: --uc mode (undetected-chrome) is used via command line, this adds extra stealth
        stealth(self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        )
        
        print(f"🤖 SeleniumBase initialized with undetected-chrome mode")
    
    def load_saved_cookies(self, cookie_file, target_url):
        """
        Load saved cookies and validate if they provide a valid session
        Returns True if session is valid, False otherwise
        """
        try:
            print(f"🍪 Loading cookies from {cookie_file}")
            
            # Navigate to base domain first
            self.open('https://www.shufersal.co.il')
            self.sleep(1.0)
            
            # Load and add cookies
            with open(cookie_file, 'r', encoding='utf-8') as fh:
                cookies = json.load(fh)
            
            cookies_loaded = 0
            for c in cookies:
                cookie = {k: v for k, v in c.items() if k in ('name', 'value', 'path', 'domain', 'secure', 'httpOnly', 'expiry')}
                try:
                    self.driver.add_cookie(cookie)
                    cookies_loaded += 1
                except Exception as e:
                    # Skip invalid cookies (expired, wrong domain, etc.)
                    pass
            
            print(f"📥 Loaded {cookies_loaded} cookies")
            
            # Test session validity by navigating to target URL
            self.open(target_url)
            self.sleep(2.0)
            
            current_url = self.get_current_url()
            if 'login' not in current_url and 'coupons' in current_url:
                print("✅ Session restored successfully!")
                return True
            else:
                print("❌ Session invalid, login required")
                return False
                
        except Exception as e:
            print(f"⚠️ Failed to load cookies: {e}")
            return False
    
    def perform_login(self, cookie_file):
        """
        Perform login with improved reliability and retry logic
        """
        import random  # Import for human-like behaviors
        
        email = os.environ.get('SHUFERSAL_EMAIL')
        passwd = os.environ.get('SHUFERSAL_PSWD')
        if not email or not passwd:
            print('❌ Missing SHUFERSAL_EMAIL or SHUFERSAL_PSWD in environment')
            return False

        print(f"🔐 Logging in with email: {email[:10]}...")
        
        for attempt in range(3):  # Retry up to 3 times
            try:
                if attempt > 0:
                    print(f"🔄 Login attempt {attempt + 1}/3")
                
                # Wait for login form
                if not self.wait_for_element_visible('#j_username', timeout=15):
                    print("❌ Login form not found")
                    continue
                
                # Clear and fill form using JavaScript with human-like typing simulation
                self.execute_script("document.querySelector('#j_username').value = '';")
                self.execute_script("document.querySelector('#j_password').value = '';")
                
                # Escape credentials for JavaScript
                esc_email = email.replace('\'', "\\'").replace('"', '\\"')
                esc_pass = passwd.replace('\'', "\\'").replace('"', '\\"')
                
                # Add human-like typing delays
                print("⌨️ Simulating human-like typing...")
                
                # Type email with random delays between characters (occasionally)
                if random.random() < 0.4:  # 40% chance to use slow typing
                    email_field = self.find_element('#j_username')
                    for char in esc_email:
                        email_field.send_keys(char)
                        self.sleep(random.uniform(0.05, 0.15))  # Random typing speed
                    self.sleep(random.uniform(0.2, 0.5))  # Pause before password
                    
                    # Sometimes use backspace and retype (very human-like mistake simulation)
                    if random.random() < 0.1:  # 10% chance
                        print("🔄 Simulating typing mistake and correction...")
                        email_field.send_keys('\b\b')  # Delete last 2 chars
                        self.sleep(random.uniform(0.1, 0.3))
                        email_field.send_keys(esc_email[-2:])  # Retype them
                        self.sleep(random.uniform(0.2, 0.4))
                    
                    # Type password with random delays
                    password_field = self.find_element('#j_password')
                    for char in esc_pass:
                        password_field.send_keys(char)
                        self.sleep(random.uniform(0.03, 0.12))
                else:
                    # Fast JavaScript method for efficiency
                    self.execute_script(f"document.querySelector('#j_username').value = '{esc_email}';")
                    self.sleep(random.uniform(0.1, 0.3))
                    self.execute_script(f"document.querySelector('#j_password').value = '{esc_pass}';")
                
                # Random delay before verification (simulate user checking input)
                self.sleep(random.uniform(0.3, 0.8))
                
                # Verify email was set correctly (check for Hebrew corruption)
                set_email = self.execute_script("return document.querySelector('#j_username').value;")
                if '.' not in set_email:
                    print("⚠️ Email corruption detected, retrying...")
                    continue
                
                # Submit form - target the specific login button
                try:
                    # Look for the submit button with the correct class
                    if self.is_element_present('#loginForm button[type="submit"].btn-login'):
                        print("🔘 Clicking login button (btn-login)...")
                        self.click('#loginForm button[type="submit"].btn-login')
                    elif self.is_element_present('#loginForm > button'):
                        print("🔘 Clicking login form button...")
                        self.click('#loginForm > button')
                    elif self.is_element_present('button[type="submit"]'):
                        print("🔘 Clicking submit button...")
                        self.click('button[type="submit"]')
                    else:
                        print("🔘 No button found, trying Enter key...")
                        self.send_keys('#j_password', '\n')
                except Exception as e:
                    print(f"⚠️ Error clicking login button: {e}")
                    # Fallback to Enter key
                    self.send_keys('#j_password', '\n')
                
                # Wait for navigation away from login
                login_successful = False
                for i in range(30):
                    self.sleep(1)
                    try:
                        current_url = self.get_current_url()
                        if 'login' not in current_url:
                            print(f"✅ Login successful! Redirected to: {current_url}")
                            login_successful = True
                            break
                    except Exception:
                        continue
                
                if login_successful:
                    # Save cookies for future use
                    try:
                        cookies = self.driver.get_cookies()
                        with open(cookie_file, 'w', encoding='utf-8') as fh:
                            json.dump(cookies, fh)
                        print(f"💾 Saved {len(cookies)} cookies for future sessions")
                    except Exception as e:
                        print(f"⚠️ Could not save cookies: {e}")
                    
                    # Handle intermediate pages (S page with coupons link)
                    try:
                        current_url = self.get_current_url()
                        if '/online/he/S' in current_url and self.is_element_present('#couponsLinkCart > div > div > img'):
                            print("🔄 Navigating from intermediate page to coupons...")
                            self.click('#couponsLinkCart > div > div > img')
                            self.sleep(1.0)
                    except Exception as e:
                        print(f"⚠️ Error handling post-login navigation: {e}")
                    
                    return True
                else:
                    print("❌ Login timed out")
                    
            except Exception as e:
                print(f"❌ Login attempt {attempt + 1} failed: {e}")
                if attempt < 2:  # Not the last attempt
                    self.sleep(2)  # Wait before retry
        
        print("❌ All login attempts failed")
        return False
    
    def run_test(self):
        # SHUFF_ID no longer needed since login session system is now used
        activateCoupons = os.getenv("ACTIVATE", 'True').lower() in ('true', '1', 't')
        save = os.getenv("SAVE", 'True').lower() in ('true', '1', 't')
        maxRows = int(os.environ.get('MAX_ROWS', sys.maxsize))

        # NEW coupons URL
        url = "https://www.shufersal.co.il/online/he/coupons"
        print("activateCoupons=%s save=%s maxRows=%d url=%s" % (activateCoupons, save, maxRows, url))

        # Cookie persistence filename (using generic name since clientId not needed)
        cookie_file = os.path.join('.', 'downloaded_files', 'cookies_shufersal.json')
        os.makedirs(os.path.dirname(cookie_file), exist_ok=True)
        
        # Enhanced cookie loading with session validation
        session_restored = False
        if os.path.exists(cookie_file):
            session_restored = self.load_saved_cookies(cookie_file, url)
        
        if not session_restored:
            print("🔐 No valid session found, login required")
        else:
            print("✅ Session restored from cookies, testing...")

        # Test if session is working by navigating to coupons page
        print(f"🌐 Navigating to: {url}")
        self.open(url)
        self.sleep(2.0)
        
        current_url = self.get_current_url()
        print(f"📍 Current URL: {current_url}")
        
        # Check if login is required
        if self.is_element_present('#j_username') or 'login' in current_url:
            print("🔐 Login required")
            login_success = self.perform_login(cookie_file)
            if not login_success:
                print("❌ Login failed, aborting")
                return
        elif 'coupons' in current_url:
            print("✅ Already logged in, proceeding to coupons")
        else:
            print(f"⚠️ Unexpected page: {current_url}")
            # Try to navigate to coupons anyway
            self.open(url)
            self.sleep(2.0)

        # Add enhanced human-like behaviors to avoid bot detection
        import random
        
        print("🤖 Applying human-like behaviors...")
        
        # Random scroll behavior (simulate reading)
        if random.random() < 0.4:  # 40% chance
            try:
                # Scroll to a random position to simulate reading
                scroll_position = random.randint(200, 800)
                self.execute_script(f"window.scrollTo(0, {scroll_position});")
                print(f"📜 Random scroll to position {scroll_position}")
                self.sleep(random.uniform(0.8, 2.0))
                
                # Scroll back up
                self.execute_script("window.scrollTo(0, 0);")
                self.sleep(random.uniform(0.3, 0.7))
            except Exception as e:
                print(f"⚠️ Could not perform scroll behavior: {e}")
        
        # Random mouse movement simulation
        if random.random() < 0.35:  # 35% chance
            try:
                # Move mouse to random elements to simulate user behavior
                from selenium.webdriver.common.action_chains import ActionChains
                action = ActionChains(self.driver)
                
                # Find some elements to hover over
                elements = self.find_elements("div, span, button")[:5]  # First 5 elements
                if elements:
                    target_element = random.choice(elements)
                    action.move_to_element(target_element).perform()
                    print("🖱️ Random mouse hover simulation")
                    self.sleep(random.uniform(0.2, 0.8))
            except Exception as e:
                print(f"⚠️ Could not perform mouse movement: {e}")
        
        # Randomly resize browser window (enhanced)
        if random.random() < 0.35:  # 35% chance (increased from 30%)
            try:
                current_size = self.driver.get_window_size()
                # Vary window size slightly from current size
                width_variance = random.randint(-150, 200)
                height_variance = random.randint(-80, 120)
                new_width = max(1000, min(1600, current_size['width'] + width_variance))
                new_height = max(700, min(1200, current_size['height'] + height_variance))
                
                self.driver.set_window_size(new_width, new_height)
                print(f"🖥️ Randomly resized browser to {new_width}x{new_height}")
                self.sleep(random.uniform(0.5, 1.8))
                
                # Occasionally minimize and restore (very human-like)
                if random.random() < 0.15:  # 15% chance when resizing
                    try:
                        self.driver.minimize_window()
                        print("📉 Minimized window")
                        self.sleep(random.uniform(0.5, 1.2))
                        self.driver.maximize_window()
                        print("📈 Restored window")
                        self.sleep(random.uniform(0.3, 0.8))
                    except Exception:
                        pass  # Some drivers don't support minimize
                        
            except Exception as e:
                print(f"⚠️ Could not resize window: {e}")
        
        # Random page interaction delays
        interaction_delay = random.uniform(1.2, 3.5)
        print(f"⏱️ Random interaction delay: {interaction_delay:.1f}s")
        self.sleep(interaction_delay)
        
        # Random chance to close disclaimer message (enhanced - 3 out of 4 times = 75%)
        if random.random() < 0.75:  # 75% chance
            try:
                disclaimer_button_selector = "#couponsPage > div.disclaimerSection > button"
                if self.is_element_present(disclaimer_button_selector):
                    print("💬 Closing disclaimer message...")
                    # Variable delay before clicking (more human-like)
                    pre_click_delay = random.uniform(0.5, 1.2)
                    self.sleep(pre_click_delay)
                    
                    # Sometimes move mouse to button first before clicking
                    if random.random() < 0.6:  # 60% chance
                        try:
                            disclaimer_element = self.find_element(disclaimer_button_selector)
                            from selenium.webdriver.common.action_chains import ActionChains
                            ActionChains(self.driver).move_to_element(disclaimer_element).perform()
                            self.sleep(random.uniform(0.2, 0.5))
                            print("🖱️ Moved mouse to disclaimer button")
                        except Exception:
                            pass
                    
                    self.click(disclaimer_button_selector)
                    post_click_delay = random.uniform(0.3, 0.9)
                    self.sleep(post_click_delay)
                    print("✅ Disclaimer closed")
                else:
                    print("ℹ️ No disclaimer message found")
            except Exception as e:
                print(f"⚠️ Could not close disclaimer: {e}")
        else:
            print("🎲 Randomly chose not to close disclaimer (human-like behavior)")
        
        # Random additional browsing simulation
        if random.random() < 0.25:  # 25% chance
            try:
                # Simulate checking page elements (like reading)
                print("👀 Simulating reading behavior...")
                self.sleep(random.uniform(1.0, 2.5))
                
                # Random refresh occasionally (very human-like when things don't load properly)
                if random.random() < 0.1:  # 10% chance within this 25%
                    print("🔄 Random page refresh")
                    self.refresh_page()
                    self.sleep(random.uniform(2.0, 4.0))
            except Exception as e:
                print(f"⚠️ Could not perform reading simulation: {e}")

        # At this point we should be on the coupons page (or close) - apply filter to show only non-activated coupons
        try:
            if self.is_element_present('#mCSB_4_container > li > div > label > button'):
                self.click('#mCSB_4_container > li > div > label > button')
                self.sleep(0.3)
            if self.is_element_present('#mCSB_4_container > div > li.wrapperBtnShowResult.showInList > button'):
                self.click('#mCSB_4_container > div > li.wrapperBtnShowResult.showInList > button')
                self.sleep(0.6)
            if not self.is_element_present('#facet-results > div > ul > li:nth-child(1) > div > button > div > span:nth-child(1)'):
                print('Warning: filter label not visible - filter may not have applied')
        except Exception as e:
            print('Filter application failed:', e)

        # Collect coupon items using the correct new page structure
        rows = []
        # Updated selector based on actual HTML structure
        list_selector = '.couponsCards .tileContainer li'
        
        ads = []
        try:
            ads = self.find_visible_elements(list_selector)
        except Exception:
            # find_visible_elements may throw if selector not present
            try:
                ads = self.find_elements(list_selector)
            except Exception as e:
                print('Failed to find coupon elements with selector "%s": %s' % (list_selector, e))

        print('Found %d coupon items' % len(ads))

        for i, ad in enumerate(ads):
            if i >= maxRows:
                break
            try:
                # Extract coupon info from the actual page structure
                title = ''
                store = ''
                description = ''
                percent = ''
                
                # Extract title from the description span within the tile
                try:
                    # Look for the description within buyDescription comment tags
                    description_elem = ad.find_element("css selector", ".description")
                    description = description_elem.text.strip()
                    
                    # Try to extract store/brand name (usually at the end after comma)
                    if ',' in description:
                        parts = description.split(',')
                        if len(parts) >= 2:
                            title = parts[0].strip()
                            store = parts[-1].strip()
                        else:
                            title = description
                    else:
                        title = description
                except:
                    pass
                
                # Extract price/offer details
                try:
                    price_elem = ad.find_element("css selector", ".price .number")
                    percent = price_elem.text.strip()
                except:
                    pass
                
                # If still no title, try alternative methods
                if not title:
                    try:
                        # Try the hidden title div
                        title_elem = ad.find_element("css selector", ".title")
                        title = title_elem.text.strip()
                    except:
                        pass
                
                # Extract from alt text if needed
                if not title:
                    try:
                        img_elem = ad.find_element("css selector", ".imgContainer img.pic")
                        alt_text = img_elem.get_attribute('alt')
                        if alt_text and 'cleartext' in alt_text:
                            # Parse the cleartext content
                            import re
                            match = re.search(r'cleartext-->(.*?)<', alt_text)
                            if match:
                                content = match.group(1)
                                if '₪' in content:
                                    parts = content.split('₪')[0].strip()
                                    title = parts
                    except:
                        pass

                # If we couldn't extract structured data, fall back to all text
                if not title and not description:
                    try:
                        all_text = ad.text.strip()
                        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                        if lines:
                            title = lines[0]
                            if len(lines) > 1:
                                description = ' '.join(lines[1:])
                    except:
                        title = f'Coupon {i+1}'
                        description = 'Unable to extract details'

                row = {
                    'title': title,
                    'store': store,
                    'description': description,
                    'percent': percent,
                    'dateValid': '',  # Will be extracted from smallText grayBg
                    'restrictions': '',  # Will be extracted from smallText grayBg
                    'activated': False  # Will be set to True if activation succeeds
                }
                
                # Extract validity date and restrictions from the smallText section
                try:
                    small_text_elem = ad.find_element("css selector", ".smallText.grayBg")
                    small_text = small_text_elem.text.strip()
                    
                    # Split by the right and left sides
                    if small_text:
                        lines = small_text.split('\n')
                        for line in lines:
                            line = line.strip()
                            if 'תקף עד:' in line:  # "Valid until" in Hebrew
                                row['dateValid'] = line
                            elif 'מוגבל' in line:  # "Limited" in Hebrew
                                row['restrictions'] = line
                except Exception:
                    # If extraction fails, keep empty strings
                    pass
                
                # Debug: Print coupon details
                print(f'Coupon {i+1}: {title} | {store} | {percent}')
                
                if activateCoupons:
                    try:
                        # Look for the activation button - based on actual HTML structure
                        activated = False
                        
                        # Add human-like delay before attempting activation
                        activation_delay = random.uniform(0.3, 1.2)
                        self.sleep(activation_delay)
                        
                        # Primary selector: the activation button
                        try:
                            activate_button = ad.find_element("css selector", "button.miglog-btn-promo.miglog-btn-add")
                            if activate_button and activate_button.is_displayed() and activate_button.is_enabled():
                                # Check if it's actually an activation button (Hebrew text)
                                btn_text = activate_button.text.strip()
                                if 'הפעלה' in btn_text:  # "הפעלה" means "activation" in Hebrew
                                    
                                    # Human-like behavior: scroll to element with random offset
                                    scroll_offset = random.randint(-50, 50)
                                    self.driver.execute_script(
                                        f"arguments[0].scrollIntoView({{block: 'center'}}); window.scrollBy(0, {scroll_offset});", 
                                        activate_button
                                    )
                                    self.sleep(random.uniform(0.4, 0.8))
                                    
                                    # Sometimes hover over button before clicking (very human-like)
                                    if random.random() < 0.7:  # 70% chance
                                        try:
                                            from selenium.webdriver.common.action_chains import ActionChains
                                            ActionChains(self.driver).move_to_element(activate_button).perform()
                                            self.sleep(random.uniform(0.2, 0.6))
                                            print(f"🖱️ Hovered over activation button for: {title}")
                                        except Exception:
                                            pass  # Continue if hover fails
                                    
                                    # Random pre-click delay
                                    pre_click_delay = random.uniform(0.1, 0.5)
                                    self.sleep(pre_click_delay)
                                    
                                    activate_button.click()
                                    
                                    # Random post-click delay
                                    post_click_delay = random.uniform(0.4, 1.0)
                                    self.sleep(post_click_delay)
                                    
                                    row['activated'] = True
                                    activated = True
                                    print(f'✓ Activated coupon: {title}')
                                else:
                                    print(f'⚠ Button found but text is: "{btn_text}" (not activation)')
                            else:
                                print(f'⚠ Activation button not clickable for: {title}')
                        except Exception as e:
                            print(f'⚠ Could not find activation button for: {title} - {e}')
                            
                    except Exception as e:
                        print(f'Failed to activate coupon {i+1}: {e}')

                rows.append(row)
                
            except Exception as e:
                print(f'Error processing coupon {i+1}: {e}')
                continue

        # Save results to CSV if requested
        if save and rows:
            try:
                df = pd.DataFrame(rows)
                timestamp = datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S')
                csv_file = os.path.join('.', 'data', f'{timestamp}.csv')
                os.makedirs(os.path.dirname(csv_file), exist_ok=True)
                df.to_csv(csv_file, index=False, encoding='utf-8-sig')
                print(f'Saved {len(rows)} coupons to {csv_file}')
            except Exception as e:
                print(f'Failed to save CSV: {e}')

        activated_count = sum(1 for row in rows if row.get('activated', False))
        print(f'Summary: Found {len(rows)} coupons, activated {activated_count}')


class Test_shufersal(BaseTestCase):
    def test_basic(self):
        self.run_test()
