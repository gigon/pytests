import os
from seleniumbase import SB

with SB(uc=True) as sb:
    email = os.environ.get('EMAIL')
    pswd = os.environ.get('PSWD')
    if email is None or pswd is None:
        print("USER or PSWD not provided in ENV")
        exit(1)
    print("email=%s" % email)

    sb.driver.uc_open_with_tab("https://www.yad2.co.il/personal/my-ads")
    sb.sleep(4)

    if sb.is_element_present("#email"):
        sb.type("#email", email)
        sb.type("#password", pswd)
        sb.click('span:contains("התחברות")')  # Use :contains() on any tag

    mail = sb.get_text_content("div[class*=profile-block_email]")
    print(mail) 
    assert(mail == email)

    sb.wait_for_element_present("div[class*=ad-details_detailsActions]", timeout=8)
    ads = sb.find_visible_elements("div[class*=ad-details_detailsActions]")
    num_ads = len(ads)
    print("found %s ads" % num_ads)
    for ad in range(num_ads):
        ind = 4 + ad             # for some reason every 2nd div is hidden
        selector = 'div[class*=general-layout_children__] > div:nth-child(%s) button[class*=ad-details_bump]' % (ind)
        print(selector)
        #breakpoint()
        if sb.is_element_present(selector):
            sb.highlight(selector)
            print("found button %s" % str(ad+1))
            sb.click(selector)

        selector = 'div[class*=general-layout_children__] > div:nth-child(%s) span[class*=details_counter]' % (ind)
        if sb.is_element_present(selector):
            sb.highlight(selector)
            timeUntilJump = sb.get_text(selector)
            print("ad %s timeUntilJump=%s" % (str(ad+1), timeUntilJump))
