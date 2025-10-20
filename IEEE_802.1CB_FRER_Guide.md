# IEEE 802.1CB FRER 표준 가이드

## 문서 정보

**표준 명칭:** IEEE Std 802.1CB-2017
**정식 제목:** Frame Replication and Elimination for Reliability
**발행일:** 2017년 10월
**분류:** IEEE 802.1 Time-Sensitive Networking (TSN) 표준군

---

## 개요

### FRER이란?

**FRER (Frame Replication and Elimination for Reliability)**는 이더넷 네트워크에서 프레임을 여러 경로로 복제하여 전송하고, 수신 측에서 중복을 제거함으로써 **무손실 전송과 고가용성**을 보장하는 IEEE 표준 기술입니다.

### 핵심 개념

```
┌──────────┐
│  Source  │ ──┐
└──────────┘   │
               ▼
          ┌─────────┐
          │ Replicate│  프레임 복제
          └─┬─────┬─┘
            │     │
       Path A   Path B  두 개 이상의 독립 경로
            │     │
          ┌─▼─────▼─┐
          │Eliminate│  중복 제거
          └─────────┘
               │
               ▼
          ┌──────────┐
          │Destination│
          └──────────┘
```

---

## 왜 FRER이 필요한가?

### 전통적인 이더넷의 한계

1. **단일 장애점 (Single Point of Failure)**
   - 스위치 또는 링크 하나가 고장나면 전체 통신 중단

2. **Spanning Tree Protocol (STP)의 문제**
   - 복구 시간이 수 초 소요 (30초 이상 가능)
   - 실시간 시스템에 부적합

3. **패킷 손실 불가 환경**
   - 산업 자동화
   - 차량 네트워크
   - 의료 기기
   → 단 하나의 패킷 손실도 치명적

### FRER의 해결책

✅ **무손실 전송**: 하나의 경로가 끊겨도 다른 경로로 전송
✅ **즉각적인 복구**: Failover 시간 **0ms** (미리 양쪽으로 전송)
✅ **투명한 운영**: 애플리케이션 레벨에서는 변경 불필요

---

## FRER 동작 원리

### 1. Stream Identification (스트림 식별)

특정 트래픽 흐름을 **Stream**으로 식별:
- MAC 주소
- VLAN ID
- IP 주소/포트 (옵션)

### 2. Sequence Encoding (시퀀스 번호 부여)

각 프레임에 **고유 시퀀스 번호** 부여:
```
Original Frame: [Header | Payload | FCS]
                      ↓
FRER Frame:     [Header | Seq# | Payload | FCS]
                        └─ 16-bit sequence number
```

### 3. Replication (프레임 복제)

**송신 측**에서 동일한 프레임을 여러 경로로 복제:
```
Frame #1234 ─┬→ Path A → Frame #1234
             └→ Path B → Frame #1234 (복사본)
```

### 4. Elimination (중복 제거)

**수신 측**에서 시퀀스 번호 기반으로 중복 제거:
```
Path A → Frame #1234 ┐
                      ├→ [Check Seq#] → Frame #1234 (한 번만 전달)
Path B → Frame #1234 ┘    └─ Duplicate discarded
```

### 5. Sequence Recovery (시퀀스 복구)

중간에 손실된 프레임 감지:
```
Received: #1231, #1232, #1234
Missing: #1233  ← 감지하고 기록
```

---

## FRER 네트워크 구성 요소

### Replication Function (복제 기능)

**위치:** Talker (송신 노드)의 출력
**역할:**
- 스트림 식별
- 시퀀스 번호 생성
- 프레임 복제
- 각 경로로 전송

**파라미터:**
- `frerSeqGenAlgorithm`: 시퀀스 번호 생성 알고리즘
- `frerSeqEncapType`: 캡슐화 타입 (R-TAG 등)

### Elimination Function (제거 기능)

**위치:** Listener (수신 노드)의 입력
**역할:**
- 시퀀스 번호 확인
- 중복 프레임 감지
- 중복 제거
- 단일 프레임만 전달

