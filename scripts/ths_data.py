#!/usr/bin/env python3
"""
THS 数据统一入口
基于 thsdk（同花顺），替代 akshare/东方财富 数据源。

用法：
  python3 ths_data.py --search 贵州茅台
  python3 ths_data.py --quote 600519
  python3 ths_data.py --klines 600519 --freq day --count 30
  python3 ths_data.py --klines 600519 --freq 5m --count 78
  python3 ths_data.py --intraday 600519
  python3 ths_data.py --technical 600519
  python3 ths_data.py --industry-list
  python3 ths_data.py --industry-rank
  python3 ths_data.py --block-constituents URFI881165
  python3 ths_data.py --concept-list
  python3 ths_data.py --wencai "连续3日主力净流入，非ST"
  python3 ths_data.py --news 600519
  python3 ths_data.py --depth 600519
  python3 ths_data.py --big-order 600519
  python3 ths_data.py --financial 600519
  python3 ths_data.py --multi-quote 600519,000001,300750
"""

import argparse
import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

try:
    from thsdk import THS
except ImportError:
    print(json.dumps({"error": "请安装 thsdk: pip install thsdk"}))
    sys.exit(1)

TZ = ZoneInfo("Asia/Shanghai")


def to_ths_code(raw: str) -> str:
    """将简写代码转换为 THSCODE"""
    raw = str(raw).strip()
    if raw.startswith("US"):
        return raw
    if raw.startswith("sh") or raw.startswith("SH"):
        return f"USHA{raw[2:]}"
    if raw.startswith("sz") or raw.startswith("SZ"):
        return f"USZA{raw[2:]}"
    if raw.startswith("bj") or raw.startswith("BJ"):
        return f"USTM{raw[2:]}"
    # 纯数字
    code = raw.zfill(6)
    if code.startswith(("60", "68")):
        return f"USHA{code}"
    elif code.startswith(("00", "30", "002", "003")):
        return f"USZA{code}"
    elif code.startswith(("8", "4")):
        return f"USTM{code}"
    return f"USHA{code}"


def serialize_df(df, orient="records") -> list:
    """DataFrame 安全转 JSON"""
    if df is None or (hasattr(df, "empty") and df.empty):
        return []
    result = df.copy()
    for col in result.columns:
        try:
            result[col] = result[col].apply(
                lambda x: x.isoformat() if hasattr(x, "isoformat") else x
            )
        except Exception:
            pass
    return result.to_dict(orient=orient)


def do_search(ths: THS, keyword: str) -> dict:
    resp = ths.search_symbols(keyword)
    if not resp:
        return {"error": resp.error or "搜索失败"}
    return {"data": resp.data, "total": len(resp.data)}


def do_quote(ths: THS, code: str) -> dict:
    ths_code = to_ths_code(code)
    resp = ths.market_data_cn(ths_code, "汇总")
    if not resp:
        return {"error": resp.error or "行情查询失败"}
    return {"data": serialize_df(resp.df), "ths_code": ths_code}


def do_multi_quote(ths: THS, codes: list) -> dict:
    results = []
    by_market = {}
    for c in codes:
        tc = to_ths_code(c)
        prefix = tc[:4]
        by_market.setdefault(prefix, []).append(tc)
    for market, code_list in by_market.items():
        resp = ths.market_data_cn(code_list, "汇总")
        if resp and resp.df is not None:
            results.extend(serialize_df(resp.df))
    return {"data": results, "total": len(results)}


def do_klines(ths: THS, code: str, freq: str, count: int) -> dict:
    ths_code = to_ths_code(code)
    resp = ths.klines(ths_code, interval=freq, count=count, adjust="forward")
    if not resp or resp.df is None or resp.df.empty:
        return {"error": resp.error if resp else "K线数据为空"}
    return {"data": serialize_df(resp.df), "ths_code": ths_code}


def do_intraday(ths: THS, code: str) -> dict:
    ths_code = to_ths_code(code)
    resp = ths.intraday_data(ths_code)
    if not resp or resp.df is None or resp.df.empty:
        return {"error": resp.error if resp else "分时数据为空"}
    return {"data": serialize_df(resp.df), "ths_code": ths_code}


