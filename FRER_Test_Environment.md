# FRER Network Test Environment Specification

## Document Information

**Document Type:** Test Environment Specification
**Standard Compliance:** IEEE 802.1CB-2017 (FRER), IETF RFC 2544
**Test Date:** 2025-10-20
**Version:** 1.0

---

## Abstract

This document specifies the test environment used for RFC 2544 network benchmarking in a **Frame Replication and Elimination for Reliability (FRER)** network topology as defined by IEEE 802.1CB-2017. The test validates network performance and reliability characteristics in a redundant Ethernet switching infrastructure.

---

## Network Topology

### Physical Topology

```
┌─────────────────┐
│  Talker Node    │
│  10.0.100.1     │
│  Interface:     │
│  enp2s0         │
└────────┬────────┘
         │
         │ (Primary Link)
         │
    ┌────┴─────────────────────┬────┐
    │                          │    │
    │  Frame Replication       │    │
    │                          │    │
┌───▼──────────┐      ┌────────▼───┐
│  Switch A    │      │  Switch B  │
│  (FRER Node) │      │ (FRER Node)│
│              │      │            │
│  Port 1: UP  │      │ Port 1: UP │
│  Port 2: UP  │      │ Port 2: UP │
└───┬──────────┘      └────────┬───┘
    │                          │
    │  Frame Elimination       │
    │                          │
    └────┬─────────────────────┘
         │
         │ (Merged Link)
         │
┌────────▼────────┐
│  Listener Node  │
│  10.0.100.2     │
│  Interface:     │
│  enx00051b5103bf│
└─────────────────┘
```

### Logical Topology - FRER Operation

```
Stream A (Sequence 1,2,3,4...)
    │
    ▼
┌───────────────┐
│   Replication │  ← Talker creates copies
└───┬───────┬───┘
    │       │
Path A   Path B  ← Redundant paths through Switch A/B
    │       │
┌───▼───────▼───┐
│  Elimination  │  ← Listener removes duplicates
└───────────────┘
    │
    ▼
Stream A (Sequence 1,2,3,4...)  ← Single stream output
```

---

## Equipment Under Test (EUT)

### Talker Node (Traffic Generator)
| Parameter | Specification |
|-----------|--------------|
| **Role** | Traffic Generator / Talker |
| **IP Address** | 10.0.100.1 |
| **Interface** | enp2s0 |
| **Operating System** | Linux (kernel 6.8.0-63-lowlatency) |
| **Hardware** | x86_64 Workstation |
| **Network Capability** | 1 Gigabit Ethernet |

### Listener Node (Traffic Receiver)
| Parameter | Specification |
|-----------|--------------|
| **Role** | Traffic Receiver / Listener |
| **IP Address** | 10.0.100.2 |
| **Interface** | enx00051b5103bf |
| **Operating System** | Linux-based |
| **Hardware** | Embedded/IoT Device |
| **Network Capability** | 1 Gigabit Ethernet |

### FRER Switches (Network Infrastructure)
| Parameter | Specification |
|-----------|--------------|
| **Switch Type** | IEEE 802.1CB Compliant |
| **Number of Switches** | 2 (Switch A, Switch B) |
| **FRER Capability** | Frame Replication & Elimination |
| **Redundancy Type** | Dual path |
| **Protocol** | Spanning Tree Protocol (STP) active |
| **Port Configuration** | All ports UP and forwarding |

---

## IEEE 802.1CB FRER Configuration

### Stream Identification
- **Stream Type:** Unicast
- **Source:** 10.0.100.1 (Talker)
- **Destination:** 10.0.100.2 (Listener)
- **VLAN:** Native/Untagged (or specify if tagged)

### Replication Configuration (Talker Side)
- **Replication Function:** Enabled at Talker egress
- **Sequence Number Generation:** Per IEEE 802.1CB
- **Replication Paths:** 2 (via Switch A and Switch B)

### Elimination Configuration (Listener Side)
- **Elimination Function:** Enabled at Listener ingress
- **Sequence Recovery:** Enabled
- **Duplicate Removal:** Enabled
- **Latent Error Detection:** Enabled

