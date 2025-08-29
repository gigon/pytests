# Coupon Preferences System

This system adds intelligent coupon filtering to the Shufersal coupon scraper based on user preferences.

## Features

- **Preference Levels**: Grade coupons as `high`, `medium`, or `not_at_all`
- **Smart Activation**: Only activate coupons based on your preferences
- **Keyword Matching**: Uses Hebrew keywords to classify products automatically
- **Learning System**: Can learn from user feedback to improve classifications
- **Statistics**: Shows preference distribution and activation decisions

## Quick Start

### 1. Basic Usage

The system works automatically with the existing coupon scraper. Preferences are enabled by default:

```bash
# Run with preferences (default)
python test_shufersal.py

# Run without preferences
USE_PREFERENCES=False python test_shufersal.py
```

### 2. Manage Preferences

Use the interactive CLI tool:

```bash
python manage_preferences.py
```

Or use the command-line interface:

```bash
# List all preferences
python coupon_preferences.py list

# Analyze a specific coupon
python coupon_preferences.py analyze --title "ממגוון מעדן גבינה 88-103 גרם" --store "דניאלה"

# Add a new preference category
python coupon_preferences.py add --name "vegetables_high" --keywords "ירקות,עגבניות,מלפפון" --level "high" --notes "Fresh vegetables"

# Remove a preference category
python coupon_preferences.py remove --name "vegetables_high"
```

## Default Preferences

The system comes with sensible defaults:

- **High Priority**: Dairy products (חלב, גבינה, יוגורט), Bread (לחם, מלווח)
- **Medium Priority**: Cleaning products (סבון, מדיח), Snacks (עוגיות, שוקולד)
- **Not Interested**: Alcohol (בירה, יין), Pet food (בונזו, לה קט), Baby products (תינוק, חיתול)

## How It Works

1. **Classification**: Each coupon is analyzed against your keyword preferences
2. **Decision**: Based on the preference level, the system decides whether to activate the coupon
3. **Tracking**: All decisions are logged in the CSV output with preference information
4. **Learning**: You can train the system by providing feedback on specific coupons

## CSV Output

The enhanced CSV includes these new columns:

- `preference_level`: high, medium, not_at_all
- `preference_category`: which preference category matched
- `activated`: whether the coupon was activated (respects preferences)

## Files

- `coupon_preferences.py`: Core preferences management system
- `coupon_preferences.json`: Your personal preferences (auto-created)
- `manage_preferences.py`: Interactive CLI for managing preferences
- `test_shufersal.py`: Enhanced main scraper with preferences integration

## Environment Variables

- `USE_PREFERENCES`: Enable/disable preferences (default: True)
- `ACTIVATE`: Enable/disable coupon activation (default: True)
- `SAVE`: Enable/disable saving to CSV (default: True)

## Testing

Run the test suite:

```bash
# Test preferences system
python -m pytest test_coupon_preferences.py -v

# Test integration
python -m pytest test_integration_preferences.py -v

# Test with sample data
python test_preferences_sample.py
```

## Examples

### Analyzing Sample Data

With the sample data, the system shows:
- 12.2% high preference coupons (always activate)
- 83.7% medium preference coupons (usually activate)
- 4.1% not interested coupons (never activate)

This means 95.9% of coupons would be activated vs. 100% without preferences.

### Adding Custom Preferences

```python
from coupon_preferences import CouponPreferencesManager

manager = CouponPreferencesManager()

# Add preference for healthy foods
manager.add_preference(
    "healthy_high",
    ["אורגני", "טבעי", "בריאות", "דל שומן"],
    "high",
    "Healthy and organic products"
)

# Add preference to ignore expensive electronics
manager.add_preference(
    "electronics_not_at_all", 
    ["טלוויזיה", "מחשב", "סמארטפון"],
    "not_at_all",
    "Electronics - too expensive"
)
```

## Future Enhancements

- Web UI for preference management
- AI-based preference recommendations
- Integration with purchase history
- Weekly coupon summaries
- Advanced product categorization