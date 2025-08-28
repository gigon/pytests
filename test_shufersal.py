import os
import sys
import datetime
import csv
import json
from seleniumbase import SB
from selenium_stealth import stealth
from seleniumbase import BaseCase

def safe_print(message):
    """Print message with Unicode handling for Windows console compatibility"""
    try:
        # First sanitize the message using safe_text
        safe_message = safe_text(str(message))
        print(safe_message)
    except UnicodeEncodeError:
        # If even the sanitized version fails, use ASCII replacement
        ascii_message = str(message).encode('ascii', 'replace').decode('ascii')
        print(ascii_message)
    except Exception as e:
        # Fallback for any other encoding issues
        print(f"[ENCODING ERROR] Could not display message: {type(e).__name__}")

def safe_text(text):
    """Keep original text intact - only used for data storage, not console output"""
    return text if text else text

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
        
        print("[ROBOT] SeleniumBase initialized with undetected-chrome mode")
    
    def perform_login(self):
        """
        Perform login with improved reliability and retry logic
        No cookie persistence - pure stealth approach
        """
        import random  # Import for human-like behaviors
        
        email = os.environ.get('SHUFERSAL_EMAIL')
        passwd = os.environ.get('SHUFERSAL_PSWD')
        if not email or not passwd:
            print('[FAIL] Missing SHUFERSAL_EMAIL or SHUFERSAL_PSWD in environment')
            return False

        print(f"[AUTH] Logging in with email: {email[:10]}...")
        
        for attempt in range(3):  # Retry up to 3 times
            try:
                if attempt > 0:
                    print(f"[RETRY] Login attempt {attempt + 1}/3")
                
                # Wait for login form
                if not self.wait_for_element_visible('#j_username', timeout=15):
                    print("[FAIL] Login form not found")
                    continue
                
                # Clear and fill form using JavaScript with human-like typing simulation
                self.execute_script("document.querySelector('#j_username').value = '';")
                self.execute_script("document.querySelector('#j_password').value = '';")
                
                # Escape credentials for JavaScript
                esc_email = email.replace('\'', "\\'").replace('"', '\\"')
                esc_pass = passwd.replace('\'', "\\'").replace('"', '\\"')
                
                # Add human-like typing delays
                print("[KEYBOARD] Simulating human-like typing...")
                
                # Type email with random delays between characters (occasionally)
                if random.random() < 0.4:  # 40% chance to use slow typing
                    email_field = self.find_element('#j_username')
                    for char in esc_email:
                        email_field.send_keys(char)
                        self.sleep(random.uniform(0.05, 0.15))  # Random typing speed
                    self.sleep(random.uniform(0.2, 0.5))  # Pause before password
                    
                    # Sometimes use backspace and retype (very human-like mistake simulation)
                    if random.random() < 0.1:  # 10% chance
                        print("[RETRY] Simulating typing mistake and correction...")
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
                    print("[WARN] Email corruption detected, retrying...")
                    continue
                
                # Submit form - target the specific login button
                try:
                    # Look for the submit button with the correct class
                    if self.is_element_present('#loginForm button[type="submit"].btn-login'):
                        print("Clicking login button (btn-login)...")
                        self.click('#loginForm button[type="submit"].btn-login')
                    elif self.is_element_present('#loginForm > button'):
                        print("Clicking login form button...")
                        self.click('#loginForm > button')
                    elif self.is_element_present('button[type="submit"]'):
                        print("Clicking submit button...")
                        self.click('button[type="submit"]')
                    else:
                        print("No button found, trying Enter key...")
                        self.send_keys('#j_password', '\n')
                except Exception as e:
                    print(f"[WARN] Error clicking login button: {e}")
                    # Fallback to Enter key
                    self.send_keys('#j_password', '\n')
                
                # Wait for navigation away from login
                login_successful = False
                for i in range(30):
                    self.sleep(1)
                    try:
                        current_url = self.get_current_url()
                        if 'login' not in current_url:
                            print(f"[OK] Login successful! Redirected to: {current_url}")
                            login_successful = True
                            break
                    except Exception:
                        continue
                
                if login_successful:
                    print("[OK] Login completed successfully - using pure stealth mode")
                    
                    # Handle intermediate pages (S page with coupons link)
                    try:
                        current_url = self.get_current_url()
                        if '/online/he/S' in current_url and self.is_element_present('#couponsLinkCart > div > div > img'):
                            print("[RETRY] Navigating from intermediate page to coupons...")
                            self.click('#couponsLinkCart > div > div > img')
                            self.sleep(1.0)
                    except Exception as e:
                        print(f"[WARN] Error handling post-login navigation: {e}")
                    
                    return True
                else:
                    print("[FAIL] Login timed out")
                    
            except Exception as e:
                print(f"[FAIL] Login attempt {attempt + 1} failed: {e}")
                if attempt < 2:  # Not the last attempt
                    self.sleep(2)  # Wait before retry
        
        print("[FAIL] All login attempts failed")
        return False
    
    def run_test(self):
        # SHUFF_ID no longer needed since login session system is now used
        activateCoupons = os.getenv("ACTIVATE", 'True').lower() in ('true', '1', 't')
        save = os.getenv("SAVE", 'True').lower() in ('true', '1', 't')
        maxRows = int(os.environ.get('MAX_ROWS', sys.maxsize))

        # Check if running in headless mode (for CI/CD compatibility)
        self.is_headless = '--headless' in sys.argv or self.driver.get_window_size().get('width', 0) == 0
        if self.is_headless:
            print("[SCREEN] Headless mode detected, human-like behaviors will be adapted")

        # NEW coupons URL
        url = "https://www.shufersal.co.il/online/he/coupons"
        print("activateCoupons=%s save=%s maxRows=%d url=%s" % (activateCoupons, save, maxRows, url))

        # Navigate directly to coupons page - let stealth handle the rest
        print(f"[WEB] Navigating to: {url}")
        self.open(url)
        self.sleep(2.0)
        
        current_url = self.get_current_url()
        print(f"[LOC] Current URL: {current_url}")
        
        # Always check for geo-blocking first, regardless of URL
        # Shufersal shows maintenance page even with correct URL when geo-blocked
        print("[GLOBE] Checking for geo-blocking or access restrictions...")
        try:
            body_html = self.get_attribute("body", "innerHTML")
            if body_html:
                # Check for specific Shufersal geo-blocking maintenance page
                # This page shows when accessing from outside Israel: <body><center><img src="maintenance image"></center></body>
                if "maintenance1.jpg" in body_html.lower() and body_html.count("<img") == 1:
                    print("[ALERT] SHUFERSAL GEO-BLOCKING DETECTED: Maintenance page shown (non-Israeli IP)")
                    print("   This indicates you're accessing from outside Israel")
                    print("   Shufersal blocks non-Israeli IPs with a maintenance page")
                    print("   Consider running from an Israeli IP or VPN")
                    print(f"   Page source length: {len(body_html)} characters")
                    return  # Exit early as geo-blocked
                    
                # Also check for the specific maintenance image URL
                if "s3-eu-west-1.amazonaws.com/www.shufersal.co.il/online/errorpage/Maintenance1.jpg" in body_html:
                    print("[ALERT] SHUFERSAL GEO-BLOCKING DETECTED: Maintenance image found")
                    print("   Detected specific geo-blocking maintenance page")
                    print(f"   Page source length: {len(body_html)} characters")
                    return  # Exit early as geo-blocked
                    
            # Check page text for other blocking indicators
            page_text = self.get_text("body").lower()
            blocked_indicators = [
                'access denied', 'not available', 'geo', 'location', 'country',
                'לא זמין', 'גישה נחסמה', 'מדינה', 'איזור'
            ]
            
            for indicator in blocked_indicators:
                if indicator in page_text:
                    print(f"[ALERT] Possible geo-blocking detected: '{indicator}' found in page")
                    
        except Exception as e:
            print(f"[WARN] Could not check for geo-blocking: {e}")
        
        # Check if login is required
        if self.is_element_present('#j_username') or 'login' in current_url:
            print("[AUTH] Login required")
            login_success = self.perform_login()
            if not login_success:
                print("[FAIL] Login failed, aborting")
                return
        elif 'coupons' in current_url:
            print("[OK] Already logged in, proceeding to coupons")
        else:
            print(f"[WARN] Unexpected page: {current_url}")
            # Try to navigate to coupons anyway
            self.open(url)
            self.sleep(2.0)

        # Add enhanced human-like behaviors to avoid bot detection
        import random
        
        print("[ROBOT] Applying human-like behaviors...")
        
        # Check if running in headless mode (for CI/CD compatibility)
        is_headless = self.is_headless
        if is_headless:
            print("[SCREEN] Headless mode detected, applying compatible behaviors only")
        
        # Random scroll behavior (simulate reading) - works in headless
        if random.random() < 0.4:  # 40% chance
            try:
                # Scroll to a random position to simulate reading
                scroll_position = random.randint(200, 800)
                self.execute_script(f"window.scrollTo(0, {scroll_position});")
                print(f"[SCROLL] Random scroll to position {scroll_position}")
                self.sleep(random.uniform(0.8, 2.0))
                
                # Scroll back up
                self.execute_script("window.scrollTo(0, 0);")
                self.sleep(random.uniform(0.3, 0.7))
            except Exception as e:
                print(f"[WARN] Could not perform scroll behavior: {e}")
        
        # Random mouse movement simulation - skip in headless mode
        if not is_headless and random.random() < 0.35:  # 35% chance
            try:
                # Move mouse to random elements to simulate user behavior
                from selenium.webdriver.common.action_chains import ActionChains
                action = ActionChains(self.driver)
                
                # Find some elements to hover over
                elements = self.find_elements("div, span, button")[:5]  # First 5 elements
                if elements:
                    target_element = random.choice(elements)
                    action.move_to_element(target_element).perform()
                    print("[MOUSE] Random mouse hover simulation")
                    self.sleep(random.uniform(0.2, 0.8))
            except Exception as e:
                print(f"[WARN] Could not perform mouse movement: {e}")
        
        # Randomly resize browser window - skip in headless mode  
        if not is_headless and random.random() < 0.35:  # 35% chance (increased from 30%)
            try:
                current_size = self.driver.get_window_size()
                # Vary window size slightly from current size
                width_variance = random.randint(-150, 200)
                height_variance = random.randint(-80, 120)
                new_width = max(1000, min(1600, current_size['width'] + width_variance))
                new_height = max(700, min(1200, current_size['height'] + height_variance))
                
                self.driver.set_window_size(new_width, new_height)
                print(f"[SCREEN] Randomly resized browser to {new_width}x{new_height}")
                self.sleep(random.uniform(0.5, 1.8))
                
                # Occasionally minimize and restore (very human-like) - skip in headless
                if random.random() < 0.15:  # 15% chance when resizing
                    try:
                        self.driver.minimize_window()
                        print("Minimized window")
                        self.sleep(random.uniform(0.5, 1.2))
                        self.driver.maximize_window()
                        print("Restored window")
                        self.sleep(random.uniform(0.3, 0.8))
                    except Exception:
                        pass  # Some drivers don't support minimize
                        
            except Exception as e:
                print(f"[WARN] Could not resize window: {e}")
        
        # Random page interaction delays - works in headless
        interaction_delay = random.uniform(1.2, 3.5)
        print(f"[TIME] Random interaction delay: {interaction_delay:.1f}s")
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
                    
                    # Sometimes move mouse to button first before clicking - skip in headless
                    if not self.is_headless and random.random() < 0.6:  # 60% chance
                        try:
                            disclaimer_element = self.find_element(disclaimer_button_selector)
                            from selenium.webdriver.common.action_chains import ActionChains
                            ActionChains(self.driver).move_to_element(disclaimer_element).perform()
                            self.sleep(random.uniform(0.2, 0.5))
                            print("[MOUSE] Moved mouse to disclaimer button")
                        except Exception:
                            pass
                    
                    self.click(disclaimer_button_selector)
                    post_click_delay = random.uniform(0.3, 0.9)
                    self.sleep(post_click_delay)
                    print("[OK] Disclaimer closed")
                else:
                    print("[INFO] No disclaimer message found")
            except Exception as e:
                # Handle Unicode encoding at the most basic level
                try:
                    safe_print("[WARN] Could not close disclaimer: " + str(e).encode('ascii', 'replace').decode('ascii'))
                except:
                    safe_print("[WARN] Could not close disclaimer: [Error details contain unsupported characters]")
        else:
            print("[DICE] Randomly chose not to close disclaimer (human-like behavior)")
        
        # Random additional browsing simulation
        if random.random() < 0.25:  # 25% chance
            try:
                # Simulate checking page elements (like reading)
                print("👀 Simulating reading behavior...")
                self.sleep(random.uniform(1.0, 2.5))
                
                # Random refresh occasionally (very human-like when things don't load properly)
                if random.random() < 0.1:  # 10% chance within this 25%
                    print("[RETRY] Random page refresh")
                    self.refresh_page()
                    self.sleep(random.uniform(2.0, 4.0))
            except Exception as e:
                # Completely avoid f-string interpolation to prevent Unicode encoding during string formation
                safe_print("[WARN] Could not perform reading simulation: " + str(e).encode('ascii', 'replace').decode('ascii'))

        # At this point we should be on the coupons page (or close) - apply filter to show only non-activated coupons
        try:
            print("[SEARCH] DEBUG: Analyzing page structure...")
            
            # Debug: Check page title and URL
            current_url = self.get_current_url()
            page_title = self.get_title()
            print(f"[PAGE] Page title: {page_title}")
            print(f"[WEB] Current URL: {current_url}")
            
            # Debug: Check if this is actually the coupons page
            if 'coupons' not in current_url:
                print(f"[WARN] WARNING: Not on coupons page! URL: {current_url}")
                
            # Debug: Check for common page elements
            print("[SEARCH] Checking for page elements...")
            body_text = self.get_text("body")[:500]  # First 500 chars
            print(f"[TEXT] Page body start: {body_text}")
            
            # Check for specific coupons page elements
            elements_to_check = [
                "h1", "h2", ".couponsCards", ".tileContainer", 
                "#couponsPage", ".disclaimerSection", "#mCSB_4_container"
            ]
            
            for selector in elements_to_check:
                is_present = self.is_element_present(selector)
                print(f"[SEARCH] Element '{selector}': {'[OK] Found' if is_present else '[FAIL] Not found'}")
                
            # Try to apply filter with detailed logging
            print("[TOOL] Attempting to apply coupon filter...")
            filter_button = '#mCSB_4_container > li > div > label > button'
            if self.is_element_present(filter_button):
                print(f"[OK] Found filter button: {filter_button}")
                self.click(filter_button)
                self.sleep(0.3)
                print("Clicked filter button")
            else:
                print(f"[FAIL] Filter button not found: {filter_button}")
                
            result_button = '#mCSB_4_container > div > li.wrapperBtnShowResult.showInList > button'
            if self.is_element_present(result_button):
                print(f"[OK] Found result button: {result_button}")
                self.click(result_button)
                self.sleep(0.6)
                print("Clicked result button")
            else:
                print(f"[FAIL] Result button not found: {result_button}")
                
            filter_label = '#facet-results > div > ul > li:nth-child(1) > div > button > div > span:nth-child(1)'
            if not self.is_element_present(filter_label):
                print('[WARN] Warning: filter label not visible - filter may not have applied')
                
                # Debug: Try alternative filter selectors
                print("[SEARCH] Searching for alternative filter elements...")
                alternative_filters = [
                    "#mCSB_4_container", ".filterContainer", ".facet-results",
                    "[data-filter]", ".filter-button", ".coupon-filter"
                ]
                
                for alt_selector in alternative_filters:
                    if self.is_element_present(alt_selector):
                        print(f"[OK] Found alternative filter element: {alt_selector}")
                        # Get the element text for debugging
                        try:
                            element_text = self.get_text(alt_selector)[:200]
                            safe_print(f"[TEXT] Element text: {element_text}")
                        except:
                            print(f"[WARN] Could not get text for {alt_selector}")
                    else:
                        print(f"[FAIL] Alternative filter not found: {alt_selector}")
            else:
                print("[OK] Filter applied successfully")
                
        except Exception as e:
            # Completely avoid f-string interpolation to prevent Unicode encoding during string formation
            safe_print('[FAIL] Filter application failed: ' + str(e).encode('ascii', 'replace').decode('ascii'))
            # Continue anyway - maybe coupons are visible without filter

        # Collect coupon items using the correct new page structure
        rows = []
        # Updated selector based on actual HTML structure
        list_selector = '.couponsCards .tileContainer li'
        
        print(f"[SEARCH] DEBUG: Searching for coupons with selector: {list_selector}")
        
        ads = []
        try:
            ads = self.find_visible_elements(list_selector)
            print(f"[OK] Found {len(ads)} visible elements with find_visible_elements")
        except Exception as e:
            print(f"[WARN] find_visible_elements failed: {e}")
            # find_visible_elements may throw if selector not present
            try:
                ads = self.find_elements(list_selector)
                print(f"[OK] Found {len(ads)} elements with find_elements")
            except Exception as e:
                print(f'[FAIL] Failed to find coupon elements with selector "{list_selector}": {e}')
                
                # Try alternative selectors
                alternative_selectors = [
                    '.couponsCards li',
                    '.tileContainer li', 
                    'li[data-coupon]',
                    '.coupon-item',
                    '.coupon-card',
                    '[class*="coupon"]',
                    '[class*="tile"]',
                    '.grid-item',
                    'li'  # Very broad fallback
                ]
                
                print("[SEARCH] Trying alternative selectors...")
                for alt_selector in alternative_selectors:
                    try:
                        alt_ads = self.find_elements(alt_selector)
                        if len(alt_ads) > 0:
                            print(f"[OK] Alternative selector '{alt_selector}' found {len(alt_ads)} elements")
                            # Take a sample to see if they look like coupons
                            if len(alt_ads) > 0:
                                sample_text = alt_ads[0].text[:100] if hasattr(alt_ads[0], 'text') else "No text"
                                print(f"[TEXT] Sample element text: {sample_text}")
                                if len(alt_ads) <= 200:  # Reasonable number for coupons
                                    ads = alt_ads
                                    list_selector = alt_selector
                                    print(f"[TARGET] Using alternative selector: {alt_selector}")
                                    break
                    except Exception:
                        continue

        print(f'[DATA] Found {len(ads)} coupon items with final selector: {list_selector}')
        
        # Debug: If still no coupons found, save page source for analysis
        if len(ads) == 0:
            print("[ALERT] NO COUPONS FOUND - Performing detailed analysis...")
            
            # Save page source for debugging
            try:
                page_source = self.get_page_source()
                debug_file = os.path.join('.', 'data', 'debug_page_source.html')
                os.makedirs(os.path.dirname(debug_file), exist_ok=True)
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                print(f"[SAVE] Saved page source to {debug_file} for analysis")
                
                # Look for any signs of coupons in the page source
                coupon_indicators = ['coupon', 'קופון', 'הפעל', 'הנחה', 'הטבה']
                for indicator in coupon_indicators:
                    if indicator in page_source:
                        print(f"[OK] Found '{indicator}' in page source")
                    else:
                        print(f"[FAIL] '{indicator}' not found in page source")
                        
                # Check page length
                print(f"[SIZE] Page source length: {len(page_source)} characters")
                
            except Exception as e:
                print(f"[WARN] Could not save page source: {e}")

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
                    description = safe_text(description_elem.text.strip())
                    
                    # Try to extract store/brand name (usually at the end after comma)
                    if ',' in description:
                        parts = description.split(',')
                        if len(parts) >= 2:
                            title = safe_text(parts[0].strip())
                            store = safe_text(parts[-1].strip())
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
                safe_print(f'Coupon {i+1}: {title} | {store} | {percent}')
                
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
                                    
                                    # Sometimes hover over button before clicking (very human-like) - skip in headless
                                    if not self.is_headless and random.random() < 0.7:  # 70% chance
                                        try:
                                            from selenium.webdriver.common.action_chains import ActionChains
                                            ActionChains(self.driver).move_to_element(activate_button).perform()
                                            self.sleep(random.uniform(0.2, 0.6))
                                            print(f"[MOUSE] Hovered over activation button for: {title}")
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
                                    safe_print(f'Activated coupon: {title}')
                                else:
                                    safe_print(f'Warning: Button found but text is: "{btn_text}" (not activation)')
                            else:
                                safe_print(f'Warning: Activation button not clickable for: {title}')
                        except Exception as e:
                            safe_print(f'Warning: Could not find activation button for: {title} - {e}')
                            
                    except Exception as e:
                        safe_print(f'Failed to activate coupon {i+1}: {e}')

                rows.append(row)
                
            except Exception as e:
                safe_print(f'Error processing coupon {i+1}: {e}')
                continue

        # Save results to CSV if requested
        if save and rows:
            try:
                timestamp = datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S')
                csv_file = os.path.join('.', 'data', f'{timestamp}.csv')
                os.makedirs(os.path.dirname(csv_file), exist_ok=True)
                
                # Write CSV using built-in csv module
                with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                    if rows:
                        fieldnames = rows[0].keys()
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(rows)
                
                print(f'Saved {len(rows)} coupons to {csv_file}')
            except Exception as e:
                print(f'Failed to save CSV: {e}')

        activated_count = sum(1 for row in rows if row.get('activated', False))
        print(f'Summary: Found {len(rows)} coupons, activated {activated_count}')


class Test_shufersal(BaseTestCase):
    def test_basic(self):
        self.run_test()
