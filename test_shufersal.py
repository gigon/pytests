import os
import sys
import datetime
import pandas as pd
from seleniumbase import SB
from selenium_stealth import stealth
from seleniumbase import BaseCase

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

        url = "https://www.shufersal.co.il/couponslp/?ClientID=%s" % clientId
        print("clientId=%s activateCoupons=%s save=%s maxRows=%d url=%s" % (clientId, activateCoupons, save, maxRows, url))

        self.driver.uc_open_with_tab(url)
        self.sleep(1.2)
        if not self.is_element_present('ul.couponsList'):
            print("OOPS... retry with undetectable")
            self.get_new_driver(undetectable=True)
            self.driver.uc_open_with_reconnect(url, reconnect_time=3)
            self.sleep(1.2)

        #self.set_window_size(800,1000)    
        rows = []

        tableItem = 'ul.couponsList li'
        ads = self.find_visible_elements(tableItem)
        num_ads = len(ads)
    
        numBtns = 0
        print("found %s ads" % num_ads)
        for ind in range(min(maxRows, num_ads)):
            row = {}

            tableItemSelector = tableItem + ':nth-child(%s)' % (ind+1)
            print(tableItemSelector)
            title = self.get_text(tableItemSelector +  ' .title')
            subtitle = self.get_text(tableItemSelector +  ' .subtitle')
            dateValid = self.get_text(tableItemSelector +  ' div.text')
            restrict = self.get_text(tableItemSelector +  ' div.bold')
            loaded = self.is_element_present(tableItemSelector +  ' .successMessageNew .miniPlus')
            print("ad %s (%s): title=%s subtitle=%s dateValid=%s restrict=%s" % (str(ind+1), str(loaded), title, subtitle, dateValid, restrict))

            row['title'] = title.strip()
            row['subtitle'] = subtitle.strip()
            row['dateValid'] = dateValid.strip()
            row['restrictions'] = restrict.strip()

            if activateCoupons and not loaded:
                self.click(tableItemSelector + ' .buttonCell')
                numBtns += 1
            
            rows.append(row)

        print("Clicked %d buttons from %d ads" % (numBtns, num_ads))

        time_now = datetime.datetime.utcnow().strftime('%m_%d_%Y_%H_%M_%S')

        if save and num_ads>0:
            dirPath = "./data/"
            if not os.path.exists(dirPath):
                os.makedirs(dirPath)
            filePath = dirPath + time_now + ".csv"

            df = pd.DataFrame(rows)
            # reverse column order of a dataframe
            # df = df[df.columns[::-1]]

            with open(filePath, 'w+', encoding='utf-8-sig') as csv_file:
                df.to_csv(csv_file, index=False, lineterminator='\n')
            print("Saved %s" % filePath)

            if maxRows == sys.maxsize:
                filePath = dirPath + "current.csv"
                with open(filePath, 'w+', encoding='utf-8-sig') as csv_file:
                    df.to_csv(csv_file, index=False, lineterminator='\n')
                print("Saved also to %s" % filePath)
        pass

class MyTests(BaseTestCase):
    def test_run(self):
        self.run_test()
                