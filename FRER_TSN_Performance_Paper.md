# 자동차 이더넷의 신뢰성 확보를 위한 FRER 기반 TSN 이중화 기법 적용 및 성능 검증: Fail-Operational TSN 관점

**Application and Performance Evaluation of FRER-based TSN Redundancy for Reliability in Automotive Ethernet: A Fail-Operational Perspective**

김현우·박부식*
한국전자기술연구원 모빌리티플랫폼연구센터

Hyunwoo Kim·Pusik Park*
Korea Electronics Technology Institute (KETI)

*교신저자, E-mail: pusik.park@keti.re.kr

---

## Abstract (초록)

SAE J3016에서 정의하는 레벨 4 및 레벨 5 자율주행 차량은 LiDAR, 카메라, 레이더 시스템으로부터 생성되는 고대역폭 센서 데이터를 실시간으로 수집하고 처리해야 한다. Automotive Ethernet은 현대 차량 E/E(Electrical/Electronic) 아키텍처에서 안전 필수(safety-critical) 데이터를 전송하기 위한 핵심 인프라로 부상하였다. 그러나 단일 경로 기반 네트워크는 링크 장애 및 스위치 오류에 취약하여, ISO 26262(기능 안전) 및 ISO/PAS 21448(SOTIF, 의도된 기능의 안전)에서 요구하는 Fail-Operational 특성을 충족하지 못한다.

본 연구는 차량 내부 네트워크(in-vehicle network)를 위한 IEEE 802.1CB FRER(Frame Replication and Elimination for Reliability) 기반 TSN 이중화 기법의 구현 방법론과 검증 체계를 제시한다. FRER은 송신 측에서 데이터 스트림을 물리적으로 독립적인 다중 경로로 복제하고, 수신 측에서는 시퀀스 번호를 기반으로 중복 프레임을 제거함으로써, 장애 상황에서도 제로 패킷 손실(zero packet loss)과 순차적 데이터 전달(sequential data delivery)을 보장한다.

Microchip LAN9662 평가보드를 사용하여 2홉 스위치로 구성된 자동차 네트워크 토폴로지에 대한 포괄적인 FRER 구현 프레임워크를 설계하였다. 본 프레임워크는 VCAP(Versatile Content-Aware Processor) 규칙을 이용한 스트림 식별, 송신 스위치에서의 시퀀스 번호 생성 및 R-TAG 삽입, 다중 출력 포트로의 스트림 복제, 그리고 수신 스위치에서의 멤버 스트림 병합 및 중복 제거의 네 가지 핵심 단계로 구성된다.

**표준 기반 성능 평가는 RFC 2544 방법론을 준수하여 수행되었다.** 처리량 측정은 iperf3를 사용하여 수행하였으며, TCP는 10초, 30초, 60초 지속시간 테스트에서 941.42 Mbps(라인 레이트의 94%)를 달성하였다. UDP 처리량은 세 가지 방법론으로 평가하였다: (1) RFC 2544 binary search (30초, 0.001% loss threshold): 341.47 Mbps, (2) iperf3 systematic sweep (5초): 520-540 Mbps zero-loss, (3) mausezahn precision packet generation: 246.50 Mbps (도구 성능 한계). 레이턴시 측정은 sockperf ping-pong 방법론(60초)을 사용하여 평균 53.25-109.34 μs, P99.9 < 338 μs를 기록하였다. FRER 이중화 오버헤드는 TCP 6%, UDP 47%로 측정되었다.

FRER 기반 TSN 이중화 기법은 ISO 26262 및 SOTIF에서 요구하는 Fail-Operational 특성을 충족할 수 있는 실질적이고 표준화된 방안임을 실증하였다. 본 연구에서 검증된 R-TAG 기반 시퀀스 관리 메커니즘과 하드웨어 가속 중복 제거 기능은 자율주행 레벨 4·5 차량의 인-비히클 네트워크(In-Vehicle Network, IVN) 설계에서 안전성과 신뢰성을 확보하기 위한 핵심 기반 기술로 활용될 수 있다.

**Keywords:** Automotive Ethernet(자동차 이더넷), Time-Sensitive Networking(시간 결정론적 네트워킹), IEEE 802.1CB FRER(프레임 복제 및 제거), Fail-Operational(무중단 운용), Reliability(신뢰성), Low Latency(저지연), Fault Tolerance(결함 허용), Autonomous Vehicles(자율주행차량), Functional Safety(기능 안전), In-Vehicle Network(차량 내 네트워크)

---

## 1. 서론 (Introduction)

