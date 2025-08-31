#!/usr/bin/env python3
"""
Enhanced Shufersal automation script with coupon exclusion support
Integrates with Flask UI system for managing coupon preferences
"""

import os
import sys
import datetime
from seleniumbase import SB
import pandas as pd

# Add coupon_ui directory to path for database imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'coupon_ui'))

def get_exclusion_preferences():
    """Get exclusion preferences from the database"""
    try:
        from app import app, get_exclusion_keywords
        with app.app_context():
            return get_exclusion_keywords()
    except ImportError:
        print("Warning: Could not import Flask app. Running without exclusion preferences.")
        return {'exclude': [], 'emphasize': []}
    except Exception as e:
        print(f"Warning: Error loading exclusion preferences: {e}")
        return {'exclude': [], 'emphasize': []}

def should_exclude_coupon(title, subtitle, restrictions, exclusions):
    """Check if a coupon should be excluded based on keywords"""
    text_to_check = f"{title} {subtitle} {restrictions}".lower()
    
    # Check for exclusion keywords
    for keyword in exclusions['exclude']:
        if keyword.lower() in text_to_check:
            return True
    
    return False

def should_emphasize_coupon(title, subtitle, restrictions, exclusions):
    """Check if a coupon should be emphasized based on keywords"""
    text_to_check = f"{title} {subtitle} {restrictions}".lower()
    
    # Check for emphasis keywords
    for keyword in exclusions['emphasize']:
        if keyword.lower() in text_to_check:
            return True
    
    return False

def save_to_database(rows):
    """Save coupon data to the database"""
    try:
        from app import app, db, Coupon
        with app.app_context():
            saved_count = 0
            for row in rows:
                # Check if coupon already exists
                existing = Coupon.query.filter_by(
                    title=row['title'],
                    subtitle=row['subtitle']
                ).first()
                
                if not existing:
                    coupon = Coupon(
                        title=row['title'],
                        subtitle=row['subtitle'],
                        date_valid=row['dateValid'],
                        restrictions=row['restrictions'],
                        activated=row.get('activated', False),
                        is_excluded=row.get('is_excluded', False),
                        is_emphasized=row.get('is_emphasized', False)
                    )
                    db.session.add(coupon)
                    saved_count += 1
                else:
                    # Update activation status if coupon exists
                    existing.activated = row.get('activated', existing.activated)
            
            db.session.commit()
            print(f"Saved {saved_count} new coupons to database")
    except ImportError:
        print("Warning: Could not import Flask app. Coupons not saved to database.")
    except Exception as e:
        print(f"Warning: Error saving to database: {e}")

def main():
    """Main execution function"""
    with SB(uc=True) as sb:
        clientId = os.environ.get('SHUFF_ID')
        if clientId is None:
            print("SHUFF_ID not provided in ENV")
            exit(1)

        activateCoupons = os.getenv("ACTIVATE", 'True').lower() in ('true', '1', 't')
        save = os.getenv("SAVE", 'True').lower() in ('true', '1', 't')
        maxRows = int(os.environ.get('MAX_ROWS', sys.maxsize))
        useExclusions = os.getenv("USE_EXCLUSIONS", 'True').lower() in ('true', '1', 't')

        # Load exclusion preferences
        exclusions = get_exclusion_preferences() if useExclusions else {'exclude': [], 'emphasize': []}
        print(f"Loaded exclusion preferences: {len(exclusions['exclude'])} exclude keywords, {len(exclusions['emphasize'])} emphasize keywords")

        url = "https://www.shufersal.co.il/couponslp/?ClientID=%s" % clientId
        print("clientId=%s activateCoupons=%s save=%s maxRows=%d useExclusions=%s url=%s" % 
              (clientId, activateCoupons, save, maxRows, useExclusions, url))

        sb.driver.uc_open_with_tab(url)
        sb.sleep(1.2)
        if not sb.is_element_present('ul.couponsList'):
            print("OOPS... retry with undetectable")
            sb.get_new_driver(undetectable=True)
            sb.driver.uc_open_with_reconnect(url, reconnect_time=3)
            sb.sleep(1.2)

        rows = []

        tableItem = 'ul.couponsList li'
        ads = sb.find_visible_elements(tableItem)
        num_ads = len(ads)
       
        numBtns = 0
        numExcluded = 0
        numEmphasized = 0
        
        print("found %s ads" % num_ads)
        for ind in range(min(maxRows, num_ads)):
            row = {}

            tableItemSelector = tableItem + ':nth-child(%s)' % (ind+1)
            print(tableItemSelector)
            title = sb.get_text(tableItemSelector + ' .title')
            subtitle = sb.get_text(tableItemSelector + ' .subtitle')
            dateValid = sb.get_text(tableItemSelector + ' div.text')
            restrict = sb.get_text(tableItemSelector + ' div.bold')
            loaded = sb.is_element_present(tableItemSelector + ' .successMessageNew .miniPlus')

            # Check exclusion/emphasis status
            is_excluded = should_exclude_coupon(title, subtitle, restrict, exclusions)
            is_emphasized = should_emphasize_coupon(title, subtitle, restrict, exclusions)
            
            status_flags = []
            if is_excluded:
                status_flags.append("EXCLUDED")
                numExcluded += 1
            if is_emphasized:
                status_flags.append("EMPHASIZED")
                numEmphasized += 1
            if loaded:
                status_flags.append("ALREADY_ACTIVATED")
                
            status_str = f" [{', '.join(status_flags)}]" if status_flags else ""
            
            print("ad %s (%s): title=%s subtitle=%s dateValid=%s restrict=%s%s" % 
                  (str(ind+1), str(loaded), title, subtitle, dateValid, restrict, status_str))

            row['title'] = title.strip()
            row['subtitle'] = subtitle.strip()
            row['dateValid'] = dateValid.strip()
            row['restrictions'] = restrict.strip()
            row['is_excluded'] = is_excluded
            row['is_emphasized'] = is_emphasized
            row['activated'] = loaded

            # Only activate if not excluded and not already loaded
            if activateCoupons and not loaded and not is_excluded:
                sb.click(tableItemSelector + ' .buttonCell')
                numBtns += 1
                row['activated'] = True
                print(f"  -> Activated coupon: {title}")
            elif activateCoupons and is_excluded:
                print(f"  -> Skipped excluded coupon: {title}")
            
            rows.append(row)

        print("Clicked %d buttons from %d ads (%d excluded, %d emphasized)" % 
              (numBtns, num_ads, numExcluded, numEmphasized))

        time_now = datetime.datetime.utcnow().strftime('%m_%d_%Y_%H_%M_%S')

        # Save to database
        if useExclusions:
            save_to_database(rows)

        # Save to CSV (preserving original functionality)
        if save and num_ads > 0:
            dirPath = "./data/"
            if not os.path.exists(dirPath):
                os.makedirs(dirPath)
            filePath = dirPath + time_now + ".csv"

            df = pd.DataFrame(rows)
            
            with open(filePath, 'w+', encoding='utf-8-sig') as csv_file:
                df.to_csv(csv_file, index=False, lineterminator='\n')
            print("Saved %s" % filePath)

            if maxRows == sys.maxsize:
                filePath = dirPath + "current.csv"
                with open(filePath, 'w+', encoding='utf-8-sig') as csv_file:
                    df.to_csv(csv_file, index=False, lineterminator='\n')
                print("Saved also to %s" % filePath)

if __name__ == "__main__":
    main()