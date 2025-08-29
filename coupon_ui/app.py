#!/usr/bin/env python3
"""
Flask Web Application for Shufersal Coupon Management
Provides UI for viewing coupons and managing exclusion preferences
"""

import os
import sys
import csv
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'shufersal-coupon-ui-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coupons.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Coupon(db.Model):
    """Model for storing coupon data"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    subtitle = db.Column(db.String(500), nullable=True)
    date_valid = db.Column(db.String(100), nullable=True)
    restrictions = db.Column(db.Text, nullable=True)
    activated = db.Column(db.Boolean, default=False)
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_excluded = db.Column(db.Boolean, default=False)
    is_emphasized = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'subtitle': self.subtitle,
            'date_valid': self.date_valid,
            'restrictions': self.restrictions,
            'activated': self.activated,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'is_excluded': self.is_excluded,
            'is_emphasized': self.is_emphasized
        }

class CouponExclusion(db.Model):
    """Model for storing user exclusion preferences"""
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(200), nullable=False, unique=True)
    exclusion_type = db.Column(db.String(50), nullable=False)  # 'exclude' or 'emphasize'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'keyword': self.keyword,
            'exclusion_type': self.exclusion_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Routes
@app.route('/')
def index():
    """Main page showing all coupons with filtering and sorting"""
    # Get filter parameters
    filter_type = request.args.get('filter', 'all')  # all, excluded, emphasized, active
    sort_by = request.args.get('sort', 'scraped_at')
    sort_order = request.args.get('order', 'desc')
    search = request.args.get('search', '')
    
    # Build query
    query = Coupon.query
    
    # Apply filters
    if filter_type == 'excluded':
        query = query.filter(Coupon.is_excluded == True)
    elif filter_type == 'emphasized':
        query = query.filter(Coupon.is_emphasized == True)
    elif filter_type == 'active':
        query = query.filter(Coupon.activated == True)
    
    # Apply search
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Coupon.title.like(search_term),
                Coupon.subtitle.like(search_term),
                Coupon.restrictions.like(search_term)
            )
        )
    
    # Apply sorting
    if sort_order == 'desc':
        query = query.order_by(desc(getattr(Coupon, sort_by)))
    else:
        query = query.order_by(asc(getattr(Coupon, sort_by)))
    
    coupons = query.all()
    
    # Get statistics
    total_coupons = Coupon.query.count()
    excluded_count = Coupon.query.filter(Coupon.is_excluded == True).count()
    emphasized_count = Coupon.query.filter(Coupon.is_emphasized == True).count()
    activated_count = Coupon.query.filter(Coupon.activated == True).count()
    
    return render_template('index.html', 
                         coupons=coupons,
                         filter_type=filter_type,
                         sort_by=sort_by,
                         sort_order=sort_order,
                         search=search,
                         stats={
                             'total': total_coupons,
                             'excluded': excluded_count,
                             'emphasized': emphasized_count,
                             'activated': activated_count
                         })

@app.route('/api/coupons/<int:coupon_id>/toggle', methods=['POST'])
def toggle_coupon_status(coupon_id):
    """Toggle exclusion/emphasis status for a coupon"""
    coupon = Coupon.query.get_or_404(coupon_id)
    action = request.json.get('action')
    
    if action == 'exclude':
        coupon.is_excluded = not coupon.is_excluded
        coupon.is_emphasized = False  # Cannot be both excluded and emphasized
    elif action == 'emphasize':
        coupon.is_emphasized = not coupon.is_emphasized
        coupon.is_excluded = False  # Cannot be both excluded and emphasized
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'coupon': coupon.to_dict()
    })

@app.route('/api/exclusions')
def get_exclusions():
    """Get all exclusion keywords"""
    exclusions = CouponExclusion.query.all()
    return jsonify([e.to_dict() for e in exclusions])

@app.route('/api/exclusions', methods=['POST'])
def add_exclusion():
    """Add new exclusion keyword"""
    data = request.json
    keyword = data.get('keyword', '').strip()
    exclusion_type = data.get('type', 'exclude')
    
    if not keyword:
        return jsonify({'error': 'Keyword is required'}), 400
    
    # Check if keyword already exists
    existing = CouponExclusion.query.filter_by(keyword=keyword).first()
    if existing:
        return jsonify({'error': 'Keyword already exists'}), 400
    
    exclusion = CouponExclusion(keyword=keyword, exclusion_type=exclusion_type)
    db.session.add(exclusion)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'exclusion': exclusion.to_dict()
    })

@app.route('/api/exclusions/<int:exclusion_id>', methods=['DELETE'])
def delete_exclusion(exclusion_id):
    """Delete exclusion keyword"""
    exclusion = CouponExclusion.query.get_or_404(exclusion_id)
    db.session.delete(exclusion)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/import')
def import_page():
    """Page for importing CSV data"""
    return render_template('import.html')

@app.route('/api/import/csv', methods=['POST'])
def import_csv():
    """Import coupons from CSV file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        # Read CSV content
        content = file.read().decode('utf-8-sig')
        reader = csv.DictReader(content.splitlines())
        
        imported_count = 0
        for row in reader:
            # Check if coupon already exists (by title and subtitle)
            existing = Coupon.query.filter_by(
                title=row.get('title', '').strip(),
                subtitle=row.get('subtitle', '').strip()
            ).first()
            
            if not existing:
                coupon = Coupon(
                    title=row.get('title', '').strip(),
                    subtitle=row.get('subtitle', '').strip(),
                    date_valid=row.get('dateValid', '').strip(),
                    restrictions=row.get('restrictions', '').strip(),
                    activated=False  # Default to not activated
                )
                db.session.add(coupon)
                imported_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'imported_count': imported_count
        })
    
    except Exception as e:
        return jsonify({'error': f'Error importing CSV: {str(e)}'}), 500

