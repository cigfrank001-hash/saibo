#!/usr/bin/env python3
"""
intent_diverge.py - Stage 2: 意图发散（V2.0 · 4 类 × N 个 · 含 V2.1 行业意图 7 大类）

V2.0 升级（2026-07-02 拍板）：
- 行业意图按 7 大类（查/选/比/问/看/找）分别发散
- 加 6 条边界判定规则
- 加 7 条禁止蔓延示例
- 候选意图池输出加"二级分类标签"列

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

# ========================================
# V2.1 行业意图 7 大类（2026-07-02 拍板）
# ========================================
INDUSTRY_INTENT_7_CATEGORIES = {
    "查种源": {
        "action": "查",
        "mindset": "从哪来？合法不？",
        "sub_categories": ["来源类", "许可证类", "政策类"],
        "prompt_template": "请列出 10 个搜索词，体现用户查询「{brand}」所在行业的产品/服务的来源、资质、合法性。例：{industry} 许可证 / {brand} 工厂地址 / {industry} 补贴政策 / 进口 {industry} 合规 等。",
    },
    "选品种": {
        "action": "选",
        "mindset": "哪个品种/型号/类型适合我？",
        "sub_categories": ["品种推荐", "品种特性", "品种对比", "品种大全"],
        "prompt_template": "请列出 10 个搜索词，体现用户在选「{brand}」所在行业的品种/型号/类型。例：{industry} 哪个好 / {industry} 推荐 / {industry} 区别 / {industry} 大全 等。",
    },
    "比价格": {
        "action": "比",
        "mindset": "多少钱？规格差价？批量价？",
        "sub_categories": ["规格价", "品种价", "批量价", "周期价"],
        "prompt_template": "请列出 10 个搜索词，体现用户对比「{brand}」所在行业的价格。例：{industry} 价格 / {industry} 多少钱 / {industry} 批发 / {industry} 行情 等。",
    },
    "问养殖": {
        "action": "问",
        "mindset": "怎么用？参数？环境？",
        "sub_categories": ["技术方法", "关键参数", "环境条件", "周期管理"],
        "prompt_template": "请列出 10 个搜索词，体现用户咨询「{brand}」所在行业的产品/服务的使用/方法/参数。例：{industry} 怎么用 / {industry} 技术 / {industry} 周期 等。",
    },
    "看实证": {
        "action": "看",
        "mindset": "谁干得好？实证案例？供应商/品牌怎么挑？",
        "sub_categories": ["实证案例", "行业供应商", "竞品对比"],
        "prompt_template": "请列出 10 个搜索词，体现用户考察「{brand}」所在行业的实证案例/供应商/品牌对比。例：{industry} 案例 / {industry} 排行 / {industry} 推荐 品牌 / {brand} vs 竞品 等。注意：必须明确点名 2 个品牌才算竞品对比，模糊排名归行业供应商。",
    },
    "找销路": {
        "action": "找",
        "mindset": "卖给谁？加工？下游？",
        "sub_categories": ["下游销售", "延伸加工", "终端采购"],
        "prompt_template": "请列出 10 个搜索词，体现用户找「{brand}」所在行业的下游/销售/加工/采购渠道。例：{industry} 收购 / {industry} 加工 / {industry} 销售 等。",
    },
    "问配套": {
        "action": "问",
        "mindset": "怎么运？合规？其他配套？",
        "sub_categories": ["运输配套", "检疫合规", "其他配套"],
        "prompt_template": "请列出 10 个搜索词，体现用户咨询「{brand}」所在行业的运输/合规/其他配套服务。例：{industry} 怎么运 / {industry} 检疫 / {industry} 配套 等。",
    },
}

# 4 类意图模板（V2.0：品牌/行业二级/区域/同维度对比）
INTENT_TYPES = [
    {
        "type": "品牌意图",
        "definition": "用户已锁定品牌（决策/比较层）—— V1.3 合并原'比较意图'+'决策意图'",
        "prompt_template": "请列出 10 个搜索词，体现用户已锁定 {brand} 品牌后的搜索行为（价格/配置/试驾/售后/对比/决策等）。注意：V1.3 品牌意图合并了'{brand} vs 竞品'/'{brand} 哪个好'/'该不该买 {brand}'等所有品牌锁定后的搜索词。",
        "subcategories": None,  # 品牌意图不分子类
    },
    {
        "type": "行业意图（V2.1 7 大类）",
        "definition": "用户没锁定品牌，但有行业/场景/品类需求（认知层）—— V2.0 按 7 大类分别发散",
        "prompt_template": None,  # 动态生成（按 7 大类）
        "subcategories": INDUSTRY_INTENT_7_CATEGORIES,
    },
    {
        "type": "区域意图",
        "definition": "用户在特定地域搜索（如 北京 30 万纯电 SUV 推荐 ），重点是地域属性",
        "prompt_template": "请列出 10 个搜索词，体现用户在特定地域（如 北京/上海/广州/深圳/成都 等城市）的搜索行为，重点是地域属性。例：北京 30 万纯电 SUV 推荐 / 上海新能源汽车推荐 / 深圳高端纯电车 等。",
        "subcategories": None,
    },
    {
        "type": "同维度对比意图（V2.0 新增）",
        "definition": "明确点名 2 个品牌对比（行业意图/看实证/竞品对比子类）—— V2.0 从行业意图拆出",
        "prompt_template": "请列出 10 个搜索词，体现用户对「{brand} 所在行业」的 2 个具体品牌做对比。必须是品牌 vs 品牌（如 '{brand} vs 竞品名' / '品牌A 和 品牌B 哪个好'）。注意：V2.1 新规不允许'品牌 vs 物种/产品'对比（如 '{brand} vs 物种名' 是禁止的）。",
        "subcategories": None,
    },
]


# ========================================
# V2.1 边界判定规则（6 条 · 防蔓延）
# ========================================
BOUNDARY_RULES = [
    {
        "rule": 1,
        "pattern": "明确点名 2 品牌",
        "归位": "→ 看实证/竞品对比",
        "note": "V2.0 增量规则 · 标杆案例：聚盛源 vs 龙兴",
    },
    {
        "rule": 2,
        "pattern": "模糊排名/不点名 2 品牌",
        "归位": "→ 看实证/行业供应商",
        "note": "V2.0 改归位 · V1.0 禁止蔓延 → V2.0 改归位",
    },
    {
        "rule": 3,
        "pattern": "单一品牌评价（'XX 怎么样'）",
        "归位": "→ ❌ 蔓延到品牌意图（禁止）",
        "note": "应放品牌意图包",
    },
    {
        "rule": 4,
        "pattern": "行业词根 + 品牌前缀",
        "归位": "→ ❌ 蔓延到品牌+行业（应拆词：去掉品牌前缀）",
        "note": "如「聚盛源鲟鱼 5cm 多少钱」→ 拆为「鲟鱼苗 5cm 多少钱」",
    },
    {
        "rule": 5,
        "pattern": "非本行业品类",
        "归位": "→ ❌ 蔓延到非本行业（禁止）",
        "note": "如鲟鱼苗意图库不允许「对虾养殖技术」",
    },
    {
        "rule": 6,
        "pattern": "品牌 vs 物种/产品（V2.1 新增）",
        "归位": "→ ❌ 蔓延（跨维度禁止）",
        "note": "如「聚盛源 vs 西伯利亚鲟鱼苗」是禁止的（西伯利亚是物种不是品牌）",
    },
]


# ========================================
# V2.1 禁止蔓延示例（7 条 · 兜底）
# ========================================
FORBIDDEN_EXAMPLES = [
    {"模式": "品牌决策", "示例": "聚盛源鲟鱼 怎么样", "归位": "❌ 蔓延到品牌意图"},
    {"模式": "行业供应商", "示例": "鲟鱼苗 品牌 排行", "归位": "⚠️ 改归位 → 看实证/行业供应商"},
    {"模式": "行业供应商", "示例": "鲟鱼苗 推荐 品牌", "归位": "⚠️ 改归位 → 看实证/行业供应商"},
    {"模式": "品牌+比价", "示例": "聚盛源鲟鱼 5cm 多少钱", "归位": "❌ 蔓延（拆词：鲟鱼苗 5cm 多少钱）"},
    {"模式": "非本行业", "示例": "鱼塘增氧设备", "归位": "❌ 蔓延（非鱼苗/鲟鱼）"},
    {"模式": "非本品类", "示例": "对虾养殖技术", "归位": "❌ 蔓延（非鲟鱼品类）"},
    {"模式": "品牌 vs 物种（V2.1 新增）", "示例": "聚盛源鲟鱼 与 西伯利亚鲟鱼苗 区别", "归位": "❌ 蔓延（跨维度）"},
]


def build_industry_prompts(archive):
    """构造行业意图 7 大类 × 5 平台 = 35 个 prompt（V2.0 新增）"""
    brand = archive["brand"]
    industry = archive["industry"]
    product = archive.get("main_product", "")
    competitors = " / ".join(archive.get("competitors", []))

    prompts = []
    for category, info in INDUSTRY_INTENT_7_CATEGORIES.items():
        prompt_text = info["prompt_template"].format(
            brand=brand,
            industry=industry,
            main_product=product,
        )
        for platform in AI_PLATFORMS:
            prompts.append({
                "intent_type": f"行业意图/{category}",
                "intent_subcategory": "、".join(info["sub_categories"]),
                "action": info["action"],
                "mindset": info["mindset"],
                "platform": platform["name"],
                "platform_color": platform["color"],
                "platform_url": platform["url"],
                "prompt": prompt_text,
            })
    return prompts


def build_prompts(archive):
    """构造全部 4 类 × 5 平台 = V2.0 数量"""
    brand = archive["brand"]
    industry = archive["industry"]
    product = archive.get("main_product", "")
    competitors = " / ".join(archive.get("competitors", []))

    prompts = []
    
    # 1. 品牌意图（5 平台）
    for intent in INTENT_TYPES[:1]:  # 品牌意图
        prompt_text = intent["prompt_template"].format(
            brand=brand, industry=industry, main_product=product, competitors=competitors
        )
        for platform in AI_PLATFORMS:
            prompts.append({
                "intent_type": intent["type"],
                "intent_subcategory": "—",
                "platform": platform["name"],
                "platform_color": platform["color"],
                "platform_url": platform["url"],
                "prompt": prompt_text,
            })
    
    # 2. 行业意图（V2.0 新增：7 大类 × 5 平台 = 35 个 prompt）
    prompts.extend(build_industry_prompts(archive))
    
    # 3. 区域意图（5 平台）
    for intent in INTENT_TYPES[2:3]:  # 区域意图
        prompt_text = intent["prompt_template"].format(
            brand=brand, industry=industry, main_product=product, competitors=competitors
        )
        for platform in AI_PLATFORMS:
            prompts.append({
                "intent_type": intent["type"],
                "intent_subcategory": "—",
                "platform": platform["name"],
                "platform_color": platform["color"],
                "platform_url": platform["url"],
                "prompt": prompt_text,
            })
    
    # 4. 同维度对比意图（5 平台，V2.0 新增）
    for intent in INTENT_TYPES[3:]:  # 同维度对比意图
        prompt_text = intent["prompt_template"].format(
            brand=brand, industry=industry, main_product=product, competitors=competitors
        )
        for platform in AI_PLATFORMS:
            prompts.append({
                "intent_type": intent["type"],
                "intent_subcategory": "看实证/竞品对比",
                "platform": platform["name"],
                "platform_color": platform["color"],
                "platform_url": platform["url"],
                "prompt": prompt_text,
            })
    
    return prompts


def apply_boundary_rules(keyword, intent_type):
    """V2.0 新增：边界判定规则应用
    
    返回：(final_type, subcategory, action)
    - final_type: 修正后的意图类型
    - subcategory: 二级分类标签
    - action: "保留" / "改归位" / "禁止蔓延"
    """
    # 规则 1: 明确点名 2 品牌 → 看实证/竞品对比
    competitors_pattern = r'(.+?)\s*(vs|和|与|跟|对比|哪个好)\s*(.+)'
    if re.search(competitors_pattern, keyword):
        # 排除"品牌 vs 物种/产品"模式
        species_keywords = ["鱼苗", "鲟鱼", "鱼", "养殖", "价格", "产品"]  # 物种/产品相关词
        match = re.search(competitors_pattern, keyword)
        if match:
            left = match.group(1).strip()
            right = match.group(3).strip()
            # 检查右侧是否为物种/产品
            if any(sk in right for sk in species_keywords):
                # 规则 6: 品牌 vs 物种/产品 → ❌ 禁止蔓延
                return ("❌禁止蔓延", "—", "规则 6")
            else:
                # 规则 1: 明确点名 2 品牌 → 看实证/竞品对比
                return ("行业意图/看实证", "竞品对比", "规则 1")
    
    # 规则 2: 模糊排名/不点名 2 品牌 → 看实证/行业供应商
    if any(kw in keyword for kw in ["排行", "推荐 品牌", "品牌 排行", "头部 品牌", "供应商 有哪些", "厂家 排行"]):
        return ("行业意图/看实证", "行业供应商", "规则 2")
    
    # 规则 3: 单一品牌评价 → ❌ 蔓延到品牌意图
    if re.search(r'(.+?)\s*(怎么样|好不好|值不值得|推荐吗|如何)$', keyword):
        return ("❌禁止蔓延", "—", "规则 3")
    
    # 规则 4: 行业词根 + 品牌前缀 → ❌ 拆词
    # 检测模式：品牌词根 + 行业词
    # 简化：包含聚盛源/聚盛源鲟鱼/北京聚盛源 + 行业相关动作
    if re.search(r'(聚盛源|北京聚盛源|聚盛源鲟鱼|聚盛源鱼)\s*(\d+cm|多少钱|价格|养殖|检疫)', keyword):
        return ("❌禁止蔓延（应拆词）", "—", "规则 4")
    
    # 规则 5: 非本行业 → ❌ 蔓延
    if any(kw in keyword for kw in ["增氧设备", "对虾", "草鱼", "鲤鱼", "罗非鱼"]):  # 非鲟鱼/鱼苗相关
        return ("❌禁止蔓延", "—", "规则 5")
    
    # 规则 6: 品牌 vs 物种/产品 → ❌ 蔓延
    # (在规则 1 中已处理)
    
    # 默认：保留原类型
    return (intent_type, "—", "保留")


def print_prompts(prompts, archive):
    """打印所有 prompt 供用户手动跑"""
    brand = archive["brand"]
    today = datetime.now().strftime("%Y%m%d")
    total = len(prompts)

    print("=" * 70)
    print(f"🎯 Stage 2: 意图发散（V2.0 · 4 类 × 5 平台 = {total} 个 prompt）")
    print("=" * 70)
    print(f"\n品牌：{brand}")
    print(f"行业：{archive['industry']}")
    print(f"\n📌 V2.0 新增：行业意图按 7 大类分别发散（35 个）+ 同维度对比意图（5 个）")
    print(f"\n📌 使用说明：")
    print(f"   1. 复制下方 {total} 个 prompt 到对应平台跑")
    print(f"   2. 每个 prompt 收集 10 个搜索词建议")
    print(f"   3. 收集完所有结果后，运行 --collect 模式输入到本脚本")
    print()

    current_type = None
    for i, p in enumerate(prompts, 1):
        if p["intent_type"] != current_type:
            current_type = p["intent_type"]
            print("\n" + "─" * 70)
            print(f"📂 {current_type}")
            if "subcategory" in p and p["intent_subcategory"] != "—":
                print(f"   二级分类：{p['intent_subcategory']}")
            if "action" in p:
                print(f"   客户动作：{p['action']} ｜ 客户心智：{p['mindset']}")
            print("─" * 70)

        print(f"\n【{i:02d}】{p['platform_color']} {p['platform']}")
        print(f"   URL：{p['platform_url']}")
        print(f"   Prompt：")
        print(f"   {p['prompt']}")

    print("\n" + "─" * 70)
    print(f"📋 V2.0 边界判定规则（{len(BOUNDARY_RULES)} 条 · 防蔓延）：")
    for rule in BOUNDARY_RULES:
        print(f"   规则 {rule['rule']}：{rule['pattern']} {rule['归位']}")
    print("─" * 70)
    
    print(f"\n🚫 禁止蔓延示例（{len(FORBIDDEN_EXAMPLES)} 条 · 兜底）：")
    for ex in FORBIDDEN_EXAMPLES:
        print(f"   {ex['模式']}：{ex['示例']} → {ex['归位']}")

    print("\n" + "=" * 70)
    print(f"📝 收集 {total} 个结果后，运行：")
    print(f"   python3 intent_diverge.py --collect --input 品牌档案-{brand}-{today}.json --results <results.json>")
    print("=" * 70)


def collect_results(archive, results):
    """收集并合并结果（V2.0 新增：边界判定 + 二级分类标签）"""
    print("=" * 70)
    print(f"📊 合并 {len(results)} 个结果中（含 V2.0 边界判定）...")
    print("=" * 70)

    # 按意图类型分组
    grouped = {}
    for r in results:
        if r["intent_type"] not in grouped:
            grouped[r["intent_type"]] = []
        grouped[r["intent_type"]].extend(r["keywords"])

    # 去重 + 边界判定
    processed = {}
    boundary_stats = {"规则 1 改归位": 0, "规则 2 改归位": 0, "规则 3 禁止": 0, "规则 4 拆词": 0, "规则 5 禁止": 0, "规则 6 禁止": 0, "保留": 0}
    
    for intent_type, kws in grouped.items():
        seen = set()
        unique = []
        for kw in kws:
            kw_clean = kw.strip()
            if kw_clean and kw_clean.lower() not in seen:
                seen.add(kw_clean.lower())
                # V2.0 新增：应用边界判定
                final_type, subcat, action = apply_boundary_rules(kw_clean, intent_type)
                if "禁止" in action:
                    boundary_stats[action] = boundary_stats.get(action, 0) + 1
                else:
                    boundary_stats["保留"] = boundary_stats.get("保留", 0) + 1
                # 收录到处理后（即使禁止也记录供学习）
                key = (final_type, subcat)
                if key not in processed:
                    processed[key] = []
                processed[key].append((kw_clean, action))
        grouped[intent_type] = unique

    # 输出候选意图池 md（V2.0 加二级分类标签）
    brand = archive["brand"]
    today = datetime.now().strftime("%Y%m%d")
    out_path = OUTPUT_DIR / f"候选意图池-{brand}-{today}.md"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# 候选意图池 - {brand}（V2.0）\n\n")
        f.write(f"> 生成日期：{today}\n")
        f.write(f"> 品牌：{archive['brand']}\n")
        f.write(f"> 行业：{archive['industry']}\n")
        f.write(f"> 主营：{archive.get('main_product', '')}\n")
        f.write(f"> 目标用户：{archive.get('target_persona', '')}\n")
        f.write(f"> 使用场景：{archive.get('main_scenario', '')}\n")
        f.write(f"> 客户动作链：{archive.get('action_chain', '未填写')}\n")
        f.write(f"> 核心竞品：{' / '.join(archive.get('competitors', []))}\n")
        f.write(f"> V2.0 升级：集成 7 大类 + 6 边界规则 + 7 禁止蔓延\n\n")

        f.write("---\n\n")
        f.write("## 4 类意图统计（含 V2.0 二级分类）\n\n")
        f.write("| 意图类型 | 二级分类 | 跑出去词数 | 边界处理 |\n")
        f.write("|---------|---------|----------|----------|\n")
        for t in INTENT_TYPES:
            if t["type"] == "行业意图（V2.1 7 大类）":
                for cat, info in INDUSTRY_INTENT_7_CATEGORIES.items():
                    subcats = "、".join(info["sub_categories"])
                    count = sum(1 for kws in processed.values() for kw, _ in kws if f"行业意图/{cat}" in str(kws) or any(s in kw[0] for s in info["sub_categories"]))
                    f.write(f"| 行业意图/{cat} | {subcats} | {count} | V2.0 边界判定 |\n")
            else:
                count = sum(1 for kws in processed.values() for kw, _ in kws if t["type"] in kw[0])
                f.write(f"| **{t['type']}** | — | {count} | V2.0 边界判定 |\n")

        f.write("\n---\n\n")
        f.write("## V2.0 边界判定结果\n\n")
        f.write(f"| 规则 | 命中数 |\n")
        f.write(f"|------|-------|\n")
        for k, v in boundary_stats.items():
            f.write(f"| {k} | {v} |\n")

        f.write("\n---\n\n")
        f.write("## V2.0 禁止蔓延示例（7 条）\n\n")
        for ex in FORBIDDEN_EXAMPLES:
            f.write(f"- {ex['示例']} → {ex['归位']}\n")
        
        f.write("\n---\n\n")
        f.write("## 下一步\n\n")
        f.write(f"运行 Stage 3 评估最小意图（含 V2.0 边界判定检查）：\n")
        f.write(f"```bash\n")
        f.write(f"python3 intent_filter.py --input {out_path}\n")
        f.write(f"```\n")

    print(f"\n✅ 候选意图池已保存：{out_path}")
    print(f"\n📊 统计：")
    for t in INTENT_TYPES:
        if t["type"] == "行业意图（V2.1 7 大类）":
            for cat, info in INDUSTRY_INTENT_7_CATEGORIES.items():
                count = sum(1 for kws in processed.values() for kw, _ in kws if any(s in kw[0] for s in info["sub_categories"]))
                print(f"   行业意图/{cat}：{count} 个")
        else:
            count = sum(1 for kws in processed.values() for kw, _ in kws if t["type"] in kw[0])
            print(f"   {t['type']}：{count} 个")
    
    print(f"\n📋 V2.0 边界判定结果：")
    for k, v in boundary_stats.items():
        print(f"   {k}：{v}")
    print(f"\n📌 下一步：python3 intent_filter.py --input {out_path}")

    return out_path


def main():
    parser = argparse.ArgumentParser(description="Stage 2: 意图发散（V2.0 · 含 7 大类 + 边界判定）")
    parser.add_argument("--input", help="Stage 1 输出（品牌档案 JSON）")
    parser.add_argument("--collect", action="store_true", help="收集模式：合并结果")
    parser.add_argument("--results", help="收集的结果 JSON")
    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        return

    # 读取品牌档案
    with open(args.input, encoding="utf-8") as f:
        archive = json.load(f)

    if args.collect:
        if not args.results:
            print("❌ --collect 模式需要 --results 参数（结果 JSON 路径）")
            return
        with open(args.results, encoding="utf-8") as f:
            results = json.load(f)
        collect_results(archive, results)
    else:
        prompts = build_prompts(archive)
        print_prompts(prompts, archive)


if __name__ == "__main__":
    main()
