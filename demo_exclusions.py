#!/usr/bin/env python3
"""
Demo script to show how the enhanced scraping with exclusions would work
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'coupon_ui'))

def demo_exclusion_logic():
    """Demonstrate exclusion logic with sample coupons"""
    
    # Sample coupons data (simulating what would be scraped)
    sample_coupons = [
        {
            'title': 'מבצע על משקאות',
            'subtitle': 'קנה 3 שלם 2 על משקאות',
            'restrictions': 'על קוקה קולה ופפסי',
            'dateValid': 'עד 31/12/2024'
        },
        {
            'title': 'קנה 2 שלם 1 על שוקולד',
            'subtitle': 'מבצע מיוחד על שוקולדים',
            'restrictions': 'על מוצרי אליט ומילקה',
            'dateValid': 'עד 30/12/2024'
        },
        {
            'title': 'חסכון של 10% על פירות וירקות',
            'subtitle': 'חסכון על פירות וירקות טריים',
            'restrictions': 'מינימום קנייה 50 שח',
            'dateValid': 'עד 31/12/2024'
        }
    ]
    
    print("=== Enhanced Scraping with Exclusions Demo ===\n")
    
    # Load exclusion preferences
    try:
        from app import app, get_exclusion_keywords
        with app.app_context():
            exclusions = get_exclusion_keywords()
            print(f"Loaded exclusion preferences:")
            print(f"  Exclude keywords: {exclusions['exclude']}")
            print(f"  Emphasize keywords: {exclusions['emphasize']}\n")
    except ImportError:
        print("Warning: Could not load exclusion preferences\n")
        exclusions = {'exclude': [], 'emphasize': []}
    
    # Process each coupon
    activated_count = 0
    excluded_count = 0
    emphasized_count = 0
    
    for i, coupon in enumerate(sample_coupons, 1):
        title = coupon['title']
        subtitle = coupon['subtitle']
        restrictions = coupon['restrictions']
        
        # Check exclusion/emphasis
        text_to_check = f"{title} {subtitle} {restrictions}".lower()
        
        is_excluded = any(keyword.lower() in text_to_check for keyword in exclusions['exclude'])
        is_emphasized = any(keyword.lower() in text_to_check for keyword in exclusions['emphasize'])
        
        # Determine action
        if is_excluded:
            action = "SKIPPED (EXCLUDED)"
            excluded_count += 1
        elif is_emphasized:
            action = "ACTIVATED (EMPHASIZED)"
            activated_count += 1
        else:
            action = "ACTIVATED"
            activated_count += 1
        
        print(f"Coupon {i}: {title}")
        print(f"  Subtitle: {subtitle}")
        print(f"  Action: {action}")
        if is_excluded:
            print(f"  Reason: Contains excluded keyword")
        elif is_emphasized:
            print(f"  Reason: Contains emphasized keyword")
        print()
    
    print("=== Summary ===")
    print(f"Total coupons processed: {len(sample_coupons)}")
    print(f"Activated: {activated_count}")
    print(f"Excluded: {excluded_count}")
    print(f"Emphasized: {emphasized_count}")
    
    print(f"\n📋 This demonstrates how the enhanced scraping script would:")
    print(f"   ✅ Skip activation of coupons containing exclusion keywords")
    print(f"   ⭐ Prioritize coupons containing emphasis keywords")
    print(f"   💾 Save all coupon data to both CSV and database")
    print(f"   🔄 Maintain full backward compatibility")

if __name__ == "__main__":
    demo_exclusion_logic()