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
        self.driver.uc_open_with_tab("https://nowsecure.nl/#relax")
        self.sleep(1.2)
        if not self.is_text_visible("OH YEAH, you passed!", "h1"):
            self.get_new_driver(undetectable=True)
            self.driver.uc_open_with_reconnect(
                "https://nowsecure.nl/#relax", reconnect_time=3
            )
            self.sleep(1.2)
        if not self.is_text_visible("OH YEAH, you passed!", "h1"):
            if self.is_element_visible('iframe[src*="challenge"]'):
                with self.frame_switch('iframe[src*="challenge"]'):
                    self.click("span.mark")
                    self.sleep(2)
        self.activate_demo_mode()
        self.assert_text("OH YEAH, you passed!", "h1", timeout=3)
        pass

class MyTests(BaseTestCase):
    def test_run(self):
        self.run_test()
                