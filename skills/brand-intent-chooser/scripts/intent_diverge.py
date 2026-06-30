#!/usr/bin/env python3
"""
intent_diverge.py - Stage 2: 意图发散（4 类 × N 个）

输入：品牌档案 JSON（Stage 1 输出）
半自动：生成 4 类意图头脑风暴 prompt，用户手动跑 5 家 AI 平台
       收集 5 家结果后，自动合并去重，输出候选意图池 md
"""

import json
import argparse
import re
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output"

# 5 家 AI 平台（V1.0 拍板写死）
AI_PLATFORMS = [
    {"name": "DeepSeek", "url": "https://chat.deepseek.com/", "color": "🟣"},
    {"name": "豆包", "url": "https://www.doubao.com/", "color": "🟢"},
    {"name": "Kimi", "url": "https://kimi.moonshot.cn/", "color": "⚫"},
    {"name": "文心一言", "url": "https://yiyan.baidu.com/", "color": "🔵"},
    {"name": "通义千问", "url": "https://tongyi.aliyun.com/", "color": "🟠"},
]

# 3 类意图模板（V1.2 拍板：品牌/行业/区域，比较+决策合并到品牌意图）
INTENT_TYPES = [
    {
        "type": "品牌意图",
        "definition": "用户已锁定品牌（决策/比较层）—— V1.3 合并原'比较意图'+'决策意图'",
        "prompt_template": "请列出 10 个搜索词，体现用户已锁定 {brand} 品牌后的搜索行为（价格/配置/试驾/售后/对比/决策等）。注意：V1.3 品牌意图合并了'{brand} vs 竞品'/'{brand} 哪个好'/'该不该买 {brand}'等所有品牌锁定后的搜索词。",
    },
    {
        "type": "行业意图",
        "definition": "用户没锁定品牌，但有行业/场景/品类/其他需求（认知层）—— V1.2 合并 V1.1 的场景/品类/其他",
        "prompt_template": "请列出 10 个搜索词，体现用户没锁定 {brand} 品牌，但有行业/场景/品类/其他需求（如 30 万级纯电 SUV / 夜间车灯升级 / 新能源汽车排行等认知层）。注意：V1.2 不再区分场景/品类/其他锚点，统一为'行业意图'。",
    },
    {
        "type": "区域意图",
        "definition": "用户在特定地域搜索（如 北京 30 万纯电 SUV 推荐 ），重点是地域属性",
        "prompt_template": "请列出 10 个搜索词，体现用户在特定地域（如 北京/上海/广州/深圳/成都 等城市）的搜索行为，重点是地域属性。例：北京 30 万纯电 SUV 推荐 / 上海新能源汽车推荐 / 深圳高端纯电车 等。",
    },
]


def build_prompts(archive):
    """构造 4 类 × 5 平台 = 20 个 prompt"""
    brand = archive["brand"]
    industry = archive["industry"]
    product = archive.get("main_product", "")
    competitors = " / ".join(archive.get("competitors", []))

    prompts = []
    for intent in INTENT_TYPES:
        prompt_text = intent["prompt_template"].format(
            brand=brand,
            industry=industry,
            main_product=product,
            competitors=competitors,
        )
        for platform in AI_PLATFORMS:
            prompts.append({
                "intent_type": intent["type"],
                "intent_definition": intent["definition"],
                "platform": platform["name"],
                "platform_color": platform["color"],
                "platform_url": platform["url"],
                "prompt": prompt_text,
            })
    return prompts


def print_prompts(prompts, archive):
    """打印所有 prompt 供用户手动跑"""
    brand = archive["brand"]
    today = datetime.now().strftime("%Y%m%d")

    print("=" * 70)
    print(f"🎯 Stage 2: 意图发散（4 类 × 5 平台 = 20 个 prompt）")
    print("=" * 70)
    print(f"\n品牌：{brand}")
    print(f"\n📌 使用说明：")
    print(f"   1. 复制下方 20 个 prompt 到对应平台跑")
    print(f"   2. 每个 prompt 收集 10 个搜索词建议")
    print(f"   3. 收集完所有结果后，运行 --collect 模式输入到本脚本")
    print()

    current_type = None
    for i, p in enumerate(prompts, 1):
        if p["intent_type"] != current_type:
            current_type = p["intent_type"]
            print("\n" + "─" * 70)
            print(f"📂 {current_type}（{p['intent_definition']}）")
            print("─" * 70)

        print(f"\n【{i:02d}】{p['platform_color']} {p['platform']}")
        print(f"   URL：{p['platform_url']}")
        print(f"   Prompt：")
        print(f"   {p['prompt']}")

    print("\n" + "=" * 70)
    print(f"📝 收集 20 个结果后，运行：")
    print(f"   python3 intent_diverge.py --collect --input 品牌档案-{brand}-{today}.json --results <results.json>")
    print("=" * 70)


