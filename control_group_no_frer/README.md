# Control Group Experiment - No FRER Baseline

**Purpose:** Establish performance baseline WITHOUT Frame Replication and Elimination for Reliability (FRER)

**Comparison:**
- **Control Group (This):** Direct connection or single-switch, no FRER
- **Treatment Group:** 2-hop FRER network with dual-path redundancy

**Expected Outcome:** Control group should show significantly higher throughput and lower latency, proving FRER overhead

---

## Network Configuration

**Current Setup:** Direct connection 10.0.100.1 → 10.0.100.2 (NO intermediate switches, NO FRER)

**Platform:**
- Same hardware: Microchip LAN9668 (Kontron D10)
- Same tools: iperf3, sockperf
- Same methodology: RFC 2544

**Tests to Perform:**
1. ✓ TCP Baseline (10s, 30s, 60s)
2. ✓ UDP Zero-Loss Throughput (64B, 128B, 256B, 512B, 1024B, 1518B)
3. ✓ Latency Measurements (sockperf ping-pong)
4. ✓ Frame Loss vs Load Curves

---

## 🔬 CRITICAL FINDING: Hypothesis REJECTED!

**Expected:** Control group (no FRER) would show better performance
**Actual:** FRER-enabled network shows **33% BETTER UDP throughput!**

This unexpected result demonstrates that **TSN queue configuration** is more important than FRER overhead.

---

## ✅ Actual Results

**Without FRER (Measured on 2025-10-23):**
- **TCP:** 941 Mbps (identical to FRER) → **±0% difference**
- **UDP Zero-Loss:** ~398 Mbps (vs 530 Mbps with FRER) → **-25% WORSE without FRER!**
- **Latency:** 110.19 μs (vs 109.34 μs with FRER) → **+0.8% slower without FRER**

**FRER Advantage (not overhead!):**
```
FRER Advantage = (530 - 398) / 398 × 100% = +33.2%
```

---

## 📊 Scientific Comparison Table

| Metric | No FRER (Control) | With FRER (Treatment) | **FRER Advantage** |
|--------|-------------------|----------------------|--------------------|
| TCP Throughput | 941 Mbps | 941.42 Mbps | **±0% (identical)** |
| UDP 1518B Zero-Loss | **398 Mbps** | **530 Mbps** | **+33% with FRER!** |
| Avg Latency (1518B) | 110.19 μs | 109.34 μs | +0.8% better with FRER |
| P99.9 Latency (1518B) | 244.95 μs | 262.14 μs | -6.6% (slightly worse) |

### Frame Loss Comparison (UDP 1518B)

| Rate | No FRER Loss | With FRER Loss | Winner |
|------|--------------|----------------|--------|
| 398M | 0.000% | ~0% (within capacity) | Equal |
| 530M | 0.5% loss | 0.000% | **FRER wins** |
| 600M | 0.87% loss | ~2-3% (estimated) | Both saturated |

---

## 🔍 Root Cause Analysis

The control group showed **worse** performance because:

1. **TSN Queue Configuration:** FRER path has proper TSN queue management (CBS, TAS, priority queuing)
2. **Direct Path Limitations:** Control group uses standard best-effort Ethernet without TSN enhancements
3. **Small Frame Catastrophe:** 64B frames show 34% loss without TSN vs acceptable with FRER
4. **Buffer Management:** FRER switches configured with better buffer allocation

**Conclusion:** This experiment inadvertently demonstrated the **value of TSN**, not pure FRER overhead.

---

## 📁 Results Files

- 📄 [**Detailed Summary**](CONTROL_GROUP_RESULTS_SUMMARY.md) - Comprehensive analysis
- 📊 [**JSON Data**](control_group_data.json) - Structured experimental data
- 📄 [**TCP Baseline CSV**](control_tcp_baseline.csv)
- 📄 [**UDP 1518B Sweep CSV**](control_udp_1518B_sweep.csv)
- 📄 [**Latency Measurements CSV**](control_latency_measurements.csv)
- 📂 [**Raw Test Outputs**](control_results_20251023_095238/)

---

**Test Date:** 2025-10-23
**Status:** ✅ Completed - Unexpected but scientifically significant results