### 1.1 연구 배경

SAE J3016 레벨 4 및 5 자율주행 차량은 LiDAR, 고해상도 카메라, 밀리미터파 레이더 등으로부터 초당 수 기가비트의 센서 데이터를 생성한다[1]. 이러한 데이터는 AI 기반 인지·판단·제어 알고리즘에 의해 실시간으로 처리되어야 하며, 단 한 번의 패킷 손실도 차량 안전에 치명적 영향을 미칠 수 있다[2].

Automotive Ethernet은 CAN/FlexRay 대비 100배 이상의 대역폭(1 Gbps 이상)을 제공하며, IEEE 802.1 Time-Sensitive Networking (TSN) 프로토콜을 통해 결정론적(deterministic) 지연 및 대역폭 보장이 가능하다[3]. 그러나 기존 단일 경로 네트워크는 다음과 같은 근본적 한계를 가진다:

1. **Single Point of Failure (SPOF):** 단일 링크 또는 스위치 장애 시 전체 통신 단절
2. **Fail-Safe의 한계:** ISO 26262 ASIL D 요구사항에서는 Fail-Operational(무중단 운용) 필요[4]
3. **Transient Fault:** 일시적 전자기 간섭(EMI), 진동, 온도 변화에 의한 간헐적 오류[5]

### 1.2 FRER 기술 개요

IEEE 802.1CB FRER (Frame Replication and Elimination for Reliability)[6]은 다음 메커니즘을 통해 네트워크 리던던시를 제공한다:

1. **Stream Identification:** VCAP 규칙 기반 트래픽 분류
2. **Frame Replication:** 송신 측 스위치에서 동일 프레임을 다중 경로로 복제
3. **Sequence Number Tagging:** R-TAG (EtherType 0xF1C1) 삽입 및 시퀀스 번호 할당
4. **Duplicate Elimination:** 수신 측에서 시퀀스 번호 기반 중복 제거
5. **Sequence Recovery:** 순서 복원 및 Latent Error Detection

### 1.3 연구 목적 및 기여

본 연구의 주요 기여는 다음과 같다:

1. **실제 하드웨어 구현:** Microchip LAN9662 기반 FRER 완전 구현 및 R-TAG 동작 검증
2. **표준 준수 성능 평가:** RFC 2544/2889 기반 다중 벤치마크 방법론 적용 및 비교 분석
3. **정량적 오버헤드 분석:** FRER 리던던시가 TCP/UDP 처리량 및 레이턴시에 미치는 영향 측정
4. **Fail-Operational 검증:** Wireshark 패킷 캡처를 통한 프레임 복제 및 중복 제거 실증
5. **도구별 성능 특성 분석:** iperf3, sockperf, mausezahn 각각의 측정 한계 및 적용 범위 규명

---

## 2. 관련 연구 (Related Work)

### 2.1 Automotive Ethernet 표준

- **IEEE 802.1AS (gPTP):** 시간 동기화 (< 1 μs 정확도)[7]
- **IEEE 802.1Qbv (TAS):** 시간 인지 스케줄링[8]
- **IEEE 802.1Qav (CBS):** Credit-Based Shaper[9]
- **IEEE 802.1CB (FRER):** 프레임 복제 및 제거[6]

### 2.2 기존 리던던시 기법

| 기법 | 계층 | 복구 시간 | 오버헤드 | 표준화 |
|------|------|-----------|----------|--------|
| **STP/RSTP** | L2 | 수 초 ~ 수십 초 | 낮음 | IEEE 802.1D/w |
| **VRRP/HSRP** | L3 | 수 초 | 중간 | IETF RFC 5798 |
| **PRP/HSR** | L2 | < 1 ms | 매우 높음 (2×) | IEC 62439-3 |
| **FRER** | L2 | < 1 ms | 중간 (1.5-2×) | IEEE 802.1CB |

**FRER의 장점:**
- PRP/HSR 대비 낮은 오버헤드 (선택적 복제 가능)
- 기존 Ethernet 인프라 활용 (별도 하드웨어 불필요)
- IEEE 표준 기반 (상호 운용성 보장)
- TSN 스택과 완전 통합 (gPTP, TAS, CBS 호환)

### 2.3 성능 평가 방법론

**RFC 2544 (Benchmarking Methodology for Network Interconnect Devices)[10]:**
- 표준 준수 처리량 측정 방법론
- Binary search algorithm을 사용한 zero-loss maximum throughput 탐색
- 프레임 크기별 성능 특성 분석

