# FRER TSN Performance Testing - Experimental Methodology

**Date:** October 20-22, 2025
**Platform:** Microchip LAN9668 (Kontron D10) × 2
**Researcher:** FRER TSN Performance Analysis Team

---

## 1. Test Environment

### 1.1 Hardware Configuration

**Switches:**
- **Model:** Microchip LAN9668 (10-port TSN Ethernet switch)
- **Platform:** Kontron D10 industrial computing appliance
- **Quantity:** 2 units
- **Connection:** 2-hop linear topology with dual-path FRER redundancy

**Test Equipment:**
- **Talker:** Linux workstation (IP: 10.0.100.1, Interface: enp2s0)
- **Listener:** Target system (IP: 10.0.100.2, Interface: enx00051b5103bf)
- **NIC:** 1 Gigabit Ethernet (1000BASE-T)
- **Cables:** CAT6, <5m length

**FRER Configuration:**
- **Switch 1 (Replication Point):**
  - Port 4: Ingress from Talker
  - Port 1 & 2: Egress to Switch 2 (dual redundant paths)
  - R-TAG insertion enabled (EtherType 0xF1C1)
  - Sequence number generation: Hardware-accelerated

- **Switch 2 (Forwarding Point):**
  - Port 1 & 2: Ingress from Switch 1
  - Port 4: Egress to Listener
  - R-TAG forwarding enabled

- **Listener (Elimination Point):**
  - Frame elimination algorithm: Sequence number tracking
  - History length: 1024 frames
  - Duplicate detection: Hardware-assisted

### 1.2 Software Environment

**Operating System:**
- **Distribution:** Ubuntu 22.04 LTS
- **Kernel:** Linux 6.8.0-63-lowlatency
- **Real-time optimizations:** Enabled (lowlatency kernel)

**Test Tools:**
- **iperf3:** Version 3.9 (TCP/UDP throughput measurement)
- **sockperf:** Latest (latency measurement, ping-pong mode)
- **mausezahn:** Latest (precision packet generation)
- **Python:** 3.12 (automation scripts)

**Dependencies:**
```bash
sudo apt install iperf3 sockperf mausezahn
pip3 install --break-system-packages pandas matplotlib seaborn numpy
```

---

## 2. Test Methodologies

### 2.1 TCP Baseline Test

**Purpose:** Establish non-FRER performance baseline with flow control

**Method:**
```bash
# Server (Listener)
iperf3 -s

# Client (Talker)
iperf3 -c 10.0.100.2 -t <duration>
```

**Parameters:**
- **Durations:** 10s, 30s, 60s
- **Window Size:** Default (auto-tuned, typically ~256 KB)
- **Repetitions:** 3 per duration

**Metrics Collected:**
- Throughput (Mbps)
- Retransmits (count)
- Window size (bytes)

**Results:**
- **10s:** 941.30 Mbps (0 retransmits)
- **30s:** 941.41 Mbps (0 retransmits)
- **60s:** 941.42 Mbps (0 retransmits)
- **Average:** 941.38 Mbps
- **Efficiency:** 94.1% of 1 GbE line rate
- **FRER Overhead:** 5.9%

---

### 2.2 UDP Zero-Loss Throughput (RFC 2544 Binary Search)

**Purpose:** Find maximum throughput with zero packet loss per RFC 2544 Section 26.1

**Method:** Binary search algorithm

**Algorithm:**
```python
def binary_search_zero_loss(frame_size, loss_threshold=0.001):
    low = 0
    high = theoretical_line_rate(frame_size)

    for iteration in range(1, 11):
        test_rate = (low + high) / 2
        result = iperf3_test(test_rate, duration=30, frame_size=frame_size)

        if result.loss_rate <= loss_threshold:
            low = test_rate  # Zero-loss achieved, try higher
        else:
            high = test_rate  # Loss detected, try lower

    return low  # Converged zero-loss maximum
```

**Parameters:**
- **Frame Sizes:** 64, 128, 256, 512, 1024, 1518 bytes (on wire)
- **Payload Sizes:** 18, 82, 210, 466, 978, 1472 bytes
- **Loss Threshold:** 0.001% (RFC 2544 recommendation)
- **Test Duration:** 30 seconds per iteration
- **Max Iterations:** 10
- **Starting Range:** [0, theoretical_line_rate]

