#!/usr/bin/env python3
"""Generate preview images for all 4 pages of the pregnancy tracker"""

import json
from PIL import Image
from pregnancy_tracker import ScreenUI, Pregnancy

# Load config
config = json.load(open('config.json'))

# Create pregnancy object
pregnancy = Pregnancy(config['expected_birth_date'])

print(f"Generating all pages for week {pregnancy.get_pregnancy_week()}...")
print(f"Days until due: {pregnancy.get_days_until_due_date()}")
print(f"Progress: {pregnancy.get_percent_str()}")
print("")

# Generate all 4 pages
pages = [
    (0, "Progress", "page0_progress.png"),
    (1, "Size Comparison", "page1_size.png"),
    (2, "Appointments", "page2_appointments.png"),
    (3, "Milestones", "page3_milestones.png")
]

for page_num, page_name, filename in pages:
    screen_ui = ScreenUI(264, 176, pregnancy, current_page=page_num)
    img = screen_ui.draw()
    img.save(filename)
    print(f"✓ Page {page_num}: {page_name} -> {filename}")

print("\nAll pages generated successfully!")