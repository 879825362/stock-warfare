#!/bin/bash
# 股票战法 - 一键安装脚本

set -e

echo "=================================="
echo "  股票战法技能包 安装脚本"
echo "=================================="
echo ""

# 1. 安装 a-share-data（数据依赖）
echo ">>> 检查 a-share-data 数据技能..."
if [ -d "$HOME/.claude/skills/a-share-data" ]; then
    echo "    a-share-data 已安装，跳过"
else
    echo "    正在克隆 a-share-data..."
    TMPDIR=$(mktemp -d)
    git clone https://github.com/shouldnotappearcalm/a-share-skill.git "$TMPDIR/a-share-skill" 2>/dev/null
    mkdir -p "$HOME/.claude/skills"
    cp -R "$TMPDIR/a-share-skill/a-share-data" "$HOME/.claude/skills/"
    rm -rf "$TMPDIR"
    echo "    a-share-data 安装完成"
fi

# 2. 安装 Python 依赖
echo ">>> 检查 Python 依赖..."
pip install akshare MyTT pandas numpy requests 2>/dev/null
echo "    Python 依赖安装完成"

# 3. 安装战法命令
echo ">>> 安装战法命令..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.claude/commands"

# 如果用户在项目级别用 Claude Code，也装一份到当前目录
if [ -n "$CLAUDE_PROJECT_DIR" ]; then
    mkdir -p "$CLAUDE_PROJECT_DIR/.claude/commands"
    cp "$SCRIPT_DIR/commands/"*.md "$CLAUDE_PROJECT_DIR/.claude/commands/"
    echo "    已安装到项目: $CLAUDE_PROJECT_DIR/.claude/commands/"
fi

cp "$SCRIPT_DIR/commands/"*.md "$HOME/.claude/commands/"
echo "    已安装到全局: ~/.claude/commands/"

echo ""
echo "=================================="
echo "  安装完成！"
echo "  重启 Claude Code 生效"
echo "=================================="
echo ""
echo "使用方法："
echo "  /个股查询 600519"
echo "  /今日热门板块"