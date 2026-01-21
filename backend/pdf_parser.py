"""
PDF Parser for MVR and DASH Reports
Extracts relevant driver information from uploaded PDF files
"""
import re
import json
from datetime import datetime
import PyPDF2
from io import BytesIO


def parse_dash_pdf(pdf_file):
    """
    Parse DASH (Driver Abstract/Summary History) PDF and extract driver information
    
    Args:
        pdf_file: File object or bytes of the PDF
        
    Returns:
        dict: Extracted DASH information
    """
    try:
        print("\n🔍 Starting DASH PDF parsing...")
        # Use pdfplumber for more robust text extraction
        import pdfplumber
        if isinstance(pdf_file, bytes):
            pdf_file = BytesIO(pdf_file)
        full_text = ""
        page_count = 0
        with pdfplumber.open(pdf_file) as pdf:
            print(f"📄 PDF has {len(pdf.pages)} pages")
            for page_idx, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                        page_count += 1
                        print(f"  Page {page_idx + 1}: Extracted {len(page_text)} characters")
                    else:
                        print(f"  Page {page_idx + 1}: No text extracted (possibly scanned image)")
                except Exception as page_error:
                    print(f"  ❌ Error extracting text from page {page_idx + 1}: {str(page_error)}")
        
        print(f"✅ Successfully extracted text from {page_count} page(s), total: {len(full_text)} characters")
        
        if not full_text or len(full_text.strip()) < 50:
            print("⚠️ WARNING: Extracted text is too short or empty")
            print(f"First 100 chars: {full_text[:100]}")

        # Parse the extracted text
        print("🔄 Calling extract_dash_fields...")
        dash_data = extract_dash_fields(full_text)
        
        print(f"✅ DASH parsing complete. Extracted fields: {list(dash_data.keys())}")
        
        return {
            "success": True,
            "data": dash_data,
            "raw_text": full_text  # For debugging
        }
    except Exception as e:
        error_msg = f"PDF Parsing Error: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": error_msg
        }

