# 股票战法 - Claude Code 股票分析技能包

基于独门战法的 A 股分析技能，支持二波机会识别、A字杀预警、洗盘/换庄/出货形态判断。

## 安装

```bash
git clone https://github.com/879825362/stock-warfare.git
bash stock-warfare/install.sh
```

然后重启 Claude Code。

`install.sh` 会自动完成：
- 安装数据依赖 [a-share-data](https://github.com/shouldnotappearcalm/a-share-skill)
- 安装 Python 依赖（akshare、MyTT、pandas、numpy、requests）
- 将战法命令部署到 `~/.claude/commands/`

## 使用

- **`/个股查询 <股票代码>`** — 按独门战法分析个股，判断进场时机
- **`/今日热门板块`** — 找出当日资金聚焦的板块和领涨股

## 依赖

- Claude Code
- [a-share-data](https://github.com/shouldnotappearcalm/a-share-skill) — A 股数据获取
- Python 3.9+

## License

MIT