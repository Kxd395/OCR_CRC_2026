#!/usr/bin/env python3
"""
Convert checkbox IDs from 0-based to 1-based indexing
"""
import json
from pathlib import Path

def main():
    template_path = Path("templates/crc_survey_l_anchors_v1/template.json")
    
    print("="*70)
    print("CONVERTING CHECKBOX IDs: 0-based → 1-based")
    print("="*70)
    
    # Load current template
    with open(template_path) as f:
        template = json.load(f)
    
    print(f"\nCurrent IDs (first 5):")
    for roi in template['checkbox_rois_norm'][:5]:
        print(f"  {roi['id']}")
    
    # Convert IDs
    print(f"\nConverting...")
    for roi in template['checkbox_rois_norm']:
        # Parse current ID (e.g., "Q1_0")
        parts = roi['id'].split('_')
        row = parts[0]  # "Q1"
        col = int(parts[1])  # 0
        
        # Convert to 1-based
        new_col = col + 1
        roi['id'] = f"{row}_{new_col}"
    
    print(f"\nNew IDs (first 5):")
    for roi in template['checkbox_rois_norm'][:5]:
        print(f"  {roi['id']}")
    
    # Show all IDs in grid format
    print("\n" + "="*70)
    print("UPDATED GRID LAYOUT")
    print("="*70)
    print("\n          Col 1    Col 2    Col 3    Col 4    Col 5")
    print("          (Left)                           (Right)")
    print("       ┌─────────┬────────┬────────┬────────┬─────────┐")
    
    for row in range(1, 6):
        row_ids = [roi['id'] for roi in template['checkbox_rois_norm'] if roi['id'].startswith(f"Q{row}_")]
        print(f"Row {row}  │  {row_ids[0]:<6} │  {row_ids[1]:<6} │  {row_ids[2]:<6} │  {row_ids[3]:<6} │  {row_ids[4]:<6} │")
        if row < 5:
            print("       ├─────────┼────────┼────────┼────────┼─────────┤")
    
    print("       └─────────┴────────┴────────┴────────┴─────────┘")
    
    # Update version
    old_version = template['version']
    template['version'] = "1.2.0"
    template['description'] = "Expanded ROI template for L-anchors survey (1-based column indexing)"
    
    # Save updated template
    backup_path = template_path.parent / "template_v1.1.0_backup.json"
    
    # Create backup
    with open(backup_path, 'w') as f:
        with open(template_path) as orig:
            f.write(orig.read())
    
    print(f"\n✅ Backup saved: {backup_path}")
    
    # Save new version
    with open(template_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"✅ Updated template: {template_path}")
    print(f"   Version: {old_version} → {template['version']}")
    
    print("\n" + "="*70)
    print("CONVERSION COMPLETE")
    print("="*70)
    print("\nCheckbox columns now numbered 1-5 (instead of 0-4)")
    print("\nOLD format: Q1_0, Q1_1, Q1_2, Q1_3, Q1_4")
    print("NEW format: Q1_1, Q1_2, Q1_3, Q1_4, Q1_5")
    
    print("\n⚠️  IMPORTANT: You'll need to regenerate overlays and re-run detection")
    print("   with the updated template for the new IDs to take effect.")

if __name__ == "__main__":
    main()
