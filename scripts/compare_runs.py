#!/usr/bin/env python3
"""
Compare runs and generate diff reports showing what changed.

This script compares configurations, metrics, and outputs between
two runs to identify differences and track improvements/regressions.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import sys


def load_json(file_path: Path) -> Optional[Dict]:
    """Load JSON file, return None if not exists."""
    if not file_path.exists():
        return None
    try:
        return json.loads(file_path.read_text())
    except Exception as e:
        print(f"Warning: Could not load {file_path}: {e}")
        return None


def compare_configs(run_a: Path, run_b: Path) -> Dict[str, Any]:
    """Compare configuration snapshots between two runs."""
    snapshot_a = run_a / "configs_snapshot"
    snapshot_b = run_b / "configs_snapshot"
    
    # Load metadata
    meta_a = load_json(snapshot_a / "metadata.json")
    meta_b = load_json(snapshot_b / "metadata.json")
    
    if not meta_a or not meta_b:
        return {"error": "Missing metadata"}
    
    # Compare checksums
    checksums_a = meta_a.get("files", {})
    checksums_b = meta_b.get("files", {})
    
    all_files = set(checksums_a.keys()) | set(checksums_b.keys())
    
    differences = []
    for filename in sorted(all_files):
        checksum_a = checksums_a.get(filename)
        checksum_b = checksums_b.get(filename)
        
        if checksum_a != checksum_b:
            differences.append({
                "file": filename,
                "changed": checksum_a is not None and checksum_b is not None,
                "added": checksum_a is None,
                "removed": checksum_b is None
            })
    
    return {
        "template_name": {
            "before": meta_a.get("template_name"),
            "after": meta_b.get("template_name"),
            "changed": meta_a.get("template_name") != meta_b.get("template_name")
        },
        "config_files": differences
    }


def compare_metrics(run_a: Path, run_b: Path) -> Dict[str, Any]:
    """Compare metrics between two runs."""
    summaries_a = load_json(run_a / "metrics" / "summaries.json")
    summaries_b = load_json(run_b / "metrics" / "summaries.json")
    
    if not summaries_a or not summaries_b:
        return {"error": "Missing metrics summaries"}
    
    # Alignment metrics delta
    align_a = summaries_a.get("alignment", {})
    align_b = summaries_b.get("alignment", {})
    
    alignment_delta = {
        "median_error_px": {
            "before": align_a.get("median_error_px"),
            "after": align_b.get("median_error_px"),
            "delta": (align_b.get("median_error_px", 0) - align_a.get("median_error_px", 0))
        },
        "max_error_px": {
            "before": align_a.get("max_error_px"),
            "after": align_b.get("max_error_px"),
            "delta": (align_b.get("max_error_px", 0) - align_a.get("max_error_px", 0))
        },
        "pages_ok": {
            "before": align_a.get("pages_ok"),
            "after": align_b.get("pages_ok"),
            "delta": (align_b.get("pages_ok", 0) - align_a.get("pages_ok", 0))
        }
    }
    
    # OCR metrics delta
    ocr_a = summaries_a.get("ocr", {})
    ocr_b = summaries_b.get("ocr", {})
    
    ocr_delta = {
        "total_text_length": {
            "before": ocr_a.get("total_text_length"),
            "after": ocr_b.get("total_text_length"),
            "delta": (ocr_b.get("total_text_length", 0) - ocr_a.get("total_text_length", 0))
        },
        "pages_with_text": {
            "before": ocr_a.get("pages_with_text"),
            "after": ocr_b.get("pages_with_text"),
            "delta": (ocr_b.get("pages_with_text", 0) - ocr_a.get("pages_with_text", 0))
        }
    }
    
    # Overall status
    overall_a = summaries_a.get("overall", {})
    overall_b = summaries_b.get("overall", {})
    
    return {
        "alignment": alignment_delta,
        "ocr": ocr_delta,
        "gates": {
            "before_pass": overall_a.get("all_gates_pass"),
            "after_pass": overall_b.get("all_gates_pass"),
            "improved": overall_b.get("all_gates_pass") and not overall_a.get("all_gates_pass"),
            "regressed": not overall_b.get("all_gates_pass") and overall_a.get("all_gates_pass")
        }
    }


def compare_environment(run_a: Path, run_b: Path) -> Dict[str, Any]:
    """Compare environment between two runs."""
    hw_a = load_json(run_a / "env" / "hardware.json")
    hw_b = load_json(run_b / "env" / "hardware.json")
    
    if not hw_a or not hw_b:
        return {"error": "Missing environment data"}
    
    differences = []
    all_keys = set(hw_a.keys()) | set(hw_b.keys())
    
    for key in sorted(all_keys):
        val_a = hw_a.get(key)
        val_b = hw_b.get(key)
        
        if val_a != val_b:
            differences.append({
                "key": key,
                "before": val_a,
                "after": val_b
            })
    
    # Compare package versions
    try:
        packages_a = (run_a / "env" / "pip_freeze.txt").read_text().splitlines()
        packages_b = (run_b / "env" / "pip_freeze.txt").read_text().splitlines()
        
        packages_changed = []
        pkgs_a_dict = {line.split("==")[0]: line for line in packages_a if "==" in line}
        pkgs_b_dict = {line.split("==")[0]: line for line in packages_b if "==" in line}
        
        for pkg_name in set(pkgs_a_dict.keys()) | set(pkgs_b_dict.keys()):
            ver_a = pkgs_a_dict.get(pkg_name)
            ver_b = pkgs_b_dict.get(pkg_name)
            
            if ver_a != ver_b:
                packages_changed.append({
                    "package": pkg_name,
                    "before": ver_a,
                    "after": ver_b
                })
    except Exception as e:
        packages_changed = [{"error": str(e)}]
    
    return {
        "hardware": differences,
        "packages": packages_changed[:10]  # Limit to first 10 for brevity
    }


def generate_diff_report(run_a: Path, run_b: Path, output_dir: Path) -> None:
    """Generate comprehensive diff report between two runs."""
    
    print(f"Generating diff report:")
    print(f"  Before: {run_a.name}")
    print(f"  After:  {run_b.name}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Compare configs
    config_diff = compare_configs(run_a, run_b)
    (output_dir / "config_diff.json").write_text(
        json.dumps(config_diff, indent=2)
    )
    print(f"  ✅ config_diff.json")
    
    # Compare metrics
    metrics_diff = compare_metrics(run_a, run_b)
    (output_dir / "metrics_delta.json").write_text(
        json.dumps(metrics_diff, indent=2)
    )
    print(f"  ✅ metrics_delta.json")
    
    # Compare environment
    env_diff = compare_environment(run_a, run_b)
    (output_dir / "environment_diff.json").write_text(
        json.dumps(env_diff, indent=2)
    )
    print(f"  ✅ environment_diff.json")
    
    # Generate summary markdown
    summary = generate_summary_markdown(run_a, run_b, config_diff, metrics_diff, env_diff)
    (output_dir / "DIFF_SUMMARY.md").write_text(summary)
    print(f"  ✅ DIFF_SUMMARY.md")


def generate_summary_markdown(
    run_a: Path,
    run_b: Path,
    config_diff: Dict,
    metrics_diff: Dict,
    env_diff: Dict
) -> str:
    """Generate human-readable diff summary."""
    
    lines = [
        f"# Diff Summary: {run_a.name} → {run_b.name}",
        "",
        "## Configuration Changes",
        ""
    ]
    
    # Config changes
    if config_diff.get("config_files"):
        for file_diff in config_diff["config_files"]:
            if file_diff.get("changed"):
                lines.append(f"- **Modified**: `{file_diff['file']}`")
            elif file_diff.get("added"):
                lines.append(f"- **Added**: `{file_diff['file']}`")
            elif file_diff.get("removed"):
                lines.append(f"- **Removed**: `{file_diff['file']}`")
    else:
        lines.append("*No configuration changes*")
    
    lines.extend([
        "",
        "## Metrics Changes",
        "",
        "### Alignment",
        ""
    ])
    
    # Alignment metrics
    if "alignment" in metrics_diff:
        align = metrics_diff["alignment"]
        
        median_delta = align["median_error_px"]["delta"]
        median_emoji = "✅" if median_delta <= 0 else "⚠️"
        lines.append(
            f"- Median error: {align['median_error_px']['before']:.2f}px → "
            f"{align['median_error_px']['after']:.2f}px "
            f"({median_delta:+.2f}px) {median_emoji}"
        )
        
        max_delta = align["max_error_px"]["delta"]
        max_emoji = "✅" if max_delta <= 0 else "⚠️"
        lines.append(
            f"- Max error: {align['max_error_px']['before']:.2f}px → "
            f"{align['max_error_px']['after']:.2f}px "
            f"({max_delta:+.2f}px) {max_emoji}"
        )
        
        pages_delta = align["pages_ok"]["delta"]
        pages_emoji = "✅" if pages_delta >= 0 else "❌"
        lines.append(
            f"- Pages OK: {align['pages_ok']['before']} → "
            f"{align['pages_ok']['after']} "
            f"({pages_delta:+d}) {pages_emoji}"
        )
    
    lines.extend([
        "",
        "### OCR",
        ""
    ])
    
    # OCR metrics
    if "ocr" in metrics_diff:
        ocr = metrics_diff["ocr"]
        
        text_delta = ocr["total_text_length"]["delta"]
        text_pct = (text_delta / ocr["total_text_length"]["before"] * 100) if ocr["total_text_length"]["before"] else 0
        lines.append(
            f"- Total text length: {ocr['total_text_length']['before']:,} → "
            f"{ocr['total_text_length']['after']:,} "
            f"({text_delta:+,} / {text_pct:+.1f}%)"
        )
    
    lines.extend([
        "",
        "## Environment Changes",
        ""
    ])
    
    # Environment changes
    if env_diff.get("packages"):
        lines.append("### Package Changes")
        lines.append("")
        for pkg_diff in env_diff["packages"][:5]:  # First 5
            if "error" not in pkg_diff:
                lines.append(f"- `{pkg_diff['package']}`")
                if pkg_diff.get("before"):
                    lines.append(f"  - Before: `{pkg_diff['before']}`")
                if pkg_diff.get("after"):
                    lines.append(f"  - After: `{pkg_diff['after']}`")
    
    if env_diff.get("hardware"):
        lines.append("")
        lines.append("### Hardware Changes")
        lines.append("")
        for hw_diff in env_diff["hardware"]:
            lines.append(f"- **{hw_diff['key']}**: `{hw_diff['before']}` → `{hw_diff['after']}`")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare two processing runs")
    parser.add_argument("run_before", type=Path, help="Earlier run directory")
    parser.add_argument("run_after", type=Path, help="Later run directory")
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory (default: run_after/diffs/against_run_before)"
    )
    
    args = parser.parse_args()
    
    if not args.run_before.exists():
        print(f"❌ Run directory not found: {args.run_before}")
        sys.exit(1)
    
    if not args.run_after.exists():
        print(f"❌ Run directory not found: {args.run_after}")
        sys.exit(1)
    
    # Default output directory
    if args.output is None:
        args.output = args.run_after / "diffs" / f"against_{args.run_before.name}"
    
    generate_diff_report(args.run_before, args.run_after, args.output)
    
    print(f"\n✅ Diff report generated: {args.output}")
    print(f"   View summary: {args.output / 'DIFF_SUMMARY.md'}")
