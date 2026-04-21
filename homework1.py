#!/usr/bin/env python3
"""
Python人工智能程序设计实践 - 作业一
背景：分布式传感器节点的状态日志生成与异常检测
"""

from __future__ import annotations

import argparse
import random
import string
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

# 固定的节点数量、天数与每个日志文件的状态码数量
NODE_COUNT = 8
DAY_COUNT = 7
CODES_PER_FILE = 1500


def generate_logs(base_dir: Path, rng: random.Random) -> None:
    """生成 Node1~Node8 目录以及每个节点 day1~day7 的日志文件。"""
    letters = string.ascii_uppercase
    for node_index in range(1, NODE_COUNT + 1):
        node_dir = base_dir / f"Node{node_index}"
        node_dir.mkdir(parents=True, exist_ok=True)
        for day_index in range(1, DAY_COUNT + 1):
            log_path = node_dir / f"day{day_index}.log"
            # 随机生成 1500 个状态码并写入文件
            codes = [rng.choice(letters) for _ in range(CODES_PER_FILE)]
            log_path.write_text("".join(codes), encoding="utf-8")


def count_logs(base_dir: Path) -> Dict[str, Counter]:
    """读取所有日志文件并统计每个文件中状态码出现的频次。"""
    file_counts: Dict[str, Counter] = {}
    letters_set = set(string.ascii_uppercase)
    for node_index in range(1, NODE_COUNT + 1):
        node_name = f"Node{node_index}"
        for day_index in range(1, DAY_COUNT + 1):
            log_path = base_dir / node_name / f"day{day_index}.log"
            content = log_path.read_text(encoding="utf-8")
            # 仅统计 A-Z 的字符
            codes = [ch for ch in content if ch in letters_set]
            file_counts[f"{node_name}/day{day_index}.log"] = Counter(codes)
    return file_counts


def summarize_node_totals(file_counts: Dict[str, Counter]) -> Tuple[Dict[str, Counter], Counter]:
    """汇总每个节点在 7 天内的状态码总数，并计算所有节点总体汇总。"""
    node_totals: Dict[str, Counter] = {f"Node{i}": Counter() for i in range(1, NODE_COUNT + 1)}
    for node_index in range(1, NODE_COUNT + 1):
        node_name = f"Node{node_index}"
        for day_index in range(1, DAY_COUNT + 1):
            key = f"{node_name}/day{day_index}.log"
            node_totals[node_name] += file_counts[key]

    overall_totals = Counter()
    for total in node_totals.values():
        overall_totals += total
    return node_totals, overall_totals


def detect_anomalies(
    file_counts: Dict[str, Counter],
    node_totals: Dict[str, Counter],
    overall_totals: Counter,
    k: float,
) -> List[Tuple[str, str, int]]:
    """
    判断异常突发状态：
    若某文件中某状态码出现次数 > 其他 7 个节点所有文件中该状态码出现次数的平均值 * k，
    则记录为异常。
    """
    anomaly_records: List[Tuple[str, str, int]] = []
    other_file_count = (NODE_COUNT - 1) * DAY_COUNT

    for node_index in range(1, NODE_COUNT + 1):
        node_name = f"Node{node_index}"
        for day_index in range(1, DAY_COUNT + 1):
            key = f"{node_name}/day{day_index}.log"
            counts = file_counts[key]
            for code in string.ascii_uppercase:
                other_total = overall_totals[code] - node_totals[node_name][code]
                average = other_total / other_file_count
                if average > 0 and counts.get(code, 0) > k * average:
                    anomaly_records.append((code, key, counts[code]))

    return anomaly_records


def main() -> None:
    parser = argparse.ArgumentParser(description="生成日志并检测异常突发状态。")
    parser.add_argument(
        "--k",
        type=float,
        default=1.3,
        help="异常阈值系数，建议多次运行调整以使异常数量稳定在 15-40 之间。",
    )
    parser.add_argument("--seed", type=int, default=None, help="随机种子，用于复现实验结果。")
    args = parser.parse_args()

    base_dir = Path.cwd()
    rng = random.Random(args.seed)

    generate_logs(base_dir, rng)
    file_counts = count_logs(base_dir)
    node_totals, overall_totals = summarize_node_totals(file_counts)
    anomaly_records = detect_anomalies(file_counts, node_totals, overall_totals, args.k)

    print(f"已生成 {NODE_COUNT} 个节点 * {DAY_COUNT} 天日志文件。")
    print(f"异常记录数量：{len(anomaly_records)}")
    for record in anomaly_records:
        print(record)


if __name__ == "__main__":
    main()
