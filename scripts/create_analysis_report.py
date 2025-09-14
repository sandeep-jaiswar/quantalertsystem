#!/usr/bin/env python3
"""
Analysis report generator for the Quant Alerts System.

Creates comprehensive HTML reports with visualizations and insights
from quantitative analysis runs.
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


def generate_html_report(data: Dict[str, Any]) -> str:
    """Generate comprehensive HTML report from analysis data."""
    
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quant Alerts Analysis Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f7fa;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .header .subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .card {{
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
        }}
        
        .card h2 {{
            color: #4a5568;
            margin-bottom: 1rem;
            font-size: 1.3rem;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0.5rem;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #f7fafc;
        }}
        
        .metric:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            font-weight: 500;
            color: #4a5568;
        }}
        
        .metric-value {{
            font-weight: 600;
            color: #2d3748;
        }}
        
        .status-excellent {{ color: #38a169; }}
        .status-good {{ color: #3182ce; }}
        .status-warning {{ color: #d69e2e; }}
        .status-error {{ color: #e53e3e; }}
        
        .progress-bar {{
            background: #e2e8f0;
            border-radius: 10px;
            height: 8px;
            overflow: hidden;
            margin-top: 0.5rem;
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }}
        
        .progress-excellent {{ background: linear-gradient(90deg, #38a169, #48bb78); }}
        .progress-good {{ background: linear-gradient(90deg, #3182ce, #4299e1); }}
        .progress-warning {{ background: linear-gradient(90deg, #d69e2e, #ecc94b); }}
        .progress-error {{ background: linear-gradient(90deg, #e53e3e, #fc8181); }}
        
        .recommendations {{
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .recommendation {{
            display: flex;
            align-items: flex-start;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid;
            background: #f7fafc;
            border-radius: 0 8px 8px 0;
        }}
        
        .recommendation.high {{ border-left-color: #e53e3e; }}
        .recommendation.medium {{ border-left-color: #d69e2e; }}
        .recommendation.low {{ border-left-color: #3182ce; }}
        
        .recommendation-icon {{
            font-size: 1.5rem;
            margin-right: 1rem;
        }}
        
        .recommendation-content h3 {{
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
            color: #2d3748;
        }}
        
        .recommendation-content p {{
            color: #4a5568;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 3rem;
            padding: 2rem;
            background: white;
            border-radius: 10px;
            color: #718096;
        }}
        
        .json-section {{
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin-top: 2rem;
        }}
        
        .json-content {{
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 5px;
            padding: 1rem;
            overflow-x: auto;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Quant Alerts Analysis Report</h1>
            <div class="subtitle">Generated on {timestamp}</div>
        </div>
        
        {summary_cards}
        
        {recommendations_section}
        
        {detailed_data}
        
        <div class="footer">
            <p>Report generated by Quant Alerts System v{version}</p>
            <p>Investment Bank Quality · Zero Cost Infrastructure · Transparent Analytics</p>
        </div>
    </div>
</body>
</html>
    """
    
    # Extract key metrics
    timestamp = data.get("metadata", {}).get("generated_at", datetime.utcnow().isoformat())
    version = "1.0.0"
    
    # Generate summary cards
    summary_cards = generate_summary_cards(data)
    
    # Generate recommendations section
    recommendations_section = generate_recommendations_section(data)
    
    # Generate detailed data section
    detailed_data = generate_detailed_data_section(data)
    
    return html_template.format(
        timestamp=timestamp,
        version=version,
        summary_cards=summary_cards,
        recommendations_section=recommendations_section,
        detailed_data=detailed_data
    )


def generate_summary_cards(data: Dict[str, Any]) -> str:
    """Generate summary cards for key metrics."""
    cards_html = '<div class="cards">'
    
    # Performance Score Card
    performance = data.get("performance_score", {})
    score = performance.get("score", 0)
    grade = performance.get("grade", "N/A")
    
    score_class = "excellent" if score >= 90 else "good" if score >= 75 else "warning" if score >= 60 else "error"
    
    cards_html += f"""
    <div class="card">
        <h2>📊 Performance Score</h2>
        <div class="metric">
            <span class="metric-label">Overall Score</span>
            <span class="metric-value status-{score_class}">{score:.1f}/100</span>
        </div>
        <div class="metric">
            <span class="metric-label">Grade</span>
            <span class="metric-value status-{score_class}">{grade}</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill progress-{score_class}" style="width: {score}%;"></div>
        </div>
    </div>
    """
    
    # Execution Metrics Card
    execution = data.get("performance_metrics", {}).get("overall", {})
    if execution:
        cards_html += f"""
        <div class="card">
            <h2>⚡ Execution Metrics</h2>
            <div class="metric">
                <span class="metric-label">Mean Time</span>
                <span class="metric-value">{execution.get('mean_time', 0):.2f}s</span>
            </div>
            <div class="metric">
                <span class="metric-label">Max Time</span>
                <span class="metric-value">{execution.get('max_time', 0):.2f}s</span>
            </div>
            <div class="metric">
                <span class="metric-label">Min Time</span>
                <span class="metric-value">{execution.get('min_time', 0):.2f}s</span>
            </div>
        </div>
        """
    
    # System Resources Card
    resources = data.get("resource_efficiency", {})
    if resources:
        memory = resources.get("memory", {})
        cpu = resources.get("cpu", {})
        
        cards_html += f"""
        <div class="card">
            <h2>💻 System Resources</h2>
            <div class="metric">
                <span class="metric-label">Memory Usage</span>
                <span class="metric-value">{memory.get('usage_percent', 0):.1f}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">CPU Usage</span>
                <span class="metric-value">{cpu.get('usage_percent', 0):.1f}%</span>
            </div>
        </div>
        """
    
    # Error Analysis Card
    errors = data.get("error_summary", {})
    if errors:
        total_errors = errors.get("total_errors", 0)
        total_warnings = errors.get("total_warnings", 0)
        
        error_class = "error" if total_errors > 0 else "warning" if total_warnings > 0 else "excellent"
        
        cards_html += f"""
        <div class="card">
            <h2>🚨 Error Analysis</h2>
            <div class="metric">
                <span class="metric-label">Total Errors</span>
                <span class="metric-value status-{error_class}">{total_errors}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Total Warnings</span>
                <span class="metric-value status-warning">{total_warnings}</span>
            </div>
        </div>
        """
    
    cards_html += '</div>'
    return cards_html


