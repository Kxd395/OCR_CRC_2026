#!/usr/bin/env python3
"""
Draw bounding boxes around checkbox row areas on the aligned/cropped image.
"""

import cv2
from pathlib import Path

def draw_checkbox_row_box(image_path, output_path, box_x, box_y, box_width, box_height, label="Checkbox Row"):
    """
    Draw a bounding box around a checkbox row area.
    
    Args:
        image_path: Path to input image
        output_path: Path to save marked image
        box_x: Left X coordinate of the box
        box_y: Top Y coordinate of the box
        box_width: Width of the box
        box_height: Height of the box
        label: Label for the box
    """
    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    img_height, img_width = img.shape[:2]
    print(f"Image dimensions: {img_width}x{img_height}px\n")
    
    # Create overlay
    overlay = img.copy()
    
    # Draw grid lines for reference (faint)
    for x in range(0, img_width + 1, 50):
        if x % 100 == 0:
            cv2.line(overlay, (x, 0), (x, img_height), (200, 200, 200), 1)  # Light gray thick
        else:
            cv2.line(overlay, (x, 0), (x, img_height), (220, 220, 220), 1)  # Lighter gray thin
    
    for y in range(0, img_height + 1, 50):
        if y % 100 == 0:
            cv2.line(overlay, (0, y), (img_width, y), (200, 200, 200), 1)  # Light gray thick
        else:
            cv2.line(overlay, (0, y), (img_width, y), (220, 220, 220), 1)  # Lighter gray thin
    
    # Draw the bounding box
    print(f"Drawing box: {label}")
    print(f"  Position: ({box_x}, {box_y})")
    print(f"  Size: {box_width}x{box_height}px")
    print(f"  Bottom-right: ({box_x + box_width}, {box_y + box_height})\n")
        print(f"Marking {label} at ({x}, {y})")
        
        # Draw crosshair
        # Vertical line
        cv2.line(overlay, (x, y - 30), (x, y + 30), (0, 0, 255), 3)
        # Horizontal line
        cv2.line(overlay, (x - 30, y), (x + 30, y), (0, 0, 255), 3)
        
        # Draw circle at exact point
        cv2.circle(overlay, (x, y), 8, (0, 255, 0), 3)
        cv2.circle(overlay, (x, y), 2, (255, 0, 0), -1)
        
        # Add label with background
        label_text = f"{label}: ({x}, {y})"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(
            label_text, font, font_scale, thickness
        )
        
        # Position label to the right of the point
        label_x = x + 40
        label_y = y + 10
        
        # Ensure label stays within image bounds
        if label_x + text_width > width:
            label_x = x - text_width - 40
        if label_y - text_height < 0:
            label_y = y + text_height + 20
        if label_y > height:
            label_y = y - 20
        
        # Draw white background for label
        padding = 5
        cv2.rectangle(
            overlay,
            (label_x - padding, label_y - text_height - padding),
            (label_x + text_width + padding, label_y + baseline + padding),
            (255, 255, 255),
            -1
        )
        
        # Draw label text
        cv2.putText(
            overlay,
            label_text,
            (label_x, label_y),
            font,
            font_scale,
            (0, 0, 255),
            thickness
        )
    
    # Add info box
    info_lines = [
        "CHECKBOX LOCATION MARKER",
        "RED crosshair = marked point",
        "GREEN circle = exact location",
        "BLUE dot = center point",
        "Gray grid = 50px/100px reference"
    ]
    
    y_offset = 30
    for i, line in enumerate(info_lines):
        font_scale = 0.8 if i == 0 else 0.6
        thickness = 2 if i == 0 else 1
        color = (0, 0, 255) if i == 0 else (0, 0, 0)
        
        (text_width, text_height), baseline = cv2.getTextSize(
            line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
        )
        
        cv2.rectangle(
            overlay,
            (10, y_offset - text_height - 5),
            (20 + text_width, y_offset + baseline + 5),
            (255, 255, 255),
            -1
        )
        
        cv2.putText(
            overlay,
            line,
            (15, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            thickness
        )
        y_offset += 30
    
    # Save
    cv2.imwrite(str(output_path), overlay)
    print(f"\n✅ Saved marked image to: {output_path}")
    
    return width, height


def main():
    # Paths
    base_dir = Path("/Users/VScode_Projects/projects/crc_ocr_dropin")
    run_dir = base_dir / "artifacts" / "run_20251001_185300"
    
    image_path = run_dir / "02_step2_alignment_and_crop" / "aligned_cropped" / "page_0001_aligned_cropped.png"
    output_path = run_dir / "checkbox_location_marked.png"
    
    print("Marking checkbox location...")
    print(f"Input: {image_path}")
    print(f"Output: {output_path}\n")
    
    # First checkbox at top-left corner
    checkbox_coords = [
        (285, 1240, "Box 1 (top-left)")
    ]
    
    # Mark the location
    width, height = mark_checkbox_location(image_path, output_path, checkbox_coords)
    
    print(f"\n{'='*60}")
    print("MARKED LOCATION")
    print(f"{'='*60}")
    print(f"\nBox 1 (top-left corner): ({285}, {1240})")
    print(f"Image size: {width}x{height}px")
    print(f"{'='*60}")
    print(f"\nOpen the image to verify:")
    print(f"  {output_path}")


if __name__ == "__main__":
    main()
