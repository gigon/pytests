import os
import sys
import datetime
import pandas as pd
import json
from seleniumbase import SB
from selenium_stealth import stealth
from seleniumbase import BaseCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BaseCase.main(__name__, __file__)

class BaseTestCase(BaseCase):
    def setUp(self):
        super().setUp()
        stealth(self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    def setUp(self):
        super().setUp()
        # <<< Run custom setUp() code for tests AFTER the super().setUp() >>>

    def tearDown(self):
        self.save_teardown_screenshot()  # On failure or "--screenshot"
        if self.has_exception():
            # <<< Run custom code if the test failed. >>>
            pass
        else:
            # <<< Run custom code if the test passed. >>>
            pass
        # (Wrap unreliable tearDown() code in a try/except block.)
        # <<< Run custom tearDown() code BEFORE the super().tearDown() >>>
        super().tearDown()
    
    def run_test(self):
        clientId = os.environ.get('SHUFF_ID')
        if clientId is None :
            print("SHUFF_ID not provided in ENV")
            exit(1)

        activateCoupons = os.getenv("ACTIVATE", 'True').lower() in ('true', '1', 't')
        save = os.getenv("SAVE", 'True').lower() in ('true', '1', 't')
        maxRows = int(os.environ.get('MAX_ROWS', sys.maxsize))

        # NEW coupons URL
        url = "https://www.shufersal.co.il/online/he/coupons"
        print("clientId=%s activateCoupons=%s save=%s maxRows=%d url=%s" % (clientId, activateCoupons, save, maxRows, url))

        # cookie persistence filename per clientId
        cookie_file = os.path.join('.', 'downloaded_files', 'cookies_shufersal_%s.json' % clientId)
        os.makedirs(os.path.dirname(cookie_file), exist_ok=True)

        # If SHUFERSAL_PROFILE_DIR is set, start Chrome with that persistent profile (headful)
        profile_dir = os.environ.get('SHUFERSAL_PROFILE_DIR')
        if profile_dir:
            print('Starting Chrome with user-data-dir=', profile_dir)
            try:
                try:
                    self.driver.quit()
                except Exception:
                    pass

                opts = Options()
                opts.add_argument(f'--user-data-dir={profile_dir}')
                profile_name = os.environ.get('SHUFERSAL_PROFILE_NAME')
                if profile_name:
                    opts.add_argument(f'--profile-directory={profile_name}')
                # Reduce automation flags but run headful so manual CAPTCHA solve is possible
                opts.add_experimental_option('excludeSwitches', ['enable-automation'])
                opts.add_experimental_option('useAutomationExtension', False)
                opts.add_argument('--disable-blink-features=AutomationControlled')
                opts.add_argument('--start-maximized')

                driver = webdriver.Chrome(options=opts)
                # Attach the new driver to the test instance
                try:
                    self.driver = driver
                except Exception:
                    self._driver = driver
                    self.driver = driver

                # Re-apply stealth to the new driver instance
                try:
                    stealth(self.driver,
                        languages=["en-US", "en"],
                        vendor="Google Inc.",
                        platform="Win32",
                        webgl_vendor="Intel Inc.",
                        renderer="Intel Iris OpenGL Engine",
                        fix_hairline=True,
                    )
                except Exception as e:
                    print('Warning: stealth() failed on persistent driver:', e)

                self.sleep(1.0)
            except Exception as e:
                print('Failed to start Chrome with profile:', e)

        # Try to reuse cookies if available (must be on same domain first)
        try:
            self.open('https://www.shufersal.co.il')
            self.sleep(1.0)
            if os.path.exists(cookie_file):
                try:
                    with open(cookie_file, 'r', encoding='utf-8') as fh:
                        cookies = json.load(fh)
                    for c in cookies:
                        cookie = {k: v for k, v in c.items() if k in ('name', 'value', 'path', 'domain', 'secure', 'httpOnly', 'expiry')}
                        try:
                            self.driver.add_cookie(cookie)
                        except Exception as e:
                            print('Warning: could not add a cookie:', e)
                    print('Loaded cookies from', cookie_file)
                except Exception as e:
                    print('Failed to load cookies:', e)
        except Exception as e:
            print('Warning opening base domain for cookies:', e)

        # Open coupons page (will redirect to login if no valid session)
        self.open(url)
        self.sleep(1.2)

        # Detect captcha early and abort to avoid bans
        try:
            if 'captcha' in self.get_page_source().lower():
                raise Exception('CAPTCHA detected on page - aborting automation')
        except Exception as e:
            print(e)
            return

        # If redirected to login or login form present -> perform login
        try:
            current = self.get_current_url()
        except Exception:
            current = ''

        if self.is_element_present('#j_username') or 'login' in current:
            print('Login required - performing login flow')
            email = os.environ.get('SHUFERSAL_EMAIL')
            passwd = os.environ.get('SHUFERSAL_PSWD')
            if not email or not passwd:
                print('Missing SHUFERSAL_EMAIL or SHUFERSAL_PSWD in env - cannot login')
                return

            # Prefer normal typing; fall back to JS assignment if typing fails
            try:
                self.wait_for_element_visible('#j_username', timeout=10)
                self.type('#j_username', email)
                self.type('#j_password', passwd)
            except Exception:
                # JS fallback (escape single quotes)
                esc_email = email.replace('\'', "\\'")
                esc_pass = passwd.replace('\'', "\\'")
                js = "var e=document.querySelector('#j_username'); if(e) e.value='%s'; var p=document.querySelector('#j_password'); if(p) p.value='%s';" % (esc_email, esc_pass)
                try:
                    self.execute_script(js)
                except Exception as e:
                    print('Failed to set credentials via JS:', e)
                    return

            # Submit form - try clicking a submit button if present, else send Enter
            try:
                if self.is_element_present('button[type=submit]'):
                    self.click('button[type=submit]')
                else:
                    self.send_keys('#j_password', '\n')
            except Exception:
                # last resort JS submit
                try:
                    self.execute_script("var f=document.querySelector('form'); if(f) f.submit();")
                except Exception as e:
                    print('Failed to submit login form:', e)
                    return

            # wait for navigation away from login
            for i in range(30):
                self.sleep(1)
                try:
                    cur = self.get_current_url()
                except Exception:
                    cur = ''
                if 'login' not in cur:
                    print('Login appears successful, current url=', cur)
                    break
            else:
                print('Timed out waiting for login to complete')
                return

            # Save cookies after login for reuse
            try:
                cookies = self.driver.get_cookies()
                with open(cookie_file, 'w', encoding='utf-8') as fh:
                    json.dump(cookies, fh)
                print('Saved cookies to', cookie_file)
            except Exception as e:
                print('Could not save cookies:', e)

            # If landed on the intermediate S page, click the coupons icon to go to coupons page
            try:
                cur = self.get_current_url()
                if '/online/he/S' in cur and self.is_element_present('#couponsLinkCart > div > div > img'):
                    self.click('#couponsLinkCart > div > div > img')
                    self.sleep(1.0)
            except Exception as e:
                print('Error handling post-login landing page:', e)

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

        # Collect coupon items using new page structure, with fallback to old selector
        rows = []
        list_selector = '#couponsPage .couponsCards section ul li'
        if not self.is_element_present(list_selector):
            list_selector = 'ul.couponsList li'

        ads = []
        try:
            ads = self.find_visible_elements(list_selector)
        except Exception:
            # find_visible_elements may throw if selector not present
            try:
                ads = self.find_elements(list_selector)
            except Exception:
                ads = []

        num_ads = len(ads)
        numBtns = 0
        print('found %s ads' % num_ads)

        for ind in range(min(maxRows, num_ads)):
            row = {}
            tableItemSelector = list_selector + ':nth-child(%s)' % (ind+1)
            # Try several possible title/subtitle selectors to be robust
            title = ''
            for t in [' .title', ' .subtitleTitle', ' .couponTitle', ' h3', ' .name']:
                try:
                    if self.is_element_present(tableItemSelector + t):
                        title = self.get_text(tableItemSelector + t)
                        break
                except Exception:
                    continue
            subtitle = ''
            for s in [' .subtitle', ' p', ' .coupon-sub']:
                try:
                    if self.is_element_present(tableItemSelector + s):
                        subtitle = self.get_text(tableItemSelector + s)
                        break
                except Exception:
                    continue

            # Determine loaded/activated state using a few heuristics
            loaded = False
            try:
                if self.is_element_present(tableItemSelector + ' .successMessageNew .miniPlus'):
                    loaded = True
                if self.is_element_present(tableItemSelector + ' .activated'):
                    loaded = True
                if self.is_element_present(tableItemSelector + ' .btn.disabled'):
                    loaded = True
            except Exception:
                pass

            print("ad %s (%s): title=%s subtitle=%s" % (str(ind+1), str(loaded), title, subtitle))
            row['title'] = title.strip()
            row['subtitle'] = subtitle.strip()

            # Activate coupon if requested and not already loaded
            if activateCoupons and not loaded:
                btn_selectors = [
                    tableItemSelector + ' button.btn.js-enable-btn.miglog-btn-promo.miglog-btn-add',
                    tableItemSelector + ' .btn.js-enable-btn',
                    tableItemSelector + ' button.btn'
                ]
                clicked = False
                for b in btn_selectors:
                    try:
                        if self.is_element_present(b):
                            self.click(b)
                            numBtns += 1
                            clicked = True
                            self.sleep(0.6)
                            break
                    except Exception as e:
                        print('Click failed for selector', b, e)
                if not clicked:
                    print('No activation button found for item', ind+1)

            rows.append(row)

        print('Clicked %d buttons from %d ads' % (numBtns, num_ads))

        time_now = datetime.datetime.utcnow().strftime('%m_%d_%Y_%H_%M_%S')

        if save and num_ads>0:
            dirPath = "./data/"
            if not os.path.exists(dirPath):
                os.makedirs(dirPath)
            filePath = dirPath + time_now + ".csv"

            df = pd.DataFrame(rows)

            with open(filePath, 'w+', encoding='utf-8-sig') as csv_file:
                df.to_csv(csv_file, index=False, lineterminator='\n')
            print('Saved %s' % filePath)

            if maxRows == sys.maxsize:
                filePath = dirPath + 'current.csv'
                with open(filePath, 'w+', encoding='utf-8-sig') as csv_file:
                    df.to_csv(csv_file, index=False, lineterminator='\n')
                print('Saved also to %s' % filePath)
        pass

class MyTests(BaseTestCase):
    def test_run(self):
        self.run_test()
