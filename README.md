# 股票战法 - Claude Code 股票分析技能包

基于独门战法的 A 股分析技能，支持二波机会识别、A字杀预警、洗盘/换庄/出货形态判断。

数据源：**同花顺 THS**（thsdk），游客模式免配置。

## 安装

```bash
git clone https://github.com/879825362/stock-warfare.git
bash stock-warfare/install.sh
```

然后重启 Claude Code。

`install.sh` 会自动完成：
- 安装 Python 依赖（thsdk、MyTT、pandas、numpy）
- 将战法命令部署到 `~/.claude/commands/`

## 使用

- **`/个股查询 <股票代码>`** — 按独门战法分析个股，判断进场时机
- **`/今日热门板块`** — 找出当日资金聚焦的板块和领涨股

## 数据能力

| 能力 | 数据来源 |
|------|---------|
| K线（日/周/月/分钟） | thsdk `klines()` |
| 实时行情+换手率+量比+市值 | thsdk `market_data_cn()` |
| 技术指标（MA/MACD/KDJ/RSI/BOLL） | thsdk K线 + MyTT 本地计算 |
| 行业排名+主力净流入+领涨股 | thsdk `market_data_block()` |
| 板块成分股 | thsdk `block_constituents()` |
| 分时走势 | thsdk `intraday_data()` |
| 盘口深度/大单流向 | thsdk `depth()` / `big_order_flow()` |
| 龙虎榜/选股 | thsdk `wencai_nlp()` |
| 集合竞价异动 | thsdk `call_auction_anomaly()` |
| 未来预期/催化剂 | WebSearch |

## 依赖

- Claude Code
- Python 3.9+
- [thsdk](https://pypi.org/project/thsdk/) — 同花顺 SDK（游客模式免账户）

## License

MIT