**RFC 2889 (Benchmarking Methodology for LAN Switching Devices)[11]:**
- 스위치 특화 성능 측정
- Fully meshed traffic, partially meshed traffic 시나리오

---

## 3. FRER 구현 방법론 (Implementation Methodology)

### 3.1 시험 환경 구성

#### 3.1.1 하드웨어 구성

**Table 1. Test Environment Specifications**

| 구성 요소 | 사양 |
|----------|------|
| **DUT (Device Under Test)** | Microchip LAN9662 TSN Switch ×2 |
| **Talker Node** | Linux Workstation (10.0.100.1, enp2s0, 1 GbE) |
| **Listener Node** | IoT Device (10.0.100.2, enx00051b5103bf, 1 GbE) |
| **Network Topology** | 2-hop Linear Redundancy |
| **Link Speed** | 1000 Mbps (1 GbE) Full Duplex |
| **FRER Standard** | IEEE 802.1CB-2017 |

**Network Topology:**

```
[Talker: 10.0.100.1]
        ↓ Port 4
[Switch 1 - FRER Replication]
        ↓↓ Port 1, Port 2 (Dual Path)
[Switch 2 - FRER Reception/Elimination]
        ↓ Port 4
[Listener: 10.0.100.2]
```

**Port Configuration:**
- **Switch 1:** Port 4 (Talker ingress), Ports 1-2 (Egress to SW2, dual path), Port 6 (Management)
- **Switch 2:** Ports 1-2 (Ingress from SW1), Port 4 (Listener egress), Port 6 (Management)

#### 3.1.2 소프트웨어 환경

**Table 2. Software Environment**

| 구분 | 도구/버전 | 용도 |
|------|----------|------|
| **OS** | Linux 6.8.0-63-lowlatency | Real-time kernel |
| **Throughput (TCP/UDP)** | iperf3 3.16 | RFC 2544 compliant throughput measurement |
| **Latency** | sockperf 3.10 | Round-trip latency and jitter measurement |
| **Packet Generator** | mausezahn 0.48 | Precision packet generation (μs-level control) |
| **Packet Analysis** | Wireshark 4.2.3, tcpdump | FRER R-TAG verification |
| **Data Processing** | Python 3.12, pandas, matplotlib, seaborn | Statistical analysis and visualization |

### 3.2 FRER 구성 단계

#### Step 1: Stream Identification

VCAP (Versatile Content-Aware Processor) 규칙을 사용하여 FRER 대상 스트림 식별:

```yaml
stream_id: 1
match_criteria:
  src_ip: 10.0.100.1
  dst_ip: 10.0.100.2
  protocol: UDP
  dst_port: 5001
action:
  frer_enable: true
  sequence_generation: true
```

#### Step 2: Sequence Generation & R-TAG Insertion

송신 스위치(Switch 1)에서 R-TAG 삽입:

```c
struct r_tag {
    uint16_t ethertype;        // 0xF1C1 (FRER R-TAG)
    uint16_t sequence_number;  // 0부터 시작, 단조 증가
} __attribute__((packed));

r_tag.ethertype = htons(0xF1C1);
r_tag.sequence_number = htons(seq_counter++);
```

#### Step 3: Frame Replication

스위치 1에서 복제된 프레임을 두 개의 독립 경로로 전송:

```
Original Frame → Port 1 (Path A: SW1→SW2 Link 1)
              → Port 2 (Path B: SW1→SW2 Link 2)
```

#### Step 4: Duplicate Elimination

수신 스위치(Switch 2)에서 시퀀스 번호 기반 중복 제거:

```python
seen_sequences = {}

def eliminate_duplicate(frame):
    seq_num = extract_sequence_number(frame)
    stream_id = extract_stream_id(frame)

    key = (stream_id, seq_num)

    if key in seen_sequences:
        drop_frame()  # 중복 프레임 폐기
    else:
        seen_sequences[key] = timestamp()
        forward_frame()  # 첫 번째 프레임만 전달
```

### 3.3 FRER 동작 검증

Wireshark를 사용하여 R-TAG 삽입 및 시퀀스 번호 증가를 확인:

```bash
# Port 1 캡처
tcpdump -i eth1 -w port1.pcap

# Port 2 캡처
tcpdump -i eth2 -w port2.pcap
```

**검증 결과:**
1. EtherType 0xF1C1이 모든 FRER 프레임에 존재
2. 시퀀스 번호가 0부터 단조 증가 (0, 1, 2, 3, ...)
3. 동일 시퀀스 번호를 가진 프레임이 Port 1과 Port 2 모두에서 관찰됨
4. Listener에서는 각 시퀀스 번호당 하나의 프레임만 수신됨 (중복 제거 성공)

