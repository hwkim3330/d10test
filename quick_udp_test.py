#!/usr/bin/env python3
import subprocess
import re

print("=== Systematic UDP Throughput Test ===\n")

bandwidths = [400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950]

results = []

for bw in bandwidths:
    print(f"Testing {bw}M...", end=" ", flush=True)

    cmd = f"iperf3 -c 10.0.100.2 -u -b {bw}M -t 5 -l 1472"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # Parse receiver line
    for line in result.stdout.split('\n'):
        if 'receiver' in line:
            parts = line.split()
            try:
                throughput = f"{parts[6]} {parts[7]}"
                loss_match = re.search(r'\(([\d.]+)%\)', line)
                loss = loss_match.group(1) if loss_match else "0"

                print(f"{throughput}, Loss: {loss}%")
                results.append({
                    'target': bw,
                    'throughput': throughput,
                    'loss': float(loss)
                })
            except:
                print("Error parsing")

print("\n=== Summary ===")
print(f"{'Target':<10} {'Actual':<15} {'Loss %':<10} {'Status':<10}")
print("-" * 50)

for r in results:
    status = "✓ Zero-loss" if r['loss'] == 0 else f"✗ {r['loss']:.2f}%"
    print(f"{r['target']}M{'':<6} {r['throughput']:<15} {r['loss']:<10.2f} {status}")

# Find max zero-loss
zero_loss = [r for r in results if r['loss'] == 0]
if zero_loss:
    max_zero = max(zero_loss, key=lambda x: x['target'])
    print(f"\n✓ Maximum zero-loss throughput: {max_zero['target']}M ({max_zero['throughput']})")