**파라미터:**
- `frerSeqRcvyHistoryLength`: 히스토리 길이 (이전 시퀀스 번호 저장)
- `frerSeqRcvyResetTimeout`: 리셋 타임아웃

---

## IEEE 802.1CB 프레임 포맷

### R-TAG (Redundancy TAG)

```
┌─────────────┬─────────────┬──────────┬─────────┬─────────┬─────┐
│ Destination │   Source    │  R-TAG   │EtherType│ Payload │ FCS │
│     MAC     │    MAC      │  (6B)    │         │         │     │
└─────────────┴─────────────┴──────────┴─────────┴─────────┴─────┘
                              ▲
                              │
                    ┌─────────┴────────┐
                    │ TPID = 0xF1C1    │ 2 bytes
                    │ Sequence Number  │ 2 bytes
                    │ Reserved/Control │ 2 bytes
                    └──────────────────┘
```

### HSR-TAG (High-availability Seamless Redundancy)

HSR과 호환 가능한 포맷:
```
┌──────────────────────────────────────┐
│ HSR-TAG (6 bytes)                    │
├──────────┬───────────┬───────────────┤
│ EtherType│  Path ID  │ Sequence Num  │
│  (2B)    │   (2B)    │     (2B)      │
└──────────┴───────────┴───────────────┘
```

---

## 토폴로지 유형

### 1. Dual Path Topology (이중 경로)

```
      Talker
        │
    ┌───┴───┐
    │       │
Switch A  Switch B
    │       │
    └───┬───┘
        │
     Listener
```

**특징:**
- 가장 간단한 구성
- 2개의 독립 경로
- 단일 장애 허용

### 2. Ring Topology (링 토폴로지)

```
    Switch A ─── Switch B
        │            │
        │            │
    Switch D ─── Switch C
```

**특징:**
- 여러 경로 가능
- HSR (High-availability Seamless Redundancy)과 결합
- 다중 장애 허용

### 3. Mesh Topology (메시 토폴로지)

```
    ┌───────┬───────┐
    │       │       │
Switch A─Switch B─Switch C
    │       │       │
    └───────┴───────┘
```

**특징:**
- 최대 가용성
- 복잡한 관리
- 대규모 네트워크

---

## FRER 성능 파라미터

### Latency (지연시간)

**FRER 오버헤드:**
- 복제: < 1 μs (하드웨어 기반)
- 제거: < 1 μs (시퀀스 번호 체크)
- **총 추가 지연: < 2 μs**

### Bandwidth (대역폭)

**오버헤드:**
- R-TAG: 6 바이트/프레임
- 프레임 복제로 인한 대역폭 2배 사용

**계산:**
```
원본 트래픽: 100 Mbps
복제 후: 200 Mbps (네트워크 전체)
수신 측: 100 Mbps (중복 제거 후)
```

### Recovery Time (복구 시간)

| 기술 | 복구 시간 |
|------|----------|
| STP (Spanning Tree) | 30초 ~ 수 분 |
| RSTP (Rapid STP) | 1~3초 |
| **FRER** | **0 ms** (사전 복제) |

---

## 실제 적용 사례

### 1. 산업 자동화 (Industrial Automation)

```
PLC ─┬─ Switch A ─┐
     │            ├─ 로봇 제어기
     └─ Switch B ─┘
```

**요구사항:**
- 제어 명령 손실 불가
- 지연시간 < 1 ms
- 가용성 99.999%

**FRER 적용:**
✅ 무손실 전송
✅ 즉각 복구
✅ 실시간 보장

### 2. 차량 네트워크 (Automotive Ethernet)

```
ECU A ─┬─ Switch 1 ─┐
       │            ├─ ECU B (브레이크)
       └─ Switch 2 ─┘
```

**요구사항:**
- 안전 관련 메시지 (ASIL-D)
- 지연시간 < 250 μs
- 패킷 손실 < 0.0001%

**FRER 적용:**
✅ Safety 요구사항 충족
✅ Fail-Operational

### 3. 전력 그리드 (Smart Grid)

```
Substation A ─┬─ Router A ─┐
              │            ├─ Control Center
              └─ Router B ─┘
```

**요구사항:**
- IEC 61850 (Substation Automation)
- 고가용성 (99.999%)
- 사이버 보안

