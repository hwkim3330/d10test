#!/bin/bash

# Control Group Tests - No FRER Baseline
# Target: 10.0.100.2 (direct connection, no FRER)

TARGET="10.0.100.2"
RESULTS_DIR="control_results_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULTS_DIR"

echo "======================================================================="
echo "CONTROL GROUP EXPERIMENT - NO FRER BASELINE"
echo "Target: $TARGET"
echo "Results: $RESULTS_DIR"
echo "======================================================================="
echo ""

# =============================================================================
# 1. TCP BASELINE
# =============================================================================
echo "=== TCP Baseline Tests ==="
echo "[10s test]"
iperf3 -c $TARGET -t 10 | tee "$RESULTS_DIR/tcp_10s.txt"
sleep 2

echo "[30s test]"
iperf3 -c $TARGET -t 30 | tee "$RESULTS_DIR/tcp_30s.txt"
sleep 2

echo "[60s test]"
iperf3 -c $TARGET -t 60 | tee "$RESULTS_DIR/tcp_60s.txt"
sleep 2

# =============================================================================
# 2. UDP ZERO-LOSS SWEEP (Quick test - not full binary search)
# =============================================================================
echo ""
echo "=== UDP Zero-Loss Sweep Tests ==="

for size in 64 128 256 512 1024 1472; do
    echo ""
    echo "Frame size: $size bytes (payload)"
    
    # Test at increasing rates to find ceiling
    for rate in 500 600 700 800 900 950 980; do
        echo "  Testing $rate Mbps..."
        iperf3 -c $TARGET -u -b ${rate}M -t 10 -l $size 2>&1 | \
            tee -a "$RESULTS_DIR/udp_sweep_${size}B.txt" | \
            grep -E "receiver|lost"
        sleep 1
    done
done

# =============================================================================
# 3. LATENCY TESTS
# =============================================================================
echo ""
echo "=== Latency Measurements (sockperf) ==="

for size in 64 256 512 1024 1518; do
    echo "Message size: $size bytes (60s test)..."
    sockperf ping-pong -i $TARGET -p 11111 -t 60 -m $size 2>&1 | \
        tee "$RESULTS_DIR/latency_${size}B.txt"
    sleep 2
done

# =============================================================================
# 4. QUICK COMPARISON TEST
# =============================================================================
echo ""
echo "=== Quick Comparison Test (1518B frame) ==="

echo "[UDP 530 Mbps - FRER achieved this]"
iperf3 -c $TARGET -u -b 530M -t 30 -l 1472 | tee "$RESULTS_DIR/udp_530_comparison.txt"
sleep 2

echo "[UDP 700 Mbps - Testing if no-FRER can exceed FRER]"
iperf3 -c $TARGET -u -b 700M -t 30 -l 1472 | tee "$RESULTS_DIR/udp_700_comparison.txt"
sleep 2

echo "[UDP 850 Mbps - High load test]"
iperf3 -c $TARGET -u -b 850M -t 30 -l 1472 | tee "$RESULTS_DIR/udp_850_comparison.txt"

echo ""
echo "======================================================================="
echo "✓ Control group tests complete!"
echo "Results saved in: $RESULTS_DIR"
echo "======================================================================="