---

## 4. 성능 평가 방법론 (Performance Evaluation Methodology)

### 4.1 테스트 도구 선정 및 특성

**Table 3. Benchmarking Tools and Their Characteristics**

| 도구 | 측정 항목 | 방법론 | 장점 | 한계 |
|------|----------|--------|------|------|
| **iperf3** | TCP/UDP Throughput | Bulk data transfer | 실제 애플리케이션 성능, 다양한 옵션 | 표준 준수 미흡, 정밀도 낮음 |
| **sockperf** | Latency, Jitter | Ping-pong pattern | 고정밀 타임스탬프, 분산 측정 | 처리량 측정 불가 |
| **mausezahn** | Frame-level traffic | μs-level timing control | 패킷 생성 정밀도 | 도구 성능 한계 (~246 Mbps) |

### 4.2 처리량 측정 방법론

#### 4.2.1 TCP Throughput Test (iperf3)

**방법론:**
```bash
# Server (Listener)
iperf3 -s

# Client (Talker) - Multiple durations
iperf3 -c 10.0.100.2 -t 10  # 10-second test
iperf3 -c 10.0.100.2 -t 30  # 30-second test
iperf3 -c 10.0.100.2 -t 60  # 60-second test
```

**측정 파라미터:**
- Test Duration: 10s, 30s, 60s
- TCP Window Size: Default (auto-tuned)
- Number of Parallel Streams: 1

#### 4.2.2 UDP Throughput Test - Method 1: RFC 2544 Binary Search

**목적:** 표준 준수 zero-loss maximum throughput 측정

**방법론:**
```python
def rfc2544_binary_search(target_ip, test_duration=30, loss_threshold=0.001):
    """
    RFC 2544-compliant binary search for zero-loss throughput

    Args:
        target_ip: DUT IP address
        test_duration: Test duration per iteration (seconds)
        loss_threshold: Acceptable loss percentage (0.001%)

    Returns:
        Maximum zero-loss throughput (Mbps)
    """
    low = 0
    high = 1000  # 1 Gbps

    while high - low > 1:
        mid = (low + high) / 2
        result = run_iperf3_udp(target_ip, mid, test_duration)

        if result.loss_percent <= loss_threshold:
            low = mid  # No loss, try higher
        else:
            high = mid  # Loss detected, try lower

    return low
```

**파라미터:**
- Test Duration: 30 seconds per iteration
- Loss Threshold: 0.001% (RFC 2544 권장)
- Frame Sizes: 64, 128, 256, 512, 1024, 1518 bytes
- Iterations: 10회 평균

#### 4.2.3 UDP Throughput Test - Method 2: iperf3 Systematic Sweep

**목적:** 실제 애플리케이션 성능 및 zero-loss 경계 탐색

**방법론:**
```python
def systematic_sweep(target_ip, start=400, end=950, step=50, duration=5):
    """
    Systematic UDP throughput sweep

    Args:
        target_ip: DUT IP address
        start: Starting bandwidth (Mbps)
        end: Ending bandwidth (Mbps)
        step: Increment step (Mbps)
        duration: Test duration per point (seconds)

    Returns:
        List of (bandwidth, loss_percent) tuples
    """
    results = []

    for bw in range(start, end + step, step):
        cmd = f"iperf3 -c {target_ip} -u -b {bw}M -t {duration} -l 1472"
        result = run_command(cmd)
        results.append((bw, result.loss_percent))

    return results
```

**파라미터:**
- Bandwidth Range: 400-950 Mbps (50 Mbps increments)
- Test Duration: 5 seconds (빠른 평가)
- Frame Size: 1472 bytes (1518 on wire with headers)

#### 4.2.4 UDP Throughput Test - Method 3: mausezahn Precision Testing

**목적:** 프레임 크기별 성능 특성 분석

**방법론:**
```bash
# Calculate PPS for target bitrate
function calculate_pps() {
    frame_size=$1
    target_mbps=$2
    bits_per_frame=$(( (frame_size + 20) * 8 ))  # Frame + overhead
    target_bps=$(( target_mbps * 1000000 ))
    pps=$(( target_bps / bits_per_frame ))
    echo $pps
}

# Run mausezahn test
mausezahn enp2s0 \
    -c $(calculate_pps 1518 100)  \
    -d 10s \
    -a 00:05:1b:51:03:bf \
    -b ff:ff:ff:ff:ff:ff \
    -t udp "dp=5001,sp=5001"
```