**FRER 적용:**
✅ 통신 중단 방지
✅ 실시간 모니터링

---

## FRER vs 기존 기술 비교

### FRER vs STP/RSTP

| 특성 | STP/RSTP | FRER |
|------|---------|------|
| 복구 시간 | 초 단위 | 0 ms |
| 경로 활용 | 단일 경로 (백업은 대기) | 모든 경로 동시 사용 |
| 대역폭 효율 | 높음 | 낮음 (복제 오버헤드) |
| 적용 | 일반 네트워크 | 미션 크리티컬 |

### FRER vs HSR (High-availability Seamless Redundancy)

| 특성 | HSR | FRER |
|------|-----|------|
| 표준 | IEC 62439-3 | IEEE 802.1CB |
| 토폴로지 | 링 필수 | 임의 |
| 상호운용성 | HSR 전용 | 표준 Ethernet 호환 |
| 적용 분야 | 전력/산업 | 범용 TSN |

---

## TSN과의 관계

FRER은 **TSN (Time-Sensitive Networking)** 표준군의 핵심 구성 요소:

```
┌──────────────────────────────────────┐
│         TSN Standards                │
├──────────────────────────────────────┤
│ 802.1AS  │ Time Synchronization      │
│ 802.1Qbv │ Time-Aware Scheduling     │
│ 802.1Qav │ Credit-Based Shaping      │
│ 802.1CB  │ FRER (Reliability) ← 여기 │
│ 802.1Qci │ Per-Stream Filtering      │
│ 802.1Qcc │ Stream Reservation        │
└──────────────────────────────────────┘
```

**통합 시나리오:**
1. **802.1AS**: 네트워크 시간 동기화
2. **802.1Qbv**: 시간 기반 트래픽 스케줄링
3. **802.1CB (FRER)**: 중요 트래픽 복제/제거
4. **802.1Qav**: 대역폭 예약

→ **결과**: 결정적(Deterministic) + 고신뢰(Reliable) 네트워크

---

## FRER 구현 요구사항

### 하드웨어 요구사항

**스위치:**
- IEEE 802.1CB 지원 칩셋
- 하드웨어 기반 시퀀스 번호 처리
- 충분한 메모리 (히스토리 버퍼)

**엔드 노드:**
- FRER 지원 NIC 또는
- 소프트웨어 스택 (Linux TSN 등)

### 소프트웨어 요구사항

**관리:**
- IEEE 802.1CB MIB
- YANG 모델 기반 설정
- NETCONF/RESTCONF API

**모니터링:**
- 시퀀스 번호 추적
- 중복 프레임 통계
- 경로별 성능 측정

---

## 성능 측정 방법론

### RFC 2544 in FRER Environment

FRER 환경에서 RFC 2544 벤치마크 수행:

#### 1. Throughput (처리량)
```
정상 상태: 양쪽 경로 활성
→ RFC 2544 throughput 측정
→ FRER 오버헤드 확인
```

#### 2. Latency (지연시간)
```
정상 상태: RTT 측정
→ FRER 처리 지연 측정
→ 경로별 지연 차이 확인
```

#### 3. Frame Loss Rate (손실률)
```
정상 상태: 0% 손실 예상
→ 한쪽 경로 다운: 여전히 0% 손실
→ Fail-Operational 검증
```

### FRER-Specific Metrics

| 메트릭 | 설명 | 목표 |
|--------|------|------|
| **Replication Latency** | 복제 지연 | < 1 μs |
| **Elimination Latency** | 제거 지연 | < 1 μs |
| **Duplicate Rate** | 수신 중복률 | ~50% (양쪽 경로 정상 시) |
| **Out-of-Order Rate** | 순서 변경 비율 | < 0.1% |
| **Sequence Gap Rate** | 시퀀스 갭 비율 | 0% (정상 상태) |

---

## 테스트 시나리오

### 시나리오 1: 정상 운영 (Normal Operation)

**조건:**
- 모든 경로 활성
- 정상 트래픽 부하

**측정:**
- Baseline 성능
- FRER 오버헤드

