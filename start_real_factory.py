#!/usr/bin/env python3
"""
Start the Real AI Factory with actual persona processors
"""

import subprocess
import sys
import time
import os

def main():
    print("🏭 Starting Real AI Factory with actual persona processors...")
    print("=" * 60)
    
    # Kill any existing processes on port 8080
    print("Checking for existing processes on port 8080...")
    try:
        result = subprocess.run(['lsof', '-ti:8080'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                print(f"Killing process {pid} on port 8080...")
                subprocess.run(['kill', '-9', pid])
            time.sleep(1)
    except:
        pass
    
    # Set Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.environ['PYTHONPATH'] = f'{current_dir}/src:{current_dir}'
    
    # Start the real factory API
    print("\n🚀 Starting Real Factory API on port 8080...")
    api_process = subprocess.Popen(
        [sys.executable, os.path.join(current_dir, 'src/api/real_factory_api.py')],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Wait for API to start
    print("Waiting for API to start...")
    time.sleep(3)
    
    # Start the dashboard
    print("\n🖥️  Starting Dashboard on port 3000...")
    dashboard_process = subprocess.Popen(
        [sys.executable, os.path.join(current_dir, 'real_dashboard.py')],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    print("\n✅ AI Factory is running!")
    print("=" * 60)
    print("📌 Dashboard: http://localhost:3000")
    print("📌 API: http://localhost:8080")
    print("\n🤖 Active Personas:")
    print("  - Steve Bot (Security Architect) ✅")
    print("  - Kav Bot (Test Engineer) ✅")
    print("  - Others: Not yet implemented ⏳")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    
    try:
        # Monitor both processes
        while True:
            # Check if processes are still running
            if api_process.poll() is not None:
                print("\n❌ API process stopped unexpectedly!")
                break
            if dashboard_process.poll() is not None:
                print("\n❌ Dashboard process stopped unexpectedly!")
                break
                
            # Print any output
            api_output = api_process.stdout.readline()
            if api_output:
                print(f"[API] {api_output.strip()}")
                
            dashboard_output = dashboard_process.stdout.readline()
            if dashboard_output:
                print(f"[Dashboard] {dashboard_output.strip()}")
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down AI Factory...")
        api_process.terminate()
        dashboard_process.terminate()
        time.sleep(1)
        api_process.kill()
        dashboard_process.kill()
        print("✅ AI Factory stopped")

if __name__ == '__main__':
    main()