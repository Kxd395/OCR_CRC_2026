#!/usr/bin/env python3
"""
Gemma Secondary Review - Use Gemma 3 (or higher model) for secondary verification
of uncertain detections identified in review queue.

This provides AI-assisted verification for:
  - Near-threshold detections
  - Conflicting selections
  - Low confidence boxes

Can be run automatically after build_review_queue.py or manually on specific pages.
"""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
import requests
import yaml

def call_gemma_api(image_path, checkbox_roi, question_context, threshold):
    """
    Call Gemma 3 API for checkbox verification
    
    Args:
        image_path: Path to aligned page image
        checkbox_roi: Dict with x, y, w, h (normalized coordinates)
        question_context: Dict with question info
        threshold: Current detection threshold
    
    Returns:
        Dict with: {
            "checked": bool,
            "confidence": float (0-1),
            "reasoning": str
        }
    """
    # TODO: Replace with actual Gemma API endpoint
    # This is a placeholder showing the interface
    
    # Load and extract checkbox region
    img = cv2.imread(str(image_path))
    h, w = img.shape[:2]
    
    x = int(checkbox_roi["x"] * w)
    y = int(checkbox_roi["y"] * h)
    box_w = int(checkbox_roi["w"] * w)
    box_h = int(checkbox_roi["h"] * h)
    
    crop = img[y:y+box_h, x:x+box_w]
    
    # Convert to base64 or save temp file for API
    _, buffer = cv2.imencode('.png', crop)
    
    # Prepare prompt for Gemma
    prompt = f"""
You are analyzing a checkbox from a scanned survey form.

Context:
- Question: {question_context.get('question_text', 'N/A')}
- Checkbox ID: {question_context.get('checkbox_id')}
- Current detection threshold: {threshold*100:.1f}%

Task: Determine if this checkbox is marked/filled.

Provide:
1. checked: true/false
2. confidence: 0.0-1.0 (how certain you are)
3. reasoning: Brief explanation of your decision

Consider:
- Partial marks (light pencil, incomplete fill)
- Print artifacts (scan noise, shadows)
- Intentional marks vs accidental marks
"""
    
    # Placeholder response - replace with actual API call
    # Example API call structure:
    """
    response = requests.post(
        "https://api.gemini.google.com/v1/models/gemma-3:analyze",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "image": base64_image,
            "prompt": prompt,
            "temperature": 0.1,  # Low temp for consistency
        }
    )
    result = response.json()
    """
    
    # For now, return structure showing expected format
    return {
        "checked": None,  # Replace with API response
        "confidence": None,
        "reasoning": "Gemma API not configured - see gemma_secondary_review.py",
        "api_configured": False
    }