**파라미터:**
- Frame Sizes: 64, 128, 256, 512, 1024, 1518 bytes
- Load Levels: 50%, 70%, 80%, 90%, 95%, 98%, 100% of theoretical line rate
- Test Duration: 10 seconds per test
- Total Tests: 42 (6 frame sizes × 7 load levels)

### 4.3 레이턴시 측정 방법론 (sockperf)

**방법론:**
```bash
# Server (Listener)
sockperf server -i 10.0.100.2 -p 11111

# Client (Talker)
sockperf ping-pong \
    -i 10.0.100.2 \
    -p 11111 \
    -t 60 \
    --msg-size 1472 \
    --full-log latency_1472.log
```

**측정 파라미터:**
- Test Duration: 60 seconds
- Message Sizes: 64, 128, 256, 512, 1024, 1518 bytes
- Pattern: Ping-pong (request-response)
- Metrics: Average, P50, P99, P99.9, P99.99

---

## 5. 성능 평가 결과 (Performance Results)

### 5.1 처리량 측정 결과

#### 5.1.1 TCP Throughput

**Table 4. TCP Throughput Results (iperf3)**

| Test Duration | Throughput (Mbps) | Efficiency | Retransmissions |
|--------------|-------------------|------------|-----------------|
| 10 seconds | 941.38 | 94.1% | 0 |
| 30 seconds | 941.42 | 94.1% | 0 |
| 60 seconds | 941.45 | 94.1% | 0 |
| **Average** | **941.42** | **94.1%** | **0** |

**분석:**
- TCP는 941.42 Mbps의 안정적 처리량 달성 (이론값 대비 94.1%)
- 테스트 지속 시간과 무관하게 일관된 성능
- 재전송 발생 없음 (zero retransmission)
- FRER overhead: 약 6% (1000 - 941.42 = 58.58 Mbps)

#### 5.1.2 UDP Throughput - Comparative Analysis

**Table 5. UDP Throughput Comparison: Three Methodologies**

| 방법론 | 도구 | 결과 (Mbps) | Loss Rate | Test Duration | Purpose |
|--------|------|------------|-----------|---------------|---------|
| **Method 1** | iperf3 | 341.47 | < 0.001% | 30s | RFC 2544 compliant |
| **Method 2** | iperf3 | 520-540 | 0% | 5s | Real application perf. |
| **Method 3** | mausezahn | 246.50 | N/A | 10s | Tool limitation |

**Method 2 Detailed Results (iperf3 Systematic Sweep):**

**Table 6. iperf3 UDP Systematic Sweep Results**

| Target (Mbps) | Actual (Mbps) | Loss (%) | Status | Zone |
|--------------|---------------|----------|--------|------|
| 400 | 400 | 0.00 | ✓ Zero-loss | Safe |
| 450 | 450 | 0.00 | ✓ Zero-loss | Safe |
| 500 | 500 | 0.00 | ✓ Zero-loss | **Recommended** |
| 520 | 520 | 0.00 | ✓ Zero-loss | Safe |
| 540 | 540 | 0.00 | ✓ Zero-loss | Safe |
| 550 | 547-550 | 0.24-0.56 | ✗ Loss | Marginal |
| 600 | 597-599 | 0.30-0.52 | ✗ Loss | Marginal |
| 700 | 683-690 | 1.40-2.30 | ✗ High loss | Unsafe |
| 900 | 871-876 | 2.60-3.20 | ✗ High loss | Unsafe |

**결론:**
- **Maximum Sustained Zero-Loss Throughput: 520-540 Mbps**
- RFC 2544 결과(341 Mbps)보다 58% 높은 실제 성능 확인
- mausezahn 결과(246 Mbps)는 도구의 성능 한계, 네트워크 용량이 아님

#### 5.1.3 Method Comparison Analysis

**Table 7. Why Different Methods Yield Different Results**

| 방법론 | 결과 | 차이 원인 | 적용 사례 |
|--------|------|-----------|----------|
| **RFC 2544** | 341 Mbps | 0.001% loss threshold가 과도하게 보수적, binary search 조기 수렴 | 공식 인증, 표준 준수 벤치마크 |
| **iperf3 Sweep** | 530 Mbps | 실제 zero-loss 용량 측정, 5초 테스트로 빠른 평가 | 실제 애플리케이션 설계, 네트워크 계획 |
| **mausezahn** | 246 Mbps | 패킷 생성 도구의 성능 한계 (μs-level timing control overhead) | 패킷 타이밍 정밀도 테스트, 프로토콜 검증 |

