#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test preferences integration with sample coupon data
"""

import csv
import os
from coupon_preferences import CouponPreferencesManager

def test_with_sample_data():
    """Test preferences with the sample CSV data."""
    sample_file = "sample/08_28_2025_23_32_02.csv"
    
    if not os.path.exists(sample_file):
        print(f"Sample file not found: {sample_file}")
        return
    
    # Initialize preferences manager
    manager = CouponPreferencesManager()
    
    # Load and analyze sample data
    high_count = 0
    medium_count = 0
    not_at_all_count = 0
    total_coupons = 0
    
    print("Analyzing sample coupon data with preferences...")
    print("=" * 80)
    
    with open(sample_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            total_coupons += 1
            title = row['title']
            store = row.get('store', '')
            description = row.get('description', '')
            was_activated = row.get('activated', 'False') == 'True'
            
            # Analyze with preferences
            level, category = manager.analyze_coupon(title, description, store)
            should_activate = manager.should_activate_coupon(title, description, store)
            
            # Count preference levels
            if level == "high":
                high_count += 1
            elif level == "medium":
                medium_count += 1
            elif level == "not_at_all":
                not_at_all_count += 1
            
            # Show examples
            if total_coupons <= 10:
                activation_status = "✓" if should_activate else "✗"
                print(f"{activation_status} [{level:12}] {title[:60]}...")
    
    print("=" * 80)
    print(f"Preference Analysis Results:")
    print(f"  Total coupons:        {total_coupons}")
    print(f"  High preference:      {high_count:3d} ({high_count/total_coupons*100:.1f}%)")
    print(f"  Medium preference:    {medium_count:3d} ({medium_count/total_coupons*100:.1f}%)")
    print(f"  Not interested:       {not_at_all_count:3d} ({not_at_all_count/total_coupons*100:.1f}%)")
    print(f"  Would activate:       {high_count + medium_count:3d} ({(high_count + medium_count)/total_coupons*100:.1f}%)")
    print(f"  Would skip:           {not_at_all_count:3d} ({not_at_all_count/total_coupons*100:.1f}%)")

if __name__ == "__main__":
    test_with_sample_data()