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
    print(f"  Top-left: ({box_x}, {box_y})")
    print(f"  Size: {box_width}x{box_height}px")
    print(f"  Bottom-right: ({box_x + box_width}, {box_y + box_height})\n")
    
    # Draw rectangle with thick red border
    cv2.rectangle(overlay, (box_x, box_y), (box_x + box_width, box_y + box_height), (0, 0, 255), 4)
    
    # Draw corner markers for precision
    corner_size = 20
    # Top-left corner
    cv2.line(overlay, (box_x, box_y), (box_x + corner_size, box_y), (0, 255, 0), 3)
    cv2.line(overlay, (box_x, box_y), (box_x, box_y + corner_size), (0, 255, 0), 3)
    # Top-right corner
    cv2.line(overlay, (box_x + box_width, box_y), (box_x + box_width - corner_size, box_y), (0, 255, 0), 3)
    cv2.line(overlay, (box_x + box_width, box_y), (box_x + box_width, box_y + corner_size), (0, 255, 0), 3)
    # Bottom-left corner
    cv2.line(overlay, (box_x, box_y + box_height), (box_x + corner_size, box_y + box_height), (0, 255, 0), 3)
    cv2.line(overlay, (box_x, box_y + box_height), (box_x, box_y + box_height - corner_size), (0, 255, 0), 3)
    # Bottom-right corner
    cv2.line(overlay, (box_x + box_width, box_y + box_height), (box_x + box_width - corner_size, box_y + box_height), (0, 255, 0), 3)
    cv2.line(overlay, (box_x + box_width, box_y + box_height), (box_x + box_width, box_y + box_height - corner_size), (0, 255, 0), 3)
    
    # Add label with background
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    thickness = 2
    
    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
    
    # Position label above the box
    label_x = box_x + 5
    label_y = box_y - 10
    
    # Adjust if label goes off screen
    if label_y - text_height < 0:
        label_y = box_y + text_height + 10
    
    # Draw white background for label
    padding = 5
    cv2.rectangle(
        overlay,
        (label_x - padding, label_y - text_height - padding),
        (label_x + text_width + padding, label_y + baseline + padding),
        (255, 255, 255),
        -1
    )
    
    # Draw border around label
    cv2.rectangle(
        overlay,
        (label_x - padding, label_y - text_height - padding),
        (label_x + text_width + padding, label_y + baseline + padding),
        (0, 0, 255),
        2
    )
    
    # Draw label text
    cv2.putText(overlay, label, (label_x, label_y), font, font_scale, (0, 0, 255), thickness)
    
    # Add coordinate labels at corners
    coord_font_scale = 0.5
    coord_thickness = 1
    
    # Top-left coordinate
    tl_text = f"({box_x},{box_y})"
    cv2.putText(overlay, tl_text, (box_x + 5, box_y + 20), 
                cv2.FONT_HERSHEY_SIMPLEX, coord_font_scale, (255, 255, 255), coord_thickness + 1)
    cv2.putText(overlay, tl_text, (box_x + 5, box_y + 20), 
                cv2.FONT_HERSHEY_SIMPLEX, coord_font_scale, (0, 255, 0), coord_thickness)
    
    # Bottom-right coordinate
    br_text = f"({box_x + box_width},{box_y + box_height})"
    (br_width, br_height), _ = cv2.getTextSize(br_text, cv2.FONT_HERSHEY_SIMPLEX, coord_font_scale, coord_thickness)
    cv2.putText(overlay, br_text, (box_x + box_width - br_width - 5, box_y + box_height - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, coord_font_scale, (255, 255, 255), coord_thickness + 1)
    cv2.putText(overlay, br_text, (box_x + box_width - br_width - 5, box_y + box_height - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, coord_font_scale, (0, 255, 0), coord_thickness)
    
    # Add info box
    info_lines = [
        "CHECKBOX ROW MARKER",
        "RED rectangle = row boundary",
        "GREEN corners = precise edges",
        "Coordinates shown at corners",
        "Gray grid = 50px/100px reference"
    ]
    
    y_offset = 30
    for i, line in enumerate(info_lines):
        fs = 0.8 if i == 0 else 0.6
        th = 2 if i == 0 else 1
        color = (0, 0, 255) if i == 0 else (0, 0, 0)
        
        (text_width, text_height), baseline = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, fs, th)
        
        cv2.rectangle(overlay, (10, y_offset - text_height - 5),
                     (20 + text_width, y_offset + baseline + 5), (255, 255, 255), -1)
        
        cv2.putText(overlay, line, (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, fs, color, th)
        y_offset += 30
    
    # Save
    cv2.imwrite(str(output_path), overlay)
    print(f"✅ Saved marked image to: {output_path}")
    
    return img_width, img_height


def main():
    # Paths
    base_dir = Path("/Users/VScode_Projects/projects/crc_ocr_dropin")
    run_dir = base_dir / "artifacts" / "run_20251001_185300"
    
    image_path = run_dir / "02_step2_alignment_and_crop" / "aligned_cropped" / "page_0001_aligned_cropped.png"
    output_path = run_dir / "checkbox_row_box.png"
    
    print("Drawing checkbox row bounding box...")
    print(f"Input: {image_path}")
    print(f"Output: {output_path}\n")
    
    # ROW 1 - Y coordinate: 1228
    row1_y = 1228
    row1_box1_x = 280
    row1_box2_x = 690
    row1_box3_x = 1100
    row1_box4_x = 1505
    row1_box5_x = 1915
    
    # ROW 2 - Y coordinate: 1500
    row2_y = 1500
    
    # Calculate row increment
    row_increment = row2_y - row1_y  # 1500 - 1228 = 272px
    
    # ROW 3 - Y coordinate
    row3_y = row2_y + row_increment  # 1500 + 272 = 1772
    
    # ROW 4 - Y coordinate
    row4_y = row3_y + row_increment  # 1772 + 272 = 2044
    
    # ROW 5 - Y coordinate
    row5_y = row4_y + row_increment  # 2044 + 272 = 2316
    
    # Box 2: Row 2, Box 2 - Top-left (690, 1500), Bottom-right (810, 1610)
    box2_x = 690
    box2_y = row2_y
    box2_width = 810 - 690    # 120px
    box2_height = 1610 - 1500  # 110px
    
    # Box 3: Row 2, Box 1 - starts at x=280
    box3_x = 280
    box3_y = 1500
    box3_width = 120
    box3_height = 110
    
    # Calculate increment between boxes
    increment = box2_x - box3_x  # 690 - 280 = 410px
    
    # Box 4: Row 2, Box 3
    box4_x = box2_x + increment  # 690 + 410 = 1100
    box4_y = 1500
    box4_width = 120
    box4_height = 110
    
    # Box 5: Row 2, Box 4 (moved back 5px)
    box5_x = box4_x + increment - 5  # 1100 + 410 - 5 = 1505
    box5_y = 1500
    box5_width = 120
    box5_height = 110
    
    # Box 6: Row 2, Box 5 (at original position)
    box6_x = box5_x + increment  # 1505 + 410 = 1915
    box6_y = 1500
    box6_width = 120
    box6_height = 110
    
    # Load image first to draw all boxes
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
            cv2.line(overlay, (x, 0), (x, img_height), (200, 200, 200), 1)
        else:
            cv2.line(overlay, (x, 0), (x, img_height), (220, 220, 220), 1)
    
    for y in range(0, img_height + 1, 50):
        if y % 100 == 0:
            cv2.line(overlay, (0, y), (img_width, y), (200, 200, 200), 1)
        else:
            cv2.line(overlay, (0, y), (img_width, y), (220, 220, 220), 1)
    
    # Common box dimensions
    box_width = 120
    box_height = 110
    
    # Draw Row 1 boxes
    print("\n=== ROW 1 (y=1240) ===")
    row1_boxes = [
        (row1_box1_x, "R1-B1", (128, 0, 128)),   # Purple
        (row1_box2_x, "R1-B2", (0, 128, 128)),   # Teal
        (row1_box3_x, "R1-B3", (128, 128, 0)),   # Olive
        (row1_box4_x, "R1-B4", (255, 128, 0)),   # Orange
        (row1_box5_x, "R1-B5", (0, 128, 255)),   # Sky blue
    ]
    
    for x, label, color in row1_boxes:
        print(f"Drawing {label} at x={x}")
        cv2.rectangle(overlay, (x, row1_y), (x + box_width, row1_y + box_height), color, 4)
        cv2.putText(overlay, label, (x + 20, row1_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    # Draw Row 2 boxes
    print("\n=== ROW 2 (y=1500) ===")
    # Draw Box 2
    print("Drawing Box 2: Specific location")
    print(f"  Top-left: ({box2_x}, {box2_y})")
    print(f"  Size: {box2_width}x{box2_height}px")
    print(f"  Bottom-right: ({box2_x + box2_width}, {box2_y + box2_height})\n")
    
    cv2.rectangle(overlay, (box2_x, box2_y), (box2_x + box2_width, box2_y + box2_height), (255, 0, 0), 4)
    
    # Draw corner markers for Box 2
    corner_size = 15
    cv2.line(overlay, (box2_x, box2_y), (box2_x + corner_size, box2_y), (0, 255, 255), 3)
    cv2.line(overlay, (box2_x, box2_y), (box2_x, box2_y + corner_size), (0, 255, 255), 3)
    cv2.line(overlay, (box2_x + box2_width, box2_y), (box2_x + box2_width - corner_size, box2_y), (0, 255, 255), 3)
    cv2.line(overlay, (box2_x + box2_width, box2_y), (box2_x + box2_width, box2_y + corner_size), (0, 255, 255), 3)
    cv2.line(overlay, (box2_x, box2_y + box2_height), (box2_x + corner_size, box2_y + box2_height), (0, 255, 255), 3)
    cv2.line(overlay, (box2_x, box2_y + box2_height), (box2_x, box2_y + box2_height - corner_size), (0, 255, 255), 3)
    cv2.line(overlay, (box2_x + box2_width, box2_y + box2_height), (box2_x + box2_width - corner_size, box2_y + box2_height), (0, 255, 255), 3)
    cv2.line(overlay, (box2_x + box2_width, box2_y + box2_height), (box2_x + box2_width, box2_y + box2_height - corner_size), (0, 255, 255), 3)
    
    # Add label for Box 2
    label2 = "Box 2"
    cv2.putText(overlay, label2, (box2_x + 5, box2_y - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    
    # Add coordinate labels for Box 2
    tl_text = f"({box2_x},{box2_y})"
    cv2.putText(overlay, tl_text, (box2_x + 5, box2_y + 15), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    
    br_text = f"({box2_x + box2_width},{box2_y + box2_height})"
    cv2.putText(overlay, br_text, (box2_x + 5, box2_y + box2_height - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
    
    # Draw Box 3 (Row 2, Box 1)
    print("Drawing Box 3: Row 2, Box 1")
    print(f"  Top-left: ({box3_x}, {box3_y})")
    print(f"  Size: {box3_width}x{box3_height}px")
    print(f"  Bottom-right: ({box3_x + box3_width}, {box3_y + box3_height})\n")
    
    cv2.rectangle(overlay, (box3_x, box3_y), (box3_x + box3_width, box3_y + box3_height), (0, 255, 0), 4)
    
    # Draw corner markers for Box 3
    cv2.line(overlay, (box3_x, box3_y), (box3_x + corner_size, box3_y), (255, 255, 0), 3)
    cv2.line(overlay, (box3_x, box3_y), (box3_x, box3_y + corner_size), (255, 255, 0), 3)
    cv2.line(overlay, (box3_x + box3_width, box3_y), (box3_x + box3_width - corner_size, box3_y), (255, 255, 0), 3)
    cv2.line(overlay, (box3_x + box3_width, box3_y), (box3_x + box3_width, box3_y + corner_size), (255, 255, 0), 3)
    cv2.line(overlay, (box3_x, box3_y + box3_height), (box3_x + corner_size, box3_y + box3_height), (255, 255, 0), 3)
    cv2.line(overlay, (box3_x, box3_y + box3_height), (box3_x, box3_y + box3_height - corner_size), (255, 255, 0), 3)
    cv2.line(overlay, (box3_x + box3_width, box3_y + box3_height), (box3_x + box3_width - corner_size, box3_y + box3_height), (255, 255, 0), 3)
    cv2.line(overlay, (box3_x + box3_width, box3_y + box3_height), (box3_x + box3_width, box3_y + box3_height - corner_size), (255, 255, 0), 3)
    
    # Add label for Box 3
    label3 = "Box 1"
    cv2.putText(overlay, label3, (box3_x + 5, box3_y - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # Add coordinate labels for Box 3
    tl_text3 = f"({box3_x},{box3_y})"
    cv2.putText(overlay, tl_text3, (box3_x + 5, box3_y + 15), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    
    br_text3 = f"({box3_x + box3_width},{box3_y + box3_height})"
    cv2.putText(overlay, br_text3, (box3_x + 5, box3_y + box3_height - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    
    # Draw Box 4 (Row 2, Box 3)
    print(f"Drawing Box 3 at x={box4_x}")
    cv2.rectangle(overlay, (box4_x, box4_y), (box4_x + box4_width, box4_y + box4_height), (255, 0, 255), 4)
    cv2.putText(overlay, "Box 3", (box4_x + 20, box4_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
    
    # Draw Box 5 (Row 2, Box 4)
    print(f"Drawing Box 4 at x={box5_x}")
    cv2.rectangle(overlay, (box5_x, box5_y), (box5_x + box5_width, box5_y + box5_height), (255, 255, 0), 4)
    cv2.putText(overlay, "Box 4", (box5_x + 20, box5_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    
    # Draw Box 6 (Row 2, Box 5)
    print(f"Drawing Box 5 at x={box6_x}")
    cv2.rectangle(overlay, (box6_x, box6_y), (box6_x + box6_width, box6_y + box6_height), (0, 255, 255), 4)
    cv2.putText(overlay, "Box 5", (box6_x + 20, box6_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    
    # Draw Row 3 boxes
    print(f"\n=== ROW 3 (y={row3_y}) ===")
    row3_boxes = [
        (row1_box1_x, "R3-B1", (100, 100, 100)),   # Dark gray
        (row1_box2_x, "R3-B2", (200, 100, 100)),   # Brownish
        (row1_box3_x, "R3-B3", (100, 200, 100)),   # Light green
        (row1_box4_x, "R3-B4", (100, 100, 200)),   # Light blue
        (row1_box5_x, "R3-B5", (200, 200, 100)),   # Yellow-green
    ]
    for x, label, color in row3_boxes:
        print(f"Drawing {label} at x={x}")
        cv2.rectangle(overlay, (x, row3_y), (x + box_width, row3_y + box_height), color, 4)
        cv2.putText(overlay, label, (x + 20, row3_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    # Draw Row 4 boxes
    print(f"\n=== ROW 4 (y={row4_y}) ===")
    row4_boxes = [
        (row1_box1_x, "R4-B1", (150, 0, 150)),     # Purple variant
        (row1_box2_x, "R4-B2", (0, 150, 150)),     # Cyan variant
        (row1_box3_x, "R4-B3", (150, 150, 0)),     # Yellow variant
        (row1_box4_x, "R4-B4", (200, 100, 50)),    # Orange variant
        (row1_box5_x, "R4-B5", (50, 150, 200)),    # Blue variant
    ]
    for x, label, color in row4_boxes:
        print(f"Drawing {label} at x={x}")
        cv2.rectangle(overlay, (x, row4_y), (x + box_width, row4_y + box_height), color, 4)
        cv2.putText(overlay, label, (x + 20, row4_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    # Draw Row 5 boxes
    print(f"\n=== ROW 5 (y={row5_y}) ===")
    row5_boxes = [
        (row1_box1_x, "R5-B1", (180, 50, 180)),    # Magenta variant
        (row1_box2_x, "R5-B2", (50, 180, 180)),    # Turquoise
        (row1_box3_x, "R5-B3", (180, 180, 50)),    # Lime
        (row1_box4_x, "R5-B4", (220, 120, 60)),    # Rust
        (row1_box5_x, "R5-B5", (60, 160, 220)),    # Sky
    ]
    for x, label, color in row5_boxes:
        print(f"Drawing {label} at x={x}")
        cv2.rectangle(overlay, (x, row5_y), (x + box_width, row5_y + box_height), color, 4)
        cv2.putText(overlay, label, (x + 20, row5_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    # Add info box
    info_lines = [
        "CHECKBOX LAYOUT - 5 Rows x 5 Boxes",
        f"Row increment: {row_increment}px",
        f"Box increment: {increment}px",
        f"Box size: {box_width}x{box_height}px",
        "Gray grid = 50px/100px"
    ]
    
    y_offset = 30
    for i, line in enumerate(info_lines):
        fs = 0.8 if i == 0 else 0.6
        th = 2 if i == 0 else 1
        color = (0, 0, 255) if i == 0 else (0, 0, 0)
        
        (text_width, text_height), baseline = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, fs, th)
        
        cv2.rectangle(overlay, (10, y_offset - text_height - 5),
                     (20 + text_width, y_offset + baseline + 5), (255, 255, 255), -1)
        
        cv2.putText(overlay, line, (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, fs, color, th)
        y_offset += 30
    
    # Save
    cv2.imwrite(str(output_path), overlay)
    print(f"✅ Saved marked image to: {output_path}")
    
    print(f"\n{'='*60}")
    print("CHECKBOX COORDINATES SUMMARY - 5 ROWS x 5 BOXES")
    print(f"{'='*60}")
    print(f"\nRow increment: {row_increment}px")
    print(f"Box increment: {increment}px")
    print(f"Box dimensions: {box_width}x{box_height}px")
    print(f"\nX coordinates (all rows): {row1_box1_x}, {row1_box2_x}, {row1_box3_x}, {row1_box4_x}, {row1_box5_x}")
    print(f"\nY coordinates:")
    print(f"  Row 1: y={row1_y}")
    print(f"  Row 2: y={row2_y}")
    print(f"  Row 3: y={row3_y}")
    print(f"  Row 4: y={row4_y}")
    print(f"  Row 5: y={row5_y}")
    print(f"\nImage size: {img_width}x{img_height}px")
    print(f"{'='*60}")
    print(f"\nOpen the image to verify:")
    print(f"  {output_path}")


if __name__ == "__main__":
    main()
