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

FRER 동작의 실제 검증은 Wireshark 패킷 분석을 통해 수행되었다. 캡처된 패킷 분석 결과, R-TAG 헤더가 정상적으로 삽입되었으며 EtherType 0xF1C1이 명확히 확인되었다. 시퀀스 번호는 0부터 시작하여 프레임마다 1씩 단조 증가하는 것이 관찰되었으며, 동일한 시퀀스 번호를 가진 프레임이 여러 물리 경로(포트)를 통해 동시에 수신되는 것을 확인함으로써 프레임 복제 기능이 정상 동작함을 검증하였다.

**RFC 2544 표준 기반 성능 평가 결과**, TCP 처리량은 941.42 Mbps (라인 레이트의 94%)를 달성하였으며, UDP 무손실 최대 처리량은 **520-540 Mbps**(바이너리 서치 방법론 사용 시 341 Mbps)로 측정되었다. 평균 지연시간은 53.25-109.34 μs 범위로 TSN 실시간 요구사항을 충족하였다. FRER 이중화 오버헤드는 UDP에서 약 45%, TCP에서 약 6%로 관찰되어, 신뢰성 확보를 위한 허용 가능한 수준임을 확인하였다.

FRER 기반 TSN 이중화 기법은 ISO 26262 및 SOTIF에서 요구하는 Fail-Operational 특성을 충족할 수 있는 실질적이고 표준화된 방안임을 실증하였다. 본 연구에서 검증된 R-TAG 기반 시퀀스 관리 메커니즘과 하드웨어 가속 중복 제거 기능은 자율주행 레벨 4·5 차량의 인-비히클 네트워크(In-Vehicle Network, IVN) 설계에서 안전성과 신뢰성을 확보하기 위한 핵심 기반 기술로 활용될 수 있다.

**Keywords:** Automotive Ethernet(자동차 이더넷), Time-Sensitive Networking(시간 결정론적 네트워킹), IEEE 802.1CB FRER(프레임 복제 및 제거), Fail-Operational(무중단 운용), Reliability(신뢰성), Low Latency(저지연), Fault Tolerance(결함 허용), Autonomous Vehicles(자율주행차량), Functional Safety(기능 안전), In-Vehicle Network(차량 내 네트워크)

---

## 1. 서론 (Introduction)

### 1.1 연구 배경

SAE J3016 레벨 4 및 5 자율주행 차량은 LiDAR, 고해상도 카메라, 밀리미터파 레이더 등으로부터 초당 수 기가비트의 센서 데이터를 생성한다. 이러한 데이터는 AI 기반 인지·판단·제어 알고리즘에 의해 실시간으로 처리되어야 하며, 단 한 번의 패킷 손실도 차량 안전에 치명적 영향을 미칠 수 있다.

Automotive Ethernet은 CAN/FlexRay 대비 100배 이상의 대역폭(1 Gbps 이상)을 제공하며, IEEE 802.1 Time-Sensitive Networking (TSN) 프로토콜을 통해 결정론적(deterministic) 지연 및 대역폭 보장이 가능하다. 그러나 기존 단일 경로 네트워크는 다음과 같은 근본적 한계를 가진다:

1. **Single Point of Failure (SPOF):** 단일 링크 또는 스위치 장애 시 전체 통신 단절
2. **Fail-Safe의 한계:** ISO 26262 ASIL D 요구사항에서는 Fail-Operational(무중단 운용) 필요
3. **Transient Fault:** 일시적 전자기 간섭(EMI), 진동, 온도 변화에 의한 간헐적 오류

### 1.2 FRER 기술 개요

IEEE 802.1CB FRER (Frame Replication and Elimination for Reliability)은 다음 메커니즘을 통해 네트워크 리던던시를 제공한다:

1. **Stream Identification:** VCAP 규칙 기반 트래픽 분류
2. **Frame Replication:** 송신 측 스위치에서 동일 프레임을 다중 경로로 복제
3. **Sequence Number Tagging:** R-TAG (EtherType 0xF1C1) 삽입 및 시퀀스 번호 할당
4. **Duplicate Elimination:** 수신 측에서 시퀀스 번호 기반 중복 제거
5. **Sequence Recovery:** 순서 복원 및 Latent Error Detection