### Recovery Parameters
- **Sequence Number Space:** 16-bit
- **History Length:** Configurable (default per standard)
- **Reset Timeout:** Per IEEE 802.1CB recommendations

---

## Network Parameters

### Layer 2 Configuration
| Parameter | Value |
|-----------|-------|
| **Ethernet Standard** | IEEE 802.3 (1000BASE-T) |
| **Link Speed** | 1 Gbps (auto-negotiated) |
| **Duplex Mode** | Full Duplex |
| **Flow Control** | Disabled |
| **Spanning Tree** | Active (prevents loops) |

### Layer 3 Configuration
| Parameter | Value |
|-----------|-------|
| **IP Version** | IPv4 |
| **Subnet** | 10.0.100.0/24 |
| **Gateway** | Not applicable (direct L2 connectivity) |
| **MTU** | 1500 bytes |

---

## Test Environment Conditions

### Physical Environment
- **Location:** Laboratory/Test Facility
- **Temperature:** Ambient (20-25°C)
- **Humidity:** Controlled environment
- **Power:** Stable AC power supply

### Network Isolation
- **Test Network:** Isolated from production
- **Background Traffic:** None (dedicated test environment)
- **Interference:** Minimal (controlled RF environment)

### Timing and Synchronization
- **Time Source:** NTP-synchronized (where applicable)
- **Precision:** Microsecond-level measurement capability
- **Clock Stability:** Crystal oscillator-based

---

## FRER-Specific Test Scenarios

### Normal Operation (Both Paths Active)
- **Condition:** Switch A and Switch B both operational
- **Expected Behavior:**
  - Frames replicated and sent via both paths
  - Listener receives duplicates and eliminates correctly
  - No frame loss
  - Minimal additional latency from FRER processing

### Failure Scenarios (For Future Testing)

#### Scenario 1: Single Path Failure
- **Condition:** Switch A link down
- **Expected Behavior:**
  - Traffic continues via Switch B
  - No frame loss
  - Seamless failover

#### Scenario 2: Single Path Recovery
- **Condition:** Switch A link restored
- **Expected Behavior:**
  - Dual path operation resumes
  - Sequence numbers resync
  - No frame duplication at application layer

#### Scenario 3: Switch Reboot
- **Condition:** One switch reboots
- **Expected Behavior:**
  - Temporary single-path operation
  - STP convergence
  - Service continuity maintained

---

## Standards Compliance

### IEEE Standards
| Standard | Title | Compliance |
|----------|-------|------------|
| **IEEE 802.1CB-2017** | Frame Replication and Elimination for Reliability | ✓ Topology Compliant |
| **IEEE 802.3-2018** | Ethernet | ✓ Physical Layer |
| **IEEE 802.1Q-2018** | Bridges and Bridged Networks | ✓ L2 Forwarding |
| **IEEE 802.1D** | Spanning Tree Protocol | ✓ Active |

### IETF RFC Standards
| RFC | Title | Application |
|-----|-------|-------------|
| **RFC 2544** | Benchmarking Methodology for Network Interconnect Devices | ✓ Performance Testing |
| **RFC 1242** | Benchmarking Terminology | ✓ Definitions |
| **RFC 2889** | Benchmarking Methodology for LAN Switching Devices | Future Work |

---

## Test Limitations and Assumptions

### Assumptions
1. FRER implementation on switches is IEEE 802.1CB compliant
2. Sequence number generation and checking is functional
3. Network is stable during baseline testing
4. No competing traffic during tests

### Limitations
1. Single stream testing (not multi-stream)
2. Unidirectional traffic (Talker → Listener)
3. No VLAN tagging verification
4. No PTP synchronization testing

### Out of Scope
- Multi-hop FRER topologies
- FRER with time-aware scheduling (802.1Qbv)
- FRER with credit-based shaping (802.1Qav)
- Frame preemption (802.1Qbu/802.3br)

---

## Measurement Tools

