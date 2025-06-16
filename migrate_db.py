#!/usr/bin/env python3
# migrate_db.py - Script to migrate the database schema

import psycopg2
import os
import sys

def migrate_database():
    """Add image_url column to products table"""
    try:
        # Connect to the database
        conn = psycopg2.connect("postgresql://catalog_user:catalog_pass@localhost:5432/catalog")
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='products' AND column_name='image_url';
        """)
        
        if cursor.fetchone() is None:
            print("Adding image_url column to products table...")
            # Add the column
            cursor.execute("""
                ALTER TABLE products 
                ADD COLUMN image_url VARCHAR(255) DEFAULT 'default-product.jpg';
            """)
            print("Column added successfully!")
        else:
            print("Column image_url already exists.")
            
        conn.close()
        return True
    except Exception as e:
        print(f"Error migrating database: {str(e)}")
        return False

if __name__ == "__main__":
    if migrate_database():
        print("Database migration completed successfully.")
        sys.exit(0)
    else:
        print("Database migration failed.")
        sys.exit(1)