import os
from seleniumbase import SB

with SB(uc=True) as sb:
    clientId = os.environ.get('SHUFF_ID')
    if clientId is None :
        print("SHUFF_ID not provided in ENV")
        exit(1)
    print("clientId=%s" % clientId)

    sb.driver.uc_open_with_tab("https://www.shufersal.co.il/couponslp/?ClientID=%s" % clientId)
    sb.set_window_size(800,1000)
    
    tableItem = 'ul.couponsList li'
    ads = sb.find_visible_elements(tableItem)
    num_ads = len(ads)
    numBtns = 0
    print("found %s ads" % num_ads)
    for ind in range(num_ads):        
        tableItemSelector = tableItem + ':nth-child(%s)' % (ind+1)
        print(tableItemSelector)
        title = sb.get_text(tableItemSelector +  ' .title')
        subtitle = sb.get_text(tableItemSelector +  ' .subtitle')
        loaded = sb.is_element_present(tableItemSelector +  ' .successMessageNew .miniPlus')
        print("ad %s (%s): title=%s subtitle=%s" % (str(ind+1), str(loaded), title, subtitle))

        if not loaded:
            sb.click(tableItemSelector + ' .buttonCell')
            numBtns += 1

    print("Clicked %d buttons from %d ads" % (numBtns, num_ads))
