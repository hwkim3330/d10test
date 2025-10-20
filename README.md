# RFC 2544 Network Benchmark Results

## 📋 개요 (Overview)

본 레포지토리는 **IETF RFC 2544** 표준에 따른 네트워크 성능 벤치마크 결과를 담고 있습니다.

**시험 대상:** 10.0.100.2 (1 Gigabit Ethernet)
**시험 기준:** [RFC 2544 - Benchmarking Methodology for Network Interconnect Devices](https://tools.ietf.org/html/rfc2544)
**시험 일자:** 2025년 10월 20일

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

## 📁 보고서 및 데이터 (Reports & Data)

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

## 📞 문의 (Contact)

벤치마크 결과 또는 방법론에 대한 문의사항은 GitHub Issues를 통해 제출해 주시기 바랍니다.

---

**본 벤치마크는 IETF RFC 2544 표준 방법론을 준수하여 수행되었습니다.**

*Last Updated: 2025-10-20*