import os
import sys
import datetime
from seleniumbase import SB
import pandas as pd

with SB(uc=True) as sb:
    clientId = os.environ.get('SHUFF_ID')
    if clientId is None :
        print("SHUFF_ID not provided in ENV")
        exit(1)

    activateCoupons = os.getenv("ACTIVATE", 'True').lower() in ('true', '1', 't')
    save = os.getenv("SAVE", 'True').lower() in ('true', '1', 't')
    maxRows = int(os.environ.get('MAX_ROWS', sys.maxsize))

    url = "https://www.shufersal.co.il/couponslp/?ClientID=%s" % clientId
    print("clientId=%s activateCoupons=%s save=%s maxRows=%d url=%s" % (clientId, activateCoupons, save, maxRows, url))

    sb.driver.uc_open_with_tab(url)
    sb.sleep(1.2)
    if not sb.is_element_present('ul.couponsList'):
        print("OOPS... retry with undetectable")
        sb.get_new_driver(undetectable=True)
        sb.driver.uc_open_with_reconnect(url, reconnect_time=3)
        sb.sleep(1.2)

    #sb.set_window_size(800,1000)    
    rows = []

    tableItem = 'ul.couponsList li'
    ads = sb.find_visible_elements(tableItem)
    num_ads = len(ads)
   
    numBtns = 0
    print("found %s ads" % num_ads)
    for ind in range(min(maxRows, num_ads)):
        row = {}

        tableItemSelector = tableItem + ':nth-child(%s)' % (ind+1)
        print(tableItemSelector)
        title = sb.get_text(tableItemSelector +  ' .title')
        subtitle = sb.get_text(tableItemSelector +  ' .subtitle')
        dateValid = sb.get_text(tableItemSelector +  ' div.text')
        restrict = sb.get_text(tableItemSelector +  ' div.bold')
        loaded = sb.is_element_present(tableItemSelector +  ' .successMessageNew .miniPlus')
        print("ad %s (%s): title=%s subtitle=%s dateValid=%s restrict=%s" % (str(ind+1), str(loaded), title, subtitle, dateValid, restrict))

        row['title'] = title.strip()
        row['subtitle'] = subtitle.strip()
        row['dateValid'] = dateValid.strip()
        row['restrictions'] = restrict.strip()

        if activateCoupons and not loaded:
            sb.click(tableItemSelector + ' .buttonCell')
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