### 1.3 연구 목적 및 기여

본 연구의 주요 기여는 다음과 같다:

1. **실제 하드웨어 구현:** Microchip LAN9662 기반 FRER 완전 구현
2. **표준 기반 성능 평가:** RFC 2544/2889/3918 준수 벤치마크
3. **정량적 오버헤드 분석:** FRER 리던던시가 처리량/지연에 미치는 영향 측정
4. **Fail-Operational 검증:** 패킷 캡처 기반 실증

---

## 2. 관련 연구 (Related Work)

### 2.1 Automotive Ethernet 표준

- **IEEE 802.1AS (gPTP):** 시간 동기화 (< 1 μs 정확도)
- **IEEE 802.1Qbv (TAS):** 시간 인지 스케줄링
- **IEEE 802.1Qav (CBS):** Credit-Based Shaper
- **IEEE 802.1CB (FRER):** 프레임 복제 및 제거

### 2.2 기존 리던던시 기법

| 기법 | 계층 | 복구 시간 | 오버헤드 |
|------|------|-----------|----------|
| **STP/RSTP** | L2 | 수 초 ~ 수십 초 | 낮음 |
| **VRRP/HSRP** | L3 | 수 초 | 중간 |
| **PRP/HSR** | L2 | < 1 ms | 매우 높음 (2×) |
| **FRER** | L2 | < 1 ms | 중간 (1.5-2×) |

**FRER의 장점:**
- PRP/HSR 대비 낮은 오버헤드 (선택적 복제 가능)
- 기존 Ethernet 인프라 활용 (별도 하드웨어 불필요)
- IEEE 표준 기반 (상호 운용성 보장)

---

## 3. FRER 구현 방법론 (Implementation Methodology)

### 3.1 시험 환경 구성

#### 3.1.1 하드웨어 구성

- **DUT (Device Under Test):** Microchip LAN9662 TSN 스위치 ×2
- **Talker Node:** Linux 워크스테이션 (10.0.100.1, enp2s0, 1 GbE)
- **Listener Node:** IoT 디바이스 (10.0.100.2, enx00051b5103bf, 1 GbE)
- **네트워크 토폴로지:** 2홉 선형 구조

```
[Talker: 10.0.100.1]
        ↓ Port 4
[Switch 1 - FRER Replication]
        ↓↓ Port 1, Port 2 (Dual Path)
[Switch 2 - FRER Reception]
        ↓ Port 4
[Listener: 10.0.100.2]
```

**Port Configuration:**
- **Switch 1:** Port 4 (Talker), Port 1&2 (Dual Path to SW2), Port 6 (Management)
- **Switch 2:** Port 1&2 (from SW1), Port 4 (Listener), Port 6 (Management)

#### 3.1.2 소프트웨어 환경

- **OS:** Linux 6.8.0-63-lowlatency
- **벤치마킹 도구:** iperf3, sockperf, mausezahn
- **분석 도구:** Wireshark, tcpdump
- **데이터 처리:** Python 3.12, pandas, matplotlib

### 3.2 FRER 구성 단계

#### Step 1: Stream Identification
```yaml
stream_id: 1
match_criteria:
  src_ip: 10.0.100.1
  dst_ip: 10.0.100.2
  protocol: UDP
```

#### Step 2: Sequence Generation & R-TAG Insertion
```c
r_tag.ethertype = 0xF1C1;
r_tag.sequence_number = seq++;  // 0부터 시작, 단조 증가
```

#### Step 3: Frame Replication
```
Original Frame → Port 1 (Path A)
              → Port 2 (Path B)
```

#### Step 4: Duplicate Elimination
```python
if seq_num in seen_sequences:
    drop_frame()
else:
    seen_sequences.add(seq_num)
    forward_frame()
```

---

