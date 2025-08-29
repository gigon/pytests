#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the coupon preferences system
"""

import unittest
import os
import tempfile
import json
from coupon_preferences import CouponPreferencesManager, CouponPreference


class TestCouponPreferences(unittest.TestCase):
    """Test cases for coupon preferences functionality."""
    
    def setUp(self):
        """Set up test environment with temporary preferences file."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.manager = CouponPreferencesManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_default_preferences_created(self):
        """Test that default preferences are created."""
        preferences = self.manager.list_preferences()
        self.assertGreater(len(preferences), 0)
        
        # Check some expected default categories
        expected_categories = ["dairy_high", "alcohol_not_at_all", "cleaning_medium"]
        for category in expected_categories:
            self.assertIn(category, preferences)
    
    def test_analyze_dairy_coupon(self):
        """Test dairy product coupon analysis."""
        level, category = self.manager.analyze_coupon("ממגוון מעדן גבינה 88-103 גרם", store="דניאלה")
        self.assertEqual(level, "high")
        self.assertEqual(category, "dairy_high")
    
    def test_analyze_alcohol_coupon(self):
        """Test alcohol product coupon analysis."""
        level, category = self.manager.analyze_coupon("ממגוון בירה ויינשטפן 500 מל")
        self.assertEqual(level, "not_at_all")
        self.assertEqual(category, "alcohol_not_at_all")
    
    def test_should_activate_coupon(self):
        """Test coupon activation decisions."""
        # High preference should activate
        self.assertTrue(self.manager.should_activate_coupon("גבינה צהובה נעם"))
        
        # Not interested should not activate  
        self.assertFalse(self.manager.should_activate_coupon("בירה ויינשטפן"))
        
        # Medium preference should activate
        self.assertTrue(self.manager.should_activate_coupon("סבון ידיים נוזלי"))
    
    def test_add_and_remove_preference(self):
        """Test adding and removing custom preferences."""
        # Add a custom preference
        self.manager.add_preference(
            "fruits_high",
            ["תפוח", "בננה", "תפוז"],
            "high",
            "Fruits - healthy choice"
        )
        
        preferences = self.manager.list_preferences()
        self.assertIn("fruits_high", preferences)
        self.assertEqual(preferences["fruits_high"].level, "high")
        
        # Remove the preference
        success = self.manager.remove_preference("fruits_high")
        self.assertTrue(success)
        
        preferences = self.manager.list_preferences()
        self.assertNotIn("fruits_high", preferences)
    
    def test_persistence(self):
        """Test that preferences are saved and loaded correctly."""
        # Add a custom preference
        self.manager.add_preference("test_category", ["test_keyword"], "medium")
        
        # Create a new manager with the same file
        new_manager = CouponPreferencesManager(self.temp_file.name)
        preferences = new_manager.list_preferences()
        
        self.assertIn("test_category", preferences)
        self.assertEqual(preferences["test_category"].level, "medium")
    
    def test_unknown_coupon_defaults_to_medium(self):
        """Test that unknown coupons default to medium preference."""
        level, category = self.manager.analyze_coupon("unknown product xyz")
        self.assertEqual(level, "medium")
        self.assertEqual(category, "default")


# Sample data for testing with real coupon data
SAMPLE_COUPONS = [
    {"title": "ממגוון מעדן גבינה 88-103 גרם", "store": "דניאלה", "expected_level": "high"},
    {"title": "ממגוון בירה ויינשטפן 500 מל", "store": "", "expected_level": "not_at_all"},
    {"title": "נייר טואלט לילי לבן מגה רול", "store": "", "expected_level": "medium"},
    {"title": "ממגוון לה קט 2.85 קג", "store": "לה קט", "expected_level": "not_at_all"},
    {"title": "מלווח מעדנות 700 גרם", "store": "", "expected_level": "high"},
]


class TestWithRealCouponData(unittest.TestCase):
    """Test preferences with real coupon data from the sample."""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.manager = CouponPreferencesManager(self.temp_file.name)
    
    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_real_coupon_classifications(self):
        """Test preferences with real coupon data."""
        for coupon in SAMPLE_COUPONS:
            with self.subTest(coupon=coupon["title"]):
                level, _ = self.manager.analyze_coupon(coupon["title"], store=coupon["store"])
                self.assertEqual(level, coupon["expected_level"], 
                               f"Failed for coupon: {coupon['title']}")
    
    def test_activation_decisions(self):
        """Test that activation decisions are correct."""
        high_and_medium_count = 0
        not_at_all_count = 0
        
        for coupon in SAMPLE_COUPONS:
            should_activate = self.manager.should_activate_coupon(coupon["title"], store=coupon["store"])
            level, _ = self.manager.analyze_coupon(coupon["title"], store=coupon["store"])
            
            if level == "not_at_all":
                self.assertFalse(should_activate, f"Should not activate: {coupon['title']}")
                not_at_all_count += 1
            else:
                self.assertTrue(should_activate, f"Should activate: {coupon['title']}")
                high_and_medium_count += 1
        
        # Verify we have a mix of activation decisions
        self.assertGreater(high_and_medium_count, 0)
        self.assertGreater(not_at_all_count, 0)


if __name__ == '__main__':
    unittest.main()