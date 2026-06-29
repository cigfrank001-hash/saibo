#!/usr/bin/env python3
"""
run_all.py - 串联 4 stages

使用：
  python3 run_all.py --brand "蔚来" --industry "新能源汽车"
"""

import argparse
import sys
import subprocess
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def run_stage(stage_num, stage_name, command, brand, date):
    """运行一个 stage"""
    print("\n" + "=" * 70)
    print(f"🚀 Stage {stage_num}: {stage_name}")
    print("=" * 70)
    print(f"   命令：{' '.join(command)}")
    print()
    result = subprocess.run(command, capture_output=False)
    if result.returncode != 0:
        print(f"\n❌ Stage {stage_num} 失败")
        return False
    print(f"\n✅ Stage {stage_num} 完成")
    return True


def main():
    parser = argparse.ArgumentParser(description="brand-intent-chooser 全流程")
    parser.add_argument("--brand", required=True, help="品牌名")
    parser.add_argument("--industry", required=True, help="行业")
    parser.add_argument("--product", help="主营产品（可选）")
    parser.add_argument("--from-stage", type=int, default=1, help="从第几 stage 开始（默认 1）")
    args = parser.parse_args()

    print("=" * 70)
    print(f"🎯 brand-intent-chooser 全流程")
    print("=" * 70)
    print(f"   品牌：{args.brand}")
    print(f"   行业：{args.industry}")
    print(f"   主营：{args.product or '（待输入）'}")
    print(f"   起始：Stage {args.from_stage}")
    print()

    # 找到最近的 output 文件
    brand_safe = args.brand
    today = subprocess.run(["date", "+%Y%m%d"], capture_output=True, text=True).stdout.strip()

    s1_input = OUTPUT_DIR / f"品牌档案-{brand_safe}-{today}.json"
    s2_input = s1_input
    s2_output = OUTPUT_DIR / f"候选意图池-{brand_safe}-{today}.md"
    s3_input = s2_output
    s3_output = OUTPUT_DIR / f"最小意图清单-{brand_safe}-{today}.xlsx"
    s4_input = s3_output

    # Stage 1
    if args.from_stage <= 1:
        cmd = ["python3", str(SCRIPTS_DIR / "brand_diagnose.py"), "--brand", args.brand, "--industry", args.industry]
        if args.product:
            cmd.extend(["--product", args.product])
        if not run_stage(1, "品牌诊断（5 问）", cmd, args.brand, today):
            return
        print(f"\n⏸️  Stage 1 完成。请检查：{s1_input}")
        print(f"   手动进入 Stage 2：python3 intent_diverge.py --input {s1_input}")
        return

    # Stage 2
    if args.from_stage <= 2:
        if not s1_input.exists():
            print(f"❌ Stage 1 输出不存在：{s1_input}")
            return
        cmd = ["python3", str(SCRIPTS_DIR / "intent_diverge.py"), "--input", str(s1_input)]
        if not run_stage(2, "意图发散（生成 prompt）", cmd, args.brand, today):
            return
        print(f"\n⏸️  Stage 2 完成。请手动跑 20 个 prompt 后用 --collect 模式")
        return

    # Stage 3
    if args.from_stage <= 3:
        if not s2_output.exists():
            print(f"❌ Stage 2 输出不存在：{s2_output}")
            return
        cmd = ["python3", str(SCRIPTS_DIR / "intent_filter.py"), "--input", str(s2_output)]
        if not run_stage(3, "最小意图收口（5 维度评估）", cmd, args.brand, today):
            return
        return

    # Stage 4
    if args.from_stage <= 4:
        if not s3_output.exists():
            print(f"❌ Stage 3 输出不存在：{s3_output}")
            return
        cmd = ["python3", str(SCRIPTS_DIR / "keyword_pick.py"), "--input", str(s3_output)]
        if not run_stage(4, "5 词选词（生成 prompt）", cmd, args.brand, today):
            return
        print(f"\n🎉 全流程完成！")
        return


if __name__ == "__main__":
    main()