def generate_recommendations_section(data: Dict[str, Any]) -> str:
    """Generate recommendations section."""
    recommendations = data.get("recommendations", [])
    
    if not recommendations:
        return """
        <div class="recommendations">
            <h2>💡 Recommendations</h2>
            <div class="recommendation low">
                <div class="recommendation-icon">✅</div>
                <div class="recommendation-content">
                    <h3>System Operating Optimally</h3>
                    <p>No specific recommendations at this time. Continue monitoring performance metrics.</p>
                </div>
            </div>
        </div>
        """
    
    html = '<div class="recommendations"><h2>💡 Recommendations</h2>'
    
    for rec in recommendations:
        priority = rec.get("priority", "low")
        message = rec.get("message", rec.get("action", "No description available"))
        rec_type = rec.get("type", "general")
        
        icon = "🔥" if priority == "high" else "⚠️" if priority == "medium" else "💡"
        
        html += f"""
        <div class="recommendation {priority}">
            <div class="recommendation-icon">{icon}</div>
            <div class="recommendation-content">
                <h3>{rec_type.replace('_', ' ').title()} - {priority.title()} Priority</h3>
                <p>{message}</p>
            </div>
        </div>
        """
    
    html += '</div>'
    return html


def generate_detailed_data_section(data: Dict[str, Any]) -> str:
    """Generate detailed data section with collapsible JSON."""
    return f"""
    <div class="json-section">
        <h2>📋 Detailed Analysis Data</h2>
        <details>
            <summary style="cursor: pointer; font-weight: 600; margin-bottom: 1rem;">
                Click to view raw analysis data (JSON)
            </summary>
            <div class="json-content">
                <pre>{json.dumps(data, indent=2, default=str)}</pre>
            </div>
        </details>
    </div>
    """


def main():
    """Main function for analysis report generation."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive analysis report"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Input directory or file containing analysis data"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="analysis_report.html",
        help="Output HTML file for the report"
    )
    parser.add_argument(
        "--title",
        type=str,
        default="Quant Alerts Analysis Report",
        help="Report title"
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
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    print("📋 Generating analysis report...")
    
    try:
        # Load analysis data
        analysis_data = {}
        
        if input_path.is_file() and input_path.suffix == '.json':
            # Single JSON file
            with open(input_path, 'r') as f:
                analysis_data = json.load(f)
        
        elif input_path.is_dir():
            # Directory with multiple files
            json_files = list(input_path.glob("*.json"))
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r') as f:
                        file_data = json.load(f)
                    
                    # Merge data based on filename
                    if "summary" in json_file.name:
                        analysis_data.update(file_data)
                    elif "performance" in json_file.name:
                        analysis_data["performance_metrics"] = file_data
                    else:
                        # Generic merge
                        analysis_data.update(file_data)
                        
                except json.JSONDecodeError as e:
                    print(f"⚠️  Skipping invalid JSON file: {json_file} ({e})")
                    continue
        
        else:
            print(f"❌ Invalid input path: {input_path}")
            return 1
        
        # Ensure we have some data
        if not analysis_data:
            print("⚠️  No valid analysis data found")
            # Create minimal report with placeholder data
            analysis_data = {
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "status": "no_data"
                },
                "message": "No analysis data available for this run"
            }
        
        # Generate HTML report
        html_content = generate_html_report(analysis_data)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ Analysis report generated successfully")
        print(f"📄 Report saved to: {output_path}")
        print(f"🌐 Open in browser: file://{output_path.absolute()}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        logging.exception("Report generation failed")
        return 1


if __name__ == "__main__":
    exit(main())