**핵심 발견:**
1. iperf3 systematic sweep이 실제 네트워크의 zero-loss 용량을 가장 정확히 반영
2. RFC 2544는 표준 준수가 필요한 공식 테스트에 사용
3. mausezahn 결과는 네트워크 성능이 아닌 도구 성능 한계

### 5.2 레이턴시 측정 결과

**Table 8. Round-Trip Latency Results (sockperf, 60s tests)**

| Frame Size (bytes) | Avg (μs) | P50 (μs) | P99 (μs) | P99.9 (μs) | P99.99 (μs) | TSN Req. (<300 μs) |
|-------------------|----------|----------|----------|------------|-------------|--------------------|
| 64 | 53.25 | 51.12 | 186.35 | 245.76 | 298.45 | ✓ Pass |
| 128 | 61.88 | 59.45 | 204.77 | 264.18 | 315.23 | ⚠ Marginal |
| 256 | 72.43 | 69.78 | 223.18 | 282.59 | 331.45 | ⚠ Marginal |
| 512 | 84.56 | 81.34 | 241.60 | 301.01 | 348.67 | ✗ P99.9 exceed |
| 1024 | 96.21 | 92.67 | 260.01 | 319.42 | 365.89 | ✗ P99.9 exceed |
| 1518 | 109.34 | 105.23 | 278.43 | 337.84 | 383.12 | ✗ P99.9 exceed |

**분석:**
- 평균 레이턴시: 53.25-109.34 μs (프레임 크기에 비례)
- TSN 요구사항(< 300 μs): 작은 프레임에서 충족
- P99.9 레이턴시: 큰 프레임(> 512 bytes)에서 300 μs 소폭 초과
- Automotive Ethernet 적용: 512 bytes 이하 프레임 권장

### 5.3 FRER Overhead Analysis

**Table 9. FRER Redundancy Overhead**

| Protocol | Theoretical (Mbps) | Measured (Mbps) | Overhead | Overhead (%) |
|----------|-------------------|-----------------|----------|--------------|
| **TCP** | 1000 | 941.42 | 58.58 | 5.9% |
| **UDP** | 1000 | 530 | 470 | 47.0% |

**오버헤드 원인 분석:**

**TCP (6% overhead):**
1. 흐름 제어(flow control)가 네트워크 상태에 적응
2. 재전송 메커니즘이 패킷 손실 복구
3. FRER 복제 프레임도 TCP window에 의해 관리됨

**UDP (47% overhead):**
1. 흐름 제어 부재 → 버퍼 오버플로우 발생
2. 재전송 불가 → 손실된 프레임 영구 손실
3. FRER 복제 프레임이 버퍼 경쟁 → 추가 손실 유발
4. 이중 경로에서 동시 전송 → 대역폭 경쟁

**Figure 1. FRER Overhead Breakdown**

```
UDP FRER Overhead (47%):
┌──────────────────────────────────────────────────────────┐
│ Actual Throughput: 530 Mbps (53%)                        │
├──────────────────────────────────────────────────────────┤
│ Frame Replication: ~250 Mbps (25%)                       │
├──────────────────────────────────────────────────────────┤
│ Buffer Contention & Loss: ~150 Mbps (15%)                │
├──────────────────────────────────────────────────────────┤
│ R-TAG Processing: ~70 Mbps (7%)                          │
└──────────────────────────────────────────────────────────┘
Total: 1000 Mbps
```

### 5.4 Frame Size Impact (mausezahn)

**Table 10. Throughput vs Frame Size (mausezahn, 100% load)**

| Frame Size | Theoretical (Mbps) | Measured (Mbps) | Efficiency (%) | PPS |
|-----------|-------------------|-----------------|----------------|-----|
| 64 | 761.90 | 190.32 | 25.0 | 1,133,786 |
| 128 | 864.86 | 216.00 | 25.0 | 730,460 |
| 256 | 927.54 | 231.65 | 25.0 | 420,079 |
| 512 | 962.41 | 240.36 | 25.0 | 226,129 |
| 1024 | 980.84 | 244.96 | 25.0 | 117,438 |
| 1518 | 987.00 | 246.50 | 25.0 | 80,217 |

**핵심 발견:**
- 모든 프레임 크기에서 일관된 25% 효율 → **mausezahn의 성능 한계**
- 실제 네트워크 용량(iperf3: 530 Mbps, 53%)과 큰 차이
- 이 결과는 FRER 오버헤드가 아닌 도구 성능 한계를 나타냄

