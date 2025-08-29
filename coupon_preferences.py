#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coupon Preferences Management System

This module provides functionality to manage user preferences for Shufersal coupons.
Users can grade products/coupons as: high, medium, not_at_all (ignore).
"""

import json
import os
import re
from typing import Dict, List, Literal, Optional
from dataclasses import dataclass

PreferenceLevel = Literal["high", "medium", "not_at_all"]

@dataclass
class CouponPreference:
    """Represents a user preference for a coupon category."""
    keywords: List[str]
    level: PreferenceLevel
    notes: str = ""

class CouponPreferencesManager:
    """Manages coupon preferences for filtering and activation decisions."""
    
    def __init__(self, preferences_file: str = "coupon_preferences.json"):
        self.preferences_file = preferences_file
        self.preferences: Dict[str, CouponPreference] = {}
        self.load_preferences()
    
    def load_preferences(self) -> None:
        """Load preferences from JSON file."""
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.preferences = {
                        name: CouponPreference(
                            keywords=pref["keywords"],
                            level=pref["level"],
                            notes=pref.get("notes", "")
                        )
                        for name, pref in data.items()
                    }
            except Exception as e:
                print(f"Error loading preferences: {e}")
                self._create_default_preferences()
        else:
            self._create_default_preferences()
    
    def save_preferences(self) -> None:
        """Save preferences to JSON file."""
        try:
            data = {
                name: {
                    "keywords": pref.keywords,
                    "level": pref.level,
                    "notes": pref.notes
                }
                for name, pref in self.preferences.items()
            }
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def _create_default_preferences(self) -> None:
        """Create default preferences based on common product categories."""
        defaults = {
            "dairy_high": CouponPreference(
                keywords=["חלב", "גבינה", "יוגורט", "חלב", "דניאלה", "יטבתה", "שטראוס", "תנובה"],
                level="high",
                notes="Dairy products - frequently used"
            ),
            "bread_high": CouponPreference(
                keywords=["לחם", "לחמניה", "בייגל", "פיתה", "מלווח"],
                level="high", 
                notes="Bread and bakery products"
            ),
            "cleaning_medium": CouponPreference(
                keywords=["ניקוי", "סבון", "אל סבון", "מדיח", "כביסה", "פיניש"],
                level="medium",
                notes="Cleaning products - occasional need"
            ),
            "snacks_medium": CouponPreference(
                keywords=["חטיף", "עוגיות", "ביסקוויט", "שוקולד", "גלידה"],
                level="medium",
                notes="Snacks and sweets"
            ),
            "alcohol_not_at_all": CouponPreference(
                keywords=["בירה", "יין", "וודקה", "וויסקי", "ליקר", "אלכוהול"],
                level="not_at_all",
                notes="Alcohol - not interested"
            ),
            "pet_food_not_at_all": CouponPreference(
                keywords=["מזון לכלבים", "מזון לחתולים", "בונזו", "לה קט", "חיות"],
                level="not_at_all",
                notes="Pet food - no pets"
            ),
            "baby_products_not_at_all": CouponPreference(
                keywords=["תינוק", "חיתול", "מזון תינוקות", "בייבי"],
                level="not_at_all",
                notes="Baby products - not needed"
            )
        }
        
        self.preferences = defaults
        self.save_preferences()
    
    def analyze_coupon(self, title: str, description: str = "", store: str = "") -> tuple[PreferenceLevel, str]:
        """
        Analyze a coupon and determine preference level.
        
        Returns:
            tuple: (preference_level, matched_category_name)
        """
        text_to_analyze = f"{title} {description} {store}".lower()
        
        # Check each preference category
        for category_name, preference in self.preferences.items():
            for keyword in preference.keywords:
                # Use case-insensitive matching
                if keyword.lower() in text_to_analyze:
                    return preference.level, category_name
        
        # Default to medium if no specific preference found
        return "medium", "default"
    
    def should_activate_coupon(self, title: str, description: str = "", store: str = "") -> bool:
        """
        Determine if a coupon should be activated based on preferences.
        
        Returns:
            bool: True if coupon should be activated
        """
        preference_level, _ = self.analyze_coupon(title, description, store)
        return preference_level != "not_at_all"
    
    def add_preference(self, name: str, keywords: List[str], level: PreferenceLevel, notes: str = "") -> None:
        """Add or update a preference category."""
        self.preferences[name] = CouponPreference(keywords, level, notes)
        self.save_preferences()
    
    def remove_preference(self, name: str) -> bool:
        """Remove a preference category."""
        if name in self.preferences:
            del self.preferences[name]
            self.save_preferences()
            return True
        return False
    
    def list_preferences(self) -> Dict[str, CouponPreference]:
        """Get all current preferences."""
        return self.preferences.copy()
    
    def update_keyword_for_coupon(self, coupon_title: str, new_level: PreferenceLevel) -> None:
        """
        Learn from user feedback - add keywords from a specific coupon title to preferences.
        """
        # Extract key words from the coupon title (simplified approach)
        words = re.findall(r'\b\w+\b', coupon_title.lower())
        # Filter out common words
        stop_words = {"ממגוון", "יח", "גרם", "ליטר", "מל", "ב", "עד", "מוגבל", "למימוש"}
        key_words = [w for w in words if len(w) > 2 and w not in stop_words]
        
        if key_words:
            category_name = f"learned_from_{coupon_title[:20]}"
            self.add_preference(
                category_name,
                key_words[:3],  # Take first 3 meaningful words
                new_level,
                f"Learned from user feedback on: {coupon_title}"
            )


def main():
    """CLI interface for managing coupon preferences."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage coupon preferences")
    parser.add_argument('action', choices=['list', 'add', 'remove', 'analyze'])
    parser.add_argument('--name', help='Preference category name')
    parser.add_argument('--keywords', help='Comma-separated keywords')
    parser.add_argument('--level', choices=['high', 'medium', 'not_at_all'])
    parser.add_argument('--notes', help='Optional notes')
    parser.add_argument('--title', help='Coupon title to analyze')
    parser.add_argument('--description', help='Coupon description')
    parser.add_argument('--store', help='Store name')
    
    args = parser.parse_args()
    
    manager = CouponPreferencesManager()
    
    if args.action == 'list':
        preferences = manager.list_preferences()
        for name, pref in preferences.items():
            print(f"\n{name}:")
            print(f"  Level: {pref.level}")
            print(f"  Keywords: {', '.join(pref.keywords)}")
            print(f"  Notes: {pref.notes}")
    
    elif args.action == 'add':
        if not all([args.name, args.keywords, args.level]):
            print("Error: --name, --keywords, and --level are required for add")
            return
        keywords = [k.strip() for k in args.keywords.split(',')]
        manager.add_preference(args.name, keywords, args.level, args.notes or "")
        print(f"Added preference: {args.name}")
    
    elif args.action == 'remove':
        if not args.name:
            print("Error: --name is required for remove")
            return
        if manager.remove_preference(args.name):
            print(f"Removed preference: {args.name}")
        else:
            print(f"Preference not found: {args.name}")
    
    elif args.action == 'analyze':
        if not args.title:
            print("Error: --title is required for analyze")
            return
        level, category = manager.analyze_coupon(
            args.title, args.description or "", args.store or ""
        )
        should_activate = manager.should_activate_coupon(
            args.title, args.description or "", args.store or ""
        )
        print(f"Title: {args.title}")
        print(f"Preference Level: {level}")
        print(f"Matched Category: {category}")
        print(f"Should Activate: {should_activate}")


if __name__ == "__main__":
    main()