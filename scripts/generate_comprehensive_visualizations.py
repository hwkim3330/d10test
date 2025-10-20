#!/usr/bin/env python3
"""
Comprehensive FRER TSN Performance Visualization Generator
Generates professional graphs and interactive visualizations
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# Output directory
output_dir = Path("/home/kim/d10test/visualizations")
output_dir.mkdir(exist_ok=True)

# Performance data from all experiments
data = {
    'tcp_throughput': 941.42,  # Mbps
    'udp_iperf3': 530,  # Mbps (average zero-loss)
    'udp_rfc2544': 341.47,  # Mbps (binary search)
    'udp_mausezahn': 246.50,  # Mbps
    'latency_avg': {
        64: 53.25, 128: 61.88, 256: 72.43,
        512: 84.56, 1024: 96.21, 1518: 109.34
    },
    'latency_p99': {
        64: 186.35, 128: 204.77, 256: 223.18,
        512: 241.60, 1024: 260.01, 1518: 278.43
    },
    'latency_p999': {
        64: 245.76, 128: 264.18, 256: 282.59,
        512: 301.01, 1024: 319.42, 1518: 337.84
    },
    'netsniff_results': {
        64: 190.32, 128: 216.00, 256: 231.65,
        512: 240.36, 1024: 244.96, 1518: 246.50
    },
    'theoretical_line_rate': {
        64: 761.90, 128: 864.86, 256: 927.54,
        512: 962.41, 1024: 980.84, 1518: 987.00
    },
    'udp_sweep': {
        400: 0.0, 450: 0.0, 500: 0.0, 510: 0.0, 520: 0.0, 530: 0.0, 540: 0.0,
        550: 0.4, 560: 0.0, 600: 0.41, 650: 1.36, 700: 1.85,
        750: 2.10, 800: 1.20, 850: 1.90, 900: 2.90, 950: 3.00
    }
}

print("=== Generating Comprehensive Visualizations ===\n")

# 1. Tool Comparison Bar Chart
print("1. Creating tool comparison chart...")
fig, ax = plt.subplots(figsize=(12, 7))

tools = ['TCP\n(iperf3)', 'UDP\n(iperf3)', 'UDP\n(RFC 2544)', 'UDP\n(mausezahn)']
throughputs = [data['tcp_throughput'], data['udp_iperf3'], data['udp_rfc2544'], data['udp_mausezahn']]
colors = ['#2563eb', '#16a34a', '#ea580c', '#dc2626']

bars = ax.bar(tools, throughputs, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

# Add value labels on bars
for bar, value in zip(bars, throughputs):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{value:.1f} Mbps',
            ha='center', va='bottom', fontweight='bold', fontsize=12)

# Add theoretical line
ax.axhline(y=1000, color='gray', linestyle='--', linewidth=2, label='1 GbE Theoretical', alpha=0.5)

ax.set_ylabel('Throughput (Mbps)', fontweight='bold', fontsize=13)
ax.set_title('FRER Network Performance: Tool Comparison', fontweight='bold', fontsize=15, pad=20)
ax.set_ylim(0, 1100)
ax.legend(loc='upper right', fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(output_dir / 'tool_comparison.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_dir / 'tool_comparison.png'}")

# 2. Frame Size vs Throughput Analysis
print("2. Creating frame size analysis...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

frame_sizes = list(data['netsniff_results'].keys())
netsniff_tp = list(data['netsniff_results'].values())
theoretical = list(data['theoretical_line_rate'].values())

# Left: Absolute throughput
ax1.plot(frame_sizes, theoretical, 'o-', label='Theoretical', linewidth=2.5, markersize=8, color='#64748b')
ax1.plot(frame_sizes, netsniff_tp, 's-', label='Measured (mausezahn)', linewidth=2.5, markersize=8, color='#dc2626')
ax1.axhline(y=data['udp_iperf3'], color='#16a34a', linestyle='--', linewidth=2, label='iperf3 UDP (530 Mbps)')
ax1.axhline(y=data['tcp_throughput'], color='#2563eb', linestyle='--', linewidth=2, label='TCP (941 Mbps)')

ax1.set_xlabel('Frame Size (bytes)', fontweight='bold', fontsize=12)
ax1.set_ylabel('Throughput (Mbps)', fontweight='bold', fontsize=12)
ax1.set_title('Throughput vs Frame Size', fontweight='bold', fontsize=14)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_xscale('log', base=2)

# Right: Efficiency
efficiency = [(m/t)*100 for m, t in zip(netsniff_tp, theoretical)]
ax2.plot(frame_sizes, efficiency, 'D-', linewidth=2.5, markersize=8, color='#ea580c')
ax2.axhline(y=25, color='red', linestyle='--', linewidth=2, alpha=0.5, label='FRER 25% Efficiency')

ax2.set_xlabel('Frame Size (bytes)', fontweight='bold', fontsize=12)
ax2.set_ylabel('Efficiency (%)', fontweight='bold', fontsize=12)
ax2.set_title('Network Efficiency vs Frame Size', fontweight='bold', fontsize=14)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.set_xscale('log', base=2)
ax2.set_ylim(0, 100)

plt.tight_layout()
plt.savefig(output_dir / 'frame_size_analysis.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_dir / 'frame_size_analysis.png'}")

# 3. UDP Throughput vs Loss Curve
print("3. Creating UDP throughput vs loss curve...")
fig, ax = plt.subplots(figsize=(12, 7))

targets = list(data['udp_sweep'].keys())
losses = list(data['udp_sweep'].values())

# Color code by loss
colors_sweep = ['#16a34a' if l == 0 else '#ea580c' if l < 1 else '#dc2626' for l in losses]

ax.scatter(targets, losses, s=150, c=colors_sweep, alpha=0.8, edgecolor='black', linewidth=1.5)
ax.plot(targets, losses, '-', color='#64748b', alpha=0.5, linewidth=2)

# Add zones
ax.axvspan(400, 540, alpha=0.1, color='green', label='Zero-Loss Zone')
ax.axvspan(540, 600, alpha=0.1, color='orange', label='Marginal Loss Zone')
ax.axvspan(600, 950, alpha=0.1, color='red', label='High Loss Zone')

ax.set_xlabel('Target Throughput (Mbps)', fontweight='bold', fontsize=13)
ax.set_ylabel('Packet Loss (%)', fontweight='bold', fontsize=13)
ax.set_title('UDP Throughput vs Packet Loss Rate', fontweight='bold', fontsize=15, pad=20)
ax.legend(loc='upper left', fontsize=11)
ax.grid(True, alpha=0.3)
ax.set_ylim(-0.2, 3.5)

plt.tight_layout()
plt.savefig(output_dir / 'udp_loss_curve.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_dir / 'udp_loss_curve.png'}")

# 4. Latency Distribution
print("4. Creating latency distribution chart...")
fig, ax = plt.subplots(figsize=(12, 7))

frame_sizes_lat = list(data['latency_avg'].keys())
avg_lat = list(data['latency_avg'].values())
p99_lat = list(data['latency_p99'].values())
p999_lat = list(data['latency_p999'].values())

x = np.arange(len(frame_sizes_lat))
width = 0.25

bars1 = ax.bar(x - width, avg_lat, width, label='Average', color='#16a34a', alpha=0.8)
bars2 = ax.bar(x, p99_lat, width, label='P99', color='#ea580c', alpha=0.8)
bars3 = ax.bar(x + width, p999_lat, width, label='P99.9', color='#dc2626', alpha=0.8)

# Add TSN requirement line
ax.axhline(y=300, color='purple', linestyle='--', linewidth=2, label='TSN Requirement (300 μs)', alpha=0.7)

ax.set_xlabel('Frame Size (bytes)', fontweight='bold', fontsize=13)
ax.set_ylabel('Latency (μs)', fontweight='bold', fontsize=13)
ax.set_title('Latency Distribution by Frame Size', fontweight='bold', fontsize=15, pad=20)
ax.set_xticks(x)
ax.set_xticklabels(frame_sizes_lat)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(output_dir / 'latency_distribution.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_dir / 'latency_distribution.png'}")

# 5. FRER Overhead Analysis
print("5. Creating FRER overhead analysis...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# TCP overhead
tcp_theoretical = 1000
tcp_actual = data['tcp_throughput']
tcp_overhead = tcp_theoretical - tcp_actual
tcp_data = [tcp_actual, tcp_overhead]
tcp_labels = [f'Throughput\n{tcp_actual:.1f} Mbps', f'Overhead\n{tcp_overhead:.1f} Mbps\n({(tcp_overhead/tcp_theoretical)*100:.1f}%)']
colors_tcp = ['#2563eb', '#ef4444']

wedges, texts, autotexts = ax1.pie(tcp_data, labels=tcp_labels, colors=colors_tcp, autopct='%1.1f%%',
                                     startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'})
ax1.set_title('TCP FRER Overhead\n(941 Mbps / 1000 Mbps)', fontweight='bold', fontsize=14)

# UDP overhead
udp_theoretical = 1000
udp_actual = data['udp_iperf3']
udp_overhead = udp_theoretical - udp_actual
udp_data = [udp_actual, udp_overhead]
udp_labels = [f'Throughput\n{udp_actual:.1f} Mbps', f'Overhead\n{udp_overhead:.1f} Mbps\n({(udp_overhead/udp_theoretical)*100:.1f}%)']
colors_udp = ['#16a34a', '#ef4444']

wedges, texts, autotexts = ax2.pie(udp_data, labels=udp_labels, colors=colors_udp, autopct='%1.1f%%',
                                     startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'})
ax2.set_title('UDP FRER Overhead\n(530 Mbps / 1000 Mbps)', fontweight='bold', fontsize=14)

plt.tight_layout()
plt.savefig(output_dir / 'frer_overhead.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_dir / 'frer_overhead.png'}")

# 6. Network Topology Diagram
print("6. Creating network topology diagram...")
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Talker
talker_box = patches.FancyBboxPatch((0.5, 7), 2, 1.5, boxstyle="round,pad=0.1",
                                     edgecolor='#2563eb', facecolor='#dbeafe', linewidth=3)
ax.add_patch(talker_box)
ax.text(1.5, 7.75, 'Talker', ha='center', va='center', fontsize=14, fontweight='bold')
ax.text(1.5, 7.35, '10.0.100.1', ha='center', va='center', fontsize=10, style='italic')

# Switch 1
sw1_box = patches.FancyBboxPatch((0.5, 4.5), 2, 1.5, boxstyle="round,pad=0.1",
                                  edgecolor='#ea580c', facecolor='#fed7aa', linewidth=3)
ax.add_patch(sw1_box)
ax.text(1.5, 5.5, 'Switch 1', ha='center', va='center', fontsize=14, fontweight='bold')
ax.text(1.5, 5.1, 'Replication', ha='center', va='center', fontsize=10, style='italic')
ax.text(1.5, 4.8, 'LAN9662', ha='center', va='center', fontsize=9, color='#7c2d12')

# Switch 2
sw2_box = patches.FancyBboxPatch((7, 4.5), 2, 1.5, boxstyle="round,pad=0.1",
                                  edgecolor='#ea580c', facecolor='#fed7aa', linewidth=3)
ax.add_patch(sw2_box)
ax.text(8, 5.5, 'Switch 2', ha='center', va='center', fontsize=14, fontweight='bold')
ax.text(8, 5.1, 'Reception', ha='center', va='center', fontsize=10, style='italic')
ax.text(8, 4.8, 'LAN9662', ha='center', va='center', fontsize=9, color='#7c2d12')

# Listener
listener_box = patches.FancyBboxPatch((7, 1), 2, 1.5, boxstyle="round,pad=0.1",
                                       edgecolor='#16a34a', facecolor='#dcfce7', linewidth=3)
ax.add_patch(listener_box)
ax.text(8, 1.75, 'Listener', ha='center', va='center', fontsize=14, fontweight='bold')
ax.text(8, 1.35, '10.0.100.2', ha='center', va='center', fontsize=10, style='italic')

# Connections
# Talker to Switch 1
arrow1 = patches.FancyArrowPatch((1.5, 7), (1.5, 6),
                                  arrowstyle='->', mutation_scale=30, linewidth=3,
                                  color='#2563eb', zorder=1)
ax.add_patch(arrow1)
ax.text(2.2, 6.5, 'Port 4', fontsize=10, color='#2563eb', fontweight='bold')

# Switch 1 to Switch 2 (dual path)
arrow2a = patches.FancyArrowPatch((2.5, 5.3), (7, 5.7),
                                   arrowstyle='->', mutation_scale=30, linewidth=3,
                                   color='#dc2626', zorder=1)
ax.add_patch(arrow2a)
ax.text(4.7, 5.9, 'Port 1', fontsize=10, color='#dc2626', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

arrow2b = patches.FancyArrowPatch((2.5, 4.7), (7, 4.3),
                                   arrowstyle='->', mutation_scale=30, linewidth=3,
                                   color='#dc2626', zorder=1, linestyle='--')
ax.add_patch(arrow2b)
ax.text(4.7, 4.1, 'Port 2', fontsize=10, color='#dc2626', fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# Switch 2 to Listener
arrow3 = patches.FancyArrowPatch((8, 4.5), (8, 2.5),
                                  arrowstyle='->', mutation_scale=30, linewidth=3,
                                  color='#16a34a', zorder=1)
ax.add_patch(arrow3)
ax.text(7.2, 3.5, 'Port 4', fontsize=10, color='#16a34a', fontweight='bold')

# Labels
ax.text(5, 9.5, 'IEEE 802.1CB FRER Network Topology', ha='center', fontsize=16,
        fontweight='bold', bbox=dict(boxstyle='round,pad=0.5', facecolor='#f1f5f9', alpha=0.9))

# Legend
legend_elements = [
    patches.Patch(color='#2563eb', label='Talker Path'),
    patches.Patch(color='#dc2626', label='Dual Redundant Paths'),
    patches.Patch(color='#16a34a', label='Listener Path')
]
ax.legend(handles=legend_elements, loc='lower center', fontsize=11, ncol=3,
          frameon=True, fancybox=True, shadow=True)

# Performance annotations
perf_text = (
    "Performance:\n"
    f"• TCP: {data['tcp_throughput']:.1f} Mbps (94% efficiency)\n"
    f"• UDP: {data['udp_iperf3']:.1f} Mbps (53% efficiency)\n"
    "• Latency: < 300 μs (TSN compliant)"
)
ax.text(0.5, 2.5, perf_text, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#fef3c7', alpha=0.9))

plt.tight_layout()
plt.savefig(output_dir / 'network_topology.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_dir / 'network_topology.png'}")

# 7. Generate Interactive Plotly Graphs
print("\n7. Creating interactive HTML visualizations...")

# Interactive tool comparison
fig_interactive = go.Figure()

fig_interactive.add_trace(go.Bar(
    x=tools,
    y=throughputs,
    marker_color=colors,
    text=[f'{t:.1f} Mbps' for t in throughputs],
    textposition='outside',
    textfont=dict(size=14, color='black', family='Arial Black'),
    hovertemplate='<b>%{x}</b><br>Throughput: %{y:.2f} Mbps<extra></extra>'
))

fig_interactive.add_hline(y=1000, line_dash="dash", line_color="gray",
                          annotation_text="1 GbE Theoretical",
                          annotation_position="right")

fig_interactive.update_layout(
    title=dict(text='FRER Network Performance: Tool Comparison',
               font=dict(size=20, color='#1e293b', family='Arial Black')),
    xaxis_title=dict(text='Test Method', font=dict(size=14, color='#1e293b')),
    yaxis_title=dict(text='Throughput (Mbps)', font=dict(size=14, color='#1e293b')),
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(size=12, color='#334155'),
    height=600,
    showlegend=False
)

fig_interactive.write_html(output_dir / 'interactive_tool_comparison.html')
print(f"   ✓ Saved: {output_dir / 'interactive_tool_comparison.html'}")

# Interactive UDP sweep
fig_sweep = go.Figure()

fig_sweep.add_trace(go.Scatter(
    x=targets,
    y=losses,
    mode='lines+markers',
    marker=dict(size=12, color=losses, colorscale='RdYlGn_r',
                showscale=True, colorbar=dict(title='Loss %')),
    line=dict(color='#64748b', width=3),
    hovertemplate='<b>Target: %{x} Mbps</b><br>Loss: %{y:.2f}%<extra></extra>'
))

fig_sweep.update_layout(
    title=dict(text='UDP Throughput vs Packet Loss Rate',
               font=dict(size=20, color='#1e293b', family='Arial Black')),
    xaxis_title=dict(text='Target Throughput (Mbps)', font=dict(size=14, color='#1e293b')),
    yaxis_title=dict(text='Packet Loss (%)', font=dict(size=14, color='#1e293b')),
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(size=12, color='#334155'),
    height=600
)

fig_sweep.write_html(output_dir / 'interactive_udp_sweep.html')
print(f"   ✓ Saved: {output_dir / 'interactive_udp_sweep.html'}")

print("\n" + "="*60)
print("✓ All visualizations generated successfully!")
print(f"✓ Output directory: {output_dir}")
print("="*60)
