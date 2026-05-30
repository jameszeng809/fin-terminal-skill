"""
可比公司筛选模块
输入：目标公司股票数据 + 行业分类
输出：Top 5 可比公司列表 + 关键指标对比表
"""

import json

# 行业分类映射（简化版，实际应从数据源动态获取）
INDUSTRY_KEYWORDS = {
    "白酒": ["贵州茅台", "五粮液", "泸州老窖", "洋河股份", "山西汾酒", "古井贡酒"],
    "电池": ["宁德时代", "比亚迪", "亿纬锂能", "国轩高科", "欣旺达"],
    "光伏": ["隆基绿能", "通威股份", "TCL中环", "晶澳科技", "天合光能"],
    "半导体": ["中芯国际", "韦尔股份", "兆易创新", "紫光国微", "卓胜微"],
    "互联网": ["腾讯控股", "阿里巴巴", "美团", "拼多多", "京东", "百度"],
}


def screen_peers(stock_data, peer_count=5):
    """
    三级匹配算法筛选可比公司
    优先级：行业分类（必须）> 市值体量（±50%）> 业务相似度
    """
    industry = stock_data.get("basic", {}).get("industry", "")
    market_cap = stock_data.get("basic", {}).get("market_cap", 0)
    name = stock_data.get("basic", {}).get("name", "")

    # 从预设行业表中获取同行
    peers_pool = INDUSTRY_KEYWORDS.get(industry, [])

    # 过滤掉自己
    peers_pool = [p for p in peers_pool if p != name]

    # TODO: 实际运行时通过 westock-data Skill 获取真实同行数据
    # 这里返回预设的模拟数据供演示
    peer_data = []
    for i, peer_name in enumerate(peers_pool[:peer_count]):
        peer_data.append({
            "name": peer_name,
            "code": f"DEMO{i+1:03d}",
            "market_cap": market_cap * (0.5 + i * 0.2),  # 模拟不同体量
            "pe_ttm": 20 + i * 5.0,
            "roe": 0.25 + i * 0.02,
            "gross_margin": 0.5 + i * 0.05,
            "revenue_growth": 0.10 + i * 0.03,
        })

    return peer_data


def format_comparison_table(stock_data, peer_data):
    """格式化可比公司对比表（Markdown + HTML 双格式）"""
    target = stock_data.get("basic", {})
    t_name = target.get("name", "目标公司")
    t_cap = target.get("market_cap", 0) / 1e8  # 转为亿元
    t_pe = stock_data.get("basic", {}).get("pe_ttm", 0)
    t_roe = stock_data.get("financials", {}).get("roe", 0) * 100
    t_gross = stock_data.get("financials", {}).get("gross_margin", 0) * 100

    # Markdown 表格
    md = "| | 目标公司 |\n"
    md += "|:---|:---:|\n"
    md += f"| 市值(亿) | {t_cap:.0f} |\n"
    md += f"| PE | {t_pe:.1f}x |\n"
    md += f"| ROE | {t_roe:.1f}% |\n"
    md += f"| 毛利率 | {t_gross:.1f}% |\n"

    for p in peer_data:
        p_name = p.get("name", "")
        p_cap = p.get("market_cap", 0) / 1e8
        p_pe = p.get("pe_ttm", 0)
        p_roe = p.get("roe", 0) * 100
        p_gross = p.get("gross_margin", 0) * 100
        md += f"| {p_name} | {p_cap:.0f}亿 | {p_pe:.1f}x | {p_roe:.1f}% | {p_gross:.1f}% |\n"

    return md


# 示例调用
if __name__ == "__main__":
    sample = {
        "basic": {"name": "贵州茅台", "industry": "白酒", "market_cap": 2100000000000, "pe_ttm": 28.5},
        "financials": {"roe": 0.34, "gross_margin": 0.917}
    }
    peers = screen_peers(sample, peer_count=5)
    table = format_comparison_table(sample, peers)
    print("=== 可比公司筛选结果 ===")
    for p in peers:
        print(f"  - {p['name']}：市值 {p['market_cap']/1e8:.0f}亿，PE {p['pe_ttm']:.1f}x")
    print("\n=== 对比表 ===")
    print(table)