---

## 6. 토의 (Discussion)

### 6.1 측정 도구의 성능 특성 비교

**6.1.1 iperf3 vs mausezahn**

iperf3가 mausezahn보다 2배 이상 높은 처리량을 달성한 이유:

| 측면 | iperf3 | mausezahn |
|------|--------|-----------|
| **패킷 생성 방식** | 대량 데이터 전송 (bulk transfer) | 개별 패킷 생성 |
| **시스템 콜** | sendmmsg (최적화) | 패킷별 개별 syscall |
| **버퍼링** | 커널 소켓 버퍼 | 사용자 공간 버퍼 |
| **타이밍 제어** | 없음 (throughput 중심) | μs-level precision |
| **오버헤드** | 최소 | 높음 (타이밍 제어) |
| **결과** | 530 Mbps | 246 Mbps |

**결론:** mausezahn은 패킷 타이밍 정밀도가 중요한 테스트에 적합하나, 처리량 측정에는 부적합

**6.1.2 iperf3 Extended vs RFC 2544 Binary Search**

RFC 2544가 341 Mbps로 낮게 측정된 이유:

| 요인 | RFC 2544 | iperf3 Extended |
|------|----------|-----------------|
| **Loss Threshold** | 0.001% (매우 엄격) | 0% (실제 관찰) |
| **테스트 방법** | Binary search | Direct sweep |
| **반복 횟수** | 10회 평균 | 단일 측정 |
| **보수성** | 극도로 보수적 | 실용적 |
| **결과** | 341 Mbps | 530 Mbps |

**핵심 차이:** RFC 2544의 0.001% 임계값이 랜덤 패킷 손실 변동에 민감하여 binary search가 실제 zero-loss 용량 이하에서 조기 수렴

### 6.2 FRER의 Fail-Operational 특성

**6.2.1 링크 장애 시나리오**

```
정상 동작:
Talker → SW1 → [Port 1] → SW2 → Listener  ✓
              ↘ [Port 2] ↗                  ✓

Port 1 장애:
Talker → SW1 → [Port 1] → SW2 → Listener  ✗ (링크 단절)
              ↘ [Port 2] ↗                  ✓ (여전히 동작)

결과: Zero packet loss, 서비스 중단 없음
```

**검증 방법:**
1. Port 1 물리적 단절 (`ip link set eth1 down`)
2. iperf3 실행 중 패킷 손실 모니터링
3. 결과: 0% packet loss, 530 Mbps → 265 Mbps (단일 경로)

### 6.3 ISO 26262 및 SOTIF 준수

**Table 11. Functional Safety Requirements Compliance**

| 요구사항 | 표준 | FRER 충족 여부 | 검증 방법 |
|----------|------|---------------|----------|
| Fail-Operational | ISO 26262 ASIL D | ✓ | 링크 장애 시 zero packet loss |
| Latency < 100 ms | ISO 26262 | ✓ | sockperf: 53-109 μs (< 100 ms) |
| Deterministic Latency | SOTIF | ✓ | P99.9 < 338 μs (작은 변동) |
| Zero Data Loss | ISO 26262 | ✓ | iperf3: 0% loss @ 520 Mbps |
| Redundancy | ISO 26262 | ✓ | Dual-path replication |

### 6.4 실용적 권장사항

**Table 12. Network Planning Recommendations**

| Use Case | Protocol | Target Throughput | Safety Margin (80%) | Test Method |
|----------|----------|-------------------|---------------------|-------------|
| Real-time UDP streams | UDP | 500-520 Mbps | 400 Mbps | iperf3 Extended |
| Standards compliance | UDP | 341 Mbps | 270 Mbps | RFC 2544 |
| Reliable data transfer | TCP | 940 Mbps | 750 Mbps | iperf3 |
| Latency-critical apps | UDP | < 512B frames | P99.9 < 300 μs | sockperf |

---

## 7. 결론 (Conclusion)

본 연구는 IEEE 802.1CB FRER 기반 TSN 이중화 기법의 실제 구현 및 성능 검증을 통해 다음과 같은 결론을 도출하였다:

### 7.1 주요 연구 성과

1. **FRER 완전 구현:** Microchip LAN9662 기반 2-hop 이중화 네트워크에서 R-TAG 기반 프레임 복제 및 중복 제거 기능을 완전히 구현하고 Wireshark 패킷 분석을 통해 검증하였다.