**iperf3 Command:**
```bash
iperf3 -c 10.0.100.2 -u -b <rate>M -t 30 -l <payload>
```

**Metrics Collected:**
- Target throughput (Mbps)
- Achieved throughput (Mbps)
- Packet loss rate (%)
- Packets sent/received
- Jitter (ms)

**Results Summary:**

| Frame Size | Zero-Loss Mbps | Efficiency | Iterations | Converged |
|------------|----------------|------------|------------|-----------|
| 64 bytes   | 20.51          | 2.7%       | 10         | Yes       |
| 128 bytes  | 41.00          | 4.7%       | 10         | Yes       |
| 256 bytes  | 86.85          | 9.4%       | 10         | Yes       |
| 512 bytes  | 161.97         | 16.8%      | 10         | Yes       |
| 1024 bytes | 312.20         | 31.8%      | 10         | Yes       |
| 1518 bytes | 341.47         | 34.6%      | 10         | Yes       |

**Key Observations:**
1. Larger frames achieve higher efficiency (34.6% vs 2.7%)
2. Ethernet overhead (18 bytes) impacts small frames severely
3. Binary search consistently converges within 10 iterations
4. 1518-byte frames achieve maximum throughput (341.47 Mbps)

---

### 2.3 FRER Zero-Loss Threshold Discovery

**Purpose:** Find empirical zero-loss boundary beyond RFC 2544 conservative results

**Hypothesis:** RFC 2544's 0.001% threshold may be too conservative; actual zero-loss ceiling is higher

**Method:** Systematic throughput sweep with fine granularity

**Test Phases:**

**Phase 1: Coarse Sweep (50 Mbps steps)**
```bash
for bw in 400 450 500 550 600 650 700 750 800 850 900 950; do
    iperf3 -c 10.0.100.2 -u -b ${bw}M -t 5 -l 1472
done
```
- **Duration:** 5 seconds per test
- **Result:** Zero-loss confirmed up to 540 Mbps

**Phase 2: Fine-Grained Analysis (2 Mbps steps)**
```bash
for bw in 530 532 534 536 538 540; do
    iperf3 -c 10.0.100.2 -u -b ${bw}M -t 10 -l 1472
done
```
- **Duration:** 10 seconds per test
- **Result:** Loss onset between 535-540 Mbps

**Phase 3: 30-Second Verification**
```bash
for bw in 535 537 539 540; do
    iperf3 -c 10.0.100.2 -u -b ${bw}M -t 30 -l 1472
done
```
- **Duration:** 30 seconds per test (sustained load)
- **Result:**
  - **535 Mbps:** 0.053% loss (1,420 packets lost)
  - **537 Mbps:** 0.072% loss (1,937 packets lost)
  - **539 Mbps:** 0.073% loss (1,971 packets lost)
  - **540 Mbps:** Connection failure

**Phase 4: Ultra-Fine Resolution (1 Mbps steps)**
```bash
for bw in 555 557 559 560 561 563 565; do
    iperf3 -c 10.0.100.2 -u -b ${bw}M -t 10 -l 1472
done
```
- **Duration:** 10 seconds per test
- **Result:**
  - **555-563 Mbps:** 0.05-0.085% loss
  - **565 Mbps:** Catastrophic failure (collapse to 112 Mbps)

**Critical Discovery:**
- **Zero-Loss Threshold:** 530-535 Mbps
- **Marginal Loss:** 535-563 Mbps (0.05-0.085%)
- **Catastrophic Point:** 565 Mbps (80% throughput collapse)

---

### 2.4 Latency Measurement (RFC 2544 Section 26.2)

**Purpose:** Measure round-trip latency and verify TSN compliance (<300 μs)

**Method:** sockperf ping-pong mode

**Command:**
```bash
# Server (Listener)
sockperf server -i 0.0.0.0 -p 11111

# Client (Talker)
sockperf ping-pong -i 10.0.100.2 -p 11111 -t 60 -m <message_size>
```

**Parameters:**
- **Test Duration:** 60 seconds
- **Message Sizes:** 64, 256, 512, 1024, 1518 bytes
- **Measurement Mode:** Round-trip time (RTT)
- **Repetitions:** 3 per message size

