#!/usr/bin/env python3
"""
Analysis summary generator for the Quant Alerts System.

Creates comprehensive summaries of analysis runs with metrics,
performance data, and actionable insights.
"""

import argparse
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import pandas as pd


def parse_log_file(log_path: Path) -> Dict[str, Any]:
    """Parse analysis log file for key metrics and events."""
    if not log_path.exists():
        return {"status": "missing", "error": f"Log file not found: {log_path}"}
    
    try:
        with open(log_path, 'r') as f:
            content = f.read()
        
        metrics = {
            "status": "parsed",
            "total_lines": len(content.splitlines()),
            "errors": [],
            "warnings": [],
            "info_messages": [],
            "performance": {},
            "symbols_processed": [],
            "signals_generated": [],
            "alerts_sent": []
        }
        
        # Parse log entries
        for line in content.splitlines():
            if "ERROR" in line:
                metrics["errors"].append(line.strip())
            elif "WARNING" in line:
                metrics["warnings"].append(line.strip())
            elif "INFO" in line:
                metrics["info_messages"].append(line.strip())
            
            # Extract symbols processed
            symbol_match = re.search(r"Processing symbol:\s+(\w+)", line)
            if symbol_match:
                metrics["symbols_processed"].append(symbol_match.group(1))
            
            # Extract signals
            signal_match = re.search(r"Generated signal for (\w+):\s+(\w+)", line)
            if signal_match:
                metrics["signals_generated"].append({
                    "symbol": signal_match.group(1),
                    "signal": signal_match.group(2)
                })
            
            # Extract performance metrics
            perf_match = re.search(r"Processing time for (\w+):\s+([\d.]+)ms", line)
            if perf_match:
                metrics["performance"][perf_match.group(1)] = float(perf_match.group(2))
        
        # Calculate summary stats
        metrics["summary"] = {
            "error_count": len(metrics["errors"]),
            "warning_count": len(metrics["warnings"]),
            "unique_symbols": len(set(metrics["symbols_processed"])),
            "total_signals": len(metrics["signals_generated"]),
            "avg_processing_time": (
                sum(metrics["performance"].values()) / len(metrics["performance"])
                if metrics["performance"] else 0
            )
        }
        
        return metrics
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }


def analyze_system_resources(input_dir: Path) -> Dict[str, Any]:
    """Analyze system resource usage during analysis."""
    resource_file = input_dir / "system_resources.json"
    
    if not resource_file.exists():
        return {"status": "missing", "message": "No system resource data found"}
    
    try:
        with open(resource_file, 'r') as f:
            resources = json.load(f)
        
        analysis = {
            "status": "analyzed",
            "resource_usage": resources,
            "recommendations": []
        }
        
        # Add recommendations based on resource usage
        if resources.get("memory_percent", 0) > 80:
            analysis["recommendations"].append({
                "type": "memory",
                "severity": "high",
                "message": "High memory usage detected. Consider optimizing data processing."
            })
        
        if resources.get("cpu_percent", 0) > 90:
            analysis["recommendations"].append({
                "type": "cpu", 
                "severity": "high",
                "message": "High CPU usage detected. Consider parallelization or optimization."
            })
        
        return analysis
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def generate_performance_metrics(input_dir: Path) -> Dict[str, Any]:
    """Generate performance metrics from analysis data."""
    metrics = {
        "status": "generated",
        "pipeline_performance": {},
        "data_quality": {},
        "strategy_effectiveness": {}
    }
    
    # Look for various log files
    log_files = list(input_dir.glob("*.log"))
    
    if not log_files:
        return {"status": "missing", "message": "No log files found for analysis"}
    
    total_processing_time = 0
    total_symbols = 0
    total_signals = 0
    
    for log_file in log_files:
        log_data = parse_log_file(log_file)
        if log_data.get("status") == "parsed":
            summary = log_data.get("summary", {})
            total_symbols += summary.get("unique_symbols", 0)
            total_signals += summary.get("total_signals", 0)
            total_processing_time += summary.get("avg_processing_time", 0)
    
    metrics["pipeline_performance"] = {
        "total_symbols_processed": total_symbols,
        "total_signals_generated": total_signals,
        "average_processing_time_ms": total_processing_time / len(log_files) if log_files else 0,
        "signals_per_symbol": total_signals / total_symbols if total_symbols > 0 else 0
    }
    
    return metrics


def create_quality_assessment(input_dir: Path) -> Dict[str, Any]:
    """Assess the quality of the analysis run."""
    assessment = {
        "status": "assessed",
        "overall_score": 100,  # Start with perfect score
        "quality_factors": {},
        "issues": [],
        "recommendations": []
    }
    
    # Check for errors in logs
    log_files = list(input_dir.glob("*.log"))
    total_errors = 0
    total_warnings = 0
    
    for log_file in log_files:
        log_data = parse_log_file(log_file)
        if log_data.get("status") == "parsed":
            summary = log_data.get("summary", {})
            total_errors += summary.get("error_count", 0)
            total_warnings += summary.get("warning_count", 0)
    
    # Deduct points for issues
    assessment["overall_score"] -= min(total_errors * 10, 50)  # Max 50 points for errors
    assessment["overall_score"] -= min(total_warnings * 2, 20)  # Max 20 points for warnings
    
    assessment["quality_factors"] = {
        "error_count": total_errors,
        "warning_count": total_warnings,
        "data_completeness": 100,  # Would need actual data to calculate
        "processing_efficiency": 100  # Would need benchmarks to compare
    }
    
    # Add recommendations based on issues
    if total_errors > 0:
        assessment["recommendations"].append({
            "priority": "high",
            "message": f"Address {total_errors} errors found in analysis logs"
        })
    
    if total_warnings > 5:
        assessment["recommendations"].append({
            "priority": "medium",
            "message": f"Review {total_warnings} warnings for potential optimizations"
        })
    
    return assessment


