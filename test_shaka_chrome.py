from seleniumbase import BaseCase
BaseCase.main(__name__, __file__)

class TestShakaBrowser(BaseCase):
    def test_shaka_support(self):
        self.open("https://shaka-player-demo.appspot.com/support.html")
        self.wait_for_element("#output")
        self.scroll_to_bottom()
        txt = self.get_text_content("#output")
        print(txt)
        assert('"com.widevine.alpha": {\n      "persistentState": true' in txt)
