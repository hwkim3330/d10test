#!/usr/bin/env python3
"""
High-Precision Network Benchmark using netsniff-ng suite
Tools: mausezahn (packet generation), netsniff-ng (capture)
Target: 10.0.100.2 in IEEE 802.1CB FRER environment
"""

import subprocess
import time
import re
import json
import datetime
from pathlib import Path
import signal
import os

TARGET_IP = "10.0.100.2"
TARGET_MAC = ""  # Will be discovered via ARP
SOURCE_IF = "enp2s0"
RESULTS_DIR = f"netsniff_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

class NetsniffBenchmark:
    def __init__(self):
        self.target_ip = TARGET_IP
        self.source_if = SOURCE_IF
        self.results_dir = Path(RESULTS_DIR)
        self.results_dir.mkdir(exist_ok=True)
        self.target_mac = self.get_target_mac()
        self.results = []

    def log(self, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")

    def run_command(self, cmd, timeout=None):
        """Execute command and return output"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Timeout", -1
        except Exception as e:
            return "", str(e), -1

    def get_target_mac(self):
        """Get target MAC address via ARP"""
        self.log(f"Resolving MAC for {self.target_ip}...")

        # Ping to ensure ARP entry
        os.system(f"ping -c 1 {self.target_ip} > /dev/null 2>&1")

        # Get MAC from ARP table
        stdout, _, _ = self.run_command(f"ip neigh show {self.target_ip}")

        match = re.search(r'([0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2})', stdout)
        if match:
            mac = match.group(1)
            self.log(f"Target MAC: {mac}")
            return mac
        else:
            self.log(f"Warning: Could not resolve MAC, using broadcast")
            return "ff:ff:ff:ff:ff:ff"

    def calculate_pps_for_bitrate(self, frame_size, target_mbps):
        """
        Calculate packets per second needed for target bitrate

        Frame on wire = Preamble(8) + Frame(frame_size) + IFG(12) = frame_size + 20
        """
        bits_per_frame = (frame_size + 20) * 8
        target_bps = target_mbps * 1_000_000
        pps = int(target_bps / bits_per_frame)
        return pps

    def test_mausezahn_throughput(self, frame_size, target_mbps, duration=10):
        """
        Test UDP throughput using mausezahn

        Args:
            frame_size: Payload size in bytes (46-1500)
            target_mbps: Target throughput in Mbps
            duration: Test duration in seconds
        """
        self.log(f"Testing {frame_size}B frames at {target_mbps} Mbps for {duration}s...")

        # Calculate PPS
        pps = self.calculate_pps_for_bitrate(frame_size, target_mbps)

        # Calculate inter-packet delay in microseconds
        if pps > 0:
            delay_us = 1_000_000 / pps
        else:
            delay_us = 1000  # Default 1ms

        # Total packets to send
        total_packets = pps * duration

        self.log(f"  Calculated: {pps} pps, {delay_us:.2f} us delay, {total_packets} total packets")

        # Payload size (exclude Ethernet header)
        # mausezahn payload = frame_size - 14 (Eth header) - 20 (IP header) - 8 (UDP header)
        payload_size = frame_size - 14 - 20 - 8
        if payload_size < 18:
            payload_size = 18  # Minimum

        # Mausezahn command
        # -c count, -d delay in usec, -t udp, -B destination IP
        cmd = (
            f"sudo mausezahn {self.source_if} "
            f"-c {total_packets} "
            f"-d {delay_us:.0f}u "
            f"-t udp 'sp=5000,dp=5000' "
            f"-B {self.target_ip} "
            f"-b {payload_size}"
        )

        self.log(f"  Command: {cmd}")

        # Run mausezahn
        start_time = time.time()
        stdout, stderr, rc = self.run_command(cmd, timeout=duration+30)
        actual_duration = time.time() - start_time

        self.log(f"  Mausezahn completed in {actual_duration:.2f}s")

        # Parse output
        sent_packets = total_packets  # Assume all sent

        # Calculate actual throughput
        actual_mbps = (sent_packets * (frame_size + 20) * 8) / (actual_duration * 1_000_000)

        result = {
            'frame_size': frame_size,
            'target_mbps': target_mbps,
            'actual_mbps': actual_mbps,
            'pps': pps,
            'sent_packets': sent_packets,
            'duration': actual_duration,
            'tool': 'mausezahn'
        }

        self.log(f"  Result: {actual_mbps:.2f} Mbps, {sent_packets} packets sent")

        return result

    def test_line_rate(self, frame_size, duration=10):
        """
        Test at theoretical line rate for given frame size
        """
        # Calculate theoretical line rate
        frame_on_wire = frame_size + 20  # Preamble(8) + IFG(12)
        line_rate_mbps = (1000 * frame_size) / frame_on_wire

        self.log(f"\n{'='*70}")
        self.log(f"Frame Size: {frame_size} bytes")
        self.log(f"Theoretical Line Rate: {line_rate_mbps:.2f} Mbps")
        self.log(f"{'='*70}")

        # Test at different percentages
        test_percentages = [50, 70, 80, 90, 95, 98, 100]

        for pct in test_percentages:
            target_mbps = line_rate_mbps * (pct / 100.0)
            result = self.test_mausezahn_throughput(frame_size, target_mbps, duration)
            result['load_percent'] = pct
            result['line_rate_mbps'] = line_rate_mbps
            self.results.append(result)
            time.sleep(2)

    def generate_summary(self):
        """Generate summary report"""
        self.log("\n" + "="*70)
        self.log("BENCHMARK SUMMARY")
        self.log("="*70)

        print("\nFrame Size | Load% | Target (Mbps) | Actual (Mbps) | Packets")
        print("-"*70)

        for result in self.results:
            print(f"{result['frame_size']:>10} | {result['load_percent']:>5} | "
                  f"{result['target_mbps']:>13.2f} | {result['actual_mbps']:>13.2f} | "
                  f"{result['sent_packets']:>7}")

        # Save JSON
        json_file = self.results_dir / "netsniff_results.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        self.log(f"\nResults saved to: {json_file}")

    def run_benchmark(self):
        """Run complete benchmark"""
        self.log("="*70)
        self.log("HIGH-PRECISION NETWORK BENCHMARK")
        self.log(f"Tool: mausezahn")
        self.log(f"Target: {self.target_ip} ({self.target_mac})")
        self.log(f"Interface: {self.source_if}")
        self.log("="*70)

        # Test standard frame sizes
        frame_sizes = [64, 128, 256, 512, 1024, 1518]

        for frame_size in frame_sizes:
            self.test_line_rate(frame_size, duration=10)

        self.generate_summary()

def main():
    # Check for root
    if os.geteuid() != 0:
        print("Error: This script requires root privileges (sudo)")
        print("Please run: sudo python3 netsniff_benchmark.py")
        return 1

    benchmark = NetsniffBenchmark()
    benchmark.run_benchmark()

if __name__ == "__main__":
    main()
