#!/usr/bin/env python3
"""检查正文连续性、禁用人物残留、引用角标及章节体量；不代替人工情节核查。"""
from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
BODY = ROOT / "小说内容" / "超兽武装小说项目" / "正文"
PATTERN = re.compile(r"^第(\d+)章.*\.md$")
HAN = re.compile(r"[\u4e00-\u9fff]")
CITATION = re.compile(r"\[\d+\]")
BANNED = ("龙戬", "泰雷", "夜凌云", "风耀")


def main():
    records = []
    issues = []
    for path in BODY.glob("*.md"):
        match = PATTERN.match(path.name)
        if not match:
            issues.append(f"文件名无法识别：{path.name}")
            continue
        n = int(match.group(1))
        text = path.read_text(encoding="utf-8")
        title, separator, body = text.partition("\n")
        if not separator or not title.startswith(f"# 第{n:03d}章"):
            issues.append(f"标题与文件名不一致：{path.name}")
        citations = CITATION.findall(body)
        if citations:
            issues.append(f"引用角标：第{n:03d}章 {citations}")
        # 风耀未来按尺度C只允许第9卷特定场景；目前仅审查已有第1卷。
        if n <= 110:
            for name in BANNED:
                if name in body:
                    issues.append(f"尺度C残留：第{n:03d}章 {name}")
        records.append((n, path.name, len(HAN.findall(body)), len(re.sub(r"\s", "", body))))
    if not records:
        print("没有找到正文文件", file=sys.stderr)
        return 1
    records.sort()
    counts = Counter(x[0] for x in records)
    for n in range(1, records[-1][0] + 1):
        if counts[n] != 1:
            issues.append(f"章节编号第{n:03d}章出现 {counts[n]} 次")
    short = [row for row in records if row[2] < 3800]
    print(f"章节：{len(records)}；范围：001—{records[-1][0]:03d}")
    print(f"正文汉字（不含标题）：{sum(r[2] for r in records):,}")
    print(f"正文非空字符（不含标题）：{sum(r[3] for r in records):,}")
    print(f"不足3800汉字：{len(short)}章（仅供人工复核；特殊章节允许较短，不影响退出码）")
    for n, _, han, _ in short:
        print(f"  第{n:03d}章：{han}汉字")
    print(f"结构/尺度C/角标问题：{len(issues)}")
    for issue in issues:
        print("  " + issue)
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
