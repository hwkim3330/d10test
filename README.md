# D10 Network Benchmark Results

## Overview

This repository contains RFC 2544 compliant network benchmark results for testing target 10.0.100.2.

## Test Summary

**Test Date:** 2025-10-20 14:34:54
**Target IP:** 10.0.100.2
**Interface:** enp2s0

### Key Performance Indicators

| Metric | Result |
|--------|--------|
| **TCP Throughput** | 941.43 Mbps |
| **UDP Max Throughput** | 939.40 Mbps (1024-byte frames) |
| **Minimum Latency** | 60.52 μs |
| **Average Latency** | 88.35 μs |
| **Average Packet Loss** | 3.476% |

### Performance Highlights

- **Near line-rate performance** achieved (>940 Mbps)
- **Excellent latency** performance (<100 μs average)
- **Zero TCP retransmissions** across all test durations
- Some packet loss detected in UDP tests (requires investigation)

## Test Methodology

Tests follow RFC 2544 Network Interconnect Benchmark standard:

1. **Throughput Testing** (iperf3)
   - TCP tests: 10s, 30s, 60s durations
   - UDP tests: Multiple frame sizes (64, 128, 256, 512, 1024, 1518 bytes)

2. **Latency Testing** (sockperf)
   - Ping-pong latency measurement
   - Message sizes: 64, 256, 512, 1024, 1518 bytes

3. **Frame Loss Testing** (mausezahn)
   - Packet generation across multiple frame sizes
   - 10,000 packets per test

## Results

Full benchmark results are available in the `rfc2544_results_20251020_142654/` directory:

- [📊 Full Benchmark Report](rfc2544_results_20251020_142654/RFC2544_Benchmark_Report.md)
- [📈 Performance Graphs](rfc2544_results_20251020_142654/rfc2544_performance_graphs.png)
- [📉 Jitter Analysis](rfc2544_results_20251020_142654/jitter_analysis.png)
- [💾 Raw JSON Data](rfc2544_results_20251020_142654/benchmark_results.json)

## Tools Used

- **iperf3** - Throughput measurement
- **sockperf** - Latency measurement
- **mausezahn** - Frame generation
- **Python 3** - Test automation and analysis

## Running the Tests

To reproduce these tests:

```bash
# Install required tools
sudo apt install iperf3 mausezahn
pip3 install --break-system-packages pandas matplotlib seaborn

# Ensure servers are running on target (10.0.100.2)
# On target machine:
iperf3 -s &
sockperf server -i 0.0.0.0 -p 11111 &

# Run benchmark
python3 rfc2544_benchmark.py
```

## Conclusions

The target system (10.0.100.2) demonstrates:

✅ **Excellent TCP performance** - Consistent ~941 Mbps throughput
✅ **Excellent latency** - Sub-100μs round-trip time
✅ **Good UDP throughput** - Approaching line rate for larger frames
⚠️ **Moderate packet loss** - 3-5% loss requires investigation

### Recommendations

1. Investigate UDP packet loss causes
   - Check for buffer overflows
   - Verify NIC offloading settings
   - Monitor CPU utilization during tests

2. Consider enabling hardware timestamping for TSN applications

3. Performance is suitable for most non-critical network applications

---

*Benchmark suite generated using RFC 2544 Network Benchmark tools*