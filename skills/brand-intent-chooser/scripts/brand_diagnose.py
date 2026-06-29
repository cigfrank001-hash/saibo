#!/usr/bin/env python3
"""
brand_diagnose.py - Stage 1: 品牌诊断（5 问）

输入：品牌 + 行业（命令行）
交互：5 问对话（行业/主营/用户角色/场景/竞品）
输出：品牌档案 JSON
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output"

# 5 问诊断模板
DIAGNOSE_QUESTIONS = [
    {
        "id": "industry",
        "question": "1️⃣ 行业是？",
        "examples": "例：新能源汽车 / 快消食品 / B2B SaaS / 医疗器械",
        "required": True,
    },
    {
        "id": "main_product",
        "question": "2️⃣ 主营产品/服务是？",
        "examples": "例：高端纯电 SUV/轿车 / 零糖气泡水 / 企业 CRM 系统",
        "required": True,
    },
    {
        "id": "target_persona",
        "question": "3️⃣ 目标用户角色是？（1 个身份为主）",
        "examples": "例：C 端高端车主 / 年轻宝妈 / 企业 IT 采购 / 医院设备科",
        "required": True,
    },
    {
        "id": "main_scenario",
        "question": "4️⃣ 主要使用场景是？（1 个情境为主）",
        "examples": "例：城市通勤+长途出行 / 家庭早餐 / 销售团队管理 / 手术室设备采购",
        "required": True,
    },
    {
        "id": "competitors",
        "question": "5️⃣ 核心竞品是哪些？（列 5 个以内）",
        "examples": "例：特斯拉/理想/小鹏/宝马/奔驰 EQ",
        "required": True,
    },
]


def ask_question(q):
    """交互式提问"""
    print(f"\n{q['question']}")
    if q.get("examples"):
        print(f"   💡 {q['examples']}")
    while True:
        answer = input("   答：").strip()
        if answer or not q.get("required", True):
            return answer
        print("   ⚠️ 必填项，请重新输入")


def parse_competitors(text):
    """解析竞品列表（支持 / , ， 分隔）"""
    for sep in ["/", ",", "，", "、", " "]:
        if sep in text:
            return [c.strip() for c in text.split(sep) if c.strip()]
    return [text]


def run_brand_diagnose(args):
    """运行品牌诊断"""
    print("=" * 60)
    print("🎯 Stage 1: 品牌诊断（5 问）")
    print("=" * 60)

    # 已传入的参数
    known = {
        "brand": args.brand,
        "industry": args.industry,
    }
    if args.product:
        known["main_product"] = args.product

    # 补全缺失问题
    answers = {"brand": args.brand, "industry": args.industry}
    for q in DIAGNOSE_QUESTIONS:
        if q["id"] in known:
            answers[q["id"]] = known[q["id"]]
            print(f"\n{q['question']}")
            print(f"   ✅ 已知：{known[q['id']]}")
        else:
            answers[q["id"]] = ask_question(q)

    # 处理竞品（转列表）
    if isinstance(answers.get("competitors"), str):
        answers["competitors"] = parse_competitors(answers["competitors"])

    # 构造品牌档案
    today = datetime.now().strftime("%Y%m%d")
    brand = answers["brand"]
    archive = {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "brand": answers["brand"],
        "industry": answers["industry"],
        "main_product": answers.get("main_product", ""),
        "target_persona": answers["target_persona"],
        "main_scenario": answers["main_scenario"],
        "competitors": answers["competitors"],
        "metadata": {
            "skill": "brand-intent-chooser",
            "stage": 1,
            "next_stage_input": "intent_diverge.py",
        },
    }

    # 保存
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"品牌档案-{brand}-{today}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"✅ 品牌档案已保存：{out_path}")
    print("=" * 60)
    print(json.dumps(archive, ensure_ascii=False, indent=2))
    print("\n📌 下一步：")
    print(f"   python3 intent_diverge.py --input {out_path}")

    return out_path


def main():
    parser = argparse.ArgumentParser(description="Stage 1: 品牌诊断")
    parser.add_argument("--brand", required=True, help="品牌名")
    parser.add_argument("--industry", required=True, help="行业")
    parser.add_argument("--product", help="主营产品（可选）")
    args = parser.parse_args()

    run_brand_diagnose(args)


if __name__ == "__main__":
    main()