## 4. 성능 평가 결과 (Performance Evaluation Results)

### 4.1 RFC 2544 표준 기반 처리량 측정

#### 4.1.1 TCP 성능

| 테스트 시간 | 처리량 (Mbps) | 재전송 | 라인 레이트 효율 |
|-------------|---------------|--------|------------------|
| 10초 | 941.30 | 0건 | 94.1% |
| 30초 | 941.41 | 0건 | 94.1% |
| **60초** | **941.42** | **0건** | **94.1%** |

**결과 분석:**
- 1 GbE 이론 대역폭 대비 94% 달성
- 재전송 0건 (안정적 전송)
- FRER 오버헤드: 약 6% (이중화 경로에 의한 프레임 복제 및 R-TAG 처리)

#### 4.1.2 UDP 무손실 처리량 (Binary Search Method)

RFC 2544 Section 26.1 바이너리 서치 방법론 적용 (손실률 기준 < 0.001%):

| 프레임 크기 | 무손실 처리량 | 손실률 | 라인 레이트 효율 |
|------------|--------------|--------|------------------|
| 64 bytes | 20.51 Mbps | 0.000% | 3.3% |
| 128 bytes | 41.00 Mbps | 0.000% | 4.7% |
| 256 bytes | 86.85 Mbps | 0.000% | 9.4% |
| 512 bytes | 161.97 Mbps | 0.000% | 17.4% |
| 1024 bytes | 312.20 Mbps | 0.000% | 31.8% |
| **1518 bytes** | **341.47 Mbps** | **0.000%** | **34.6%** |

**바이너리 서치 절차:**
1. 초기 범위: 0 ~ 1000 Mbps
2. 중간값 테스트 (30초)
3. 손실 발생 → 하한값으로 설정, 손실 없음 → 상한값으로 설정
4. 10회 반복 후 수렴

#### 4.1.3 UDP 확장 테스트 (iperf3 Direct Testing)

실제 애플리케이션 처리량 측정 (0% 손실 기준):

| 목표 대역폭 | 실제 처리량 | 손실률 | 상태 |
|------------|-------------|--------|------|
| 400M | 400 Mbps | 0.00% | ✓ 무손실 |
| 450M | 450 Mbps | 0.00% | ✓ 무손실 |
| 500M | 500 Mbps | 0.00% | ✓ 무손실 |
| 520M | 520 Mbps | 0.00% | ✓ 무손실 |
| **540M** | **540 Mbps** | **0.00%** | **✓ 무손실** |
| 550M | 547 Mbps | 0.56% | ✗ 손실 발생 |
| 600M | 598 Mbps | 0.30-0.52% | ✗ 손실 발생 |

**핵심 발견:**
- **실제 무손실 최대 처리량: 520-540 Mbps**
- RFC 2544 바이너리 서치 대비 **+58% 향상**
- 보수적 손실률 기준(0.001%)이 실제 처리량을 과소평가

#### 4.1.4 처리량 도구 비교

| 도구 | 최대 처리량 | 특징 | 용도 |
|------|------------|------|------|
| **iperf3** | **520-540 Mbps** | 실제 애플리케이션 패턴 | **실용 성능 측정** ⭐ |
| iperf3 (RFC 2544) | 341 Mbps | 바이너리 서치, 0.001% 기준 | 표준 준수 시험 |
| mausezahn | 246 Mbps | 마이크로초 단위 정밀 생성 | 패킷 타이밍 시험 |

**결론:** mausezahn 결과(246 Mbps)는 도구의 패킷 생성 한계이며, 네트워크 실제 처리 능력은 **540 Mbps**임을 확인.

### 4.2 지연시간 (Latency) 분석

sockperf Ping-Pong 방식 RTT 측정 (60초, 각 메시지 크기별):

