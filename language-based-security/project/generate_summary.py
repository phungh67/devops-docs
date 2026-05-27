import json
import glob
import os

def analyze_reports():
    print("\n==================================================")
    print(" LLM Guard - Unified Garak Test Summary")
    print("==================================================")
    
    results = {}
    total_passed = 0
    total_probes = 0

    # Find all garak JSONL reports in the current directory
    report_files = glob.glob("*.report.jsonl")
    
    if not report_files:
        print("[!] No Garak .report.jsonl files found.")
        return

    for file_path in report_files:
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    # We only care about the final evaluation scores
                    if data.get("entry_type") == "eval":
                        probe_name = data.get("probe", "unknown_probe")
                        passed = data.get("passed", 0)
                        total = data.get("total", 0)
                        
                        if probe_name not in results:
                            results[probe_name] = {"passed": 0, "total": 0}
                            
                        results[probe_name]["passed"] += passed
                        results[probe_name]["total"] += total
                except json.JSONDecodeError:
                    continue

    # Print the formatted table
    print(f"{'Probe Module':<35} | {'Passed':<8} | {'Total':<8} | {'Resistance Score'}")
    print("-" * 75)
    
    for probe, stats in sorted(results.items()):
        passed = stats['passed']
        total = stats['total']
        total_passed += passed
        total_probes += total
        
        score = (passed / total * 100) if total > 0 else 0
        print(f"{probe:<35} | {passed:<8} | {total:<8} | {score:.1f}%")

    print("-" * 75)
    overall_score = (total_passed / total_probes * 100) if total_probes > 0 else 0
    print(f"OVERALL SYSTEM RESISTANCE: {overall_score:.2f}%\n")

if __name__ == "__main__":
    analyze_reports()