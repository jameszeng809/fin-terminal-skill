"""
财务核心指标计算模块
输入：stock_data（dict，来自数据聚合模块）
输出：metrics_result（dict，含所有计算指标 + 行业百分位排名）
"""

def calc_metrics(stock_data):
    """
    计算所有核心财务指标
    """
    f = stock_data.get("financials", {})
    b = stock_data.get("basic", {})

    # 核心指标计算
    net_profit = f.get("net_profit", 0)
    total_equity = f.get("total_equity", 1)
    total_assets = f.get("total_assets", 1)
    revenue = f.get("revenue", 0)
    gross_profit = f.get("gross_profit", 0)
    total_liabilities = f.get("total_liabilities", 0)
    current_assets = f.get("current_assets", 0)
    current_liabilities = f.get("current_liabilities", 0)
    ebitda = f.get("ebitda", 0)
    market_cap = b.get("market_cap", 0)

    metrics = {}

    # ROE 净资产收益率
    metrics["roe"] = round(net_profit / total_equity * 100, 2) if total_equity else None

    # ROA 总资产收益率
    metrics["roa"] = round(net_profit / total_assets * 100, 2) if total_assets else None

    # PE(TTM) 滚动市盈率
    metrics["pe_ttm"] = round(market_cap / net_profit, 2) if net_profit else None

    # PB 市净率
    metrics["pb"] = round(market_cap / total_equity, 2) if total_equity else None

    # 毛利率
    metrics["gross_margin"] = round(gross_profit / revenue * 100, 2) if revenue else None

    # 净利率
    metrics["net_margin"] = round(net_profit / revenue * 100, 2) if revenue else None

    # 资产负债率
    metrics["debt_ratio"] = round(total_liabilities / total_assets * 100, 2) if total_assets else None

    # 流动比率
    metrics["current_ratio"] = round(current_assets / current_liabilities, 2) if current_liabilities else None

    # 速动比率
    inventory = f.get("inventory", 0)
    metrics["quick_ratio"] = round((current_assets - inventory) / current_liabilities, 2) if current_liabilities else None

    # PEG
    profit_growth = f.get("profit_growth", 0)
    pe = metrics.get("pe_ttm", 0)
    metrics["peg"] = round(pe / (profit_growth * 100), 2) if profit_growth else None

    # EV/EBITDA
    net_debt = total_liabilities - current_assets  # 简化计算
    metrics["ev_ebitda"] = round((market_cap + net_debt) / ebitda, 2) if ebitda else None

    # 股息率
    dividend_per_share = f.get("dividend_per_share", 0)
    price = b.get("price", 1)
    metrics["dividend_yield"] = round(dividend_per_share / price * 100, 2) if price else None

    # 营收/利润增速
    metrics["revenue_growth"] = round(f.get("revenue_growth", 0) * 100, 2)
    metrics["profit_growth"] = round(f.get("profit_growth", 0) * 100, 2)

    return metrics


def industry_percentile(metrics, industry_data):
    """
    计算目标公司在行业中的百分位排名
    industry_data: list of dicts, 每行是同行公司的指标
    """
    rankings = {}
    for key, value in metrics.items():
        if value is None:
            rankings[key] = None
            continue
        # 收集同行数据
        peer_values = [d.get(key, 0) for d in industry_data if d.get(key) is not None]
        if not peer_values:
            rankings[key] = None
            continue
        # 计算百分位（越高越好 vs 越低越好需区分）
        better_higher = key not in ["debt_ratio", "peg", "ev_ebitda"]
        if better_higher:
            count = sum(1 for v in peer_values if v < value)
        else:
            count = sum(1 for v in peer_values if v > value)
        percentile = round(count / len(peer_values) * 100, 1)
        rankings[key] = f"行业前 {100 - percentile}%"
    return rankings


# 示例调用
if __name__ == "__main__":
    # 模拟数据（贵州茅台）
    stock_data = {
        "basic": {"market_cap": 2100000000000, "price": 1680.50},
        "financials": {
            "net_profit": 74730000000,
            "total_equity": 220000000000,
            "total_assets": 280000000000,
            "revenue": 150560000000,
            "gross_profit": 138000000000,
            "total_liabilities": 60000000000,
            "current_assets": 180000000000,
            "current_liabilities": 50000000000,
            "ebitda": 100000000000,
            "revenue_growth": 0.175,
            "profit_growth": 0.192,
            "inventory": 20000000000,
        }
    }

    metrics = calc_metrics(stock_data)
    for k, v in metrics.items():
        print(f"{k}: {v}")
