# Shufersal Coupon UI System

This Flask web application provides a user interface for managing Shufersal coupons and exclusion preferences.

## Features

- **Web Interface**: View all scraped coupons with filtering, sorting, and search
- **Exclusion Management**: Mark coupons for exclusion or emphasis
- **Keyword Management**: Define keywords for automatic exclusion/emphasis
- **CSV Import**: Import existing coupon data from CSV files
- **Database Storage**: SQLite database for persistent coupon and preference storage
- **Integration**: Seamless integration with existing scraping workflow

## Quick Start

1. **Start the Web UI**:
   ```bash
   python run_coupon_ui.py
   ```
   
2. **Access the interface**: Open http://localhost:5000 in your browser

3. **Import existing data** (optional):
   - Go to the Import page
   - Click "Import from Data Directory" to load existing CSV files

4. **Set up exclusion keywords**:
   - Go to the Import page
   - Add keywords in the "Manage Exclusion Keywords" section
   - Choose "Exclude" to prevent activation or "Emphasize" to highlight

5. **Run enhanced scraping**:
   ```bash
   USE_EXCLUSIONS=True ACTIVATE=True SAVE=True python test_shufersal_enhanced.py
   ```

## Environment Variables

### Flask UI
- `FLASK_HOST`: Host to bind to (default: 127.0.0.1)
- `FLASK_PORT`: Port to listen on (default: 5000)
- `FLASK_DEBUG`: Enable debug mode (default: True)

### Enhanced Scraping
- `SHUFF_ID`: Shufersal client ID (required)
- `ACTIVATE`: Whether to activate coupons (default: True)
- `SAVE`: Whether to save to CSV (default: True)
- `MAX_ROWS`: Maximum coupons to process (default: unlimited)
- `USE_EXCLUSIONS`: Whether to use exclusion preferences (default: True)

## Database Schema

### Coupons Table
- `id`: Primary key
- `title`: Coupon title
- `subtitle`: Coupon subtitle
- `date_valid`: Expiration date
- `restrictions`: Usage restrictions
- `activated`: Whether coupon was activated
- `scraped_at`: When coupon was scraped
- `is_excluded`: Manual exclusion flag
- `is_emphasized`: Manual emphasis flag

### Coupon Exclusions Table
- `id`: Primary key
- `keyword`: Exclusion keyword
- `exclusion_type`: 'exclude' or 'emphasize'
- `created_at`: When keyword was added

## API Endpoints

### Coupons
- `GET /`: Main coupon listing page
- `POST /api/coupons/<id>/toggle`: Toggle coupon exclusion/emphasis

### Exclusions
- `GET /api/exclusions`: Get all exclusion keywords
- `POST /api/exclusions`: Add new exclusion keyword
- `DELETE /api/exclusions/<id>`: Delete exclusion keyword

### Import
- `GET /import`: Import page
- `POST /api/import/csv`: Import CSV file
- `GET /api/import/data-directory`: Import from data directory

## Integration with Existing System

The enhanced scraping script (`test_shufersal_enhanced.py`) maintains full backward compatibility:

1. **CSV Output**: Still saves to timestamped CSV files in `./data/`
2. **Environment Variables**: Uses same variables as original script
3. **Exclusion Logic**: Only applies when `USE_EXCLUSIONS=True`
4. **Database Storage**: Automatically saves to database when exclusions are enabled

## Workflow

1. **Initial Setup**: Import existing CSV data using the web interface
2. **Define Preferences**: Add exclusion/emphasis keywords through the UI
3. **Mark Individual Coupons**: Use the web interface to manually mark specific coupons
4. **Automated Scraping**: Run the enhanced script with `USE_EXCLUSIONS=True`
5. **Review Results**: Use the web interface to review activated coupons

## Security Notes

- The application runs in debug mode by default for development
- For production use, set `FLASK_DEBUG=False` and use a proper WSGI server
- The SQLite database file is created in the `coupon_ui/` directory
- No authentication is implemented - suitable for local/internal use only