def main():
    ap = argparse.ArgumentParser(description="Secondary AI review using Gemma 3")
    ap.add_argument("--run-dir", help="Run directory (default: latest)")
    ap.add_argument("--review-queue", help="Path to review_queue.csv (default: auto-detect)")
    ap.add_argument("--priority", choices=["HIGH", "MEDIUM", "LOW", "ALL"], default="HIGH",
                   help="Which priority level to review (default: HIGH)")
    ap.add_argument("--api-config", default="configs/gemma.yaml", 
                   help="Gemma API configuration file")
    ap.add_argument("--output", help="Output file for secondary review results")
    args = ap.parse_args()

    # Find run directory
    if args.run_dir:
        run = Path(args.run_dir)
    else:
        artifacts = Path("artifacts")
        runs = sorted([d for d in artifacts.glob("run_*") if d.is_dir()])
        if not runs:
            print("❌ No run directories found")
            return
        run = runs[-1]
    
    print(f"\n{'='*70}")
    print("GEMMA SECONDARY REVIEW")
    print(f"{'='*70}")
    print(f"Run: {run.name}")
    print(f"Priority: {args.priority}")
    
    # Load review queue
    if args.review_queue:
        queue_file = Path(args.review_queue)
    else:
        queue_file = run / "review" / "review_queue.csv"
    
    if not queue_file.exists():
        print(f"❌ Review queue not found: {queue_file}")
        print("Run build_review_queue.py first")
        return
    
    import pandas as pd
    queue = pd.read_csv(queue_file)
    
    # Filter by priority
    if args.priority != "ALL":
        queue = queue[queue["priority"] == args.priority]
    
    if queue.empty:
        print(f"✅ No pages with priority {args.priority} need review")
        return
    
    print(f"Pages to review: {len(queue)}")
    
    # Load API config
    api_config = {}
    if Path(args.api_config).exists():
        api_config = yaml.safe_load(open(args.api_config))
    else:
        print(f"⚠️  Gemma config not found: {args.api_config}")
        print("   Secondary review will run in dry-run mode")
    
    # Load OCR results and template
    results_file = run / "step4_ocr_results" / "results.json"
    results = json.loads(results_file.read_text())
    
    # Load template for question context
    template_file = Path("templates/crc_survey_l_anchors_v1/template.json")
    if template_file.exists():
        template = json.loads(template_file.read_text())
        checkbox_rois = {roi["id"]: roi for roi in template.get("checkbox_rois_norm", [])}
    else:
        checkbox_rois = {}
    
    # Process each page in queue
    secondary_results = []
    images_dir = run / "step2_alignment_and_crop" / "aligned_cropped"
    
    for idx, row in queue.iterrows():
        page_name = row["page"]
        print(f"\n📄 Reviewing {page_name}...")
        
        # Find page results
        page_result = next((p for p in results if p["page"] == page_name), None)
        if not page_result:
            print(f"  ⚠️  No results found for {page_name}")
            continue
        
        # Get image path
        image_path = images_dir / page_name
        if not image_path.exists():
            print(f"  ⚠️  Image not found: {image_path}")
            continue
        
        # Review each checkbox with issues
        for box in page_result.get("checkboxes", []):
            box_id = box["id"]
            score = box.get("score", 0)
            checked = box.get("checked", False)
            
            # Check if this box needs secondary review
            # (near threshold or low confidence)
            needs_review = False
            reason = ""
            
            # You can customize these thresholds
            if abs(score - 0.115) < 0.03:  # Within 3% of threshold
                needs_review = True
                reason = "near-threshold"
            elif score > 0.08 and score < 0.15:  # Uncertain range
                needs_review = True
                reason = "low-confidence"
            
            if not needs_review:
                continue
            
            print(f"  🔍 {box_id}: {score*100:.1f}% (original: {'✓' if checked else '✗'})")
            
            # Get ROI info
            roi = checkbox_rois.get(box_id, {})
            
            # Call Gemma API (or dry-run)
            question_context = {
                "checkbox_id": box_id,
                "question_text": roi.get("label", ""),
            }
            
            gemma_result = call_gemma_api(
                image_path, 
                roi, 
                question_context, 
                0.115
            )
            
            # Store result
            secondary_results.append({
                "page": page_name,
                "checkbox_id": box_id,
                "original_score": score,
                "original_checked": checked,
                "gemma_checked": gemma_result.get("checked"),
                "gemma_confidence": gemma_result.get("confidence"),
                "gemma_reasoning": gemma_result.get("reasoning"),
                "review_reason": reason,
                "agreement": gemma_result.get("checked") == checked if gemma_result.get("checked") is not None else None
            })
            
            if gemma_result.get("api_configured"):
                print(f"    Gemma: {'✓' if gemma_result['checked'] else '✗'} "
                     f"(confidence: {gemma_result['confidence']*100:.0f}%)")
                if gemma_result["checked"] != checked:
                    print(f"    ⚠️  DISAGREEMENT - manual review recommended")
    
    # Save results
    if secondary_results:
        output_file = args.output
        if not output_file:
            output_file = run / "review" / "gemma_secondary_review.json"
        else:
            output_file = Path(output_file)
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(secondary_results, f, indent=2)
        
        print(f"\n{'='*70}")
        print("SECONDARY REVIEW SUMMARY")
        print(f"{'='*70}")
        print(f"Total checkboxes reviewed: {len(secondary_results)}")
        
        if any(r.get("api_configured") for r in secondary_results):
            agreements = [r for r in secondary_results if r.get("agreement") is True]
            disagreements = [r for r in secondary_results if r.get("agreement") is False]
            print(f"Agreements: {len(agreements)}")
            print(f"Disagreements: {len(disagreements)}")
            
            if disagreements:
                print(f"\n⚠️  {len(disagreements)} disagreements found - manual review recommended:")
                for d in disagreements[:5]:  # Show first 5
                    print(f"  - {d['page']}: {d['checkbox_id']}")
        else:
            print("\n⚠️  Gemma API not configured - dry run only")
            print("To enable Gemma secondary review:")
            print("1. Configure configs/gemma.yaml with API credentials")
            print("2. Implement API call in gemma_secondary_review.py")
        
        print(f"\n📁 Results saved: {output_file}")
        print(f"{'='*70}\n")
    else:
        print("\n✅ No checkboxes required secondary review")

if __name__ == "__main__":
    main()