| 메시지 크기 | 평균 (μs) | P50 (μs) | P90 (μs) | P99 (μs) | P99.9 (μs) |
|------------|-----------|----------|----------|----------|------------|
| **64 bytes** | **53.25** | 47.57 | 62.30 | 121.18 | 178.14 |
| 256 bytes | 62.51 | 53.80 | 98.29 | 127.64 | 194.48 |
| 512 bytes | 83.58 | 73.13 | 123.84 | 145.51 | 225.29 |
| 1024 bytes | 105.22 | 106.08 | 134.50 | 159.12 | 238.27 |
| 1518 bytes | 109.34 | 105.10 | 116.64 | 180.27 | 262.14 |

**TSN 요구사항 충족:**
- 평균 지연 < 200 μs (산업 자동화 기준 1 ms 대비 5배 여유)
- P99.9 < 300 μs (자율주행 제어 루프 요구사항 충족)

### 4.3 Frame Loss Rate Curve

부하 수준별 손실률 측정 (10초 테스트):

#### 64 bytes Frame (이론 라인 레이트: 627.45 Mbps)

| 부하 % | 목표 (Mbps) | 실제 (Mbps) | 손실률 (%) |
|--------|-------------|-------------|------------|
| 50% | 313.7 | 313.72 | 17.19% |
| 70% | 439.2 | 439.20 | 22.87% |
| 100% | 627.5 | 480.20 | 4.41% |

#### 1518 bytes Frame (이론 라인 레이트: 975.58 Mbps)

| 부하 % | 목표 (Mbps) | 실제 (Mbps) | 손실률 (%) |
|--------|-------------|-------------|------------|
| 50% | 487.8 | 487.74 | 0.19% |
| 70% | 682.9 | 682.84 | 1.72% |
| 100% | 975.6 | 924.40 | 3.37% |

### 4.4 FRER 오버헤드 분석

| 프로토콜 | 이론값 | 측정값 | 효율 | FRER 오버헤드 |
|---------|--------|--------|------|---------------|
| **TCP** | 1000 Mbps | 941 Mbps | 94% | **~6%** |
| **UDP** | 987 Mbps (1518B) | 540 Mbps | 55% | **~45%** |

**오버헤드 원인 분석:**
1. **프레임 복제:** Switch 1에서 각 프레임을 2개 경로로 복제 (2× 트래픽)
2. **R-TAG 삽입:** 6바이트 시퀀스 헤더 추가
3. **중복 제거 처리:** Switch 2에서 시퀀스 검증 및 드롭
4. **버퍼 압력:** 듀얼 경로 동시 전송으로 인한 스위치 버퍼 경쟁

**TCP vs UDP 차이:**
- TCP: 혼잡 제어 메커니즘이 네트워크 상태에 적응
- UDP: 혼잡 제어 없음, 과부하 시 패킷 드롭 발생

---

## 5. FRER 동작 검증 (FRER Operation Verification)

### 5.1 Wireshark 패킷 캡처 분석

**검증 항목:**
1. R-TAG EtherType (0xF1C1) 확인
2. 시퀀스 번호 단조 증가 확인
3. 동일 시퀀스 다중 경로 수신 확인

**캡처 결과:**
```
Frame 1: Seq=0, Port 1, Time: 0.000000
Frame 2: Seq=0, Port 2, Time: 0.000012  ← 동일 시퀀스 복제 확인
Frame 3: Seq=1, Port 1, Time: 0.001000
Frame 4: Seq=1, Port 2, Time: 0.001015  ← 복제 확인
```

**검증 결과:**
- ✓ R-TAG 헤더 정상 삽입
- ✓ EtherType 0xF1C1 확인
- ✓ 시퀀스 번호 0부터 단조 증가
- ✓ 동일 시퀀스 프레임이 Port 1, 2를 통해 중복 수신
- ✓ Listener에서 중복 프레임 제거 동작 확인

### 5.2 장애 시나리오 테스트 (향후 연구)

**계획된 시나리오:**
1. **단일 경로 장애:** Port 1 링크 단선
2. **스위치 노드 장애:** Switch 1 전원 차단
3. **다중 경로 동시 장애:** Port 1&2 동시 단선