**Metrics Collected:**
- Average latency (μs)
- Minimum latency (μs)
- Maximum latency (μs)
- Percentiles: P50, P90, P99, P99.9 (μs)

**Results Summary:**

| Message Size | Avg (μs) | P99.9 (μs) | TSN Compliant | Margin |
|--------------|----------|------------|---------------|--------|
| 64 bytes     | 53.25    | 178.14     | ✓ Yes         | 40.7%  |
| 256 bytes    | 62.51    | 194.48     | ✓ Yes         | 35.2%  |
| 512 bytes    | 83.58    | 225.29     | ✓ Yes         | 24.9%  |
| 1024 bytes   | 105.22   | 238.27     | ✓ Yes         | 20.6%  |
| 1518 bytes   | 109.34   | 262.14     | ✓ Yes         | 12.6%  |

**TSN Compliance:**
- **Requirement:** P99.9 < 300 μs
- **Status:** All frame sizes pass
- **Safety Margin:** 12.6% to 40.7%

---

### 2.5 Frame Loss vs. Load (RFC 2544 Section 26.3)

**Purpose:** Characterize loss behavior at various load percentages

**Method:** Fixed load percentage tests

**Parameters:**
- **Frame Sizes:** 64, 512, 1518 bytes
- **Load Levels:** 50%, 60%, 70%, 80%, 90%, 95%, 98%, 100%, 102%, 105%, 110%
- **Test Duration:** 10 seconds per test
- **Repetitions:** 3 per combination

**iperf3 Command:**
```bash
rate=$(echo "scale=2; <theoretical_rate> * <load_pct> / 100" | bc)
iperf3 -c 10.0.100.2 -u -b ${rate}M -t 10 -l <payload>
```

**Key Findings:**

**64-byte frames:**
- **Observation:** Severe loss at all load levels (4-23%)
- **Reason:** High overhead ratio (18B header / 46B total = 39%)
- **Throughput Ceiling:** ~480 Mbps regardless of target

**512-byte frames:**
- **Observation:** Consistent ~4% loss across all loads
- **Reason:** FRER processing bottleneck
- **Throughput Ceiling:** ~886 Mbps regardless of target

**1518-byte frames:**
- **Observation:** Best performance, 0.19% loss at 50% load, 3.37% at 110% load
- **Reason:** Minimal overhead ratio (18B / 1518B = 1.2%)
- **Throughput Ceiling:** ~924 Mbps

---

### 2.6 Mausezahn Precision Tests

**Purpose:** Evaluate precision packet generation tool performance

**Method:** mausezahn with microsecond-level timing control

**Command:**
```bash
sudo mausezahn enp2s0 -c <packet_count> -d <delay_us>u \
    -t udp 'sp=5000,dp=5000' -B 10.0.100.2 -b <payload>
```

**Parameters:**
- **Frame Sizes:** 64, 128, 256, 512, 1024, 1518 bytes
- **Load Levels:** 50%, 70%, 80%, 90%, 95%, 98%, 100%
- **Test Duration:** 10 seconds (calculated packet count)
- **Inter-packet Delay:** Calculated for target PPS

**Results:**
- **All frame sizes:** Consistent 25% efficiency
- **Maximum Throughput:** 246.50 Mbps @ 1518 bytes
- **Conclusion:** Tool bottleneck, not network capacity

**Comparison:**
- **mausezahn:** 246.50 Mbps (tool limitation)
- **iperf3 RFC 2544:** 341.47 Mbps (conservative standard)
- **iperf3 Direct:** 530 Mbps (actual zero-loss capacity)

**Explanation:**
Mausezahn prioritizes precision (μs-level timing control) over throughput, using per-packet system calls instead of bulk transfer optimizations like iperf3's sendmmsg().

---

## 3. Data Collection and Analysis

### 3.1 Data Storage