def do_technical(ths: THS, code: str, freq: str = "day", count: int = 120) -> dict:
    """基于 THS K线数据 + MyTT 计算技术指标"""
    try:
        from MyTT import MA, EMA, MACD, KDJ, RSI, WR, BOLL
    except ImportError:
        return {"error": "请安装 MyTT: pip install MyTT"}

    ths_code = to_ths_code(code)
    resp = ths.klines(ths_code, interval=freq, count=count, adjust="forward")
    if not resp or resp.df is None or resp.df.empty:
        return {"error": resp.error if resp else "K线数据为空"}

    df = resp.df.copy()
    close = df["收盘价"].values.astype(float)
    high = df["最高价"].values.astype(float)
    low = df["最低价"].values.astype(float)
    vol = df["成交量"].values.astype(float)

    df["MA5"] = MA(close, 5)
    df["MA10"] = MA(close, 10)
    df["MA20"] = MA(close, 20)
    df["MA60"] = MA(close, 60)
    dif, dea, macd_val = MACD(close)
    df["MACD_DIF"] = dif
    df["MACD_DEA"] = dea
    df["MACD_BAR"] = macd_val
    k, d, j = KDJ(close, high, low)
    df["KDJ_K"] = k
    df["KDJ_D"] = d
    df["KDJ_J"] = j
    df["RSI"] = RSI(close)
    up, mid, low_b = BOLL(close)
    df["BOLL_UP"] = up
    df["BOLL_MID"] = mid
    df["BOLL_DOWN"] = low_b
    wr1, wr2 = WR(close, high, low)
    df["WR10"] = wr1
    df["WR6"] = wr2

    result = serialize_df(df)
    last = result[-1] if result else {}
    return {
        "data": result,
        "ths_code": ths_code,
        "latest": {
            "price": last.get("收盘价"),
            "ma5": last.get("MA5"),
            "ma10": last.get("MA10"),
            "ma20": last.get("MA20"),
            "ma60": last.get("MA60"),
            "macd_dif": last.get("MACD_DIF"),
            "macd_dea": last.get("MACD_DEA"),
            "macd_bar": last.get("MACD_BAR"),
            "kdj_k": last.get("KDJ_K"),
            "kdj_d": last.get("KDJ_D"),
            "kdj_j": last.get("KDJ_J"),
            "rsi": last.get("RSI"),
        },
    }


def do_industry_list(ths: THS) -> dict:
    resp = ths.ths_industry()
    if not resp:
        return {"error": resp.error or "行业列表获取失败"}
    return {"data": resp.data, "total": resp.extra.get("total_count", len(resp.data))}


def do_industry_rank(ths: THS) -> dict:
    """获取全行业涨跌幅排名 + 主力净流入 + 领涨股

    两步走：
    1. 扩展 → 涨幅、主力净流入、涨速、量比
    2. 基础数据 → 领涨股、上涨家数、下跌家数、板块市值
    合并后按涨幅排序。
    """
    resp = ths.ths_industry()
    if not resp:
        return {"error": resp.error or "行业列表获取失败"}

    industries = []
    for item in resp.data:
        try:
            detail_ext = ths.market_data_block(item["代码"], "扩展")
            detail_base = ths.market_data_block(item["代码"])
            row = {}
            if detail_ext and detail_ext.df is not None and not detail_ext.df.empty:
                row.update(detail_ext.df.iloc[0].to_dict())
            if detail_base and detail_base.df is not None and not detail_base.df.empty:
                row.update(detail_base.df.iloc[0].to_dict())
            row["行业名称"] = item["名称"]
            row["行业代码"] = item["代码"]
            industries.append(row)
        except Exception:
            continue

    industries.sort(key=lambda x: float(x.get("涨幅", 0) or 0), reverse=True)
    return {
        "data": industries,
        "total": len(industries),
        "top_inflow": sorted(
            industries,
            key=lambda x: float(x.get("主力净流入", 0) or 0),
            reverse=True,
        )[:10],
        "top_outflow": sorted(
            industries, key=lambda x: float(x.get("主力净流入", 0) or 0)
        )[:10],
    }


def do_block_constituents(ths: THS, link_code: str) -> dict:
    resp = ths.block_constituents(link_code)
    if not resp:
        return {"error": resp.error or "成分股获取失败"}
    return {"data": resp.data, "total": resp.extra.get("total_count", len(resp.data))}


def do_concept_list(ths: THS) -> dict:
    resp = ths.ths_concept()
    if not resp:
        return {"error": resp.error or "概念板块列表获取失败"}
    return {"data": resp.data, "total": resp.extra.get("total_count", len(resp.data))}


def do_wencai(ths: THS, condition: str) -> dict:
    resp = ths.wencai_nlp(condition)
    if not resp or resp.df is None or resp.df.empty:
        return {"error": resp.error if resp else "问财查询无结果"}
    return {"data": serialize_df(resp.df), "total": len(resp.data)}