def generate_comprehensive_summary(input_dir: Path) -> Dict[str, Any]:
    """Generate comprehensive analysis summary."""
    summary = {
        "metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "input_directory": str(input_dir)
        },
        "execution": {},
        "performance": {},
        "quality": {},
        "system": {},
        "recommendations": []
    }
    
    # Gather all analysis components
    summary["execution"] = parse_log_file(input_dir / "analysis_output.log")
    summary["performance"] = generate_performance_metrics(input_dir)
    summary["quality"] = create_quality_assessment(input_dir)
    summary["system"] = analyze_system_resources(input_dir)
    
    # Aggregate recommendations
    all_recommendations = []
    
    for component in [summary["quality"], summary["system"]]:
        if isinstance(component, dict) and "recommendations" in component:
            all_recommendations.extend(component["recommendations"])
    
    summary["recommendations"] = all_recommendations
    
    # Determine overall status
    quality_score = summary["quality"].get("overall_score", 0)
    if quality_score >= 90:
        summary["overall_status"] = "excellent"
    elif quality_score >= 75:
        summary["overall_status"] = "good"
    elif quality_score >= 60:
        summary["overall_status"] = "acceptable"
    else:
        summary["overall_status"] = "needs_improvement"
    
    return summary


def main():
    """Main function for analysis summary generation."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive analysis summary"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input directory containing analysis logs"
    )
    parser.add_argument(
        "--output", 
        type=str,
        default="analysis_summary.json",
        help="Output file for analysis summary"
    )
    parser.add_argument(
        "--format",
        choices=["json", "html", "markdown"],
        default="json",
        help="Output format"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    input_dir = Path(args.input)
    output_path = Path(args.output)
    
    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return 1
    
    print("📊 Generating analysis summary...")
    
    # Generate summary
    try:
        summary = generate_comprehensive_summary(input_dir)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save summary based on format
        if args.format == "json":
            with open(output_path, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
        
        elif args.format == "html":
            html_content = generate_html_summary(summary)
            with open(output_path, 'w') as f:
                f.write(html_content)
        
        elif args.format == "markdown":
            md_content = generate_markdown_summary(summary)
            with open(output_path, 'w') as f:
                f.write(md_content)
        
        # Print summary
        print(f"✅ Analysis summary generated successfully")
        print(f"📄 Output saved to: {output_path}")
        print(f"📈 Overall Status: {summary.get('overall_status', 'unknown').upper()}")
        
        if summary.get('recommendations'):
            print(f"💡 Recommendations: {len(summary['recommendations'])} items")
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to generate summary: {e}")
        logging.exception("Summary generation failed")
        return 1


def generate_html_summary(summary: Dict[str, Any]) -> str:
    """Generate HTML summary report."""
    # This is a simplified version - could be expanded with templates
    html = f"""
    <html>
    <head>
        <title>Quant Analysis Summary</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
            .status-excellent {{ color: #27ae60; }}
            .status-good {{ color: #f39c12; }}
            .status-acceptable {{ color: #e67e22; }}
            .status-needs_improvement {{ color: #e74c3c; }}
        </style>
    </head>
    <body>
        <h1 class="header">Quant Analysis Summary</h1>
        <h2>Overall Status: <span class="status-{summary.get('overall_status', '')}">{summary.get('overall_status', 'Unknown').upper()}</span></h2>
        <p>Generated: {summary.get('metadata', {}).get('generated_at', 'Unknown')}</p>
        
        <h3>Performance Metrics</h3>
        <pre>{json.dumps(summary.get('performance', {}), indent=2)}</pre>
        
        <h3>Quality Assessment</h3>
        <pre>{json.dumps(summary.get('quality', {}), indent=2)}</pre>
        
        <h3>Recommendations</h3>
        <ul>
        {"".join(f"<li>{rec.get('message', 'No message')}</li>" for rec in summary.get('recommendations', []))}
        </ul>
    </body>
    </html>
    """
    return html


def generate_markdown_summary(summary: Dict[str, Any]) -> str:
    """Generate Markdown summary report."""
    md = f"""
# Quant Analysis Summary

**Overall Status:** {summary.get('overall_status', 'Unknown').upper()}
**Generated:** {summary.get('metadata', {}).get('generated_at', 'Unknown')}

## Performance Metrics

```json
{json.dumps(summary.get('performance', {}), indent=2)}
```

## Quality Assessment

```json
{json.dumps(summary.get('quality', {}), indent=2)}
```

## Recommendations

{"".join(f"- {rec.get('message', 'No message')}" for rec in summary.get('recommendations', []))}
    """
    return md


if __name__ == "__main__":
    exit(main())