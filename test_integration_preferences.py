#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration test for the preferences system with the main coupon scraper
"""

import unittest
import tempfile
import os
import csv
from unittest.mock import Mock, patch
from coupon_preferences import CouponPreferencesManager


class TestIntegratedPreferences(unittest.TestCase):
    """Test the preferences integration with coupon processing."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_prefs_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_prefs_file.close()
        
        self.temp_csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.temp_csv_file.close()
        
        self.manager = CouponPreferencesManager(self.temp_prefs_file.name)
    
    def tearDown(self):
        """Clean up temporary files."""
        for file_path in [self.temp_prefs_file.name, self.temp_csv_file.name]:
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    def test_process_coupons_with_preferences(self):
        """Test processing a list of coupons with preferences applied."""
        # Sample coupon data (similar to what the scraper would find)
        sample_coupons = [
            {"title": "ממגוון מעדן גבינה 88-103 גרם", "store": "דניאלה", "description": "גבינה טעימה"},
            {"title": "ממגוון בירה ויינשטפן 500 מל", "store": "", "description": "בירה איכותית"},
            {"title": "נייר טואלט לילי לבן", "store": "", "description": "נייר רך"},
            {"title": "מזון לכלבים בונזו 3 קג", "store": "לה קט", "description": "מזון חיות"},
            {"title": "לחם פרוס", "store": "", "description": "לחם טרי"},
        ]
        
        processed_coupons = []
        activated_count = 0
        skipped_count = 0
        
        # Process each coupon with preferences
        for coupon_data in sample_coupons:
            # Analyze preferences
            level, category = self.manager.analyze_coupon(
                coupon_data["title"], 
                coupon_data["description"], 
                coupon_data["store"]
            )
            
            should_activate = self.manager.should_activate_coupon(
                coupon_data["title"], 
                coupon_data["description"], 
                coupon_data["store"]
            )
            
            # Simulate activation decision
            activated = should_activate  # In real system, this would depend on web scraping success
            
            if activated:
                activated_count += 1
            else:
                skipped_count += 1
            
            processed_coupon = {
                **coupon_data,
                "preference_level": level,
                "preference_category": category,
                "activated": activated
            }
            processed_coupons.append(processed_coupon)
        
        # Verify results
        self.assertEqual(len(processed_coupons), 5)
        
        # Check specific expectations
        dairy_coupon = next(c for c in processed_coupons if "גבינה" in c["title"])
        self.assertEqual(dairy_coupon["preference_level"], "high")
        self.assertTrue(dairy_coupon["activated"])
        
        beer_coupon = next(c for c in processed_coupons if "בירה" in c["title"])
        self.assertEqual(beer_coupon["preference_level"], "not_at_all")
        self.assertFalse(beer_coupon["activated"])
        
        pet_food_coupon = next(c for c in processed_coupons if "בונזו" in c["title"])
        self.assertEqual(pet_food_coupon["preference_level"], "not_at_all") 
        self.assertFalse(pet_food_coupon["activated"])
        
        # Verify activation statistics
        self.assertGreater(activated_count, 0)
        self.assertGreater(skipped_count, 0)
        self.assertEqual(activated_count + skipped_count, len(sample_coupons))
    
    def test_save_coupons_with_preferences_to_csv(self):
        """Test saving coupon data with preference information to CSV."""
        # Sample processed coupon data
        processed_coupons = [
            {
                "title": "ממגוון מעדן גבינה",
                "store": "דניאלה", 
                "description": "גבינה טעימה",
                "percent": "8 יח ב- 26₪",
                "dateValid": "תקף עד: 29/08/2025",
                "restrictions": "מוגבל למימוש אחד",
                "activated": True,
                "preference_level": "high",
                "preference_category": "dairy_high"
            },
            {
                "title": "ממגוון בירה ויינשטפן",
                "store": "",
                "description": "בירה איכותית", 
                "percent": "2 יח ב- 20₪",
                "dateValid": "תקף עד: 29/08/2025",
                "restrictions": "מוגבל ל 2 מימושים",
                "activated": False,
                "preference_level": "not_at_all",
                "preference_category": "alcohol_not_at_all"
            }
        ]
        
        # Save to CSV
        with open(self.temp_csv_file.name, 'w', newline='', encoding='utf-8-sig') as f:
            if processed_coupons:
                fieldnames = processed_coupons[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(processed_coupons)
        
        # Verify CSV was created and contains expected data
        self.assertTrue(os.path.exists(self.temp_csv_file.name))
        
        # Read back and verify
        with open(self.temp_csv_file.name, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            saved_coupons = list(reader)
        
        self.assertEqual(len(saved_coupons), 2)
        
        # Check first coupon (dairy - should be activated)
        dairy_coupon = saved_coupons[0]
        self.assertEqual(dairy_coupon["preference_level"], "high")
        self.assertEqual(dairy_coupon["activated"], "True")
        
        # Check second coupon (alcohol - should not be activated)
        alcohol_coupon = saved_coupons[1]
        self.assertEqual(alcohol_coupon["preference_level"], "not_at_all")
        self.assertEqual(alcohol_coupon["activated"], "False")
    
    def test_preference_statistics(self):
        """Test calculation of preference statistics."""
        sample_results = [
            {"preference_level": "high", "activated": True},
            {"preference_level": "high", "activated": True},
            {"preference_level": "medium", "activated": True},
            {"preference_level": "medium", "activated": True},
            {"preference_level": "medium", "activated": True},
            {"preference_level": "not_at_all", "activated": False},
            {"preference_level": "not_at_all", "activated": False},
        ]
        
        # Calculate statistics
        pref_stats = {}
        activated_count = 0
        skipped_count = 0
        
        for result in sample_results:
            level = result["preference_level"]
            pref_stats[level] = pref_stats.get(level, 0) + 1
            
            if result["activated"]:
                activated_count += 1
            else:
                skipped_count += 1
        
        # Verify statistics
        self.assertEqual(pref_stats["high"], 2)
        self.assertEqual(pref_stats["medium"], 3)
        self.assertEqual(pref_stats["not_at_all"], 2)
        self.assertEqual(activated_count, 5)
        self.assertEqual(skipped_count, 2)
        self.assertEqual(activated_count + skipped_count, len(sample_results))
    
    def test_environment_variable_controls(self):
        """Test that environment variables control preference usage."""
        # Test with preferences enabled (default)
        with patch.dict(os.environ, {"USE_PREFERENCES": "True"}):
            use_preferences = os.getenv("USE_PREFERENCES", 'True').lower() in ('true', '1', 't')
            self.assertTrue(use_preferences)
        
        # Test with preferences disabled
        with patch.dict(os.environ, {"USE_PREFERENCES": "False"}):
            use_preferences = os.getenv("USE_PREFERENCES", 'True').lower() in ('true', '1', 't')
            self.assertFalse(use_preferences)


if __name__ == '__main__':
    unittest.main()