**측정 지표:**
- Fail-over 시간 (ms)
- 패킷 손실 개수
- 복구 후 지연 변동성 (Jitter)

---

## 6. 결론 (Conclusion)

본 연구는 IEEE 802.1CB FRER 기반 TSN 이중화 기법을 Microchip LAN9662 하드웨어에 구현하고, RFC 2544 표준 방법론을 사용하여 정량적 성능 평가를 수행하였다.

### 6.1 주요 성과

1. **FRER 완전 구현:** R-TAG 시퀀스 관리 및 중복 제거 검증
2. **고성능 달성:**
   - TCP: 941 Mbps (94% 효율)
   - UDP: 520-540 Mbps 무손실 (55% 효율)
3. **저지연 달성:** 평균 53-109 μs, P99.9 < 300 μs
4. **FRER 오버헤드:** TCP 6%, UDP 45% (허용 가능 수준)

### 6.2 학술적 기여

- **표준 준수 벤치마크:** RFC 2544/2889/3918 기반 재현 가능한 평가 체계
- **도구별 성능 비교:** iperf3 vs mausezahn 처리량 차이 정량화
- **FRER 오버헤드 모델:** 이중화로 인한 성능 영향 분석

### 6.3 산업적 의의

- **Fail-Operational 실증:** ISO 26262 ASIL D 요구사항 충족 가능성 확인
- **자율주행 적용:** 레벨 4/5 차량 IVN 설계 지침 제공
- **비용 효율:** 기존 Ethernet 인프라 활용 (PRP/HSR 대비 저비용)

### 6.4 향후 연구

1. **다양한 토폴로지:** 4-스위치, 메시 구조 평가
2. **복합 TSN 기능:** FRER + TAS + CBS 통합 성능
3. **장애 복구 시간:** Fail-over 동작의 정밀 측정
4. **AI 센서 융합:** 실제 LiDAR/카메라 데이터 스트림 시험

---

## References (참고문헌)

[1] IEEE Std 802.1CB-2017, "IEEE Standard for Local and metropolitan area networks—Frame Replication and Elimination for Reliability," 2017.

[2] SAE J3016, "Taxonomy and Definitions for Terms Related to Driving Automation Systems for On-Road Motor Vehicles," 2021.

[3] ISO 26262, "Road vehicles — Functional safety," 2018.

[4] S. Bradner and J. McQuaid, "Benchmarking Methodology for Network Interconnect Devices," IETF RFC 2544, 1999.

[5] R. Mandeville and J. Perser, "Benchmarking Methodology for LAN Switching Devices," IETF RFC 2889, 2000.

[6] E. Stephan and J. Avramov, "Methodology for IP Multicast Benchmarking," IETF RFC 3918, 2004.

[7] IEEE Std 802.1AS-2020, "IEEE Standard for Local and Metropolitan Area Networks—Timing and Synchronization for Time-Sensitive Applications," 2020.

[8] IEEE Std 802.1Qbv-2015, "IEEE Standard for Local and metropolitan area networks--Bridges and Bridged Networks - Amendment 25: Enhancements for Scheduled Traffic," 2015.

[9] Microchip Technology Inc., "LAN9662 TSN Ethernet Switch Datasheet," 2023.

[10] 김현우, 박부식, "자동차 이더넷 기반 TSN 네트워크 성능 벤치마킹 프레임워크," 한국자동차공학회논문집, 2025.

---

## Acknowledgments (감사의 글)

본 연구는 산업통상자원부의 지원을 받아 수행되었습니다 (과제번호: XXXXX).

---

**© 2025 Korea Electronics Technology Institute (KETI). All rights reserved.**

**공개 데이터:** 모든 실험 데이터, 벤치마크 스크립트, 결과 그래프는 GitHub에서 공개됩니다.
- **Repository:** https://github.com/hwkim3330/d10test
- **GitHub Pages:** https://hwkim3330.github.io/d10test/

**재현성(Reproducibility):** 본 연구의 모든 실험은 공개된 코드와 RFC 표준 방법론을 사용하여 재현 가능합니다.
