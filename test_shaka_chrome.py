import time
from seleniumbase import BaseCase
BaseCase.main(__name__, __file__)

class TestShakaBrowser(BaseCase):
    def test_shaka_support(self):
        self.open("https://shaka-player-demo.appspot.com/support.html")
        self.wait_for_element("#output")
        self.scroll_to_bottom()
        txt = self.get_text_content("#output")
        print(txt)
        assert('"com.widevine.alpha": {\n      "persistentState":' in txt)

    def test_playback(self):
        # clear asset
        #url = "https://harmonicinc-com.github.io/shaka-player/latest/demo/#audiolang=en-US;textlang=en-US;uilang=en-US;panel=HOME;build=debug_compiled"
        # asset encrypted with widevine
        url = "https://harmonicinc-com.github.io/shaka-player/latest/demo/#audiolang=en-US;textlang=en-US;uilang=en-US;panel=ALL_CONTENT;panelData=source:SHAKA,drm:WIDEVINE,MP4,DASH,VOD;build=debug_compiled"
        self.open(url)

        self.wait_for_element('//button[text()="Play"]', by='xpath')
        self.click('//button[text()="Play"]', by='xpath')

        videoEl = self.wait_for_element("video#video",timeout=4)

        readyState = videoEl.get_attribute("readyState")
        #self.assert_equal(readyState, "0", msg=None)

        self.wait_for_attribute("video#video", "readyState", "4", timeout=4)

        src = videoEl.get_attribute("src")
        self.console_log_string("playing src: " + src)

        secondsToPlay = 2
        time.sleep(secondsToPlay + 1)

        currentTime = int(float(self.get_attribute("video#video", "currentTime")))
        self.assertTrue(currentTime >= secondsToPlay, msg=None)
