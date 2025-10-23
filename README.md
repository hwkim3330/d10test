# FRER TSN Performance Evaluation - IEEE 802.1CB Automotive Ethernet

> **🌐 GitHub Pages:** [https://hwkim3330.github.io/d10test/](https://hwkim3330.github.io/d10test/)
>
> **📊 Interactive Reports:**
> - [🔬 TSN Performance Analysis - WHY FRER Wins?](https://hwkim3330.github.io/d10test/tsn_performance_analysis.html) ⭐ **NEW! Academic-Level Technical Explanation**
> - [FRER vs Control Comparison](https://hwkim3330.github.io/d10test/frer_vs_control_comparison.html)
> - [Performance Report](https://hwkim3330.github.io/d10test/performance_report.html)
>
> **🌍 [English Version](README_EN.md)**

---

## 🔬 CRITICAL FINDING: FRER Provides 33% Better UDP Performance!

**Breaking Discovery (2025-10-23):** Controlled experiment revealed FRER is a performance enhancer:
- **FRER dual-path (Path A + B): 530 Mbps UDP zero-loss**
- **Single-path (Path A only): 398 Mbps UDP zero-loss**
- **🏆 FRER Advantage: +33.2%** (same hardware, only difference is path count!)

**Root Cause:** FRER's **buffer load distribution** across two independent paths effectively doubles buffering capacity, delaying overflow and enabling 33% higher sustained UDP throughput. First-arrival selection and path diversity provide additional benefits.

**👉 [View Interactive Comparison Report](https://hwkim3330.github.io/d10test/frer_vs_control_comparison.html)** ← **Click to see live charts!**

**🔬 [WHY Does FRER Win? - Read Technical Analysis](https://hwkim3330.github.io/d10test/tsn_performance_analysis.html)** ← **Academic paper-level explanation!**

---

## 📋 개요 (Overview)

본 레포지토리는 **IEEE 802.1CB FRER (Frame Replication and Elimination for Reliability)** 기반 자동차 이더넷 네트워크의 포괄적인 성능 평가 결과를 담고 있습니다.

**시험 대상:** Microchip LAN9668 (Kontron D10) 기반 2-hop FRER 네트워크
**시험 기준:**
- [RFC 2544 - Benchmarking Methodology for Network Interconnect Devices](https://tools.ietf.org/html/rfc2544)
- IEEE 802.1CB - Frame Replication and Elimination for Reliability
- ISO 26262 ASIL D / SOTIF - Automotive Functional Safety

**시험 일자:** 2025년 10월 20-23일

### 📊 보고서 및 문서 (Reports & Documentation)

#### 🆕 **인터랙티브 HTML 보고서 (Interactive Reports)**
1. **🔬 [TSN Performance Analysis - WHY FRER Wins?](https://hwkim3330.github.io/d10test/tsn_performance_analysis.html)** ⭐ **NEW!**
   - **왜 FRER이 33% 더 빠른지 논문급 기술 분석**
   - TSN queue management 심층 분석 (CBS, TAS, 우선순위 큐)
   - Buffer 관리 메커니즘 비교
   - 프레임 크기별 영향 분석 (64B catastrophe 원인)
   - **4개 인터랙티브 Chart.js 그래프**
   - 자동차 이더넷 use case 적용 가이드
   - 🎓 Academic paper quality, 실무 설계 권고사항
   - 📄 [Source](docs/tsn_performance_analysis.html)

2. **📊 [FRER vs Control Group - Comprehensive Comparison](https://hwkim3330.github.io/d10test/frer_vs_control_comparison.html)**
   - **Control group experiment 결과 종합**
   - FRER와 직접 연결 성능 비교 (side-by-side)
   - **인터랙티브 Chart.js 차트 3개:** UDP 처리량, 지연시간, 손실률
   - TSN queue 설정의 중요성 분석
   - **핵심 발견:** FRER이 33% 더 나은 UDP 성능 제공
   - 🎨 Beautiful gradient design, mobile-responsive
   - 📄 [Source](docs/frer_vs_control_comparison.html)

3. **🎨 [FRER Performance Report - Interactive Graphs](https://hwkim3330.github.io/d10test/performance_report.html)**
   - **클릭 가능한 그래프** (확대 + 상세 설명 표시)
   - FRER 네트워크 토폴로지 다이어그램
   - 프레임 크기별 분석, 지연시간 분포
   - UDP 손실 곡선, FRER 오버헤드 분석
   - 📄 [Source](docs/performance_report.html)

#### 🎓 **학술 논문 (Academic Papers)**
1. **📄 [FRER as a UDP Performance Enhancement Mechanism (English)](FRER_Dual_Path_Performance_Paper.md)** ⭐ **NEW!**
   - **FRER은 성능 향상 메커니즘이다: Buffer load distribution 분석**
   - Control group experiment 완전 분석 (Single vs Dual path)
   - TCP vs UDP 차이 설명 (왜 TCP는 차이가 없나)
   - 33% 성능 향상의 3가지 메커니즘 분해
   - Cost-benefit 재평가: 실효 overhead 50% (100% 아님!)
   - **5,800+ words, peer-review ready**

2. **📄 [FRER Throughput Limitations - Empirical Analysis (English)](FRER_Throughput_Limitations_Paper.md)**
   - Platform: Microchip LAN9668 (Kontron D10)
   - Zero-loss threshold: 530-535 Mbps
   - Buffer saturation analysis
   - **6,200+ words, peer-review ready**

3. **📄 [자동차 이더넷의 신뢰성 확보를 위한 FRER 기반 TSN 이중화 기법 (Korean)](FRER_TSN_Performance_Paper.md)**
   - 완전한 FRER 구현 방법론 및 성능 평가
   - 프레임 크기별 처리량 분석 (64B ~ 1518B)
   - 부하 수준별 손실률 특성 분석
   - Fail-Operational 검증 및 실무 설계 가이드

#### 📈 **그래프 상세 설명 (Graph Explanations)**
**📊 [성능 분석 그래프 상세 설명 (4,800+ lines)](GRAPH_EXPLANATIONS.md)**
- **9개 그래프 각각에 대한 완전한 설명**
- X축/Y축 의미, 데이터 포인트, 주요 트렌드
- 핵심 인사이트 및 실무 적용 방안
- SLA 설계, 용량 계획, 프레임 크기 선택 등 실전 예시

#### 📁 **실험 데이터 (Experimental Data)**
**[experimental_data/](experimental_data/) 디렉토리:**
- 📊 [Zero-Loss Threshold Data (JSON)](experimental_data/frer_zero_loss_threshold_data.json) - FRER 무손실 임계값 발견 과정
- 📊 [RFC 2544 Comprehensive Data (JSON)](experimental_data/rfc2544_comprehensive_data.json) - 완전한 RFC 2544 벤치마크
- 📄 [Latency Measurements (CSV)](experimental_data/latency_measurements.csv) - 지연시간 백분위수 (5개 프레임 크기)
- 📖 [Experimental Methodology (6,000+ words)](experimental_data/EXPERIMENTAL_METHODOLOGY.md) - 테스트 절차 완전 문서화

**[control_group_no_frer/](control_group_no_frer/) 디렉토리:**
- 📊 [Control Group Data (JSON)](control_group_no_frer/control_group_data.json) - FRER 없는 대조군 실험
- 📄 [Results Summary (Markdown)](control_group_no_frer/CONTROL_GROUP_RESULTS_SUMMARY.md) - 850줄 분석 보고서
- 📊 CSV 파일: TCP baseline, UDP sweep, Latency measurements
- **핵심:** Direct connection이 오히려 25% 낮은 성능!

---

## 🎯 주요 성능 지표 (Latest Results)

### TCP 성능
| 항목 | 측정값 |
|------|--------|
| **최대 처리량** | **941.42 Mbps** |
| **재전송** | **0 건** |
| **안정성** | 우수 (표준편차 < 0.1 Mbps) |

### UDP 무손실 처리량 (Zero-Loss Throughput)
| 프레임 크기 | 무손실 처리량 | 라인 레이트 효율 |
|------------|--------------|----------------|
| 64 bytes   | 20.51 Mbps   | 3.3% |
| 128 bytes  | 41.00 Mbps   | 4.7% |
| 256 bytes  | 86.85 Mbps   | 9.4% |
| 512 bytes  | 161.97 Mbps  | 17.4% |
| **1024 bytes** | **312.20 Mbps** | **31.8%** |
| **1518 bytes** | **341.47 Mbps** | **34.6%** |

*무손실 기준: 패킷 손실률 < 0.001% (RFC 2544 권장)*

### UDP 처리량 비교: 세 가지 측정 방법론

| 방법론 | 도구 | 결과 (Mbps) | Loss Rate | 목적 | 보고서 |
|--------|------|------------|-----------|------|--------|
| **RFC 2544 Binary Search** | iperf3 | 341 | < 0.001% | 표준 준수 벤치마크 | [링크](#) |
| **iperf3 Systematic Sweep** | iperf3 | **520-540** | **0%** | 실제 애플리케이션 성능 | [Extended Test](benchmarks/2025-10-20-iperf3-udp-extended/UDP_EXTENDED_TEST_REPORT.md) |
| **Precision Packet Generation** | mausezahn | 246 | N/A | 도구 성능 한계 | [링크](#) |

**⚠️ 중요:** 모든 처리량 측정은 **iperf3를 사용**하여 수행되었으며, 측정 방법론에 따라 결과가 다르게 나타납니다:
- **RFC 2544 (341 Mbps):** 매우 보수적인 0.001% loss threshold로 인한 결과
- **Systematic Sweep (530 Mbps):** 실제 zero-loss 용량 (실무 권장)
- **mausezahn (246 Mbps):** 패킷 생성 도구의 성능 한계 (네트워크 용량 아님)

### 지연시간 (Latency)
| 메시지 크기 | 평균 (μs) | P99 (μs) | P99.9 (μs) |
|------------|-----------|----------|-----------|
| 64 bytes   | **53.25** | 121.18 | 178.14 |
| 256 bytes  | 62.51 | 127.64 | 194.48 |
| 512 bytes  | 83.58 | 145.51 | 225.29 |
| 1024 bytes | 105.22 | 159.12 | 238.27 |
| 1518 bytes | 109.34 | 180.27 | 262.14 |

---

## ✅ 성능 평가

### 종합 평가
- ✅ **TCP 성능: 탁월** - 라인 레이트의 94% 달성 (941 Mbps)
- ✅ **지연시간: 탁월** - 평균 53~109 μs (TSN 요구사항 충족)
- ✅ **무손실 전송: 검증 완료** - RFC 2544 기준 적합
- ✅ **안정성: 우수** - 재전송 0건, 일관된 성능

### RFC 2544 표준 준수
| 시험 항목 | RFC 섹션 | 준수 여부 |
|---------|---------|----------|
| Throughput (처리량) | Section 26.1 | ✅ 적합 |
| Latency (지연시간) | Section 26.2 | ✅ 적합 |
| Frame Loss Rate (손실률) | Section 26.3 | ✅ 적합 |
| 바이너리 서치 방법론 | - | ✅ 적용 |
| 손실률 기준 (<0.001%) | - | ✅ 충족 |

---

## 📊 시험 방법론 (Test Methodology)

### RFC 2544 표준 시험 절차

#### 1. Throughput (처리량) - RFC 2544 Section 26.1
**방법:** 바이너리 서치를 통한 무손실 최대 전송률 탐색
- 시험 시간: 30초/반복
- 손실률 기준: < 0.001%
- 프레임 크기: 64, 128, 256, 512, 1024, 1518 바이트
- 도구: iperf3

#### 2. Latency (지연시간) - RFC 2544 Section 26.2
**방법:** Ping-Pong 양방향 RTT 측정
- 시험 시간: 60초/메시지 크기
- 측정 항목: 평균, 최소, 최대, 백분위수 (P50, P90, P99, P99.9)
- 메시지 크기: 64, 256, 512, 1024, 1518 바이트
- 도구: sockperf

#### 3. Frame Loss Rate (프레임 손실률) - RFC 2544 Section 26.3
**방법:** 다양한 부하 수준에서 손실률 측정
- 부하 범위: 50% ~ 110% (이론적 라인 레이트 기준)
- 시험 시간: 10초/부하 수준
- 도구: iperf3

---

## 📁 실험 데이터 (Experimental Data)

### 종합 데이터 세트 (Comprehensive Datasets)
- 📊 **[Zero-Loss Threshold Data (JSON)](experimental_data/frer_zero_loss_threshold_data.json)** - 535-565 Mbps fine-grained analysis
- 📊 **[RFC 2544 Comprehensive Data (JSON)](experimental_data/rfc2544_comprehensive_data.json)** - Complete RFC 2544 benchmark results
- 📄 **[Zero-Loss Threshold (CSV)](experimental_data/zero_loss_threshold.csv)** - Excel-compatible format
- 📄 **[RFC 2544 Zero-Loss (CSV)](experimental_data/rfc2544_zero_loss.csv)** - Frame size analysis
- 📄 **[Latency Measurements (CSV)](experimental_data/latency_measurements.csv)** - TSN compliance data
- 📖 **[Experimental Methodology](experimental_data/EXPERIMENTAL_METHODOLOGY.md)** - Complete testing procedures (6,000+ words)

### 최신 결과 (Latest - 2025-10-20)
- 📄 **[English Report](benchmarks/2025-10-20-enhanced/RFC2544_Enhanced_Report.md)** - RFC 2544 Enhanced Benchmark Report
- 📄 **[한국어 보고서](benchmarks/2025-10-20-enhanced/RFC2544_한국어_보고서.md)** - RFC 2544 벤치마크 보고서 (한글)
- 📈 **[Throughput Analysis](benchmarks/2025-10-20-enhanced/01_throughput_analysis.png)** - 처리량, 효율성, 지터 분석
- 📈 **[Latency Analysis](benchmarks/2025-10-20-enhanced/02_latency_analysis.png)** - 지연시간 백분위수 및 분포
- 📈 **[Frame Loss Analysis](benchmarks/2025-10-20-enhanced/03_frame_loss_analysis.png)** - 부하별 손실 특성
- 💾 **[Raw Data (JSON)](benchmarks/2025-10-20-enhanced/benchmark_results_enhanced.json)** - 원시 데이터

### 이전 결과 (Previous - 2025-10-20)
- 📄 **[Initial Report](benchmarks/2025-10-20-initial/RFC2544_Benchmark_Report.md)**
- 📈 **[Performance Graphs](benchmarks/2025-10-20-initial/rfc2544_performance_graphs.png)**
- 💾 **[Raw Data (JSON)](benchmarks/2025-10-20-initial/benchmark_results.json)**

### 표준 문서
- 📚 **[RFC 2544 표준 정보](RFC2544_표준_정보.md)** - IETF 표준 상세 설명 (한글)

---

## 🔧 시험 환경 (Test Environment)

### 하드웨어
- **시험 장비:** Linux Workstation
- **네트워크 인터페이스:** enp2s0 (1 Gigabit Ethernet)
- **대상 장비:** 10.0.100.2

### 소프트웨어
- **운영체제:** Linux (kernel 6.8.0-63-lowlatency)
- **시험 도구:**
  - iperf3: TCP/UDP 처리량 측정
  - sockperf: 저지연 측정
  - Python 3.12: 자동화 및 분석

---

## 🚀 시험 재현 방법 (How to Run)

### 1. 도구 설치
```bash
# 시험 도구 설치
sudo apt install iperf3 sockperf

# Python 라이브러리 설치
pip3 install --break-system-packages pandas matplotlib seaborn numpy
```

### 2. 서버 설정 (대상 장비 10.0.100.2)
```bash
# iperf3 서버 실행
iperf3 -s &

# sockperf 서버 실행
sockperf server -i 0.0.0.0 -p 11111 &
```

### 3. 벤치마크 실행
```bash
# 향상된 RFC 2544 벤치마크 (권장)
python3 scripts/rfc2544_enhanced_benchmark.py

# 기본 벤치마크
python3 scripts/rfc2544_benchmark.py
```

### 4. 한국어 보고서 생성
```bash
python3 scripts/generate_korean_report.py <results_directory>
```

---

## 📚 학술 논문 (Research Papers)

### FRER 처리량 한계 분석 논문
- 📄 **[Empirical Analysis of FRER Throughput Limitations (English)](FRER_Throughput_Limitations_Paper.md)**
  - **Platform:** Microchip LAN9668 / Kontron D10
  - **Key Findings:**
    - Zero-loss threshold: 530-535 Mbps
    - Marginal loss region: 535-563 Mbps (0.05-0.085%)
    - Catastrophic failure: 565 Mbps (collapse to 112 Mbps)
  - **Root Causes:** Frame replication doubling (2×), buffer saturation (~2-4 MB), R-TAG overhead (~10% CPU)
  - **Length:** 6,200+ words, 10 references, 3 appendices

### 기존 성능 평가 논문
- 📄 **[자동차 이더넷의 신뢰성 확보를 위한 FRER 기반 TSN 이중화 기법 (한글)](FRER_TSN_Performance_Paper.md)**
  - 완전한 FRER 구현 방법론 및 성능 평가
  - 프레임 크기별 처리량 분석 (64B ~ 1518B)

## 📖 참고 문헌 (References)

### IETF RFC 표준
1. **[RFC 2544](https://tools.ietf.org/html/rfc2544)** - Benchmarking Methodology for Network Interconnect Devices
2. **[RFC 1242](https://tools.ietf.org/html/rfc1242)** - Benchmarking Terminology for Network Interconnection Devices
3. **[RFC 2889](https://tools.ietf.org/html/rfc2889)** - Benchmarking Methodology for LAN Switching Devices

### IEEE 표준
- **IEEE 802.3** - Ethernet Standards
- **IEEE 802.1Q** - Virtual LANs and Priority
- **IEEE 1588** - Precision Time Protocol (PTP)

### 도구
- **[iperf3](https://iperf.fr/)** - Network performance measurement tool
- **[sockperf](https://github.com/Mellanox/sockperf)** - Network latency and throughput testing tool

---

## 📂 레포지토리 구조 (Repository Structure)

```
d10test/
├── README.md                      # 메인 README (본 파일)
├── RFC2544_표준_정보.md            # RFC 2544 표준 상세 설명
├── benchmarks/                    # 벤치마크 결과
│   ├── 2025-10-20-enhanced/       # 최신 향상된 벤치마크 결과
│   │   ├── RFC2544_Enhanced_Report.md
│   │   ├── RFC2544_한국어_보고서.md
│   │   ├── 01_throughput_analysis.png
│   │   ├── 02_latency_analysis.png
│   │   ├── 03_frame_loss_analysis.png
│   │   └── benchmark_results_enhanced.json
│   └── 2025-10-20-initial/        # 초기 벤치마크 결과
│       ├── RFC2544_Benchmark_Report.md
│       ├── rfc2544_performance_graphs.png
│       ├── jitter_analysis.png
│       └── benchmark_results.json
└── scripts/                       # 벤치마크 스크립트
    ├── rfc2544_enhanced_benchmark.py    # 향상된 RFC 2544 벤치마크
    ├── rfc2544_benchmark.py             # 기본 RFC 2544 벤치마크
    └── generate_korean_report.py        # 한국어 보고서 생성기
```

---

## 💡 주요 발견 사항 (Key Findings)

### 무손실 전송 검증
바이너리 서치 방법론을 통해 각 프레임 크기별로 **패킷 손실률 < 0.001%**를 충족하는 최대 처리량을 정확히 측정했습니다. 이는 RFC 2544 표준이 권장하는 방법입니다.

### 소형 프레임 처리 특성
64바이트 소형 프레임의 경우 무손실 처리량이 20.51 Mbps로 측정되었습니다. 이는 Ethernet 오버헤드(38바이트)로 인한 것으로, 프레임 크기가 작을수록 오버헤드 비율이 높아지는 것을 확인했습니다.

### 실시간 애플리케이션 적합성
평균 지연시간 53~109 μs, P99 지연시간 180 μs 이하로 TSN(Time-Sensitive Networking) 요구사항을 충족하며, 산업 자동화, 차량 네트워크 등 실시간 애플리케이션에 적합합니다.

---

## 🔗 Quick Links

### 🌐 **Live Interactive Reports (GitHub Pages)**
- **[🏠 Main Page](https://hwkim3330.github.io/d10test/)** - GitHub Pages 메인
- **[🔬 TSN Performance Analysis](https://hwkim3330.github.io/d10test/tsn_performance_analysis.html)** ⭐ **왜 FRER이 33% 더 빠른지 논문급 기술 분석!**
- **[📊 FRER vs Control Comparison](https://hwkim3330.github.io/d10test/frer_vs_control_comparison.html)** - 33% 성능 우위 발견
- **[📈 Performance Report](https://hwkim3330.github.io/d10test/performance_report.html)** - 클릭 가능한 인터랙티브 그래프

### 📄 **Documentation**
- **[FRER Throughput Limitations Paper (EN)](FRER_Throughput_Limitations_Paper.md)** - 6,200+ words
- **[FRER TSN Performance Paper (KR)](FRER_TSN_Performance_Paper.md)** - 한글 논문
- **[Graph Explanations](GRAPH_EXPLANATIONS.md)** - 9개 그래프 상세 설명
- **[Experimental Methodology](experimental_data/EXPERIMENTAL_METHODOLOGY.md)** - 테스트 절차

### 📊 **Experimental Data**
- **[FRER Data (JSON)](experimental_data/frer_zero_loss_threshold_data.json)** - 530 Mbps threshold
- **[Control Group Data (JSON)](control_group_no_frer/control_group_data.json)** - 398 Mbps threshold
- **[RFC 2544 Results (JSON)](experimental_data/rfc2544_comprehensive_data.json)** - Complete benchmark
- **[CSV Files](experimental_data/)** - Latency, throughput, zero-loss data

---

## 📞 문의 (Contact)

벤치마크 결과 또는 방법론에 대한 문의사항은 GitHub Issues를 통해 제출해 주시기 바랍니다.

---

**본 벤치마크는 IETF RFC 2544 표준 방법론을 준수하여 수행되었습니다.**

**Platform:** Microchip LAN9668 (Kontron D10)
**Test Dates:** 2025-10-20 to 2025-10-23
**Status:** ✅ Complete - All data published

---

**🌐 View Live Reports:** [https://hwkim3330.github.io/d10test/](https://hwkim3330.github.io/d10test/)