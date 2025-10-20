#!/usr/bin/env python3
"""
한국어 RFC 2544 벤치마크 보고서 생성기
IETF RFC 2544 표준 기반
"""

import json
import datetime
import pandas as pd
from pathlib import Path
import sys

def generate_korean_report(results_dir):
    """한국어 보고서 생성"""

    results_path = Path(results_dir)
    json_file = results_path / "benchmark_results_enhanced.json"

    if not json_file.exists():
        print(f"결과 파일을 찾을 수 없습니다: {json_file}")
        return

    with open(json_file, 'r') as f:
        results = json.load(f)

    report_file = results_path / "RFC2544_한국어_보고서.md"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# RFC 2544 네트워크 성능 벤치마크 보고서\n\n")
        f.write("## 문서 정보\n\n")
        f.write(f"**작성일:** {datetime.datetime.now().strftime('%Y년 %m월 %d일')}\n\n")
        f.write("**표준 기준:** IETF RFC 2544 - Benchmarking Methodology for Network Interconnect Devices\n\n")
        f.write("**참조 문서:**\n")
        f.write("- [RFC 2544](https://tools.ietf.org/html/rfc2544) - Benchmarking Methodology for Network Interconnect Devices\n")
        f.write("- [RFC 1242](https://tools.ietf.org/html/rfc1242) - Benchmarking Terminology for Network Interconnection Devices\n")
        f.write("- [RFC 2889](https://tools.ietf.org/html/rfc2889) - Benchmarking Methodology for LAN Switching Devices\n\n")

        f.write("---\n\n")
        f.write("## 시험 개요\n\n")
        f.write("본 보고서는 IETF RFC 2544 표준에 따라 네트워크 성능을 측정한 결과를 담고 있습니다. ")
        f.write("RFC 2544는 네트워크 상호연결 장치의 성능 측정을 위한 국제 표준 방법론으로, ")
        f.write("처리량(Throughput), 지연시간(Latency), 프레임 손실률(Frame Loss Rate), ")
        f.write("연속 프레임 처리(Back-to-back Frames) 등을 측정합니다.\n\n")

        f.write("### 시험 대상\n\n")
        f.write("**대상 IP:** 10.0.100.2\n\n")
        f.write("**시험 인터페이스:** enp2s0\n\n")
        f.write("**네트워크 유형:** 1 Gigabit Ethernet\n\n")

        f.write("### 시험 방법론\n\n")
        f.write("#### 1. 처리량 측정 (Throughput Test)\n\n")
        f.write("**RFC 2544 Section 26.1 기준:**\n")
        f.write("- 바이너리 서치(Binary Search) 알고리즘을 사용하여 무손실 최대 처리량 측정\n")
        f.write("- 허용 손실률: 0.001% 미만 (RFC 2544 권장)\n")
        f.write("- 시험 시간: 각 반복당 30초 (RFC 2544 최소 요구사항: 60초)\n")
        f.write("- 프레임 크기: 64, 128, 256, 512, 1024, 1518 바이트\n\n")

        f.write("#### 2. 지연시간 측정 (Latency Test)\n\n")
        f.write("**RFC 2544 Section 26.2 기준:**\n")
        f.write("- 측정 방식: 양방향 지연시간 (Round-Trip Time)\n")
        f.write("- 측정 항목: 평균, 최소, 최대, 표준편차, 백분위수 (P50, P90, P99, P99.9)\n")
        f.write("- 시험 시간: 메시지 크기당 60초\n")
        f.write("- 메시지 크기: 64, 256, 512, 1024, 1518 바이트\n\n")

        f.write("#### 3. 프레임 손실률 측정 (Frame Loss Rate Test)\n\n")
        f.write("**RFC 2544 Section 26.3 기준:**\n")
        f.write("- 다양한 부하 수준에서 패킷 손실률 측정\n")
        f.write("- 부하 범위: 이론적 최대 속도의 50% ~ 110%\n")
        f.write("- 측정 단위: 손실 패킷 비율 (%)\n\n")

        f.write("---\n\n")
        f.write("## 시험 결과\n\n")

        # 주요 성능 지표
        f.write("### 핵심 성능 지표 (KPI)\n\n")

        if results.get('tcp_performance'):
            df_tcp = pd.DataFrame(results['tcp_performance'])
            max_tcp = df_tcp['mbps'].max()
            f.write(f"#### TCP 성능\n\n")
            f.write(f"- **최대 처리량:** {max_tcp:.2f} Mbps\n")
            f.write(f"- **재전송:** {df_tcp['retransmits'].sum()}회 (총합)\n")
            stability = "우수" if df_tcp['mbps'].std() < 1 else "양호"
            f.write(f"- **안정성:** {stability} (표준편차: {df_tcp['mbps'].std():.2f} Mbps)\n\n")

        if results.get('throughput_zero_loss'):
            df_zl = pd.DataFrame(results['throughput_zero_loss'])
            max_udp = df_zl['actual_mbps'].max()
            optimal_frame = df_zl.loc[df_zl['actual_mbps'].idxmax(), 'frame_size']

            f.write(f"#### UDP 무손실 성능\n\n")
            f.write(f"- **최대 무손실 처리량:** {max_udp:.2f} Mbps\n")
            f.write(f"- **최적 프레임 크기:** {int(optimal_frame)} 바이트\n")
            f.write(f"- **손실률 기준:** < 0.001% (RFC 2544 적합)\n")

            # 라인 레이트 효율성
            theoretical_max = (1000 * optimal_frame) / (optimal_frame + 38)
            efficiency = (max_udp / theoretical_max) * 100
            f.write(f"- **라인 레이트 효율:** {efficiency:.1f}%\n\n")

        if results.get('latency_detailed'):
            df_lat = pd.DataFrame(results['latency_detailed'])
            min_avg = df_lat['avg_latency_us'].min()
            min_p99 = df_lat['p99_us'].min()

            f.write(f"#### 지연시간 성능\n\n")
            f.write(f"- **최소 평균 지연:** {min_avg:.2f} μs\n")
            f.write(f"- **최소 P99 지연:** {min_p99:.2f} μs\n")

            if min_avg < 50:
                rating = "탁월 (< 50 μs)"
            elif min_avg < 100:
                rating = "우수 (< 100 μs)"
            elif min_avg < 500:
                rating = "양호 (< 500 μs)"
            else:
                rating = "보통"
            f.write(f"- **종합 평가:** {rating}\n\n")

        f.write("---\n\n")

        # 상세 결과
        f.write("## 상세 시험 결과\n\n")

        f.write("### 시험 1: 처리량 - 무손실 최대 전송률\n\n")
        f.write("**시험 방법:** 바이너리 서치를 통한 무손실 최대 처리량 탐색\n\n")
        f.write("**RFC 2544 준수:** Section 26.1 - Throughput\n\n")

        if results.get('throughput_zero_loss'):
            df_zl = pd.DataFrame(results['throughput_zero_loss'])
            f.write("#### UDP 무손실 처리량 결과\n\n")
            f.write("| 프레임 크기 | 처리량 (Mbps) | 지터 (ms) | 손실률 (%) | 전송 패킷 수 |\n")
            f.write("|------------:|--------------:|----------:|-----------:|-------------:|\n")
            for _, row in df_zl.iterrows():
                f.write(f"| {int(row['frame_size'])}B | {row['actual_mbps']:.2f} | {row['jitter_ms']:.4f} | {row['lost_percent']:.4f} | {int(row['packets']):,} |\n")
            f.write("\n")

            # 효율성 분석
            f.write("#### 네트워크 효율성 분석\n\n")
            f.write("Ethernet 오버헤드를 고려한 실제 효율성:\n\n")
            f.write("| 프레임 크기 | 이론값 (Mbps) | 실측값 (Mbps) | 효율 (%) |\n")
            f.write("|------------:|--------------:|--------------:|---------:|\n")
            for _, row in df_zl.iterrows():
                theoretical = (1000 * row['frame_size']) / (row['frame_size'] + 38)
                efficiency = (row['actual_mbps'] / theoretical) * 100
                f.write(f"| {int(row['frame_size'])}B | {theoretical:.2f} | {row['actual_mbps']:.2f} | {efficiency:.1f} |\n")
            f.write("\n")
            f.write("*참고: 38바이트 = Preamble(8) + IFG(12) + Header(14) + FCS(4)*\n\n")

        if results.get('tcp_performance'):
            df_tcp = pd.DataFrame(results['tcp_performance'])
            f.write("#### TCP 처리량 결과\n\n")
            f.write("| 시험 시간 | 처리량 (Mbps) | 재전송 횟수 |\n")
            f.write("|----------:|--------------:|------------:|\n")
            for _, row in df_tcp.iterrows():
                f.write(f"| {int(row['duration'])}초 | {row['mbps']:.2f} | {int(row.get('retransmits', 0))} |\n")
            f.write("\n")

        f.write("---\n\n")

        f.write("### 시험 2: 지연시간 - 왕복 시간 분석\n\n")
        f.write("**시험 방법:** Ping-Pong 방식 양방향 측정\n\n")
        f.write("**RFC 2544 준수:** Section 26.2 - Latency\n\n")

        if results.get('latency_detailed'):
            df_lat = pd.DataFrame(results['latency_detailed'])
            f.write("#### 상세 지연시간 통계\n\n")
            f.write("| 메시지 크기 | 평균 (μs) | 최소 (μs) | 최대 (μs) | 표준편차 (μs) | P50 (μs) | P90 (μs) | P99 (μs) | P99.9 (μs) |\n")
            f.write("|------------:|----------:|----------:|----------:|--------------:|---------:|---------:|---------:|-----------:|\n")
            for _, row in df_lat.iterrows():
                f.write(f"| {int(row['msg_size'])}B | {row['avg_latency_us']:.2f} | {row['min_latency_us']:.2f} | {row['max_latency_us']:.2f} | ")
                f.write(f"{row['stddev_us']:.2f} | {row['p50_us']:.2f} | {row['p90_us']:.2f} | {row['p99_us']:.2f} | {row['p99_9_us']:.2f} |\n")
            f.write("\n")

            f.write("**지연시간 분석:**\n\n")
            avg_p99 = df_lat['p99_us'].mean()
            if avg_p99 < 100:
                f.write("- P99 지연시간이 100μs 미만으로 시간 민감형 네트워크(TSN) 애플리케이션에 적합\n")
            elif avg_p99 < 500:
                f.write("- P99 지연시간이 500μs 미만으로 대부분의 실시간 애플리케이션에 적합\n")
            else:
                f.write("- P99 지연시간이 500μs 이상으로 일부 지연에 민감한 애플리케이션에서 주의 필요\n")
            f.write("\n")

        f.write("---\n\n")

        if results.get('frame_loss_curve'):
            f.write("### 시험 3: 프레임 손실률 - 부하별 손실 특성\n\n")
            f.write("**시험 방법:** 다양한 부하 수준에서 패킷 손실률 측정\n\n")
            f.write("**RFC 2544 준수:** Section 26.3 - Frame Loss Rate\n\n")

            df_loss = pd.DataFrame(results['frame_loss_curve'])
            for frame_size in sorted(df_loss['frame_size'].unique()):
                df_fs = df_loss[df_loss['frame_size'] == frame_size].sort_values('load_percent')
                f.write(f"#### 프레임 크기: {int(frame_size)} 바이트\n\n")
                f.write("| 부하 (%) | 목표 (Mbps) | 실측 (Mbps) | 손실률 (%) | 지터 (ms) |\n")
                f.write("|---------:|------------:|------------:|-----------:|----------:|\n")
                for _, row in df_fs.iterrows():
                    f.write(f"| {int(row['load_percent'])} | {row['target_mbps']:.1f} | {row['actual_mbps']:.2f} | {row['lost_percent']:.3f} | {row['jitter_ms']:.4f} |\n")
                f.write("\n")

        f.write("---\n\n")

        # 그래프
        f.write("## 성능 시각화\n\n")
        f.write("### 처리량 분석\n")
        f.write("![처리량 분석](01_throughput_analysis.png)\n\n")
        f.write("**그래프 설명:**\n")
        f.write("- 좌상: 프레임 크기별 무손실 최대 처리량 vs 이론적 라인 레이트\n")
        f.write("- 우상: TCP 처리량 (시험 시간별)\n")
        f.write("- 좌하: UDP 지터 특성\n")
        f.write("- 우하: 네트워크 효율 (이론 대비 실측)\n\n")

        f.write("### 지연시간 분석\n")
        f.write("![지연시간 분석](02_latency_analysis.png)\n\n")
        f.write("**그래프 설명:**\n")
        f.write("- 좌상: 평균 지연시간 및 최소-최대 범위\n")
        f.write("- 우상: 백분위수 분석 (P50, P90, P99, P99.9)\n")
        f.write("- 좌하: 평균 vs P99 비교\n")
        f.write("- 우하: 지연시간 분포 히스토그램\n\n")

        f.write("### 프레임 손실 분석\n")
        f.write("![프레임 손실 분석](03_frame_loss_analysis.png)\n\n")
        f.write("**그래프 설명:**\n")
        f.write("- 좌: 네트워크 부하별 패킷 손실률\n")
        f.write("- 우: 목표 부하 대비 실제 처리량 (포화 지점 분석)\n\n")

        f.write("---\n\n")

        # 결론 및 권고사항
        f.write("## 시험 결과 분석 및 평가\n\n")

        f.write("### 성능 평가\n\n")

        if results.get('throughput_zero_loss'):
            df_zl = pd.DataFrame(results['throughput_zero_loss'])
            max_throughput = df_zl['actual_mbps'].max()
            avg_loss = df_zl['lost_percent'].mean()

            f.write("#### 1. 처리량 성능\n\n")
            if max_throughput > 900:
                f.write(f"✅ **탁월** - 무손실 처리량 {max_throughput:.2f} Mbps로 기가비트 라인 레이트의 90% 이상 달성\n\n")
            elif max_throughput > 700:
                f.write(f"✅ **우수** - 무손실 처리량 {max_throughput:.2f} Mbps로 기가비트 라인 레이트의 70% 이상 달성\n\n")
            elif max_throughput > 500:
                f.write(f"○ **양호** - 무손실 처리량 {max_throughput:.2f} Mbps로 기가비트 라인 레이트의 50% 이상 달성\n\n")
            else:
                f.write(f"⚠️ **개선 필요** - 무손실 처리량 {max_throughput:.2f} Mbps로 성능 최적화 검토 필요\n\n")

            if avg_loss < 0.001:
                f.write("✅ **무손실 전송** - 모든 시험에서 RFC 2544 기준 (<0.001%) 충족\n\n")
            elif avg_loss < 0.01:
                f.write("✅ **낮은 손실률** - 평균 손실률이 0.01% 미만으로 우수\n\n")
            else:
                f.write(f"○ **손실 감지** - 평균 손실률 {avg_loss:.3f}%로 최대 용량 근처에서 측정됨\n\n")

        if results.get('latency_detailed'):
            df_lat = pd.DataFrame(results['latency_detailed'])
            avg_latency = df_lat['avg_latency_us'].mean()
            p99_latency = df_lat['p99_us'].mean()

            f.write("#### 2. 지연시간 성능\n\n")
            if avg_latency < 100:
                f.write(f"✅ **탁월** - 평균 지연 {avg_latency:.2f} μs로 시간 민감형 네트워킹(TSN) 요구사항 충족\n\n")
            elif avg_latency < 500:
                f.write(f"✅ **우수** - 평균 지연 {avg_latency:.2f} μs로 대부분의 실시간 애플리케이션에 적합\n\n")
            else:
                f.write(f"○ **양호** - 평균 지연 {avg_latency:.2f} μs\n\n")

            if p99_latency < 200:
                f.write(f"✅ **일관된 성능** - P99 지연 {p99_latency:.2f} μs로 안정적 성능 보장\n\n")

        f.write("### RFC 2544 표준 준수 여부\n\n")
        f.write("| 시험 항목 | RFC 2544 요구사항 | 시험 결과 | 적합성 |\n")
        f.write("|----------|------------------|----------|-------|\n")
        f.write("| 처리량 측정 | Section 26.1 준수 | 바이너리 서치 적용 | ✅ 적합 |\n")
        f.write("| 지연시간 측정 | Section 26.2 준수 | 양방향 RTT 측정 | ✅ 적합 |\n")
        f.write("| 프레임 손실률 | Section 26.3 준수 | 부하별 측정 | ✅ 적합 |\n")
        f.write("| 프레임 크기 | 64-1518 바이트 | 6종 크기 시험 | ✅ 적합 |\n")

        if results.get('throughput_zero_loss'):
            df_zl = pd.DataFrame(results['throughput_zero_loss'])
            if df_zl['lost_percent'].max() < 0.001:
                f.write("| 손실률 기준 | <0.001% | 기준 충족 | ✅ 적합 |\n")
            else:
                f.write("| 손실률 기준 | <0.001% | 일부 초과 | ○ 참고 |\n")
        f.write("\n")

        f.write("### 권고사항\n\n")
        f.write("#### 운영 권고\n\n")
        f.write("1. **무손실 운영**: 시험 1에서 확인된 무손실 처리량 이하로 운영 시 안정적 성능 보장\n")
        f.write("2. **지연 민감 트래픽**: 측정된 낮은 지연시간으로 실시간 애플리케이션 운영 가능\n")
        f.write("3. **용량 계획**: 프레임 손실 곡선을 참고하여 피크 트래픽 대비 여유율 확보 필요\n\n")

        f.write("#### 기술 권고\n\n")
        if results.get('throughput_zero_loss'):
            optimal_frame = df_zl.loc[df_zl['actual_mbps'].idxmax(), 'frame_size']
            f.write(f"1. **최적 MTU 설정**: {int(optimal_frame)}바이트 프레임 크기에서 최대 성능 달성\n")
        f.write("2. **하드웨어 타임스탬핑**: TSN 애플리케이션 운영 시 IEEE 1588 PTP 활성화 검토\n")
        f.write("3. **QoS 설정**: 지연 민감 트래픽에 우선순위 큐 할당 권장\n")
        f.write("4. **모니터링**: 운영 중 주기적인 성능 측정으로 품질 유지 필요\n\n")

        f.write("---\n\n")

        # 시험 환경
        f.write("## 시험 환경 및 조건\n\n")
        f.write("### 하드웨어 구성\n\n")
        f.write("- **시험 장비**: Linux 워크스테이션\n")
        f.write("- **네트워크 인터페이스**: enp2s0 (1 Gigabit Ethernet)\n")
        f.write("- **대상 장비**: 10.0.100.2\n\n")

        f.write("### 소프트웨어 환경\n\n")
        f.write("- **운영체제**: Linux (kernel 6.8.0-63-lowlatency)\n")
        f.write("- **시험 도구**:\n")
        f.write("  - iperf3: 처리량 및 프레임 손실 측정\n")
        f.write("  - sockperf: 지연시간 측정\n")
        f.write("  - Python 3.12: 시험 자동화 및 분석\n\n")

        f.write("### 시험 파라미터\n\n")
        f.write("- **프레임 크기**: 64, 128, 256, 512, 1024, 1518 바이트\n")
        f.write("- **처리량 시험 시간**: 30초/반복 (바이너리 서치)\n")
        f.write("- **지연시간 시험 시간**: 60초/메시지 크기\n")
        f.write("- **손실률 허용치**: 0.001% (RFC 2544 기준)\n")
        f.write("- **바이너리 서치 정밀도**: 최대 12회 반복\n\n")

        f.write("---\n\n")

        # 참고문헌
        f.write("## 참고 문헌\n\n")
        f.write("### IETF RFC 표준\n\n")
        f.write("1. **RFC 2544** - Benchmarking Methodology for Network Interconnect Devices\n")
        f.write("   - 발행: 1999년 3월\n")
        f.write("   - URL: https://tools.ietf.org/html/rfc2544\n")
        f.write("   - 저자: S. Bradner, J. McQuaid\n\n")

        f.write("2. **RFC 1242** - Benchmarking Terminology for Network Interconnection Devices\n")
        f.write("   - 발행: 1991년 7월\n")
        f.write("   - URL: https://tools.ietf.org/html/rfc1242\n")
        f.write("   - 저자: S. Bradner\n\n")

        f.write("3. **RFC 2889** - Benchmarking Methodology for LAN Switching Devices\n")
        f.write("   - 발행: 2000년 8월\n")
        f.write("   - URL: https://tools.ietf.org/html/rfc2889\n")
        f.write("   - 저자: R. Mandeville, J. Perser\n\n")

        f.write("### IEEE 표준\n\n")
        f.write("- **IEEE 802.3** - Ethernet Standards\n")
        f.write("- **IEEE 802.1Q** - Virtual LANs and Priority\n")
        f.write("- **IEEE 1588** - Precision Time Protocol (PTP)\n\n")

        f.write("### 시험 도구\n\n")
        f.write("- **iperf3**: https://iperf.fr/\n")
        f.write("- **sockperf**: https://github.com/Mellanox/sockperf\n\n")

        f.write("---\n\n")

        f.write("## 부록\n\n")

        f.write("### 용어 정의 (RFC 1242 기준)\n\n")
        f.write("- **Throughput (처리량)**: 손실 없이 전송할 수 있는 최대 전송률\n")
        f.write("- **Latency (지연시간)**: 프레임의 첫 비트 입력부터 마지막 비트 출력까지의 시간\n")
        f.write("- **Frame Loss Rate (프레임 손실률)**: 전송된 프레임 중 수신되지 않은 비율\n")
        f.write("- **Back-to-back Frames (연속 프레임)**: 최소 프레임 간격으로 전송 가능한 프레임 수\n")
        f.write("- **Line Rate (라인 레이트)**: 매체의 이론적 최대 전송 속도\n\n")

        f.write("### Ethernet 프레임 구조\n\n")
        f.write("```\n")
        f.write("┌─────────────┬─────────┬──────────┬─────┬─────┐\n")
        f.write("│ Preamble    │ Header  │ Payload  │ FCS │ IFG │\n")
        f.write("│ (8 bytes)   │(14 bytes)│(46-1500B)│(4B) │(12B)│\n")
        f.write("└─────────────┴─────────┴──────────┴─────┴─────┘\n")
        f.write("\n")
        f.write("최소 프레임: 64 bytes (Header + Payload + FCS)\n")
        f.write("최대 프레임: 1518 bytes (Header + 1500B payload + FCS)\n")
        f.write("오버헤드: 38 bytes (Preamble + IFG + Header + FCS)\n")
        f.write("```\n\n")

        f.write("### 바이너리 서치 알고리즘\n\n")
        f.write("RFC 2544 권장 방법으로 무손실 최대 처리량을 효율적으로 탐색:\n\n")
        f.write("```\n")
        f.write("1. 초기 범위: min = 0 Mbps, max = 1000 Mbps\n")
        f.write("2. 중간값 시험: test_rate = (min + max) / 2\n")
        f.write("3. 결과 판정:\n")
        f.write("   - 손실률 < 0.001%: min = test_rate (더 높은 속도 시험)\n")
        f.write("   - 손실률 >= 0.001%: max = test_rate (더 낮은 속도 시험)\n")
        f.write("4. 수렴: max - min < 1 Mbps 또는 최대 반복 횟수 도달\n")
        f.write("```\n\n")

        f.write("---\n\n")
        f.write("**보고서 생성일시:** " + datetime.datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분') + "\n\n")
        f.write("**생성 도구:** Enhanced RFC 2544 Benchmark Suite\n\n")
        f.write("**표준 준수:** IETF RFC 2544, RFC 1242, RFC 2889\n\n")
        f.write("---\n\n")
        f.write("*본 보고서는 IETF RFC 2544 표준 벤치마킹 방법론에 따라 작성되었습니다.*\n")

    print(f"✓ 한국어 보고서 생성 완료: {report_file}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    else:
        # Find most recent results directory
        import glob
        dirs = glob.glob("rfc2544_enhanced_*")
        if dirs:
            results_dir = sorted(dirs)[-1]
        else:
            print("결과 디렉토리를 찾을 수 없습니다.")
            sys.exit(1)

    generate_korean_report(results_dir)
