#!/usr/bin/env python3
"""Simple script to run quantitative analysis."""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quantalertsystem.main import QuantAlertSystem


async def main():
    """Run analysis with default settings."""
    system = QuantAlertSystem()
    
    try:
        print("🚀 Starting Quantitative Analysis...")
        
        # Run analysis
        results = await system.run_analysis()
        
        if results['success']:
            print("✅ Analysis completed successfully!")
            print(f"📊 Symbols analyzed: {results['symbols_analyzed']}")
            print(f"📈 Total signals: {results['total_signals']}")
            print(f"🎯 Consensus signals: {results['consensus_signals']}")
            print(f"📱 Alerts sent: {results['alerts_sent']}")
            
            # Display top signals
            if results['actionable_signals']:
                print("\n🔝 Top Signals:")
                for i, signal in enumerate(results['actionable_signals'][:5], 1):
                    print(f"  {i}. {signal['symbol']} - {signal['signal_type']} "
                          f"({signal['confidence']:.1%} confidence)")
        else:
            print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"💥 Error: {str(e)}")
    
    finally:
        system.cleanup()


if __name__ == "__main__":
    asyncio.run(main())