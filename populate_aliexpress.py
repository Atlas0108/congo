#!/usr/bin/env python3
"""
Script to populate database with products from AliExpress
Usage: python populate_aliexpress.py [--count 100] [--api-key YOUR_API_KEY]
"""

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.utils.aliexpress import populate_products_from_aliexpress

def main():
    parser = argparse.ArgumentParser(description='Populate database with AliExpress products')
    parser.add_argument('--count', type=int, default=100, help='Number of products to fetch (default: 100)')
    parser.add_argument('--api-key', type=str, default=None, help='AliExpress API key (optional, uses mock data if not provided)')
    
    args = parser.parse_args()
    
    print(f"🛒 Fetching {args.count} products from AliExpress...")
    print("")
    
    if not args.api_key:
        print("ℹ️  No API key provided. Using mock data for testing.")
        print("   To use real AliExpress API, get an API key from RapidAPI or AliExpress Affiliate Program")
        print("   and run: python populate_aliexpress.py --api-key YOUR_KEY --count 100")
        print("")
    
    try:
        count = populate_products_from_aliexpress(args.api_key, args.count)
        print(f"\n✅ Successfully populated {count} products!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