def extract_dash_fields(text):
    """
    Extract specific fields from DASH text
    """
    data = {}
    print("=== DASH PDF TEXT SAMPLE (First 2000 chars) ===")
    print(text[:2000])
    print("=== END SAMPLE ===")
    report_date_match = re.search(r'Report\s*Date:\s*(\d{4}-\d{1,2}\s*\d{1,2}-\d{1,2})', text, re.IGNORECASE)
    if report_date_match:
        # Remove any spaces from the date
        date_str = report_date_match.group(1).replace(' ', '')
        data['issue_date'] = normalize_date(date_str)
        data['report_date'] = normalize_date(date_str)
        print(f"✓ Found Report Date: {data['report_date']}")
    
    # Driver Name - DASH format is "Garnica, Ivan" right after "DRIVER REPORT"
    name_patterns = [
        r'DRIVER\s+REPORT\s*\n\s*([A-Z][a-z]+,\s*[A-Z][a-z]+)',  # "Garnica, Ivan"
        r'(?:Driver|Name|Client)[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'([A-Z][a-z]+,\s*[A-Z][a-z]+)',  # Generic: Last, First
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['name'] = match.group(1).strip()
            print(f"Found name: {data['name']}")
            break
    
    # Address - format: "Address: 201-1480 Eglinton Ave W ,Toronto,ON M6C2G5"
    address_patterns = [
        r'Address:\s*(.+?)\s+Number of',  # Get everything until "Number of"
        r'Address:\s*([^\n]+)',
    ]
    for pattern in address_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['address'] = match.group(1).strip()
            print(f"Found address: {data['address']}")
            break
    
    # License Number - format: "DLN: G6043-37788-80203"
    license_patterns = [
        r'DLN:\s*([A-Z0-9\-]+)',  # DLN: G6043-37788-80203
        r'License\s*(?:Number|#|No\.?)?[:\s]+([A-Z0-9\-]+)',
        r'DL\s*(?:Number|#)?[:\s]+([A-Z0-9\-]+)',
    ]
    for pattern in license_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['license_number'] = match.group(1).strip()
            break
    
    # Date of Birth - format: "Date of Birth: 1980-02-03"
    dob_patterns = [
        r'Date\s+of\s+Birth:\s*(\d{4}-\d{2}-\d{2})',  # 1980-02-03
        r'(?:Date\s*of\s*)?Birth(?:\s*Date)?[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'DOB[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
    ]
    for pattern in dob_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['dob'] = normalize_date(match.group(1))
            break
    
    # Expiry Date
    expiry_patterns = [
        r'Expir(?:y|ation)\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Exp\.?\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Valid\s*(?:Through|Until)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    for pattern in expiry_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['expiry_date'] = normalize_date(match.group(1))
            break
    
    # Issue/Renewal Date
    issue_patterns = [
        r'Report\s*Date[:\s]+(\d{4}-\d{2}-\d{2})',  # Report Date: 2025-01-05
        r'Issue\s*Date[:\s]+(\d{4}-\d{2}-\d{2})',
        r'Issue\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Issued[:\s]+(\d{4}-\d{2}-\d{2})',
        r'Issued[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Renewal\s*Date[:\s]+(\d{4}-\d{2}-\d{2})',
        r'Renewal\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(?:Issue|Issued)[:\s]+(\d{4}-\d{2}-\d{2})'  # DASH format: 2025-01-05
    ]
    for pattern in issue_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['issue_date'] = normalize_date(match.group(1))
            print(f"✓ Found issue/renewal/report date: {data['issue_date']} (pattern: {pattern[:30]}...)")
            break
    
    if not data.get('issue_date'):
        print("⚠️ No issue/renewal/report date found in PDF")
    
    # Class
    class_patterns = [
        r'Class[:\s]+([A-Z0-9]+)',
        r'License\s*Class[:\s]+([A-Z0-9]+)'
    ]
    for pattern in class_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['license_class'] = match.group(1).strip()
            break
    
    # VIN Number - 17 character vehicle identification number
    # Format in PDF: "2012  TOYOTA - SIENNA  LE V6 AWD - 5TDJK3DC8CS035732"
    vin_patterns = [
        r'VIN[:\s#]*([A-HJ-NPR-Z0-9]{17})',  # Standard VIN (excludes I, O, Q)
        r'Vehicle\s*Identification\s*(?:Number|#)?[:\s]+([A-HJ-NPR-Z0-9]{17})',
        r'V\.?I\.?N\.?[:\s]*([A-HJ-NPR-Z0-9]{17})',
        r'-\s*([A-HJ-NPR-Z0-9]{17})\s+Coverage',  # Extract VIN before "Coverage"
        r'AWD\s*-\s*([A-HJ-NPR-Z0-9]{17})'  # After AWD/FWD etc
    ]
    for pattern in vin_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['vin'] = match.group(1).strip().upper()
            print(f"✓ Found VIN: {data['vin']}")
            break
    
    if not data.get('vin'):
        print("⚠️ No VIN found in PDF")
    
    # Vehicle Year/Make/Model - Format: "2012  TOYOTA - SIENNA  LE V6 AWD"
    vehicle_match = re.search(r'Vehicle #1:\s*(\d{4})\s+([A-Z]+)\s*-\s*([^-]+?)\s*-\s*[A-HJ-NPR-Z0-9]{17}', text)
    if vehicle_match:
        year = vehicle_match.group(1)
        make = vehicle_match.group(2)
        model = vehicle_match.group(3).strip()
        data['vehicle_year_make_model'] = f"{year} {make} {model}"
        print(f"✓ Found Vehicle: {data['vehicle_year_make_model']}")
    
    # Years of Continuous Insurance
    cont_ins_match = re.search(r'Years\s+of\s+Continuous\s+Insurance:\s*(\d+)', text, re.IGNORECASE)
    if cont_ins_match:
        data['years_continuous_insurance'] = cont_ins_match.group(1)
        print(f"✓ Years of Continuous Insurance: {data['years_continuous_insurance']}")
    
    # Policy dates for gap calculation
    # Find all policies in the Policies section: "#1 2025-08-08 to 2026-08-08 ..."
    policies_section_match = re.search(r'Policies\s*\n(.*?)(?:Claims|Page \d+ of \d+|$)', text, re.DOTALL | re.IGNORECASE)
    if policies_section_match:
        policies_text = policies_section_match.group(1)
        # Extract all policies with pattern: #N YYYY-MM-DD to YYYY-MM-DD
        policy_pattern = r'#(\d+)\s+(\d{4}-\d{1,2}-\d{1,2})\s+to\s+(\d{4}-\d{1,2}-\d{1,2})'
        policy_matches = list(re.finditer(policy_pattern, policies_text))
        
        if policy_matches:
            # Store ALL policies for gap calculation
            all_policies = []
            for match in policy_matches:
                policy = {
                    'number': int(match.group(1)),
                    'start_date': normalize_date(match.group(2).replace(' ', '')),
                    'end_date': normalize_date(match.group(3).replace(' ', ''))
                }
                all_policies.append(policy)
            
            # Sort by policy number to ensure correct order
            all_policies.sort(key=lambda x: x['number'])
            data['all_policies'] = all_policies
            print(f"✓ Extracted {len(all_policies)} policies for gap calculation")
            
            # Get the LAST policy (oldest one, highest number)
            last_policy = policy_matches[-1]
            policy_num = last_policy.group(1)
            start_date = last_policy.group(2).replace(' ', '')  # Remove any spaces
            end_date = last_policy.group(3).replace(' ', '')
            
            # First insurance = start date of the LAST/oldest policy
            data['first_insurance_date'] = normalize_date(start_date)
            print(f"✓ First Insurance Date (from Policy #{policy_num} start): {data['first_insurance_date']}")
            
            # Get the FIRST policy (current/latest one, #1)
            first_policy = policy_matches[0]
            current_start = first_policy.group(2).replace(' ', '')
            current_end = first_policy.group(3).replace(' ', '')
            
            data['policy_start_date'] = normalize_date(current_start)
            data['policy_end_date'] = normalize_date(current_end)
            data['renewal_date'] = normalize_date(current_end)  # Always add renewal_date as expiry of policy #1
            print(f"✓ Current Policy Dates: {data['policy_start_date']} to {data['policy_end_date']}")
            print(f"✓ Renewal Date (Policy #1 Expiry): {data['renewal_date']}")
    
    # Fallback: Try to get from detail section if policies section not found
    if not data.get('policy_start_date'):
        earliest_term_match = re.search(r'Start\s+of\s+the\s+Earliest\s+Term:\s*(\d{4}-\d{2}-\d{2})', text)
        if earliest_term_match:
            data['policy_start_date'] = normalize_date(earliest_term_match.group(1))
            print(f"✓ Policy Start Date (fallback): {data['policy_start_date']}")
    
    if not data.get('policy_end_date'):
        latest_term_match = re.search(r'End\s+of\s+the\s+Latest\s+Term:\s*(\d{4}-\d{2}-\d{2})', text)
        if latest_term_match:
            data['policy_end_date'] = normalize_date(latest_term_match.group(1))
            print(f"✓ Policy End Date (fallback): {data['policy_end_date']}")
    
    # Status
    status_patterns = [
        r'Status[:\s]+(Valid|Active|Suspended|Revoked|Expired)',
        r'License\s*Status[:\s]+(Valid|Active|Suspended|Revoked|Expired)'
    ]
    for pattern in status_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['license_status'] = match.group(1).strip()
            break
    
    # Demerit Points
    points_patterns = [
        r'(?:Demerit\s*)?Points?[:\s]+(\d+)',
        r'Point\s*Balance[:\s]+(\d+)',
        r'Current\s*Points[:\s]+(\d+)'
    ]
    for pattern in points_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['demerit_points'] = match.group(1)
            break
    
    # Conditions/Restrictions
    conditions_match = re.search(r'Conditions?[:\s]+([^\n]+)', text, re.IGNORECASE)
    if conditions_match:
        data['conditions'] = conditions_match.group(1).strip()
    
    # Claims History - extract ONLY from the "Claims" section
    # NOT from the "Policies" section
    claims = []
    
    print("\n=== EXTRACTING CLAIMS ===")
    
    # Find the "Claims" section in the PDF - improved to capture all claims across pages
    # Look for Claims section and capture until "Previous Inquiries" section
    claims_section_match = re.search(r'Claims\s*\n(.*?)(?:Previous Inquiries)', text, re.DOTALL | re.IGNORECASE)
    
    # If not found, try alternative: capture from Claims to end of document
    if not claims_section_match:
        claims_section_match = re.search(r'Claims\s*\n(.*?)$', text, re.DOTALL | re.IGNORECASE)
    
    if claims_section_match:
        claims_text = claims_section_match.group(1)
        print(f"\n=== CLAIMS SECTION ({len(claims_text)} chars) ===")
        print(f"First 1000 chars:\n{claims_text[:1000]}")
        
        # Count potential claim markers
        claim_num_markers = re.findall(r'#(\d+)', claims_text)
        print(f"\n[DEBUG] Found claim number markers: {claim_num_markers}")
        print(f"[DEBUG] Total markers found: {len(claim_num_markers)}")
        
        # Strategy: Split by claim numbers and extract data from each section
        print(f"\n[EXTRACT] Splitting by claim number patterns...")
        
        # Split by # followed by digit
        parts = re.split(r'(?=#\d)', claims_text)
        claim_matches = []
        
        for part_idx, part in enumerate(parts):
            part = part.strip()
            if not part or not part.startswith('#'):
                continue
                
            # Extract claim number
            num_match = re.match(r'#(\d+)', part)
            if not num_match:
                continue
                
            claim_num = num_match.group(1)
            print(f"\n[CLAIM {claim_num}] Processing...")
            
            # Extract date of loss
            date_match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', part)
            loss_date = date_match.group(1) if date_match else "0000-00-00"
            print(f"  Date: {loss_date}")
            
            # Extract at-fault percentage
            fault_match = re.search(r'At-?Fault\s*:\s*(\d+)\s*%', part, re.IGNORECASE)
            at_fault_pct = fault_match.group(1) if fault_match else "0"
            print(f"  At-Fault: {at_fault_pct}%")
            
            # Extract company name (usually between Date and At-Fault)
            company_match = re.search(rf'#{claim_num}\s+.*?(\d{{4}}[-/]\d{{1,2}}[-/]\d{{1,2}})\s+(.*?)(?:At-?Fault|$)', part, re.IGNORECASE | re.DOTALL)
            company = company_match.group(2).strip() if company_match else ""
            if company:
                company = company.split('\n')[0].strip()  # Take first line only
            print(f"  Company: {company}")
            
            # Create a match-like object to maintain compatibility
            class PartMatch:
                def __init__(self, num, date, company, fault, full_text):
                    self._num = num
                    self._date = date
                    self._company = company
                    self._fault = fault
                    self._text = full_text
                def group(self, idx):
                    if idx == 0: return self._text
                    elif idx == 1: return self._num
                    elif idx == 2: return self._date
                    elif idx == 3: return self._company
                    elif idx == 4: return self._fault
                    return None
                def groups(self):
                    return (self._num, self._date, self._company, self._fault)
                def end(self):
                    return len(self._text)
            
            claim_matches.append(PartMatch(claim_num, loss_date, company, at_fault_pct, part))
        
        print(f"\n[EXTRACT] Total claims extracted: {len(claim_matches)}")
        print(f"[EXTRACT] Expected: {len(claim_num_markers)}, Found: {len(claim_matches)}")
        
        total_claims_found = len(claim_matches)
        print(f"\n[CLAIMS] TOTAL FOUND: {total_claims_found}")
        
        for idx, match in enumerate(claim_matches, 1):
            claim = {}
            print(f"\n[CLAIM {idx}/{total_claims_found}] Processing...")
            claim_num = match.group(1)
            loss_date = match.group(2)
            
            # Extract company name and at-fault percentage
            if len(match.groups()) >= 4:
                # We have the full match with company and at-fault
                company_and_notes = match.group(3).strip()
                at_fault_pct = match.group(4)
                print(f"  [FULL] Company='{company_and_notes}', AtFault={at_fault_pct}%")
            else:
                # Fallback: extract from text after the loss date
                company_and_notes = ""
                at_fault_pct = "0"
                # Try to find at-fault percentage in the text following this claim
                search_start = match.end()
                search_end = min(search_start + 200, len(claims_text))
                next_section = claims_text[search_start:search_end]
                at_fault_match = re.search(r'At-?Fault\s*:\s*(\d+)\s*%', next_section, re.IGNORECASE)
                if at_fault_match:
                    at_fault_pct = at_fault_match.group(1)
                    # Extract company from between loss date and at-fault
                    company_section = next_section[:at_fault_match.start()]
                    company_and_notes = company_section.strip()
                    print(f"  [PARTIAL] Company='{company_and_notes}', AtFault={at_fault_pct}%")
            
            claim['date'] = normalize_date(loss_date)
            
            # Extract company name (remove *THIRD PARTY* if present)
            company = re.sub(r'\*.*?\*', '', company_and_notes).strip()
            claim['company'] = company
            
            # At-fault
            if at_fault_pct == '0':
                claim['fault'] = 'No'
            elif at_fault_pct == '100':
                claim['fault'] = 'Yes'
            else:
                claim['fault'] = f'{at_fault_pct}%'
            
            # Try to find claim details in the detailed section below
            # Look for the specific claim number section and extract financial details
            claim_detail_pattern = rf'Claim #{claim_num}\s+Date of Loss\s+\d{{4}}-\d{{2}}-\d{{2}}.*?Total Loss:\s*\$\s*([\d,\.]+).*?Total Expense:\s*\$\s*([\d,\.]+)'
            detail_match = re.search(claim_detail_pattern, text, re.DOTALL | re.IGNORECASE)
            
            if detail_match:
                loss_val = detail_match.group(1).replace(',', '').strip()
                expense_val = detail_match.group(2).replace(',', '').strip()
                
                claim['loss'] = loss_val
                claim['expense'] = expense_val
                
                # Calculate total
                try:
                    total = float(loss_val) + float(expense_val)
                    claim['total'] = f'{total:.2f}'
                    print(f"  → Financials: Loss=${loss_val}, Expense=${expense_val}, Total=${total:.2f}")
                except ValueError:
                    print(f"  ⚠️ Could not calculate total for claim #{claim_num}")
            else:
                print(f"  ⚠️ No financial details found for claim #{claim_num}")
            
            # Try to find claim status
            status_pattern = rf'Claim #{claim_num}.*?Claim\s*Status:\s*(\w+)'
            status_match = re.search(status_pattern, text, re.DOTALL | re.IGNORECASE)
            if status_match:
                claim['status'] = status_match.group(1).strip()
            else:
                claim['status'] = 'Closed'  # Default if not found
            
            print(f"✓ Claim #{claim_num}: {claim['date']}, Company={claim['company']}, At-Fault={claim['fault']}, Status={claim.get('status', 'N/A')}")
            claims.append(claim)
    else:
        print("⚠️ No 'Claims' section found in PDF")
    
    print(f"\n✓ FINAL: {len(claims)} claims extracted from Claims section")
    
    if claims:
        data['claims'] = claims
        data['claims_count'] = str(len(claims))
        print(f"✓ Returning {len(claims)} valid claims\n")
    else:
        data['claims'] = []
        data['claims_count'] = '0'
        print(f"ℹ No valid claims found in PDF\n")
    
    # Email
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if email_match:
        data['email'] = email_match.group(0)
    
    # Phone number - if present
    phone_patterns = [
        r'Phone[:\s]+(\+?[\d\-\(\)\s]+)',
        r'Tel[:\s]+(\+?[\d\-\(\)\s]+)',
        r'Mobile[:\s]+(\+?[\d\-\(\)\s]+)'
    ]
    for pattern in phone_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['phone'] = match.group(1).strip()
            print(f"Found phone: {data['phone']}")
            break
    
    # Email - if present
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if email_match:
        data['email'] = email_match.group(0)
        print(f"Found email: {data['email']}")
    
    # Log what was extracted
    extracted_fields = [k for k, v in data.items() if v]
    print(f"\n✅ DASH extraction complete:")
    print(f"  Fields extracted: {extracted_fields}")
    print(f"  Total fields with values: {len(extracted_fields)} out of {len(data)}")
    print(f"=== DASH EXTRACTED DATA ===")
    print(json.dumps(data, indent=2, default=str))
    print(f"=== END DATA ===")
    
    if not extracted_fields:
        print("\n⚠️ WARNING: No fields were extracted from the PDF text!")
        print("This could mean:")
        print("  1. PDF is image-based/scanned (needs OCR)")
        print("  2. Text layout doesn't match expected patterns")
        print("  3. PDF is corrupted")
    
    return data


def parse_mvr_pdf(pdf_file):
    """
    Parse MVR PDF and extract driver information
    
    Args:
        pdf_file: File object or bytes of the PDF
        
    Returns:
        dict: Extracted MVR information
    """
    try:
        # Read PDF
        if isinstance(pdf_file, bytes):
            pdf_file = BytesIO(pdf_file)
        
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text() + "\n"
        
        # Parse the extracted text
        mvr_data = extract_mvr_fields(full_text)
        
        return {
            "success": True,
            "data": mvr_data,
            "raw_text": full_text  # For debugging
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def extract_mvr_fields(text):
    """
    Extract specific fields from MVR text using regex patterns
    """
    data = {}
    
    print("=== MVR PDF TEXT SAMPLE (First 2000 chars) ===")
    print(text[:2000])
    print("=== END SAMPLE ===")
    
    # License Number - various patterns
    license_patterns = [
        r'Licence Number:\s*([A-Z0-9\-]+)',  # MVR format
        r'License\s*(?:Number|#|No\.?)?[:\s]+([A-Z0-9\-]+)',
        r'DL\s*(?:Number|#|No\.?)?[:\s]+([A-Z0-9\-]+)',
        r'Driver[\'s]?\s*License[:\s]+([A-Z0-9\-]+)'
    ]
    for pattern in license_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['license_number'] = match.group(1).strip()
            print(f"✓ Found License Number: {data['license_number']}")
            break
    
    # Expiry Date - MVR format: "Expiry Date: 03/02/2030"
    expiry_patterns = [
        r'Expiry Date:\s*(\d{1,2}/\d{1,2}/\d{4})',  # MVR format
        r'Expir(?:y|ation)\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Exp\.?\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Valid\s*(?:Through|Until)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    for pattern in expiry_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['expiry_date'] = normalize_date(match.group(1))
            print(f"✓ Found Expiry Date: {data['expiry_date']}")
            break
    
    # Date of Birth - MVR format: "Birth Date: 03/02/1980"
    dob_patterns = [
        r'Birth Date:\s*(\d{1,2}/\d{1,2}/\d{4})',  # MVR format
        r'(?:Date\s*of\s*)?Birth\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'DOB[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Born[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    for pattern in dob_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['dob'] = normalize_date(match.group(1))
            print(f"✓ Found DOB: {data['dob']}")
            break
    
    # Issue Date - MVR format: "Issue Date: 16/11/2001"
    issue_patterns = [
        r'Issue Date:\s*(\d{1,2}/\d{1,2}/\d{4})',  # MVR format
        r'Issue\s*Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Issued[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    for pattern in issue_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['issue_date'] = normalize_date(match.group(1))
            print(f"✓ Found Issue Date: {data['issue_date']}")
            break
    
    # License Status - MVR format: "Status: LICENCED"
    status_patterns = [
        r'Status:\s*(LICENCED|LICENSED|VALID|ACTIVE|SUSPENDED|REVOKED|EXPIRED)',  # MVR format
        r'Status[:\s]+(Valid|Suspended|Revoked|Expired)',
        r'License\s*Status[:\s]+(Valid|Suspended|Revoked|Expired)'
    ]
    for pattern in status_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            status = match.group(1).strip().upper()
            # Normalize "LICENCED" to "Valid"
            if status in ['LICENCED', 'LICENSED', 'ACTIVE']:
                data['license_status'] = 'Valid'
            else:
                data['license_status'] = status.capitalize()
            print(f"✓ Found License Status: {data['license_status']}")
            break
    
    # Class/Type - MVR format: "Class: G***"
    class_patterns = [
        r'Class:\s*([A-Z0-9\*]+)',  # MVR format
        r'Class[:\s]+([A-Z0-9]+)',
        r'License\s*Class[:\s]+([A-Z0-9]+)',
        r'Type[:\s]+([A-Z0-9]+)'
    ]
    for pattern in class_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['license_class'] = match.group(1).strip().replace('*', '')
            print(f"✓ Found License Class: {data['license_class']}")
            break
    
    # Demerit Points - MVR format: "Demerit Points: 00"
    points_patterns = [
        r'Demerit Points:\s*(\d+)',  # MVR format
        r'(?:Demerit\s*)?Points?[:\s]+(\d+)',
        r'Point\s*Balance[:\s]+(\d+)',
        r'Total\s*Points[:\s]+(\d+)'
    ]
    for pattern in points_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['demerit_points'] = match.group(1)
            print(f"✓ Found Demerit Points: {data['demerit_points']}")
            break
    
    # Conditions/Restrictions - MVR format: "Conditions: */N"
    conditions_patterns = [
        r'Conditions:\s*([^\n]+)',  # MVR format
        r'Conditions?[:\s]+([^\n]+)'
    ]
    for pattern in conditions_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            cond = match.group(1).strip()
            # Skip if it's just */N or similar placeholder
            if cond and cond not in ['*/N', '*', 'N', 'None', 'NONE']:
                data['conditions'] = cond
                print(f"✓ Found Conditions: {data['conditions']}")
            break
    
    # Number of Convictions - MVR format: "***Number of Convictions: 0 ***"
    convictions_pattern = r'\*+\s*Number of Convictions:\s*(\d+)\s*\*+'
    conv_match = re.search(convictions_pattern, text, re.IGNORECASE)
    if conv_match:
        conv_count = int(conv_match.group(1))
        data['convictions_count'] = str(conv_count)
        print(f"✓ Found Convictions Count: {conv_count}")
        
        # If there are convictions, try to extract them
        if conv_count > 0:
            convictions = []
            
            # Find the "Number of Convictions" section
            conv_section_start = conv_match.end()
            # Look for the next section header or end of document
            next_section = re.search(r'(?:^\*+|^[A-Z\*]{3,})', text[conv_section_start:], re.MULTILINE)
            if next_section:
                conv_section = text[conv_section_start:conv_section_start + next_section.start()]
            else:
                conv_section = text[conv_section_start:]
            
            print(f"\n=== CONVICTIONS SECTION (First 2000 chars) ===")
            print(conv_section[:2000])
            print(f"=== END CONVICTIONS SECTION ===\n")
            
            # Try multiple patterns to extract conviction details
            # Pattern 1: Standard MVR format - lines with date, offense, and penalties
            # Looking for patterns like:
            # 01/15/2023 Speeding 20+ km/h over limit Fine: $280
            # Or: 01/15/2023 - Speeding...
            # Or list format with conviction headers
            
            conv_detail_patterns = [
                # Date + offense + fine (most common MVR format)
                r'(\d{1,2}/\d{1,2}/\d{4})\s+([A-Za-z\s\-\(\)0-9\.&/]+?)(?:\s+Fine:\s*\$?[\d,.]+|\s+Penalty.*)?(?:\n|$)',
                # Date - description format
                r'(\d{1,2}/\d{1,2}/\d{4})\s*[\-–]\s*([A-Za-z\s\-\(\)0-9\.&/]+?)(?:\n|$)',
                # Numbered conviction format: 1. Date Description
                r'^\s*\d+\.\s+(\d{1,2}/\d{1,2}/\d{4})\s+([A-Za-z\s\-\(\)0-9\.&/]+?)$',
                # Conviction list format with newlines separating offense from fine
                r'(\d{1,2}/\d{1,2}/\d{4})\s*\n\s*([A-Za-z\s\-\(\)0-9\.&/]+?)(?=\n\d{1,2}/\d{1,2}/\d{4}|\n---|\n\*|\Z)',
            ]
            
            for pattern in conv_detail_patterns:
                print(f"\n[PATTERN] Trying pattern: {pattern[:80]}...")
                conv_matches = re.finditer(pattern, conv_section, re.IGNORECASE | re.MULTILINE)
                matched_count = 0
                
                for match in conv_matches:
                    date_str = match.group(1).strip()
                    description = match.group(2).strip()
                    
                    # Clean up description - remove extra whitespace and common artifacts
                    description = re.sub(r'\s+', ' ', description)
                    description = re.sub(r'\s*[Ff]ine:\s*\$?[\d,.]+\s*', '', description)
                    description = re.sub(r'\s*[Pp]enalty.*?$', '', description, flags=re.MULTILINE)
                    description = description.strip()
                    
                    # Skip if description is empty or just punctuation
                    if description and description not in ['', '-', '*', 'N', 'None', 'NONE'] and len(description) > 2:
                        conviction = {
                            'date': normalize_date(date_str),
                            'description': description
                        }
                        # Avoid duplicates
                        if conviction not in convictions:
                            convictions.append(conviction)
                            matched_count += 1
                            print(f"  ✓ Found: {conviction['date']} - {conviction['description'][:60]}...")
                
                # If we found enough convictions with this pattern, use it
                if len(convictions) >= conv_count:
                    print(f"✓ Pattern matched {matched_count} convictions, stopping pattern search")
                    break
                elif matched_count > 0:
                    print(f"✓ Pattern matched {matched_count} conviction(s)")
            
            if convictions:
                data['convictions'] = convictions
                print(f"\n✅ Extracted {len(convictions)} conviction details out of {conv_count} expected")
                if len(convictions) < conv_count:
                    print(f"⚠️  Note: Expected {conv_count} but found {len(convictions)} - PDF format may vary")
            else:
                # If we couldn't extract details, at least show count
                print(f"⚠️  Could not extract conviction details (found count: {conv_count})")
                print(f"    This might be due to PDF format variation. Please check the PDF manually.")
    else:
        # Default to 0 if not found
        data['convictions_count'] = '0'
        print(f"✓ No convictions section found (defaulting to 0 convictions)")
    
    print(f"=== MVR EXTRACTED DATA ===")
    print(json.dumps(data, indent=2))
    print(f"=== END DATA ===")
    
    return data


def normalize_date(date_str):
    """
    Convert various date formats to MM/DD/YYYY
    """
    try:
        # Try different date formats
        formats = [
            '%m/%d/%Y', '%m-%d-%Y',
            '%m/%d/%y', '%m-%d-%y',
            '%d/%m/%Y', '%d-%m-%Y',
            '%Y-%m-%d', '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%m/%d/%Y')
            except ValueError:
                continue
        
        return date_str  # Return original if no format matches
    except:
        return date_str