def do_news(ths: THS, code: str = None) -> dict:
    resp = ths.news()
    if not resp:
        return {"error": resp.error or "资讯获取失败"}
    return {"data": resp.data, "total": len(resp.data)}


def do_depth(ths: THS, code: str) -> dict:
    ths_code = to_ths_code(code)
    resp = ths.depth(ths_code)
    if not resp or resp.df is None or resp.df.empty:
        return {"error": resp.error if resp else "盘口数据为空"}
    return {"data": serialize_df(resp.df), "ths_code": ths_code}


def do_big_order(ths: THS, code: str) -> dict:
    ths_code = to_ths_code(code)
    resp = ths.big_order_flow(ths_code)
    if not resp or resp.df is None or resp.df.empty:
        return {"error": resp.error if resp else "大单数据为空"}
    return {"data": serialize_df(resp.df), "ths_code": ths_code}


def do_financial(ths: THS, code: str) -> dict:
    """通过 market_data_cn + wencai 获取财务数据"""
    ths_code = to_ths_code(code)
    resp = ths.market_data_cn(ths_code, "汇总")
    if not resp or resp.df is None or resp.df.empty:
        return {"error": resp.error if resp else "行情查询失败"}
    row = resp.df.iloc[0].to_dict()
    name = row.get("名称", "")
    raw_code = code.zfill(6) if len(str(code)) <= 6 else code
    fin_result = {}
    if name:
        wresp = ths.wencai_nlp(f"股票简称 {name}，市盈率，市净率，roe，净利润，营业收入，总市值，流通市值")
        if wresp and wresp.df is not None and not wresp.df.empty:
            fin_result = wresp.df.iloc[0].to_dict()
    return {
        "data": {
            "quote": {k: str(v) for k, v in row.items()},
            "financial": {k: str(v) for k, v in fin_result.items()},
        },
        "ths_code": ths_code,
    }


def main():
    parser = argparse.ArgumentParser(description="THS 数据统一入口")
    parser.add_argument("--search", help="搜索股票名称/代码")
    parser.add_argument("--quote", help="单只实时行情")
    parser.add_argument("--multi-quote", help="多只实时行情，逗号分隔")
    parser.add_argument("--klines", help="K线数据")
    parser.add_argument("--freq", default="day", help="K线周期: 1m/5m/15m/30m/60m/day/week/month")
    parser.add_argument("--count", type=int, default=30, help="K线条数")
    parser.add_argument("--intraday", help="当日分时数据")
    parser.add_argument("--technical", help="技术指标计算（需 MyTT）")
    parser.add_argument("--industry-list", action="store_true", help="行业列表")
    parser.add_argument("--industry-rank", action="store_true", help="行业排名（涨跌幅+主力净流入）")
    parser.add_argument("--block-constituents", help="板块成分股，传入 link_code")
    parser.add_argument("--concept-list", action="store_true", help="概念板块列表")
    parser.add_argument("--wencai", help="问财自然语言查询")
    parser.add_argument("--news", nargs="?", const="", help="实时资讯")
    parser.add_argument("--depth", help="五档盘口")
    parser.add_argument("--big-order", help="大单流向")
    parser.add_argument("--financial", help="财务数据汇总")
    parser.add_argument("--json", action="store_true", default=True, help="JSON 输出（默认）")

    args = parser.parse_args()

    try:
        with THS() as ths:
            if args.search:
                result = do_search(ths, args.search)
            elif args.quote:
                result = do_quote(ths, args.quote)
            elif args.multi_quote:
                codes = [c.strip() for c in args.multi_quote.split(",") if c.strip()]
                result = do_multi_quote(ths, codes)
            elif args.klines:
                result = do_klines(ths, args.klines, args.freq, args.count)
            elif args.intraday:
                result = do_intraday(ths, args.intraday)
            elif args.technical:
                result = do_technical(ths, args.technical, args.freq, args.count)
            elif args.industry_list:
                result = do_industry_list(ths)
            elif args.industry_rank:
                result = do_industry_rank(ths)
            elif args.block_constituents:
                result = do_block_constituents(ths, args.block_constituents)
            elif args.concept_list:
                result = do_concept_list(ths)
            elif args.wencai:
                result = do_wencai(ths, args.wencai)
            elif args.news is not None:
                result = do_news(ths, args.news if args.news else None)
            elif args.depth:
                result = do_depth(ths, args.depth)
            elif args.big_order:
                result = do_big_order(ths, args.big_order)
            elif args.financial:
                result = do_financial(ths, args.financial)
            else:
                result = {"error": "请指定操作参数"}

            print(json.dumps(result, ensure_ascii=False, indent=2, default=str))

    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()