### 시나리오 2: 단일 경로 장애 (Single Path Failure)

**조건:**
- 경로 A 다운 (케이블 분리)
- 트래픽 계속 전송

**측정:**
- 패킷 손실 (예상: 0%)
- 복구 시간 (예상: 0 ms)
- 성능 변화

### 시나리오 3: 경로 복구 (Path Recovery)

**조건:**
- 경로 A 복구
- 이중 경로로 전환

**측정:**
- 중복 프레임 처리
- 시퀀스 동기화
- 성능 회복 시간

### 시나리오 4: 스위치 재부팅 (Switch Reboot)

**조건:**
- Switch A 재부팅
- STP 재수렴

**측정:**
- 서비스 중단 시간
- 패킷 손실
- 복구 절차

---

## 구현 가이드라인

### 설정 체크리스트

- [ ] Stream 식별 규칙 정의
- [ ] 시퀀스 번호 생성 방식 선택 (R-TAG/HSR-TAG)
- [ ] Replication point 설정
- [ ] Elimination point 설정
- [ ] 히스토리 길이 설정
- [ ] 타임아웃 파라미터 설정
- [ ] 모니터링 활성화

### 베스트 프랙티스

1. **경로 독립성 보장**
   - 물리적으로 분리된 케이블
   - 다른 스위치 사용
   - 공통 장애점 제거

2. **시퀀스 번호 관리**
   - 16-bit 공간 효율적 사용
   - 오버플로우 처리
   - 리셋 메커니즘

3. **성능 모니터링**
   - 지속적인 통계 수집
   - 이상 징후 감지
   - 로깅 및 알람

---

## 트러블슈팅

### 문제: 중복 프레임이 애플리케이션에 전달됨

**원인:**
- Elimination 기능 미활성화
- 시퀀스 번호 불일치

**해결:**
- Elimination 설정 확인
- 시퀀스 번호 생성 검증

### 문제: 패킷 손실 발생

**원인:**
- 양쪽 경로 동시 장애
- 버퍼 오버플로우

**해결:**
- 경로 독립성 확인
- 버퍼 크기 증설

### 문제: 높은 지연시간

**원인:**
- 소프트웨어 처리 오버헤드
- 경로 불균형

**해결:**
- 하드웨어 FRER 사용
- 경로 최적화

---

## 참고 문헌

### IEEE 표준
1. **IEEE Std 802.1CB-2017** - Frame Replication and Elimination for Reliability
2. **IEEE Std 802.1Q-2018** - Bridges and Bridged Networks
3. **IEEE Std 802.1AS-2020** - Timing and Synchronization
4. **IEEE Std 802.1Qbv-2015** - Enhancements for Scheduled Traffic

### IEC 표준
- **IEC 62439-3** - High-availability Seamless Redundancy (HSR)
- **IEC 61784-2** - Industrial communication networks (Profiles)

### IETF RFC
- **RFC 2544** - Benchmarking Methodology
- **RFC 1242** - Benchmarking Terminology

### 추가 자료
- **TSN Task Group**: https://1.ieee802.org/tsn/
- **IEC 61850**: Substation Automation
- **AUTOSAR**: Automotive Ethernet Standards

---

## 용어 정리

| 용어 | 영문 | 설명 |
|------|------|------|
| **프레임 복제** | Frame Replication | 송신 측에서 프레임을 여러 경로로 복사 |
| **프레임 제거** | Frame Elimination | 수신 측에서 중복 프레임 감지 및 제거 |
| **시퀀스 번호** | Sequence Number | 프레임 순서 및 고유성 식별용 번호 |
| **스트림** | Stream | 동일한 송신-수신 간 트래픽 흐름 |
| **R-TAG** | Redundancy TAG | FRER용 이더넷 태그 (6 bytes) |
| **Talker** | Talker | 트래픽 송신 노드 |
| **Listener** | Listener | 트래픽 수신 노드 |
| **Fail-Operational** | - | 장애 시에도 동작 계속 (안전 기능) |

---

**본 가이드는 IEEE 802.1CB-2017 표준을 기반으로 작성되었습니다.**

*Last Updated: 2025-10-20*
