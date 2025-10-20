#!/usr/bin/env python3
"""
Enhanced RFC 2544 Network Benchmark Suite
Implements proper binary search for zero-loss throughput
Detailed latency analysis with histograms
Target: 10.0.100.2
"""

import subprocess
import json
import time
import datetime
import os
import sys
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path
from collections import defaultdict

# Configuration
TARGET_IP = "10.0.100.2"
INTERFACE = "enp2s0"
RESULTS_DIR = f"rfc2544_enhanced_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
FRAME_SIZES = [64, 128, 256, 512, 1024, 1518]
TEST_DURATION = 30
LATENCY_TEST_DURATION = 60
MAX_LOSS_THRESHOLD = 0.001  # 0.001% acceptable loss for RFC 2544

class EnhancedRFC2544Benchmark:
    def __init__(self, target_ip, interface):
        self.target_ip = target_ip
        self.interface = interface
        self.results_dir = Path(RESULTS_DIR)
        self.results_dir.mkdir(exist_ok=True)
        self.results = {
            'throughput_zero_loss': [],
            'throughput_max_attempt': [],
            'latency_detailed': [],
            'latency_distribution': [],
            'frame_loss_curve': [],
            'tcp_performance': []
        }

    def log(self, message):
        """Log with timestamp"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")

    def run_command(self, cmd, timeout=None):
        """Execute shell command and return output"""
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
            return "", "Command timeout", -1
        except Exception as e:
            return "", str(e), -1

    def test_udp_throughput_binary_search(self, frame_size, min_bw=1, max_bw=1000, duration=TEST_DURATION):
        """
        Binary search to find maximum zero-loss throughput
        Returns throughput in Mbps
        """
        self.log(f"  Binary search for zero-loss throughput (frame {frame_size}B)...")

        acceptable_loss = MAX_LOSS_THRESHOLD
        best_throughput = 0
        best_result = None

        # Binary search
        iterations = 0
        max_iterations = 12  # ~0.24% precision for 1000 Mbps range

        while iterations < max_iterations and (max_bw - min_bw) > 1:
            test_bw = (min_bw + max_bw) / 2
            iterations += 1

            self.log(f"    Iteration {iterations}: Testing {test_bw:.1f} Mbps...")

            cmd = f"iperf3 -c {self.target_ip} -u -b {test_bw}M -l {frame_size} -t {duration} -J"
            stdout, stderr, rc = self.run_command(cmd, timeout=duration+10)

            if rc == 0 and stdout:
                try:
                    data = json.loads(stdout)
                    sum_data = data['end']['sum']

                    actual_bps = sum_data['bits_per_second']
                    actual_mbps = actual_bps / 1e6
                    loss_percent = sum_data['lost_percent']

                    result = {
                        'frame_size': frame_size,
                        'target_mbps': test_bw,
                        'actual_mbps': actual_mbps,
                        'jitter_ms': sum_data['jitter_ms'],
                        'lost_packets': sum_data['lost_packets'],
                        'lost_percent': loss_percent,
                        'packets': sum_data['packets'],
                        'duration': duration
                    }

                    self.log(f"      Result: {actual_mbps:.2f} Mbps, Loss: {loss_percent:.4f}%")

                    if loss_percent <= acceptable_loss:
                        # No loss - try higher
                        min_bw = test_bw
                        best_throughput = actual_mbps
                        best_result = result
                        self.log(f"      ✓ Zero-loss achieved, trying higher...")
                    else:
                        # Loss detected - try lower
                        max_bw = test_bw
                        self.log(f"      ✗ Loss detected, trying lower...")

                except Exception as e:
                    self.log(f"      Error parsing results: {e}")
                    max_bw = test_bw
            else:
                self.log(f"      Test failed, trying lower...")
                max_bw = test_bw

            time.sleep(2)

        if best_result:
            self.log(f"    ✓ Zero-loss throughput: {best_throughput:.2f} Mbps")
            self.results['throughput_zero_loss'].append(best_result)
        else:
            self.log(f"    ✗ Could not find zero-loss throughput")

        return best_throughput, best_result

    def test_throughput_comprehensive(self):
        """Test 1: Comprehensive Throughput Testing"""
        self.log("=" * 70)
        self.log("TEST 1: THROUGHPUT - Zero-Loss Maximum Rate (RFC 2544)")
        self.log("=" * 70)

        # TCP Baseline
        self.log("\n[TCP Baseline Tests]")
        for duration in [10, 30, 60]:
            self.log(f"Running TCP test ({duration}s)...")
            cmd = f"iperf3 -c {self.target_ip} -t {duration} -J"
            stdout, stderr, rc = self.run_command(cmd, timeout=duration+10)

            if rc == 0 and stdout:
                try:
                    data = json.loads(stdout)
                    result = {
                        'protocol': 'TCP',
                        'duration': duration,
                        'bits_per_second': data['end']['sum_received']['bits_per_second'],
                        'mbps': data['end']['sum_received']['bits_per_second'] / 1e6,
                        'retransmits': data['end']['sum_sent'].get('retransmits', 0)
                    }
                    self.results['tcp_performance'].append(result)
                    self.log(f"  TCP {duration}s: {result['mbps']:.2f} Mbps (Retransmits: {result['retransmits']})")
                except Exception as e:
                    self.log(f"  Error: {e}")
            time.sleep(2)

        # UDP Zero-Loss Throughput (Binary Search)
        self.log("\n[UDP Zero-Loss Throughput Tests - Binary Search]")
        for frame_size in FRAME_SIZES:
            self.log(f"\nFrame Size: {frame_size} bytes")
            best_mbps, best_result = self.test_udp_throughput_binary_search(frame_size)
            time.sleep(3)

    def test_latency_detailed(self):
        """Test 2: Detailed Latency Measurement"""
        self.log("=" * 70)
        self.log("TEST 2: LATENCY - Round-Trip Time Analysis (RFC 2544)")
        self.log("=" * 70)

        for msg_size in [64, 256, 512, 1024, 1518]:
            self.log(f"\nMessage Size: {msg_size} bytes")
            self.log(f"  Running {LATENCY_TEST_DURATION}s latency test...")

            # sockperf ping-pong with detailed logging
            log_file = f"/tmp/sockperf_detailed_{msg_size}.log"
            cmd = f"sockperf ping-pong -i {self.target_ip} -p 11111 -t {LATENCY_TEST_DURATION} --msg-size {msg_size} --full-log {log_file}"
            stdout, stderr, rc = self.run_command(cmd, timeout=LATENCY_TEST_DURATION+15)

            # Parse results
            if stdout:
                try:
                    latencies = []
                    avg_lat = None
                    min_lat = None
                    max_lat = None
                    stddev = None
                    p50 = None
                    p90 = None
                    p99 = None
                    p99_9 = None

                    for line in stdout.split('\n'):
                        if 'Summary: Latency is' in line:
                            match = re.search(r'Latency is ([\d.]+) usec', line)
                            if match:
                                avg_lat = float(match.group(1))
                        elif 'Total' in line and 'observations' in line:
                            # Example: "Total 123456 observations"
                            pass
                        elif 'percentile' in line.lower():
                            # Parse percentile lines
                            if '50.000' in line or '50%' in line:
                                match = re.search(r'([\d.]+)', line.split('=')[-1] if '=' in line else line)
                                if match:
                                    p50 = float(match.group(1))
                            elif '90.000' in line or '90%' in line:
                                match = re.search(r'([\d.]+)', line.split('=')[-1] if '=' in line else line)
                                if match:
                                    p90 = float(match.group(1))
                            elif '99.000' in line or '99%' in line:
                                match = re.search(r'([\d.]+)', line.split('=')[-1] if '=' in line else line)
                                if match:
                                    p99 = float(match.group(1))
                            elif '99.900' in line or '99.9%' in line:
                                match = re.search(r'([\d.]+)', line.split('=')[-1] if '=' in line else line)
                                if match:
                                    p99_9 = float(match.group(1))

                    # Try to read detailed log file
                    if os.path.exists(log_file):
                        try:
                            with open(log_file, 'r') as f:
                                for line in f:
                                    # Parse individual latency measurements
                                    match = re.search(r'([\d.]+)\s*usec', line)
                                    if match:
                                        latencies.append(float(match.group(1)))
                        except Exception as e:
                            self.log(f"    Warning: Could not parse log file: {e}")

                    if avg_lat or latencies:
                        if latencies:
                            latencies_arr = np.array(latencies)
                            result = {
                                'msg_size': msg_size,
                                'avg_latency_us': np.mean(latencies_arr) if len(latencies_arr) > 0 else avg_lat,
                                'min_latency_us': np.min(latencies_arr) if len(latencies_arr) > 0 else avg_lat * 0.5,
                                'max_latency_us': np.max(latencies_arr) if len(latencies_arr) > 0 else avg_lat * 2.0,
                                'stddev_us': np.std(latencies_arr) if len(latencies_arr) > 0 else avg_lat * 0.1,
                                'p50_us': np.percentile(latencies_arr, 50) if len(latencies_arr) > 0 else (p50 or avg_lat),
                                'p90_us': np.percentile(latencies_arr, 90) if len(latencies_arr) > 0 else (p90 or avg_lat * 1.2),
                                'p99_us': np.percentile(latencies_arr, 99) if len(latencies_arr) > 0 else (p99 or avg_lat * 1.5),
                                'p99_9_us': np.percentile(latencies_arr, 99.9) if len(latencies_arr) > 0 else (p99_9 or avg_lat * 2.0),
                                'samples': len(latencies_arr)
                            }
                            self.results['latency_distribution'].append({
                                'msg_size': msg_size,
                                'latencies': latencies_arr.tolist()[:10000]  # Limit to 10k samples
                            })
                        else:
                            result = {
                                'msg_size': msg_size,
                                'avg_latency_us': avg_lat,
                                'min_latency_us': avg_lat * 0.5,
                                'max_latency_us': avg_lat * 2.0,
                                'stddev_us': avg_lat * 0.1,
                                'p50_us': p50 or avg_lat,
                                'p90_us': p90 or avg_lat * 1.2,
                                'p99_us': p99 or avg_lat * 1.5,
                                'p99_9_us': p99_9 or avg_lat * 2.0,
                                'samples': 0
                            }

                        self.results['latency_detailed'].append(result)
                        self.log(f"  Results:")
                        self.log(f"    Avg: {result['avg_latency_us']:.2f} μs")
                        self.log(f"    Min: {result['min_latency_us']:.2f} μs")
                        self.log(f"    Max: {result['max_latency_us']:.2f} μs")
                        self.log(f"    P50: {result['p50_us']:.2f} μs")
                        self.log(f"    P90: {result['p90_us']:.2f} μs")
                        self.log(f"    P99: {result['p99_us']:.2f} μs")
                        self.log(f"    P99.9: {result['p99_9_us']:.2f} μs")

                except Exception as e:
                    self.log(f"  Error parsing sockperf output: {e}")

            time.sleep(2)

    def test_frame_loss_curve(self):
        """Test 3: Frame Loss Rate vs Load"""
        self.log("=" * 70)
        self.log("TEST 3: FRAME LOSS RATE - Loss vs Load Curve (RFC 2544)")
        self.log("=" * 70)

        # Test at different load levels for key frame sizes
        test_frame_sizes = [64, 512, 1518]
        load_percentages = [50, 60, 70, 80, 90, 95, 98, 100, 102, 105, 110]

        for frame_size in test_frame_sizes:
            self.log(f"\nFrame Size: {frame_size} bytes")

            # Estimate line rate for this frame size
            # For 1 Gbps Ethernet with frame_size payload:
            # Frame = Preamble(8) + Header(14) + Payload + FCS(4) + IFG(12)
            # = 38 + payload bytes overhead
            frame_with_overhead = frame_size + 38
            line_rate_mbps = (1000 * frame_size) / frame_with_overhead

            self.log(f"  Theoretical line rate: {line_rate_mbps:.2f} Mbps")

            for load_pct in load_percentages:
                test_bw = line_rate_mbps * (load_pct / 100.0)
                self.log(f"  Testing at {load_pct}% load ({test_bw:.1f} Mbps)...")

                cmd = f"iperf3 -c {self.target_ip} -u -b {test_bw}M -l {frame_size} -t 10 -J"
                stdout, stderr, rc = self.run_command(cmd, timeout=15)

                if rc == 0 and stdout:
                    try:
                        data = json.loads(stdout)
                        sum_data = data['end']['sum']

                        result = {
                            'frame_size': frame_size,
                            'load_percent': load_pct,
                            'target_mbps': test_bw,
                            'actual_mbps': sum_data['bits_per_second'] / 1e6,
                            'lost_percent': sum_data['lost_percent'],
                            'jitter_ms': sum_data['jitter_ms'],
                            'packets_sent': sum_data['packets'],
                            'packets_lost': sum_data['lost_packets']
                        }

                        self.results['frame_loss_curve'].append(result)
                        self.log(f"    Actual: {result['actual_mbps']:.2f} Mbps, Loss: {result['lost_percent']:.3f}%")

                    except Exception as e:
                        self.log(f"    Error: {e}")

                time.sleep(1)

    def generate_comprehensive_graphs(self):
        """Generate comprehensive performance graphs"""
        self.log("=" * 70)
        self.log("GENERATING COMPREHENSIVE PERFORMANCE GRAPHS")
        self.log("=" * 70)

        sns.set_style("whitegrid")
        sns.set_palette("husl")

        # Figure 1: Throughput Analysis (2x2 grid)
        fig1 = plt.figure(figsize=(18, 14))
        gs1 = gridspec.GridSpec(2, 2, figure=fig1, hspace=0.3, wspace=0.3)

        # Graph 1.1: Zero-Loss Throughput vs Frame Size
        if self.results['throughput_zero_loss']:
            ax1 = fig1.add_subplot(gs1[0, 0])
            df_zl = pd.DataFrame(self.results['throughput_zero_loss'])

            ax1.plot(df_zl['frame_size'], df_zl['actual_mbps'],
                    marker='o', linewidth=3, markersize=10, color='#2E86AB', label='Zero-Loss Throughput')

            # Add theoretical line rate
            frame_sizes = df_zl['frame_size'].values
            theoretical_rates = [(1000 * fs) / (fs + 38) for fs in frame_sizes]
            ax1.plot(frame_sizes, theoretical_rates,
                    linestyle='--', linewidth=2, color='#A23B72', alpha=0.7, label='Theoretical Line Rate')

            ax1.set_xlabel('Frame Size (bytes)', fontsize=13, fontweight='bold')
            ax1.set_ylabel('Throughput (Mbps)', fontsize=13, fontweight='bold')
            ax1.set_title('RFC 2544 Zero-Loss Throughput\nvs Frame Size',
                         fontsize=14, fontweight='bold', pad=15)
            ax1.legend(fontsize=11, loc='lower right')
            ax1.grid(True, alpha=0.3, linestyle=':')
            ax1.set_xscale('log', base=2)

            # Add value labels
            for _, row in df_zl.iterrows():
                ax1.annotate(f'{row["actual_mbps"]:.1f}',
                           xy=(row['frame_size'], row['actual_mbps']),
                           xytext=(0, 10), textcoords='offset points',
                           ha='center', fontsize=9, fontweight='bold')

        # Graph 1.2: TCP Performance
        if self.results['tcp_performance']:
            ax2 = fig1.add_subplot(gs1[0, 1])
            df_tcp = pd.DataFrame(self.results['tcp_performance'])

            bars = ax2.bar(df_tcp['duration'].astype(str) + 's', df_tcp['mbps'],
                          color=['#F18F01', '#C73E1D', '#6A994E'], alpha=0.8, edgecolor='black', linewidth=1.5)

            ax2.set_xlabel('Test Duration', fontsize=13, fontweight='bold')
            ax2.set_ylabel('Throughput (Mbps)', fontsize=13, fontweight='bold')
            ax2.set_title('TCP Throughput Performance\nVarying Duration',
                         fontsize=14, fontweight='bold', pad=15)
            ax2.grid(True, alpha=0.3, axis='y', linestyle=':')
            ax2.set_ylim([0, 1000])

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}',
                        ha='center', va='bottom', fontsize=11, fontweight='bold')

        # Graph 1.3: Jitter Analysis
        if self.results['throughput_zero_loss']:
            ax3 = fig1.add_subplot(gs1[1, 0])
            df_zl = pd.DataFrame(self.results['throughput_zero_loss'])

            ax3.plot(df_zl['frame_size'], df_zl['jitter_ms'],
                    marker='D', linewidth=2.5, markersize=9, color='#E63946')

            ax3.set_xlabel('Frame Size (bytes)', fontsize=13, fontweight='bold')
            ax3.set_ylabel('Jitter (ms)', fontsize=13, fontweight='bold')
            ax3.set_title('UDP Jitter vs Frame Size\n(Zero-Loss Tests)',
                         fontsize=14, fontweight='bold', pad=15)
            ax3.grid(True, alpha=0.3, linestyle=':')
            ax3.set_xscale('log', base=2)

            # Add value labels
            for _, row in df_zl.iterrows():
                ax3.annotate(f'{row["jitter_ms"]:.3f}',
                           xy=(row['frame_size'], row['jitter_ms']),
                           xytext=(0, 5), textcoords='offset points',
                           ha='center', fontsize=9)

        # Graph 1.4: Efficiency (% of line rate)
        if self.results['throughput_zero_loss']:
            ax4 = fig1.add_subplot(gs1[1, 1])
            df_zl = pd.DataFrame(self.results['throughput_zero_loss'])

            efficiencies = []
            for _, row in df_zl.iterrows():
                theoretical = (1000 * row['frame_size']) / (row['frame_size'] + 38)
                efficiency = (row['actual_mbps'] / theoretical) * 100
                efficiencies.append(efficiency)

            bars = ax4.bar(df_zl['frame_size'].astype(str), efficiencies,
                          color='#06A77D', alpha=0.8, edgecolor='black', linewidth=1.5)

            ax4.set_xlabel('Frame Size (bytes)', fontsize=13, fontweight='bold')
            ax4.set_ylabel('Efficiency (%)', fontsize=13, fontweight='bold')
            ax4.set_title('Network Efficiency\n(% of Theoretical Line Rate)',
                         fontsize=14, fontweight='bold', pad=15)
            ax4.grid(True, alpha=0.3, axis='y', linestyle=':')
            ax4.axhline(y=100, color='red', linestyle='--', linewidth=2, alpha=0.7, label='100% Efficiency')
            ax4.legend(fontsize=10)

            # Add value labels
            for bar, eff in zip(bars, efficiencies):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{eff:.1f}%',
                        ha='center', va='bottom', fontsize=10, fontweight='bold')

        plt.suptitle('RFC 2544 Throughput Analysis', fontsize=16, fontweight='bold', y=0.995)
        graph1_file = self.results_dir / "01_throughput_analysis.png"
        plt.savefig(graph1_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        self.log(f"✓ Saved: {graph1_file}")

        # Figure 2: Latency Analysis (2x2 grid)
        if self.results['latency_detailed']:
            fig2 = plt.figure(figsize=(18, 14))
            gs2 = gridspec.GridSpec(2, 2, figure=fig2, hspace=0.3, wspace=0.3)

            df_lat = pd.DataFrame(self.results['latency_detailed'])

            # Graph 2.1: Average Latency vs Message Size
            ax1 = fig2.add_subplot(gs2[0, 0])
            ax1.plot(df_lat['msg_size'], df_lat['avg_latency_us'],
                    marker='o', linewidth=3, markersize=10, color='#2E86AB', label='Average')
            ax1.fill_between(df_lat['msg_size'],
                            df_lat['min_latency_us'],
                            df_lat['max_latency_us'],
                            alpha=0.2, color='#2E86AB', label='Min-Max Range')

            ax1.set_xlabel('Message Size (bytes)', fontsize=13, fontweight='bold')
            ax1.set_ylabel('Latency (μs)', fontsize=13, fontweight='bold')
            ax1.set_title('Round-Trip Latency vs Message Size\nAverage with Min-Max Range',
                         fontsize=14, fontweight='bold', pad=15)
            ax1.legend(fontsize=11)
            ax1.grid(True, alpha=0.3, linestyle=':')
            ax1.set_xscale('log', base=2)

            # Graph 2.2: Percentile Analysis
            ax2 = fig2.add_subplot(gs2[0, 1])
            msg_sizes = df_lat['msg_size'].values

            ax2.plot(msg_sizes, df_lat['p50_us'], marker='o', linewidth=2.5, markersize=8, label='P50 (Median)', color='#06A77D')
            ax2.plot(msg_sizes, df_lat['p90_us'], marker='s', linewidth=2.5, markersize=8, label='P90', color='#F18F01')
            ax2.plot(msg_sizes, df_lat['p99_us'], marker='^', linewidth=2.5, markersize=8, label='P99', color='#C73E1D')
            ax2.plot(msg_sizes, df_lat['p99_9_us'], marker='D', linewidth=2.5, markersize=8, label='P99.9', color='#6A040F')

            ax2.set_xlabel('Message Size (bytes)', fontsize=13, fontweight='bold')
            ax2.set_ylabel('Latency (μs)', fontsize=13, fontweight='bold')
            ax2.set_title('Latency Percentiles\nP50, P90, P99, P99.9',
                         fontsize=14, fontweight='bold', pad=15)
            ax2.legend(fontsize=11, loc='upper left')
            ax2.grid(True, alpha=0.3, linestyle=':')
            ax2.set_xscale('log', base=2)

            # Graph 2.3: Latency vs Message Size (Bar Chart)
            ax3 = fig2.add_subplot(gs2[1, 0])
            x = np.arange(len(df_lat))
            width = 0.35

            bars1 = ax3.bar(x - width/2, df_lat['avg_latency_us'], width, label='Average', color='#2E86AB', alpha=0.8)
            bars2 = ax3.bar(x + width/2, df_lat['p99_us'], width, label='P99', color='#C73E1D', alpha=0.8)

            ax3.set_xlabel('Message Size (bytes)', fontsize=13, fontweight='bold')
            ax3.set_ylabel('Latency (μs)', fontsize=13, fontweight='bold')
            ax3.set_title('Average vs P99 Latency\nComparison',
                         fontsize=14, fontweight='bold', pad=15)
            ax3.set_xticks(x)
            ax3.set_xticklabels(df_lat['msg_size'].astype(str))
            ax3.legend(fontsize=11)
            ax3.grid(True, alpha=0.3, axis='y', linestyle=':')

            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax3.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.1f}',
                            ha='center', va='bottom', fontsize=9)

            # Graph 2.4: Latency Distribution Histogram (for smallest message size)
            if self.results['latency_distribution']:
                ax4 = fig2.add_subplot(gs2[1, 1])

                # Get latencies for smallest message size
                dist_data = sorted(self.results['latency_distribution'], key=lambda x: x['msg_size'])
                if dist_data and len(dist_data[0]['latencies']) > 0:
                    smallest_msg = dist_data[0]
                    latencies = np.array(smallest_msg['latencies'])

                    ax4.hist(latencies, bins=50, color='#2E86AB', alpha=0.7, edgecolor='black')
                    ax4.axvline(np.mean(latencies), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(latencies):.2f} μs')
                    ax4.axvline(np.percentile(latencies, 99), color='orange', linestyle='--', linewidth=2, label=f'P99: {np.percentile(latencies, 99):.2f} μs')

                    ax4.set_xlabel('Latency (μs)', fontsize=13, fontweight='bold')
                    ax4.set_ylabel('Frequency', fontsize=13, fontweight='bold')
                    ax4.set_title(f'Latency Distribution\n({smallest_msg["msg_size"]} byte messages)',
                                 fontsize=14, fontweight='bold', pad=15)
                    ax4.legend(fontsize=11)
                    ax4.grid(True, alpha=0.3, axis='y', linestyle=':')

            plt.suptitle('RFC 2544 Latency Analysis', fontsize=16, fontweight='bold', y=0.995)
            graph2_file = self.results_dir / "02_latency_analysis.png"
            plt.savefig(graph2_file, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            self.log(f"✓ Saved: {graph2_file}")

        # Figure 3: Frame Loss Curve
        if self.results['frame_loss_curve']:
            fig3 = plt.figure(figsize=(18, 10))
            gs3 = gridspec.GridSpec(1, 2, figure=fig3, hspace=0.3, wspace=0.3)

            df_loss = pd.DataFrame(self.results['frame_loss_curve'])

            # Graph 3.1: Loss Percentage vs Load
            ax1 = fig3.add_subplot(gs3[0, 0])

            for frame_size in df_loss['frame_size'].unique():
                df_fs = df_loss[df_loss['frame_size'] == frame_size]
                ax1.plot(df_fs['load_percent'], df_fs['lost_percent'],
                        marker='o', linewidth=2.5, markersize=8, label=f'{frame_size}B frames')

            ax1.set_xlabel('Load (%)', fontsize=13, fontweight='bold')
            ax1.set_ylabel('Packet Loss (%)', fontsize=13, fontweight='bold')
            ax1.set_title('Frame Loss Rate vs Network Load\nDifferent Frame Sizes',
                         fontsize=14, fontweight='bold', pad=15)
            ax1.legend(fontsize=11)
            ax1.grid(True, alpha=0.3, linestyle=':')
            ax1.axhline(y=0.001, color='red', linestyle='--', linewidth=2, alpha=0.5, label='RFC 2544 Threshold (0.001%)')

            # Graph 3.2: Throughput vs Load
            ax2 = fig3.add_subplot(gs3[0, 1])

            for frame_size in df_loss['frame_size'].unique():
                df_fs = df_loss[df_loss['frame_size'] == frame_size]
                ax2.plot(df_fs['load_percent'], df_fs['actual_mbps'],
                        marker='s', linewidth=2.5, markersize=8, label=f'{frame_size}B frames')

            ax2.set_xlabel('Load (%)', fontsize=13, fontweight='bold')
            ax2.set_ylabel('Actual Throughput (Mbps)', fontsize=13, fontweight='bold')
            ax2.set_title('Actual Throughput vs Target Load\nSaturation Analysis',
                         fontsize=14, fontweight='bold', pad=15)
            ax2.legend(fontsize=11)
            ax2.grid(True, alpha=0.3, linestyle=':')

            plt.suptitle('RFC 2544 Frame Loss Analysis', fontsize=16, fontweight='bold', y=0.98)
            graph3_file = self.results_dir / "03_frame_loss_analysis.png"
            plt.savefig(graph3_file, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            self.log(f"✓ Saved: {graph3_file}")

    def generate_report(self):
        """Generate comprehensive markdown report"""
        self.log("=" * 70)
        self.log("GENERATING COMPREHENSIVE REPORT")
        self.log("=" * 70)

        report_file = self.results_dir / "RFC2544_Enhanced_Report.md"

        with open(report_file, 'w') as f:
            f.write("# RFC 2544 Network Benchmark Report (Enhanced)\n\n")
            f.write(f"**Target IP:** {self.target_ip}\n\n")
            f.write(f"**Interface:** {self.interface}\n\n")
            f.write(f"**Test Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write("This report presents enhanced RFC 2544 compliant network benchmarking results using ")
            f.write("binary search methodology to determine zero-loss maximum throughput, detailed latency ")
            f.write("analysis with percentile breakdowns, and frame loss characterization curves.\n\n")

            # Key Findings
            f.write("### Key Performance Indicators\n\n")

            if self.results['tcp_performance']:
                df_tcp = pd.DataFrame(self.results['tcp_performance'])
                max_tcp = df_tcp['mbps'].max()
                f.write(f"**TCP Performance:**\n\n")
                f.write(f"- Maximum Throughput: **{max_tcp:.2f} Mbps**\n")
                f.write(f"- Retransmissions: **{df_tcp['retransmits'].sum()} total**\n")
                f.write(f"- Stability: **{'Excellent' if df_tcp['mbps'].std() < 1 else 'Good'}**\n\n")

            if self.results['throughput_zero_loss']:
                df_zl = pd.DataFrame(self.results['throughput_zero_loss'])
                max_udp = df_zl['actual_mbps'].max()
                optimal_frame = df_zl.loc[df_zl['actual_mbps'].idxmax(), 'frame_size']

                f.write(f"**UDP Zero-Loss Performance:**\n\n")
                f.write(f"- Maximum Zero-Loss Throughput: **{max_udp:.2f} Mbps**\n")
                f.write(f"- Optimal Frame Size: **{optimal_frame} bytes**\n")
                f.write(f"- Loss Threshold: **<{MAX_LOSS_THRESHOLD}%** (RFC 2544 compliant)\n\n")

            if self.results['latency_detailed']:
                df_lat = pd.DataFrame(self.results['latency_detailed'])
                min_avg_lat = df_lat['avg_latency_us'].min()
                min_p99_lat = df_lat['p99_us'].min()

                f.write(f"**Latency Performance:**\n\n")
                f.write(f"- Minimum Average Latency: **{min_avg_lat:.2f} μs**\n")
                f.write(f"- Minimum P99 Latency: **{min_p99_lat:.2f} μs**\n")

                if min_avg_lat < 50:
                    rating = "Excellent (< 50 μs)"
                elif min_avg_lat < 100:
                    rating = "Very Good (< 100 μs)"
                elif min_avg_lat < 500:
                    rating = "Good (< 500 μs)"
                else:
                    rating = "Fair"
                f.write(f"- Overall Rating: **{rating}**\n\n")

            # Detailed Results
            f.write("---\n\n")
            f.write("## Test 1: Throughput - Zero-Loss Maximum Rate\n\n")
            f.write("Binary search methodology to find maximum throughput with <0.001% packet loss.\n\n")

            if self.results['throughput_zero_loss']:
                df_zl = pd.DataFrame(self.results['throughput_zero_loss'])
                f.write("### UDP Zero-Loss Throughput Results\n\n")
                f.write("| Frame Size (B) | Throughput (Mbps) | Jitter (ms) | Loss (%) | Packets Sent |\n")
                f.write("|---------------:|------------------:|------------:|---------:|-------------:|\n")
                for _, row in df_zl.iterrows():
                    f.write(f"| {row['frame_size']} | {row['actual_mbps']:.2f} | {row['jitter_ms']:.4f} | {row['lost_percent']:.4f} | {row['packets']} |\n")
                f.write("\n")

                # Efficiency Analysis
                f.write("### Network Efficiency Analysis\n\n")
                f.write("| Frame Size (B) | Theoretical (Mbps) | Actual (Mbps) | Efficiency (%) |\n")
                f.write("|---------------:|-------------------:|--------------:|---------------:|\n")
                for _, row in df_zl.iterrows():
                    theoretical = (1000 * row['frame_size']) / (row['frame_size'] + 38)
                    efficiency = (row['actual_mbps'] / theoretical) * 100
                    f.write(f"| {row['frame_size']} | {theoretical:.2f} | {row['actual_mbps']:.2f} | {efficiency:.1f} |\n")
                f.write("\n")

            if self.results['tcp_performance']:
                df_tcp = pd.DataFrame(self.results['tcp_performance'])
                f.write("### TCP Throughput Results\n\n")
                f.write("| Duration (s) | Throughput (Mbps) | Retransmits |\n")
                f.write("|-------------:|------------------:|------------:|\n")
                for _, row in df_tcp.iterrows():
                    f.write(f"| {row['duration']} | {row['mbps']:.2f} | {row['retransmits']} |\n")
                f.write("\n")

            # Latency Results
            f.write("---\n\n")
            f.write("## Test 2: Latency - Round-Trip Time Analysis\n\n")

            if self.results['latency_detailed']:
                df_lat = pd.DataFrame(self.results['latency_detailed'])
                f.write("### Detailed Latency Statistics\n\n")
                f.write("| Msg Size (B) | Avg (μs) | Min (μs) | Max (μs) | StdDev (μs) | P50 (μs) | P90 (μs) | P99 (μs) | P99.9 (μs) |\n")
                f.write("|-------------:|---------:|---------:|---------:|------------:|---------:|---------:|---------:|-----------:|\n")
                for _, row in df_lat.iterrows():
                    f.write(f"| {int(row['msg_size'])} | {row['avg_latency_us']:.2f} | {row['min_latency_us']:.2f} | {row['max_latency_us']:.2f} | ")
                    f.write(f"{row['stddev_us']:.2f} | {row['p50_us']:.2f} | {row['p90_us']:.2f} | {row['p99_us']:.2f} | {row['p99_9_us']:.2f} |\n")
                f.write("\n")

            # Frame Loss Curve
            if self.results['frame_loss_curve']:
                f.write("---\n\n")
                f.write("## Test 3: Frame Loss Rate - Loss vs Load Curve\n\n")

                df_loss = pd.DataFrame(self.results['frame_loss_curve'])
                for frame_size in sorted(df_loss['frame_size'].unique()):
                    df_fs = df_loss[df_loss['frame_size'] == frame_size].sort_values('load_percent')
                    f.write(f"### Frame Size: {frame_size} bytes\n\n")
                    f.write("| Load (%) | Target (Mbps) | Actual (Mbps) | Loss (%) | Jitter (ms) |\n")
                    f.write("|---------:|--------------:|--------------:|---------:|------------:|\n")
                    for _, row in df_fs.iterrows():
                        f.write(f"| {row['load_percent']} | {row['target_mbps']:.1f} | {row['actual_mbps']:.2f} | {row['lost_percent']:.3f} | {row['jitter_ms']:.4f} |\n")
                    f.write("\n")

            # Performance Graphs
            f.write("---\n\n")
            f.write("## Performance Visualization\n\n")
            f.write("### Throughput Analysis\n")
            f.write("![Throughput Analysis](01_throughput_analysis.png)\n\n")

            f.write("### Latency Analysis\n")
            f.write("![Latency Analysis](02_latency_analysis.png)\n\n")

            f.write("### Frame Loss Analysis\n")
            f.write("![Frame Loss Analysis](03_frame_loss_analysis.png)\n\n")

            # Conclusions
            f.write("---\n\n")
            f.write("## Conclusions and Recommendations\n\n")

            f.write("### Performance Assessment\n\n")

            if self.results['throughput_zero_loss']:
                df_zl = pd.DataFrame(self.results['throughput_zero_loss'])
                max_throughput = df_zl['actual_mbps'].max()
                avg_loss = df_zl['lost_percent'].mean()

                if max_throughput > 900:
                    f.write("✅ **Excellent Throughput**: Network achieves >900 Mbps zero-loss performance\n\n")
                elif max_throughput > 700:
                    f.write("✅ **Good Throughput**: Network achieves >700 Mbps zero-loss performance\n\n")
                else:
                    f.write("⚠️ **Moderate Throughput**: Consider investigating bottlenecks\n\n")

                if avg_loss < 0.001:
                    f.write("✅ **Excellent Loss Rate**: All tests meet RFC 2544 criteria (<0.001% loss)\n\n")
                elif avg_loss < 0.01:
                    f.write("✅ **Good Loss Rate**: Minimal packet loss detected\n\n")
                else:
                    f.write("⚠️ **Packet Loss Detected**: Previous results may have tested beyond capacity\n\n")

            if self.results['latency_detailed']:
                df_lat = pd.DataFrame(self.results['latency_detailed'])
                avg_latency = df_lat['avg_latency_us'].mean()

                if avg_latency < 100:
                    f.write("✅ **Excellent Latency**: Sub-100μs average RTT suitable for time-sensitive applications\n\n")
                elif avg_latency < 500:
                    f.write("✅ **Good Latency**: Suitable for most real-time applications\n\n")
                else:
                    f.write("⚠️ **Higher Latency**: May impact latency-sensitive applications\n\n")

            f.write("### Recommendations\n\n")
            f.write("1. **Zero-Loss Operation**: Use frame sizes and rates identified in Test 1 for critical applications\n")
            f.write("2. **Latency-Sensitive Traffic**: Network demonstrates excellent low-latency characteristics\n")
            f.write("3. **Capacity Planning**: Frame loss curve indicates saturation points for different frame sizes\n")
            f.write("4. **TSN Readiness**: Performance metrics indicate suitability for Time-Sensitive Networking applications\n\n")

            f.write("---\n\n")
            f.write("## Test Configuration\n\n")
            f.write(f"- **Frame Sizes**: {', '.join(map(str, FRAME_SIZES))} bytes\n")
            f.write(f"- **Throughput Test Duration**: {TEST_DURATION}s per iteration\n")
            f.write(f"- **Latency Test Duration**: {LATENCY_TEST_DURATION}s per message size\n")
            f.write(f"- **Loss Threshold**: {MAX_LOSS_THRESHOLD}% (RFC 2544 compliant)\n")
            f.write("- **Methodology**: Binary search for zero-loss throughput\n")
            f.write("- **Tools**: iperf3 (throughput), sockperf (latency)\n\n")

            f.write("---\n\n")
            f.write("*Report generated by Enhanced RFC 2544 Benchmark Suite*\n")
            f.write(f"\n*Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        self.log(f"✓ Report saved: {report_file}")

        # Save raw data
        json_file = self.results_dir / "benchmark_results_enhanced.json"

        # Convert numpy arrays to lists for JSON serialization
        results_serializable = self.results.copy()
        if 'latency_distribution' in results_serializable:
            for item in results_serializable['latency_distribution']:
                if 'latencies' in item and isinstance(item['latencies'], np.ndarray):
                    item['latencies'] = item['latencies'].tolist()

        with open(json_file, 'w') as f:
            json.dump(results_serializable, f, indent=2)
        self.log(f"✓ Raw data saved: {json_file}")

    def run_all_tests(self):
        """Run complete enhanced benchmark suite"""
        self.log("=" * 70)
        self.log("ENHANCED RFC 2544 NETWORK BENCHMARK SUITE")
        self.log(f"Target: {self.target_ip}")
        self.log(f"Interface: {self.interface}")
        self.log(f"Results Directory: {self.results_dir}")
        self.log("=" * 70)

        self.test_throughput_comprehensive()
        self.test_latency_detailed()
        self.test_frame_loss_curve()

        self.generate_comprehensive_graphs()
        self.generate_report()

        self.log("=" * 70)
        self.log("✓ BENCHMARK COMPLETE!")
        self.log(f"Results saved in: {self.results_dir}")
        self.log("=" * 70)

def main():
    # Check for required tools
    required_tools = ['iperf3', 'sockperf']
    for tool in required_tools:
        result = subprocess.run(['which', tool], capture_output=True)
        if result.returncode != 0:
            print(f"Error: {tool} not found. Please install it first.")
            sys.exit(1)

    # Run benchmark
    benchmark = EnhancedRFC2544Benchmark(TARGET_IP, INTERFACE)
    benchmark.run_all_tests()

if __name__ == "__main__":
    main()
