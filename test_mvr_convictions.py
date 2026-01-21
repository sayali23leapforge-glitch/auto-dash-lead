#!/usr/bin/env python
"""
Test script to verify MVR conviction extraction improvements
"""
import sys
sys.path.insert(0, 'backend')

from pdf_parser import extract_mvr_fields

# Sample MVR text with convictions (simulating actual MVR format)
sample_mvr_text = """
DRIVER LICENSE RECORD

Licence Number: A1234567
Birth Date: 03/15/1990
Issue Date: 01/20/2020
Expiry Date: 01/20/2028
Status: LICENCED
Class: G***
Conditions: */N
Demerit Points: 06

***Number of Convictions: 3 ***

Conviction History:
01/15/2023 - Speeding 20+ km/h over limit - $280.00
05/22/2021 - Failed to Obey Traffic Signal - $165.00
11/10/2019 - Improper Lane Change - $110.00

End of Record
"""

print("Testing MVR conviction extraction with sample data...\n")
print("Sample MVR Text:")
print("=" * 60)
print(sample_mvr_text)
print("=" * 60)

# Extract fields
result = extract_mvr_fields(sample_mvr_text)

print("\n\nExtraction Results:")
print("=" * 60)
if 'convictions_count' in result:
    print(f"Convictions Count: {result['convictions_count']}")
    
if 'convictions' in result:
    print(f"\nConvictions List:")
    for i, conv in enumerate(result['convictions'], 1):
        print(f"  {i}. Date: {conv.get('date', 'N/A')}")
        print(f"     Description: {conv.get('description', 'N/A')}")
else:
    print("⚠️  No convictions extracted!")

print("\nFull Result:")
import json
print(json.dumps(result, indent=2))
