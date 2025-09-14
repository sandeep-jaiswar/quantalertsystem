#!/usr/bin/env python3
"""
Performance metrics analyzer for the Quant Alerts System.

Analyzes system performance, identifies bottlenecks, and provides
optimization recommendations based on execution data.
"""

import argparse
import json
import logging
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import pandas as pd


def analyze_execution_times(log_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze execution times from log data."""
    execution_times = []
    component_times = {}
    
    for entry in log_data:
        if "execution_time" in entry:
            execution_times.append(entry["execution_time"])
        
        if "component" in entry and "duration" in entry:
            component = entry["component"]
            if component not in component_times:
                component_times[component] = []
            component_times[component].append(entry["duration"])
    
    analysis = {
        "total_executions": len(execution_times),
        "performance_metrics": {}
    }
    
    if execution_times:
        analysis["performance_metrics"]["overall"] = {
            "mean_time": statistics.mean(execution_times),
            "median_time": statistics.median(execution_times),
            "min_time": min(execution_times),
            "max_time": max(execution_times),
            "std_dev": statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        }
    
    # Analyze component performance
    for component, times in component_times.items():
        if times:
            analysis["performance_metrics"][component] = {
                "mean_time": statistics.mean(times),
                "median_time": statistics.median(times),
                "min_time": min(times),
                "max_time": max(times),
                "execution_count": len(times),
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0
            }
    
    return analysis


def analyze_resource_usage(resource_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze system resource usage patterns."""
    analysis = {
        "resource_efficiency": {},
        "bottlenecks": [],
        "recommendations": []
    }
    
    # Memory analysis
    if "memory" in resource_data:
        memory = resource_data["memory"]
        memory_usage = memory.get("percent_used", 0)
        
        analysis["resource_efficiency"]["memory"] = {
            "usage_percent": memory_usage,
            "status": "efficient" if memory_usage < 70 else "high" if memory_usage < 90 else "critical"
        }
        
        if memory_usage > 80:
            analysis["bottlenecks"].append({
                "type": "memory",
                "severity": "high" if memory_usage > 90 else "medium",
                "description": f"High memory usage: {memory_usage}%"
            })
            analysis["recommendations"].append({
                "type": "memory",
                "priority": "high",
                "action": "Consider implementing data streaming or batch processing for large datasets"
            })
    
    # CPU analysis
    if "cpu_percent" in resource_data:
        cpu_usage = resource_data["cpu_percent"]
        
        analysis["resource_efficiency"]["cpu"] = {
            "usage_percent": cpu_usage,
            "status": "efficient" if cpu_usage < 80 else "high" if cpu_usage < 95 else "critical"
        }
        
        if cpu_usage > 85:
            analysis["bottlenecks"].append({
                "type": "cpu",
                "severity": "high" if cpu_usage > 95 else "medium",
                "description": f"High CPU usage: {cpu_usage}%"
            })
            analysis["recommendations"].append({
                "type": "cpu",
                "priority": "medium",
                "action": "Consider parallel processing or algorithm optimization"
            })
    
    return analysis


def analyze_error_patterns(log_entries: List[str]) -> Dict[str, Any]:
    """Analyze error patterns and frequencies."""
    errors = [line for line in log_entries if "ERROR" in line]
    warnings = [line for line in log_entries if "WARNING" in line]
    
    error_types = {}
    warning_types = {}
    
    # Categorize errors
    for error in errors:
        # Simple categorization based on keywords
        if "network" in error.lower() or "connection" in error.lower():
            error_types["network"] = error_types.get("network", 0) + 1
        elif "timeout" in error.lower():
            error_types["timeout"] = error_types.get("timeout", 0) + 1
        elif "data" in error.lower() or "parse" in error.lower():
            error_types["data_processing"] = error_types.get("data_processing", 0) + 1
        else:
            error_types["other"] = error_types.get("other", 0) + 1
    
    # Categorize warnings
    for warning in warnings:
        if "rate limit" in warning.lower():
            warning_types["rate_limit"] = warning_types.get("rate_limit", 0) + 1
        elif "missing" in warning.lower() or "not found" in warning.lower():
            warning_types["missing_data"] = warning_types.get("missing_data", 0) + 1
        else:
            warning_types["other"] = warning_types.get("other", 0) + 1
    
    analysis = {
        "error_summary": {
            "total_errors": len(errors),
            "total_warnings": len(warnings),
            "error_types": error_types,
            "warning_types": warning_types
        },
        "reliability_metrics": {
            "error_rate": len(errors) / max(len(log_entries), 1),
            "warning_rate": len(warnings) / max(len(log_entries), 1)
        }
    }
    
    # Add recommendations based on error patterns
    recommendations = []
    
    if error_types.get("network", 0) > 0:
        recommendations.append({
            "type": "reliability",
            "priority": "high",
            "action": "Implement robust retry logic and network error handling"
        })
    
    if error_types.get("timeout", 0) > 0:
        recommendations.append({
            "type": "performance",
            "priority": "medium", 
            "action": "Review timeout configurations and optimize slow operations"
        })
    
    if warning_types.get("rate_limit", 0) > 0:
        recommendations.append({
            "type": "configuration",
            "priority": "medium",
            "action": "Adjust API rate limiting parameters"
        })
    
    analysis["recommendations"] = recommendations
    return analysis


def generate_performance_score(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Generate overall performance score based on various metrics."""
    score = 100  # Start with perfect score
    factors = {}
    
    # Performance factors
    if "performance_metrics" in metrics:
        perf = metrics["performance_metrics"]
        if "overall" in perf:
            mean_time = perf["overall"].get("mean_time", 0)
            # Deduct points for slow execution (assuming target is < 60 seconds)
            if mean_time > 60:
                deduction = min((mean_time - 60) / 10, 30)  # Max 30 points
                score -= deduction
                factors["execution_speed"] = f"-{deduction:.1f} (slow execution: {mean_time:.1f}s)"
    
    # Resource efficiency factors
    if "resource_efficiency" in metrics:
        resource = metrics["resource_efficiency"]
        
        if "memory" in resource and resource["memory"]["status"] in ["high", "critical"]:
            deduction = 15 if resource["memory"]["status"] == "high" else 25
            score -= deduction
            factors["memory_usage"] = f"-{deduction} ({resource['memory']['status']} memory usage)"
        
        if "cpu" in resource and resource["cpu"]["status"] in ["high", "critical"]:
            deduction = 10 if resource["cpu"]["status"] == "high" else 20
            score -= deduction
            factors["cpu_usage"] = f"-{deduction} ({resource['cpu']['status']} CPU usage)"
    
    # Reliability factors
    if "reliability_metrics" in metrics:
        reliability = metrics["reliability_metrics"]
        error_rate = reliability.get("error_rate", 0)
        
        if error_rate > 0.01:  # More than 1% error rate
            deduction = min(error_rate * 100, 20)  # Max 20 points
            score -= deduction
            factors["error_rate"] = f"-{deduction:.1f} (error rate: {error_rate:.2%})"
    
    return {
        "score": max(score, 0),  # Ensure score doesn't go below 0
        "grade": get_performance_grade(score),
        "factors": factors
    }


def get_performance_grade(score: float) -> str:
    """Convert performance score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def analyze_trends(historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze performance trends over time."""
    if len(historical_data) < 2:
        return {"status": "insufficient_data", "message": "Need at least 2 data points for trend analysis"}
    
    # Extract time series data
    scores = []
    execution_times = []
    timestamps = []
    
    for data in historical_data:
        if "timestamp" in data and "performance_score" in data:
            timestamps.append(data["timestamp"])
            scores.append(data["performance_score"]["score"])
        
        if "performance_metrics" in data:
            overall = data["performance_metrics"].get("overall", {})
            if "mean_time" in overall:
                execution_times.append(overall["mean_time"])
    
    trends = {"status": "analyzed"}
    
    # Analyze score trend
    if len(scores) >= 2:
        score_trend = "improving" if scores[-1] > scores[0] else "declining"
        score_change = scores[-1] - scores[0]
        trends["score_trend"] = {
            "direction": score_trend,
            "change": score_change,
            "current_score": scores[-1],
            "data_points": len(scores)
        }
    
    # Analyze execution time trend
    if len(execution_times) >= 2:
        time_trend = "improving" if execution_times[-1] < execution_times[0] else "declining"
        time_change = execution_times[-1] - execution_times[0]
        trends["execution_time_trend"] = {
            "direction": time_trend,
            "change_seconds": time_change,
            "current_time": execution_times[-1],
            "data_points": len(execution_times)
        }
    
    return trends


def main():
    """Main function for performance metrics analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze performance metrics for Quant Alerts System"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input directory containing log files"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="performance_metrics.json",
        help="Output file for performance analysis"
    )
    parser.add_argument(
        "--historical",
        type=str,
        help="Path to historical performance data for trend analysis"
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
    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return 1
    
    print("📊 Analyzing performance metrics...")
    
    try:
        # Collect all available data
        log_files = list(input_dir.glob("*.log"))
        json_files = list(input_dir.glob("*.json"))
        
        # Parse log data
        all_log_entries = []
        for log_file in log_files:
            with open(log_file, 'r') as f:
                all_log_entries.extend(f.readlines())
        
        # Parse JSON data
        resource_data = {}
        execution_data = []
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                if "cpu" in data or "memory" in data:
                    resource_data.update(data)
                elif isinstance(data, list):
                    execution_data.extend(data)
                elif "execution_time" in data:
                    execution_data.append(data)
                    
            except json.JSONDecodeError:
                continue
        
        # Perform analysis
        performance_analysis = {
            "metadata": {
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "input_directory": str(input_dir),
                "log_files_analyzed": len(log_files),
                "json_files_analyzed": len(json_files)
            }
        }
        
        # Analyze different aspects
        performance_analysis.update(analyze_execution_times(execution_data))
        
        if resource_data:
            performance_analysis.update(analyze_resource_usage(resource_data))
        
        if all_log_entries:
            error_analysis = analyze_error_patterns(all_log_entries)
            performance_analysis.update(error_analysis)
        
        # Generate performance score
        performance_score = generate_performance_score(performance_analysis)
        performance_analysis["performance_score"] = performance_score
        
        # Historical trend analysis
        if args.historical and Path(args.historical).exists():
            try:
                with open(args.historical, 'r') as f:
                    historical_data = json.load(f)
                
                trends = analyze_trends(historical_data + [performance_analysis])
                performance_analysis["trends"] = trends
                
            except Exception as e:
                print(f"⚠️  Could not analyze trends: {e}")
        
        # Save results
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(performance_analysis, f, indent=2, default=str)
        
        # Print summary
        print("✅ Performance analysis completed")
        print(f"📄 Results saved to: {output_path}")
        
        score_info = performance_analysis.get("performance_score", {})
        print(f"📈 Performance Score: {score_info.get('score', 'N/A'):.1f}/100 (Grade: {score_info.get('grade', 'N/A')})")
        
        if "recommendations" in performance_analysis:
            print(f"💡 Recommendations: {len(performance_analysis['recommendations'])} items")
        
        return 0
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        logging.exception("Performance analysis failed")
        return 1


if __name__ == "__main__":
    exit(main())