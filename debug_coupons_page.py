import os
from seleniumbase import BaseCase

class DebugCouponsPage(BaseCase):
    def test_debug_page_structure(self):
        # Load credentials
        email = os.environ.get('SHUFERSAL_EMAIL', 'gil.gonen@gmail.com')
        passwd = os.environ.get('SHUFERSAL_PSWD', 'Vy3%6pjQ')
        
        # Navigate to login and authenticate
        self.open('https://www.shufersal.co.il/online/he/coupons')
        self.sleep(2)
        
        # Login if required
        if self.is_element_present('#j_username'):
            self.type('#j_username', email)
            self.type('#j_password', passwd)
            self.click('#loginForm button[type="submit"].btn-login')
            self.sleep(3)
        
        # Save the page source for analysis
        page_source = self.get_page_source()
        
        # Save to file
        with open('./web_extracts/shufersal/coupons_page_current.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        
        print("✅ Page source saved to ./web_extracts/shufersal/coupons_page_current.html")
        
        # Try to find coupon elements with various selectors
        selectors_to_test = [
            '#couponsPage .couponsCards section ul li',
            'ul.couponsList li',
            '.coupon-card',
            '.coupon-item',
            '[data-testid*="coupon"]',
            '.card',
            'li[class*="coupon"]',
            'div[class*="coupon"]'
        ]
        
        for selector in selectors_to_test:
            try:
                elements = self.find_elements(selector)
                print(f"Selector '{selector}': Found {len(elements)} elements")
                if len(elements) > 0:
                    # Show first element's text and HTML
                    first_elem = elements[0]
                    print(f"  First element text: {first_elem.text[:100]}...")
                    print(f"  First element HTML: {first_elem.get_attribute('outerHTML')[:200]}...")
                    print()
            except Exception as e:
                print(f"Selector '{selector}': Error - {e}")