@app.route('/api/import/data-directory')
def import_data_directory():
    """Import all CSV files from the data directory"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    if not os.path.exists(data_dir):
        return jsonify({'error': 'Data directory not found'}), 404
    
    imported_files = []
    total_imported = 0
    
    try:
        for filename in os.listdir(data_dir):
            if filename.endswith('.csv'):
                filepath = os.path.join(data_dir, filename)
                with open(filepath, 'r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file)
                    file_imported = 0
                    
                    for row in reader:
                        # Check if coupon already exists
                        existing = Coupon.query.filter_by(
                            title=row.get('title', '').strip(),
                            subtitle=row.get('subtitle', '').strip()
                        ).first()
                        
                        if not existing:
                            coupon = Coupon(
                                title=row.get('title', '').strip(),
                                subtitle=row.get('subtitle', '').strip(),
                                date_valid=row.get('dateValid', '').strip(),
                                restrictions=row.get('restrictions', '').strip(),
                                activated=False
                            )
                            db.session.add(coupon)
                            file_imported += 1
                    
                    if file_imported > 0:
                        imported_files.append({
                            'filename': filename,
                            'count': file_imported
                        })
                        total_imported += file_imported
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'imported_files': imported_files,
            'total_imported': total_imported
        })
    
    except Exception as e:
        return jsonify({'error': f'Error importing from data directory: {str(e)}'}), 500

def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully")

def get_exclusion_keywords():
    """Get exclusion keywords for use by scraping script"""
    with app.app_context():
        exclusions = CouponExclusion.query.all()
        return {
            'exclude': [e.keyword for e in exclusions if e.exclusion_type == 'exclude'],
            'emphasize': [e.keyword for e in exclusions if e.exclusion_type == 'emphasize']
        }

def should_exclude_coupon(title, subtitle, restrictions):
    """Check if a coupon should be excluded based on keywords"""
    exclusions = get_exclusion_keywords()
    text_to_check = f"{title} {subtitle} {restrictions}".lower()
    
    # Check for exclusion keywords
    for keyword in exclusions['exclude']:
        if keyword.lower() in text_to_check:
            return True
    
    return False

def should_emphasize_coupon(title, subtitle, restrictions):
    """Check if a coupon should be emphasized based on keywords"""
    exclusions = get_exclusion_keywords()
    text_to_check = f"{title} {subtitle} {restrictions}".lower()
    
    # Check for emphasis keywords
    for keyword in exclusions['emphasize']:
        if keyword.lower() in text_to_check:
            return True
    
    return False

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)