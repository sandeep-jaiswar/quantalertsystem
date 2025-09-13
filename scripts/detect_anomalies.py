#!/usr/bin/env python3
"""
Anomaly detection script for the Quant Alerts System.

Detects unusual patterns, performance anomalies, and potential issues
in quantitative analysis runs using statistical methods.
"""

import argparse
import json
import logging
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


def detect_performance_anomalies(metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Detect performance anomalies in execution metrics."""
    anomalies = []
    
    # Check overall performance
    overall_metrics = metrics.get("performance_metrics", {}).get("overall", {})
    if overall_metrics:
        mean_time = overall_metrics.get("mean_time", 0)
        max_time = overall_metrics.get("max_time", 0)
        
        # Anomaly: Execution time too high
        if mean_time > 120:  # 2 minutes threshold
            anomalies.append({
                "type": "performance",
                "severity": "high",
                "description": f"Mean execution time is unusually high: {mean_time:.2f}s",
                "metric": "execution_time",
                "value": mean_time,
                "threshold": 120,
                "recommendation": "Investigate slow data processing or network issues"
            })
        
        # Anomaly: Large variance in execution times
        if max_time > mean_time * 3 and mean_time > 0:
            anomalies.append({
                "type": "performance",
                "severity": "medium", 
                "description": f"High variance in execution times (max: {max_time:.2f}s, mean: {mean_time:.2f}s)",
                "metric": "execution_variance",
                "value": max_time / mean_time,
                "threshold": 3.0,
                "recommendation": "Check for intermittent network or processing issues"
            })
    
    return anomalies


def detect_resource_anomalies(resource_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Detect resource usage anomalies."""
    anomalies = []
    
    # Memory anomalies
    memory = resource_data.get("memory", {})
    if memory:
        memory_percent = memory.get("percent_used", 0)
        
        if memory_percent > 95:
            anomalies.append({
                "type": "resource",
                "severity": "critical",
                "description": f"Critical memory usage: {memory_percent}%",
                "metric": "memory_usage",
                "value": memory_percent,
                "threshold": 95,
                "recommendation": "Immediate action required - system may become unstable"
            })
        elif memory_percent > 85:
            anomalies.append({
                "type": "resource",
                "severity": "high",
                "description": f"High memory usage: {memory_percent}%",
                "metric": "memory_usage", 
                "value": memory_percent,
                "threshold": 85,
                "recommendation": "Consider optimizing data processing or increasing memory"
            })
    
    # CPU anomalies
    cpu_percent = resource_data.get("cpu_percent", 0)
    if cpu_percent > 98:
        anomalies.append({
            "type": "resource",
            "severity": "high",
            "description": f"Extremely high CPU usage: {cpu_percent}%",
            "metric": "cpu_usage",
            "value": cpu_percent,
            "threshold": 98,
            "recommendation": "Check for infinite loops or CPU-intensive operations"
        })
    
    return anomalies


def detect_error_anomalies(error_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Detect error patterns and anomalies."""
    anomalies = []
    
    error_summary = error_data.get("error_summary", {})
    if error_summary:
        total_errors = error_summary.get("total_errors", 0)
        total_warnings = error_summary.get("total_warnings", 0)
        error_types = error_summary.get("error_types", {})
        
        # Anomaly: High error rate
        if total_errors > 10:
            anomalies.append({
                "type": "reliability",
                "severity": "high",
                "description": f"High number of errors: {total_errors}",
                "metric": "error_count",
                "value": total_errors,
                "threshold": 10,
                "recommendation": "Review error logs and improve error handling"
            })
        
        # Anomaly: Excessive warnings
        if total_warnings > 50:
            anomalies.append({
                "type": "reliability", 
                "severity": "medium",
                "description": f"Excessive warnings: {total_warnings}",
                "metric": "warning_count",
                "value": total_warnings,
                "threshold": 50,
                "recommendation": "Review warning patterns and address underlying issues"
            })
        
        # Anomaly: Network error concentration
        network_errors = error_types.get("network", 0)
        if network_errors > 5:
            anomalies.append({
                "type": "network",
                "severity": "medium",
                "description": f"High network error count: {network_errors}",
                "metric": "network_errors",
                "value": network_errors,
                "threshold": 5,
                "recommendation": "Check network connectivity and implement better retry logic"
            })
    
    return anomalies


def detect_data_anomalies(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Detect data quality and processing anomalies."""
    anomalies = []
    
    # Check for missing or incomplete data
    execution_data = data.get("execution", {})
    if execution_data.get("status") == "parsed":
        summary = execution_data.get("summary", {})
        symbols_processed = summary.get("unique_symbols", 0)
        signals_generated = summary.get("total_signals", 0)
        
        # Anomaly: No signals generated
        if symbols_processed > 0 and signals_generated == 0:
            anomalies.append({
                "type": "data_quality",
                "severity": "medium",
                "description": f"No signals generated despite processing {symbols_processed} symbols",
                "metric": "signal_generation",
                "value": 0,
                "threshold": 1,
                "recommendation": "Check strategy parameters and market data quality"
            })
        
        # Anomaly: Very low signal rate
        if symbols_processed > 10 and signals_generated > 0:
            signal_rate = signals_generated / symbols_processed
            if signal_rate < 0.1:  # Less than 10% signal rate
                anomalies.append({
                    "type": "data_quality",
                    "severity": "low",
                    "description": f"Low signal generation rate: {signal_rate:.2%}",
                    "metric": "signal_rate",
                    "value": signal_rate,
                    "threshold": 0.1,
                    "recommendation": "Review strategy sensitivity and market conditions"
                })
    
    return anomalies


def detect_configuration_anomalies(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Detect configuration-related anomalies."""
    anomalies = []
    
    # Check configuration status
    config = data.get("configuration", {})
    if config.get("status") == "error":
        anomalies.append({
            "type": "configuration",
            "severity": "critical",
            "description": f"Configuration error: {config.get('error', 'Unknown error')}",
            "metric": "config_status",
            "value": "error",
            "threshold": "healthy",
            "recommendation": "Fix configuration issues before running analysis"
        })
    
    # Check for test mode in production
    if data.get("metadata", {}).get("test_mode") and data.get("metadata", {}).get("environment") == "production":
        anomalies.append({
            "type": "configuration",
            "severity": "medium",
            "description": "Test mode enabled in production environment",
            "metric": "test_mode_production",
            "value": True,
            "threshold": False,
            "recommendation": "Disable test mode for production runs"
        })
    
    return anomalies


def calculate_anomaly_score(anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate overall anomaly score based on detected anomalies."""
    if not anomalies:
        return {
            "score": 0,
            "level": "normal",
            "description": "No anomalies detected"
        }
    
    # Weight anomalies by severity
    severity_weights = {"critical": 10, "high": 5, "medium": 2, "low": 1}
    total_score = sum(severity_weights.get(a.get("severity", "low"), 1) for a in anomalies)
    
    # Determine level
    if total_score >= 20:
        level = "critical"
        description = "Critical anomalies detected requiring immediate attention"
    elif total_score >= 10:
        level = "high"
        description = "Significant anomalies detected"
    elif total_score >= 5:
        level = "medium"
        description = "Moderate anomalies detected"
    else:
        level = "low"
        description = "Minor anomalies detected"
    
    return {
        "score": total_score,
        "level": level,
        "description": description,
        "anomaly_count": len(anomalies)
    }


def generate_anomaly_report(input_dir: Path) -> Dict[str, Any]:
    """Generate comprehensive anomaly report."""
    report = {
        "metadata": {
            "generated_at": datetime.utcnow().isoformat(),
            "input_directory": str(input_dir),
            "version": "1.0.0"
        },
        "anomalies": [],
        "summary": {}
    }
    
    # Load analysis data from various sources
    analysis_files = {
        "summary": input_dir / "analysis_summary.json",
        "performance": input_dir / "performance_metrics.json", 
        "health": input_dir / "health_check_report.json"
    }
    
    combined_data = {}
    
    for data_type, file_path in analysis_files.items():
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    combined_data[data_type] = data
                    if isinstance(data, dict):
                        combined_data.update(data)
            except (json.JSONDecodeError, IOError):
                continue
    
    # Run anomaly detection
    all_anomalies = []
    
    # Performance anomalies
    all_anomalies.extend(detect_performance_anomalies(combined_data))
    
    # Resource anomalies
    if "system_resources" in combined_data:
        all_anomalies.extend(detect_resource_anomalies(combined_data["system_resources"]))
    
    # Error anomalies
    all_anomalies.extend(detect_error_anomalies(combined_data))
    
    # Data quality anomalies
    all_anomalies.extend(detect_data_anomalies(combined_data))
    
    # Configuration anomalies
    all_anomalies.extend(detect_configuration_anomalies(combined_data))
    
    # Calculate overall score
    anomaly_score = calculate_anomaly_score(all_anomalies)
    
    report["anomalies"] = all_anomalies
    report["summary"] = anomaly_score
    
    return report


def main():
    """Main function for anomaly detection."""
    parser = argparse.ArgumentParser(
        description="Detect anomalies in Quant Alerts analysis runs"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input directory containing analysis data"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="anomalies.json",
        help="Output file for anomaly report"
    )
    parser.add_argument(
        "--threshold",
        type=str,
        choices=["low", "medium", "high", "critical"],
        default="medium",
        help="Minimum severity threshold for reporting"
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
    
    print("🔍 Detecting anomalies in analysis data...")
    
    try:
        # Generate anomaly report
        report = generate_anomaly_report(input_dir)
        
        # Filter by threshold
        threshold_order = ["low", "medium", "high", "critical"]
        min_threshold_idx = threshold_order.index(args.threshold)
        
        filtered_anomalies = [
            a for a in report["anomalies"]
            if threshold_order.index(a.get("severity", "low")) >= min_threshold_idx
        ]
        
        report["filtered_anomalies"] = filtered_anomalies
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save report
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print("✅ Anomaly detection completed")
        print(f"📄 Report saved to: {output_path}")
        print(f"🚨 Anomalies detected: {len(report['anomalies'])} total, {len(filtered_anomalies)} above threshold")
        
        summary = report.get("summary", {})
        print(f"📊 Anomaly Score: {summary.get('score', 0)} ({summary.get('level', 'unknown')})")
        
        # Print critical anomalies
        critical_anomalies = [a for a in report["anomalies"] if a.get("severity") == "critical"]
        if critical_anomalies:
            print(f"\n🔥 Critical Anomalies:")
            for anomaly in critical_anomalies:
                print(f"  - {anomaly.get('description', 'No description')}")
        
        # Return appropriate exit code
        if summary.get("level") == "critical":
            return 2  # Critical issues
        elif summary.get("level") in ["high", "medium"] and len(filtered_anomalies) > 0:
            return 1  # Issues found
        else:
            return 0  # No significant issues
        
    except Exception as e:
        print(f"❌ Anomaly detection failed: {e}")
        logging.exception("Anomaly detection failed")
        return 1


if __name__ == "__main__":
    exit(main())