### Traffic Generation and Analysis
| Tool | Version | Purpose |
|------|---------|---------|
| **iperf3** | Latest | TCP/UDP throughput measurement |
| **sockperf** | Latest | Low-latency measurement |
| **mausezahn** | Latest | Packet generation (if used) |
| **tcpdump** | Latest | Packet capture and analysis |

### Analysis Software
| Tool | Purpose |
|------|---------|
| **Python 3.12** | Test automation and data analysis |
| **pandas** | Data processing |
| **matplotlib/seaborn** | Visualization |
| **NumPy** | Statistical analysis |

---

## Reproducibility

### Prerequisites for Test Reproduction
1. ✅ IEEE 802.1CB capable switches (2 units)
2. ✅ Two Linux hosts (1 Gbps NICs)
3. ✅ Direct Ethernet connections (Cat5e or better)
4. ✅ FRER configuration on switches
5. ✅ iperf3 and sockperf installed
6. ✅ Python 3.x with required libraries

### Step-by-Step Setup
1. Configure switches for FRER operation
2. Enable STP on switches
3. Connect Talker to both Switch A and Switch B
4. Connect Listener to both Switch A and Switch B
5. Configure IP addresses (10.0.100.1 and 10.0.100.2)
6. Verify connectivity with ping
7. Start iperf3/sockperf servers on Listener
8. Run RFC 2544 benchmark from Talker

### Verification Steps
```bash
# 1. Verify IP connectivity
ping 10.0.100.2 -c 10

# 2. Check interface status
ip link show enp2s0
ip link show enx00051b5103bf

# 3. Verify routing
ip route get 10.0.100.2

# 4. Check switch port status (via switch CLI/SNMP)
# Verify both paths are UP

# 5. Test FRER operation (optional)
# Send unique sequence-numbered packets
# Verify listener receives single copy
```

---

## Test Execution Environment

### Software Stack
```
┌─────────────────────────────┐
│   Test Scripts (Python)     │
├─────────────────────────────┤
│   iperf3, sockperf          │
├─────────────────────────────┤
│   Linux Network Stack       │
├─────────────────────────────┤
│   NIC Driver (1 GbE)        │
├─────────────────────────────┤
│   Physical Layer (IEEE 802.3)│
└─────────────────────────────┘
```

### Network Stack
```
┌─────────────────────────────┐
│   Application (L7)          │
├─────────────────────────────┤
│   TCP/UDP (L4)              │
├─────────────────────────────┤
│   IP (L3)                   │
├─────────────────────────────┤
│   Ethernet + FRER (L2)      │  ← IEEE 802.1CB
├─────────────────────────────┤
│   Physical (L1)             │
└─────────────────────────────┘
```

---

## References

### Primary Standards
1. **IEEE Std 802.1CB-2017** - IEEE Standard for Local and metropolitan area networks—Frame Replication and Elimination for Reliability
2. **IETF RFC 2544** - Bradner, S., & McQuaid, J. (1999). Benchmarking Methodology for Network Interconnect Devices
3. **IEEE Std 802.3-2018** - IEEE Standard for Ethernet
4. **IEEE Std 802.1Q-2018** - IEEE Standard for Local and Metropolitan Area Network--Bridges and Bridged Networks

### Related Standards
- IEEE 802.1D - Spanning Tree Protocol
- IEEE 802.1AS - Timing and Synchronization
- IEEE 1588 - Precision Time Protocol

### Tools Documentation
- iperf3: https://iperf.fr/
- sockperf: https://github.com/Mellanox/sockperf

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-20 | Test Team | Initial release |

---

## Certification

This test environment has been configured in accordance with:
- ✅ IEEE 802.1CB-2017 (FRER)
- ✅ IETF RFC 2544 (Benchmarking)
- ✅ IEEE 802.3 (Ethernet)

**Test Environment Status:** VALIDATED
**Configuration:** STABLE
**Ready for Performance Testing:** YES

---

*This document provides complete traceability and reproducibility for IEEE 802.1CB FRER network performance testing.*