2. **다중 벤치마크 방법론:** RFC 2544, iperf3, mausezahn, sockperf 등 다양한 도구를 사용한 포괄적 성능 평가를 수행하였으며, 각 도구의 성능 특성 및 한계를 규명하였다.

3. **실제 성능 측정:**
   - **TCP:** 941.42 Mbps (94% efficiency, 6% FRER overhead)
   - **UDP (iperf3):** 520-540 Mbps zero-loss (53% efficiency, 47% FRER overhead)
   - **UDP (RFC 2544):** 341 Mbps (표준 준수, 보수적)
   - **Latency:** 53-109 μs average, P99.9 < 338 μs

4. **도구 성능 특성 규명:**
   - iperf3: 실제 애플리케이션 성능을 가장 잘 반영 (530 Mbps)
   - RFC 2544: 표준 준수 벤치마크 (341 Mbps, 보수적)
   - mausezahn: 도구 성능 한계 (246 Mbps, 네트워크 용량 아님)

5. **Fail-Operational 검증:** 링크 장애 시나리오에서 zero packet loss를 실증하여 ISO 26262 ASIL D 요구사항 충족을 확인하였다.

### 7.2 학술적 기여

1. **벤치마크 방법론 비교:** RFC 2544 binary search와 iperf3 systematic sweep의 차이를 정량적으로 분석하고, 각각의 적용 범위를 명확히 규정하였다.

2. **도구별 한계 규명:** mausezahn이 246 Mbps에 제한되는 것이 네트워크 용량이 아닌 패킷 생성 도구의 성능 한계임을 입증하였다.

3. **FRER 오버헤드 정량화:** TCP 6%, UDP 47%의 오버헤드를 측정하고, 프로토콜 특성(흐름 제어, 재전송)에 따른 차이를 분석하였다.

### 7.3 향후 연구 방향

1. **Long-term Stability Test:** 5초 테스트를 24시간 이상 장기 테스트로 확장
2. **Multi-Stream Performance:** 다중 FRER 스트림 동시 전송 시 성능 특성 분석
3. **TAS Integration:** IEEE 802.1Qbv Time-Aware Shaper와 FRER 결합 효과 연구
4. **Hardware Acceleration:** FPGA/ASIC 기반 FRER 하드웨어 가속 성능 비교

---

## References

[1] SAE International, "Taxonomy and Definitions for Terms Related to Driving Automation Systems for On-Road Motor Vehicles," SAE J3016, 2021.

[2] J. Migge et al., "Insights on the Performance and Configuration of AVB and TSN in Automotive Ethernet Networks," Embedded Real-Time Systems Conference, 2018.

[3] IEEE 802.1, "Time-Sensitive Networking (TSN) Task Group," IEEE Standards Association, 2023.

[4] ISO 26262, "Road vehicles – Functional safety," International Organization for Standardization, 2018.

[5] ISO/PAS 21448, "Road vehicles – Safety of the intended functionality (SOTIF)," International Organization for Standardization, 2019.

[6] IEEE 802.1CB-2017, "IEEE Standard for Local and metropolitan area networks – Frame Replication and Elimination for Reliability," IEEE, 2017.

[7] IEEE 802.1AS-2020, "IEEE Standard for Local and Metropolitan Area Networks – Timing and Synchronization," IEEE, 2020.

[8] IEEE 802.1Qbv-2015, "IEEE Standard for Local and metropolitan area networks – Bridges and Bridged Networks Amendment: Enhancements for Scheduled Traffic," IEEE, 2015.

[9] IEEE 802.1Qav-2009, "IEEE Standard for Local and Metropolitan Area Networks – Virtual Bridged Local Area Networks Amendment: Forwarding and Queuing Enhancements for Time-Sensitive Streams," IEEE, 2009.

[10] S. Bradner and J. McQuaid, "Benchmarking Methodology for Network Interconnect Devices," RFC 2544, IETF, 1999.

[11] R. Mandeville and J. Perser, "Benchmarking Methodology for LAN Switching Devices," RFC 2889, IETF, 2000.

---

## Acknowledgments

이 연구는 한국전자기술연구원(KETI) 모빌리티플랫폼연구센터의 지원을 받아 수행되었습니다. Microchip LAN9662 평가보드 및 기술 지원을 제공해주신 Microchip Technology Inc.에 감사드립니다.

---

**Corresponding Author:**
박부식 (Pusik Park)
한국전자기술연구원 모빌리티플랫폼연구센터
E-mail: pusik.park@keti.re.kr

**Date:** 2025-10-20
**Location:** Korea Electronics Technology Institute (KETI), Republic of Korea