def collect_results(archive, results):
    """收集并合并 20 个结果"""
    print("=" * 70)
    print(f"📊 合并 20 个结果中...")
    print("=" * 70)

    # 按意图类型分组
    grouped = {t["type"]: [] for t in INTENT_TYPES}
    for r in results:
        if r["intent_type"] in grouped:
            grouped[r["intent_type"]].extend(r["keywords"])

    # 去重 + 去空白
    for intent_type in grouped:
        seen = set()
        unique = []
        for kw in grouped[intent_type]:
            kw_clean = kw.strip()
            if kw_clean and kw_clean.lower() not in seen:
                seen.add(kw_clean.lower())
                unique.append(kw_clean)
        grouped[intent_type] = unique

    # 输出候选意图池 md
    brand = archive["brand"]
    today = datetime.now().strftime("%Y%m%d")
    out_path = OUTPUT_DIR / f"候选意图池-{brand}-{today}.md"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# 候选意图池 - {brand}\n\n")
        f.write(f"> 生成日期：{today}\n")
        f.write(f"> 品牌：{archive['brand']}\n")
        f.write(f"> 行业：{archive['industry']}\n")
        f.write(f"> 主营：{archive.get('main_product', '')}\n")
        f.write(f"> 目标用户：{archive.get('target_persona', '')}\n")
        f.write(f"> 使用场景：{archive.get('main_scenario', '')}\n")
        f.write(f"> 核心竞品：{' / '.join(archive.get('competitors', []))}\n\n")

        f.write("---\n\n")
        f.write("## 4 类意图统计\n\n")
        f.write("| 意图类型 | 定义 | 跑出去词数 |\n")
        f.write("|---------|------|----------|\n")
        for t in INTENT_TYPES:
            f.write(f"| **{t['type']}** | {t['definition']} | {len(grouped[t['type']])} |\n")

        f.write("\n---\n\n")
        for t in INTENT_TYPES:
            f.write(f"## {t['type']}（{t['definition']}）\n\n")
            for i, kw in enumerate(grouped[t["type"]], 1):
                f.write(f"{i}. {kw}\n")
            f.write("\n")

        f.write("---\n\n")
        f.write("## 下一步\n\n")
        f.write(f"运行 Stage 3 评估最小意图：\n")
        f.write(f"```bash\n")
        f.write(f"python3 intent_filter.py --input {out_path}\n")
        f.write(f"```\n")

    print(f"\n✅ 候选意图池已保存：{out_path}")
    print(f"\n📊 统计：")
    for t in INTENT_TYPES:
        print(f"   {t['type']}：{len(grouped[t['type']])} 个唯一词")
    print(f"\n📌 下一步：python3 intent_filter.py --input {out_path}")

    return out_path


def main():
    parser = argparse.ArgumentParser(description="Stage 2: 意图发散")
    parser.add_argument("--input", help="Stage 1 输出（品牌档案 JSON）")
    parser.add_argument("--collect", action="store_true", help="收集模式：合并 20 个结果")
    parser.add_argument("--results", help="收集的结果 JSON")
    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        return

    # 读取品牌档案
    with open(args.input, encoding="utf-8") as f:
        archive = json.load(f)

    if args.collect:
        # 收集模式
        if not args.results:
            print("❌ --collect 模式需要 --results 参数（结果 JSON 路径）")
            return
        with open(args.results, encoding="utf-8") as f:
            results = json.load(f)
        collect_results(archive, results)
    else:
        # 打印 prompt 模式
        prompts = build_prompts(archive)
        print_prompts(prompts, archive)


if __name__ == "__main__":
    main()