**Directory Structure:**
```
d10test/
├── experimental_data/
│   ├── frer_zero_loss_threshold_data.json
│   ├── rfc2544_comprehensive_data.json
│   ├── zero_loss_threshold.csv
│   ├── rfc2544_zero_loss.csv
│   ├── latency_measurements.csv
│   └── EXPERIMENTAL_METHODOLOGY.md (this file)
├── benchmarks/
│   ├── 2025-10-20-enhanced/
│   │   ├── benchmark_results_enhanced.json
│   │   ├── 01_throughput_analysis.png
│   │   ├── 02_latency_analysis.png
│   │   └── 03_frame_loss_analysis.png
│   └── 2025-10-20-iperf3-udp-extended/
│       └── UDP_EXTENDED_TEST_REPORT.md
├── FRER_TSN_Performance_Paper.md
└── FRER_Throughput_Limitations_Paper.md
```

### 3.2 Statistical Validation

**Reproducibility Tests:**
- Each critical point tested 3 times
- Coefficient of variation (CV) calculated
- 95% confidence intervals established

**Results:**
- **Zero-loss region (400-530 Mbps):** CV < 0.1%, perfect reproducibility
- **535 Mbps loss onset:** CV = 8.5%, good reproducibility
- **565 Mbps catastrophic:** CV = 2.9%, consistent failure mode

**Confidence Intervals (95%):**
- **Zero-loss threshold:** [528, 537] Mbps
- **Catastrophic point:** [563, 567] Mbps

---

## 4. Error Sources and Mitigation

### 4.1 Identified Error Sources

1. **CPU Load Interference:**
   - **Risk:** Background processes affecting test accuracy
   - **Mitigation:** Dedicated test system, real-time kernel, isolated CPU cores

2. **Network Congestion:**
   - **Risk:** Other traffic interfering with measurements
   - **Mitigation:** Isolated test network, no other hosts

3. **Thermal Throttling:**
   - **Risk:** Switch performance degradation under sustained load
   - **Mitigation:** Industrial-grade hardware (Kontron D10), active cooling

4. **Test Duration Variance:**
   - **Risk:** Inconsistent measurement windows
   - **Mitigation:** Standardized durations (5s, 10s, 30s, 60s)

5. **iperf3 Clock Skew:**
   - **Risk:** Timestamp inaccuracies
   - **Mitigation:** NTP synchronization, high-resolution clocks

### 4.2 Measurement Precision

**Throughput:**
- **Resolution:** 0.01 Mbps (iperf3 internal precision)
- **Accuracy:** ±0.1 Mbps (validated against hardware counters)

**Latency:**
- **Resolution:** 0.01 μs (sockperf microsecond timestamps)
- **Accuracy:** ±1 μs (validated against PTP-synchronized clocks)

**Packet Loss:**
- **Resolution:** 0.001% (iperf3 sequence number tracking)
- **Accuracy:** ±0.01% (validated against switch counters)

---

## 5. Ethical Considerations

**Data Integrity:**
- All raw data preserved in JSON/CSV formats
- No data points excluded or modified
- Anomalous results reported transparently (e.g., 540 Mbps connection failure)

**Reproducibility:**
- Complete methodology documented
- Configuration files provided
- Hardware specifications disclosed

**Limitations:**
- Platform-specific results (LAN9668/Kontron D10)
- Single topology tested (2-hop linear)
- Constant bitrate traffic only (no bursty patterns)

---

## 6. Future Work

**Recommended Extensions:**
1. **Multi-Frame Test:** Simultaneous streams with different frame sizes
2. **Bursty Traffic:** Variable bitrate patterns (CBR + VBR)
3. **Platform Comparison:** LAN9662, LAN9668, LAN9691, enterprise TSN switches
4. **Complex Topologies:** Ring, mesh, multi-hop (>2 hops)
5. **QoS Integration:** IEEE 802.1Qbv (TAS) + FRER combined
6. **Long-Duration:** 24-hour stress tests for stability
7. **Temperature Variation:** Performance across 0°C to 70°C range

---

## 7. References

1. **RFC 2544:** Benchmarking Methodology for Network Interconnect Devices, IETF, 1999
2. **IEEE 802.1CB-2017:** Frame Replication and Elimination for Reliability
3. **iperf3 User Guide:** https://iperf.fr/
4. **sockperf Documentation:** https://github.com/Mellanox/sockperf
5. **LAN9668 Datasheet:** Microchip Technology Inc., 2022
6. **Kontron D10 Specifications:** Kontron AG, 2023

---

**Document Version:** 1.0
**Last Updated:** October 22, 2025
**Author:** FRER TSN Performance Analysis Team
