"""Test date parsing logic."""
import re
from datetime import datetime

message = "Plan me 3 day trip to Korea from 22/11/2025 to 25/11/2025"
user_msg = message.lower()

print("Testing date extraction:")
print(f"Message: {message}\n")

# Test 1: Day pattern
day_match = re.search(r'(\d+)\s*[-\s]?\s*days?', user_msg)
if day_match:
    num_days = int(day_match.group(1))
    print(f"✓ Day pattern found: {num_days} days")
else:
    print("✗ Day pattern not found")

# Test 2: Date range pattern
date_pattern = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
dates = re.findall(date_pattern, user_msg)
print(f"\n✓ Found {len(dates)} dates: {dates}")

if len(dates) >= 2:
    try:
        # Parse dates
        start = datetime(int(dates[0][2]), int(dates[0][1]), int(dates[0][0]))
        end = datetime(int(dates[1][2]), int(dates[1][1]), int(dates[1][0]))
        num_days_from_dates = (end - start).days + 1
        print(f"✓ Date range: {start.date()} to {end.date()}")
        print(f"✓ Calculated days: {num_days_from_dates}")
        print(f"\nDifference calculation:")
        print(f"  End - Start = {(end - start).days} days")
        print(f"  Adding 1 for inclusive = {num_days_from_dates} days")
    except Exception as e:
        print(f"✗ Error parsing dates: {e}")

# Test actual dates
print("\n" + "="*50)
print("Manual calculation:")
start = datetime(2025, 11, 22)
end = datetime(2025, 11, 25)
print(f"22/11/2025 to 25/11/2025")
print(f"Days difference: {(end - start).days}")
print(f"Inclusive days: {(end - start).days + 1}")
print(f"Actual days: Nov 22, 23, 24, 25 = 4 days")
