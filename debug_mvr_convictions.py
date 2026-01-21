#!/usr/bin/env python
"""
Debug script for testing MVR conviction extraction
Upload your actual MVR PDF to test the conviction parsing
"""
import sys
import os
sys.path.insert(0, 'backend')

from pdf_parser import parse_mvr_pdf
import json

# Test with actual files in the directory
mvr_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf') and 'mvr' in f.lower()]

if not mvr_files:
    print("❌ No MVR PDF files found in current directory")
    print("Please add MVR PDF files with 'mvr' in the filename to test")
    print("\nUsage: Place MVR PDF files in the current directory and run this script")
    sys.exit(1)

print(f"Found {len(mvr_files)} MVR PDF file(s) to test:\n")

for pdf_file in mvr_files:
    print(f"\n{'='*70}")
    print(f"📄 Testing: {pdf_file}")
    print(f"{'='*70}")
    
    try:
        with open(pdf_file, 'rb') as f:
            pdf_content = f.read()
        
        result = parse_mvr_pdf(pdf_content)
        
        if result['success']:
            data = result['data']
            
            print(f"\n✅ Parsed Successfully!")
            print(f"\nBasic Info:")
            print(f"  License: {data.get('license_number', 'N/A')}")
            print(f"  Status: {data.get('license_status', 'N/A')}")
            print(f"  Class: {data.get('license_class', 'N/A')}")
            print(f"  Demerit Points: {data.get('demerit_points', 'N/A')}")
            
            # Convictions
            conv_count = data.get('convictions_count', '0')
            print(f"\n🚓 Convictions: {conv_count}")
            
            if 'convictions' in data and data['convictions']:
                print(f"\nConviction Details ({len(data['convictions'])} found):")
                for i, conv in enumerate(data['convictions'], 1):
                    print(f"  {i}. Date: {conv.get('date', 'N/A')}")
                    print(f"     Description: {conv.get('description', 'N/A')}")
            else:
                if conv_count == '0' or conv_count == 0:
                    print("  ✓ No convictions on record")
                else:
                    print(f"  ⚠️  Count says {conv_count} but no details extracted")
            
            # Raw text sample for debugging
            if 'raw_text' in result:
                raw = result['raw_text']
                # Find and display conviction section
                if 'convictions' in raw.lower():
                    conv_idx = raw.lower().find('convictions')
                    print(f"\n[DEBUG] Raw text around convictions section (500 chars):")
                    print(raw[max(0, conv_idx-100):conv_idx+500])
        else:
            print(f"❌ Parse failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*70}")
print("Testing complete!")
print("If convictions are not extracting correctly, the raw text debug section")
print("above will help identify the format used in your MVR PDF.")
