#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple CLI tool for managing coupon preferences
"""

import sys
from coupon_preferences import CouponPreferencesManager

def main():
    """Main CLI interface."""
    manager = CouponPreferencesManager()
    
    while True:
        print("\n" + "="*60)
        print("Coupon Preferences Manager")
        print("="*60)
        print("1. List all preferences")
        print("2. Analyze a coupon")
        print("3. Add new preference category") 
        print("4. Remove preference category")
        print("5. Show preference statistics")
        print("6. Exit")
        print("="*60)
        
        try:
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == '1':
                list_preferences(manager)
            elif choice == '2':
                analyze_coupon(manager)
            elif choice == '3':
                add_preference(manager)
            elif choice == '4':
                remove_preference(manager)
            elif choice == '5':
                show_statistics(manager)
            elif choice == '6':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def list_preferences(manager):
    """List all current preferences."""
    preferences = manager.list_preferences()
    
    if not preferences:
        print("No preferences found.")
        return
    
    print(f"\nCurrent Preferences ({len(preferences)} categories):")
    print("-" * 60)
    
    for name, pref in preferences.items():
        print(f"\n📁 {name}")
        print(f"   Level: {pref.level}")
        print(f"   Keywords: {', '.join(pref.keywords)}")
        if pref.notes:
            print(f"   Notes: {pref.notes}")

def analyze_coupon(manager):
    """Analyze a specific coupon."""
    print("\nAnalyze Coupon")
    print("-" * 30)
    
    title = input("Enter coupon title: ").strip()
    if not title:
        print("Title is required.")
        return
    
    description = input("Enter description (optional): ").strip()
    store = input("Enter store name (optional): ").strip()
    
    level, category = manager.analyze_coupon(title, description, store)
    should_activate = manager.should_activate_coupon(title, description, store)
    
    print(f"\nAnalysis Results:")
    print(f"Title: {title}")
    print(f"Preference Level: {level}")
    print(f"Matched Category: {category}")
    print(f"Should Activate: {'Yes' if should_activate else 'No'}")
    
    # Ask if user wants to learn from this
    if level == 'medium' and category == 'default':
        learn = input("\nThis coupon matched no specific preferences. Would you like to set a preference for it? (y/n): ").strip().lower()
        if learn == 'y':
            new_level = get_preference_level()
            if new_level:
                manager.update_keyword_for_coupon(title, new_level)
                print(f"Added preference based on this coupon!")

def add_preference(manager):
    """Add a new preference category."""
    print("\nAdd New Preference Category")
    print("-" * 30)
    
    name = input("Enter category name: ").strip()
    if not name:
        print("Category name is required.")
        return
    
    keywords_str = input("Enter keywords (comma-separated): ").strip()
    if not keywords_str:
        print("Keywords are required.")
        return
    
    keywords = [k.strip() for k in keywords_str.split(',')]
    level = get_preference_level()
    if not level:
        return
    
    notes = input("Enter notes (optional): ").strip()
    
    manager.add_preference(name, keywords, level, notes)
    print(f"Added preference category: {name}")

def remove_preference(manager):
    """Remove a preference category."""
    preferences = manager.list_preferences()
    
    if not preferences:
        print("No preferences to remove.")
        return
    
    print("\nCurrent Categories:")
    for i, name in enumerate(preferences.keys(), 1):
        print(f"{i}. {name}")
    
    try:
        choice = int(input("\nEnter number to remove (0 to cancel): "))
        if choice == 0:
            return
        
        categories = list(preferences.keys())
        if 1 <= choice <= len(categories):
            category_name = categories[choice - 1]
            confirm = input(f"Are you sure you want to remove '{category_name}'? (y/n): ").strip().lower()
            if confirm == 'y':
                manager.remove_preference(category_name)
                print(f"Removed preference category: {category_name}")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Please enter a valid number.")

def get_preference_level():
    """Get preference level from user."""
    print("Select preference level:")
    print("1. High (always activate)")
    print("2. Medium (usually activate)")  
    print("3. Not at all (never activate)")
    
    try:
        choice = int(input("Enter choice (1-3): "))
        if choice == 1:
            return "high"
        elif choice == 2:
            return "medium"
        elif choice == 3:
            return "not_at_all"
        else:
            print("Invalid choice.")
            return None
    except ValueError:
        print("Please enter a valid number.")
        return None

def show_statistics(manager):
    """Show statistics about current preferences."""
    preferences = manager.list_preferences()
    
    if not preferences:
        print("No preferences found.")
        return
    
    stats = {"high": 0, "medium": 0, "not_at_all": 0}
    total_keywords = 0
    
    for pref in preferences.values():
        stats[pref.level] += 1
        total_keywords += len(pref.keywords)
    
    print(f"\nPreference Statistics:")
    print("-" * 30)
    print(f"Total categories: {len(preferences)}")
    print(f"Total keywords: {total_keywords}")
    print(f"High preference: {stats['high']} categories")
    print(f"Medium preference: {stats['medium']} categories")
    print(f"Not interested: {stats['not_at_all']} categories")

if __name__ == "__main__":
    main()