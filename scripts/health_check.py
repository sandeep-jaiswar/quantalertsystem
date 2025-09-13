#!/usr/bin/env python3
"""
System health check script for the Quant Alerts System.

Performs comprehensive system validation and health monitoring
according to investment bank quality standards.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import psutil
import requests

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import get_settings


def check_system_resources() -> Dict[str, Any]:
    """Check system resource availability."""
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent_used": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent_used": round((disk.used / disk.total) * 100, 2)
            }
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_network_connectivity() -> Dict[str, Any]:
    """Check network connectivity to required services."""
    services = {
        "yahoo_finance": "https://finance.yahoo.com",
        "telegram_api": "https://api.telegram.org",
        "github": "https://github.com"
    }
    
    results = {"status": "healthy", "services": {}}
    
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=10)
            results["services"][service] = {
                "status": "accessible" if response.status_code == 200 else "degraded",
                "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2),
                "status_code": response.status_code
            }
        except Exception as e:
            results["services"][service] = {
                "status": "error",
                "error": str(e)
            }
            results["status"] = "degraded"
    
    return results


def check_configuration() -> Dict[str, Any]:
    """Validate application configuration."""
    try:
        settings = get_settings()
        
        # Basic validation
        config_status = {
            "status": "healthy",
            "telegram_configured": bool(settings.telegram_bot_token and settings.telegram_chat_id),
            "database_path": str(settings.database_path),
            "log_level": settings.log_level,
            "default_symbols": settings.default_symbols,
            "strategies_enabled": {
                "rsi": settings.rsi_strategy_enabled,
                "ma": settings.ma_strategy_enabled, 
                "bollinger": settings.bollinger_strategy_enabled,
                "consensus": settings.consensus_strategy_enabled
            }
        }
        
        # Check if directories exist
        required_dirs = ["data", "logs"]
        for dir_name in required_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                config_status[f"{dir_name}_created"] = True
            else:
                config_status[f"{dir_name}_exists"] = True
        
        return config_status
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }


def check_dependencies() -> Dict[str, Any]:
    """Check if all required dependencies are available."""
    required_packages = [
        "pandas", "numpy", "yfinance", "telegram", "duckdb", 
        "pyarrow", "pydantic", "schedule", "requests"
    ]
    
    results = {"status": "healthy", "packages": {}}
    
    for package in required_packages:
        try:
            __import__(package)
            results["packages"][package] = {"status": "available"}
        except ImportError as e:
            results["packages"][package] = {
                "status": "missing",
                "error": str(e)
            }
            results["status"] = "degraded"
    
    return results


def check_file_permissions() -> Dict[str, Any]:
    """Check file system permissions for required operations."""
    test_dirs = ["data", "logs", "reports"]
    results = {"status": "healthy", "permissions": {}}
    
    for dir_name in test_dirs:
        dir_path = Path(dir_name)
        try:
            # Ensure directory exists
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Test write permissions
            test_file = dir_path / "health_check_test.tmp"
            test_file.write_text("test")
            test_file.unlink()
            
            results["permissions"][dir_name] = {
                "readable": True,
                "writable": True,
                "status": "ok"
            }
        except Exception as e:
            results["permissions"][dir_name] = {
                "status": "error",
                "error": str(e)
            }
            results["status"] = "degraded"
    
    return results


def run_comprehensive_health_check() -> Dict[str, Any]:
    """Run comprehensive system health check."""
    health_report = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "overall_status": "healthy",
        "checks": {}
    }
    
    # Define all health checks
    health_checks = {
        "system_resources": check_system_resources,
        "network_connectivity": check_network_connectivity,
        "configuration": check_configuration,
        "dependencies": check_dependencies,
        "file_permissions": check_file_permissions
    }
    
    # Run each check
    failed_checks = []
    for check_name, check_function in health_checks.items():
        print(f"Running {check_name} check...")
        try:
            result = check_function()
            health_report["checks"][check_name] = result
            
            if result.get("status") != "healthy":
                failed_checks.append(check_name)
                
        except Exception as e:
            health_report["checks"][check_name] = {
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            }
            failed_checks.append(check_name)
    
    # Determine overall status
    if failed_checks:
        if any(health_report["checks"][check].get("status") == "error" for check in failed_checks):
            health_report["overall_status"] = "unhealthy"
        else:
            health_report["overall_status"] = "degraded"
        health_report["failed_checks"] = failed_checks
    
    return health_report


def main():
    """Main function for health check script."""
    parser = argparse.ArgumentParser(description="System health check for Quant Alerts")
    parser.add_argument(
        "--output", 
        type=str,
        default="health_check_report.json",
        help="Output file for health check report"
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
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print("🏥 Starting Quant Alerts System Health Check...")
    print("=" * 60)
    
    # Run health check
    health_report = run_comprehensive_health_check()
    
    # Save report to file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(health_report, f, indent=2, default=str)
    
    # Print summary
    print("\n📊 Health Check Summary:")
    print(f"Overall Status: {health_report['overall_status'].upper()}")
    print(f"Timestamp: {health_report['timestamp']}")
    
    if health_report['overall_status'] == 'healthy':
        print("✅ All systems operational")
    elif health_report['overall_status'] == 'degraded':
        print("⚠️  System operational with warnings")
        if 'failed_checks' in health_report:
            print(f"Warning checks: {', '.join(health_report['failed_checks'])}")
    else:
        print("❌ System has critical issues")
        if 'failed_checks' in health_report:
            print(f"Failed checks: {', '.join(health_report['failed_checks'])}")
    
    print(f"\n📄 Detailed report saved to: {output_path}")
    
    # Exit with appropriate code
    if health_report['overall_status'] == 'unhealthy':
        sys.exit(1)
    elif health_report['overall_status'] == 'degraded':
        sys.exit(2)  # Warning exit code
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()