"""
图表自动生成模块
生成 3 张专业图表：K线图 / 财务对比柱状图 / 多维雷达图
输出到 assets/ 目录（PNG 格式，Base64 嵌入 HTML 报告）
"""

import sys
import subprocess
import os

def ensure_deps():
    """自动安装依赖（如未安装）"""
    deps = ["matplotlib>=3.7.0", "numpy>=1.24.0"]
    for dep in deps:
        try:
            if dep.startswith("matplotlib"):
                import matplotlib
            elif dep.startswith("numpy"):
                import numpy
        except ImportError:
            print(f"正在安装 {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep.split(">=")[0]])


def gen_kline(stock_name, prices, volumes, output_path):
    """
    K线趋势图（近6个月）
    若 mplfinance 可用则用它，否则降级为收盘价折线图
    """
    try:
        import mplfinance as mpf
        import pandas as pd
        import matplotlib.pyplot as plt

        # 构造 OHLC 数据（演示用随机数据，实际由数据模块传入）
        dates = pd.date_range("2025-12-01", periods=len(prices), freq="B")
        df = pd.DataFrame({
            "Open": [p * 0.99 for p in prices],
            "High": [p * 1.02 for p in prices],
            "Low":  [p * 0.98 for p in prices],
            "Close": prices,
            "Volume": volumes,
        }, index=dates)

        mpf.plot(df, type="candle", volume=True,
                 title=f"{stock_name} K线走势（近6个月）",
                 style="yahoo",
                 savefig=output_path)
        print(f"✓ K线图已生成：{output_path}")
        return True

    except ImportError:
        # 降级：matplotlib 收盘价折线图
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np

        plt.figure(figsize=(10, 5))
        plt.plot(range(len(prices)), prices, color="#D32F2F", linewidth=1.5)
        plt.fill_between(range(len(prices)), prices, alpha=0.15, color="#D32F2F")
        plt.title(f"{stock_name} 收盘价走势（近6个月）", fontsize=13, fontweight="bold")
        plt.xlabel("交易日")
        plt.ylabel("收盘价（元）")
        plt.grid(True, linestyle="--", alpha=0.4)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"✓ 降级折线图已生成：{output_path}")
        return True


def gen_comparison_bar(stock_name, target_metrics, peer_metrics_list, output_path):
    """
    财务对比柱状图：目标公司 vs 可比公司 核心指标
    target_metrics: dict，目标公司指标
    peer_metrics_list: list of dict，可比公司指标
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    labels = ["ROE(%)", "毛利率(%)", "PE(x)", "营收增速(%)"]
    target_vals = [
        target_metrics.get("roe", 0) * 100,
        target_metrics.get("gross_margin", 0) * 100,
        target_metrics.get("pe_ttm", 0),
        target_metrics.get("revenue_growth", 0) * 100,
    ]

    peer_vals = []
    peer_names = []
    for p in peer_metrics_list[:5]:
        peer_names.append(p.get("name", "未知"))
        peer_vals.append([
            p.get("roe", 0) * 100,
            p.get("gross_margin", 0) * 100,
            p.get("pe_ttm", 0),
            p.get("revenue_growth", 0) * 100,
        ])

    x = np.arange(len(labels))
    width = 0.15

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(x - width * (len(peer_vals) / 2), target_vals, width,
            label=stock_name, color="#1565C0", alpha=0.85)

    colors = ["#42A5F5", "#66BB6A", "#FFA726", "#AB47BC", "#EF5350"]
    for i, (name, vals) in enumerate(zip(peer_names, peer_vals)):
        ax.bar(x + width * (i - len(peer_vals) // 2 + 1), vals, width,
                label=name, color=colors[i % len(colors)], alpha=0.7)

    ax.set_ylabel("数值")
    ax.set_title(f"{stock_name} vs 可比公司 — 核心财务指标对比", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(fontsize=9)
    ax.grid(True, axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✓ 财务对比柱状图已生成：{output_path}")
    return True


def gen_radar(stock_name, metrics, output_path):
    """
    多维雷达图：估值 / 盈利 / 成长 / 偿债 / 营运 / 现金流 六维评分
    metrics: dict，含各维度评分（0-100）
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np

    categories = ["盈利", "成长", "估值\n吸引力", "偿债\n安全", "营运\n效率", "现金\n流"]

    # 默认评分（实际由指标计算模块传入）
    values = [
        metrics.get("profitability", 80),
        metrics.get("growth", 70),
        metrics.get("valuation", 60),
        metrics.get("solvency", 85),
        metrics.get("operation", 75),
        metrics.get("cashflow", 70),
    ]
    values += values[:1]  # 闭合

    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, "o-", linewidth=2, color="#1565C0")
    ax.fill(angles, values, color="#1565C0", alpha=0.2)
    ax.set_thetagrids((np.array(angles[:-1]) * 180 / np.pi, categories)
    ax.set_ylim(0, 100)
    ax.set_title(f"{stock_name} 六维综合评分", fontsize=13, fontweight="bold", pad=20)
    ax.grid(True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"✓ 雷达图已生成：{output_path}")
    return True


# ========== 主流程 ==========
if __name__ == "__main__":
    ensure_deps()

    assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # 演示数据（实际由 Skill 主流程传入）
    demo_prices = [1580, 1600, 1620, 1610, 1650, 1680, 1670, 1690,
                   1720, 1700, 1680, 1650, 1630, 1600, 1620, 1650,
                   1680, 1700, 1720, 1710, 1730, 1750, 1740, 1720]
    demo_volumes = [det * 1e5 for det in demo_prices]

    # 1. K线图
    gen_kline("贵州茅台", demo_prices, demo_volumes,
               os.path.join(assets_dir, "kline.png"))

    # 2. 财务对比柱状图
    target_m = {"roe": 0.34, "gross_margin": 0.917, "pe_ttm": 28.5, "revenue_growth": 0.175}
    peers_m = [
        {"name": "五粮液", "roe": 0.25, "gross_margin": 0.75, "pe_ttm": 22.0, "revenue_growth": 0.12},
        {"name": "泸州老窖", "roe": 0.28, "gross_margin": 0.82, "pe_ttm": 25.3, "revenue_growth": 0.15},
        {"name": "洋河股份", "roe": 0.20, "gross_margin": 0.68, "pe_ttm": 18.7, "revenue_growth": 0.08},
    ]
    gen_comparison_bar("贵州茅台", target_m, peers_m,
                       os.path.join(assets_dir, "comparison_bar.png"))

    # 3. 雷达图
    demo_scores = {"profitability": 92, "growth": 78, "valuation": 55,
                   "solvency": 88, "operation": 80, "cashflow": 85}
    gen_radar("贵州茅台", demo_scores,
               os.path.join(assets_dir, "radar.png"))

    print("\n✅ 所有图表生成完毕，存放于：", assets_dir)
