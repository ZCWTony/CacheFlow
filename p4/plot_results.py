#!/usr/bin/env python3
"""
绘图脚本：读取 p4/results/ 下的实验结果文件，
绘制命中率随数据包数量变化的曲线，并保存为 PNG。
"""
import os
import re
import argparse
import matplotlib.pyplot as plt

def parse_result_file(filepath):
    """
    解析实验结果文件，提取 (packet_count, hit_rate) 列表。
    文件格式应包含 "After X packets: Y%" 的行。
    """
    counts = []
    rates = []
    with open(filepath, 'r') as f:
        for line in f:
            match = re.search(r'After (\d+) packets: ([\d.]+)%', line)
            if match:
                count = int(match.group(1))
                rate = float(match.group(2))
                counts.append(count)
                rates.append(rate)
    return counts, rates

def plot_learning_curve(counts, rates, title=None, output_file=None):
    """绘制学习曲线"""
    plt.figure(figsize=(10, 6))
    plt.plot(counts, rates, marker='o', linestyle='-', linewidth=2, markersize=4)
    plt.xlabel('Number of Packets', fontsize=14)
    plt.ylabel('Hit Rate (%)', fontsize=14)
    if title:
        plt.title(title, fontsize=16)
    else:
        plt.title('CacheFlow Learning Curve (Uniform Random Flows)', fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.ylim(0, 100)
    if output_file:
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"Figure saved to {output_file}")
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description='Plot hit rate learning curve')
    parser.add_argument('input_file', help='Path to the result text file')
    parser.add_argument('--output', '-o', default=None, help='Output PNG file path (default: same dir as input with .png)')
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: File '{args.input_file}' not found.")
        return

    counts, rates = parse_result_file(args.input_file)
    if not counts:
        print("No valid data found in the file (expected 'After X packets: Y%').")
        return

    # 默认输出文件：与输入同目录，同名 .png
    if args.output is None:
        base = os.path.splitext(args.input_file)[0]
        output_file = base + '.png'
    else:
        output_file = args.output

    plot_learning_curve(counts, rates, output_file=output_file)

if __name__ == '__main__':
    main()
