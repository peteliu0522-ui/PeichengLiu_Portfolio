from __future__ import annotations

import os
import shutil
from pathlib import Path

import fitz
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Peter_Liu_Resume.pdf"
COPY_OUT = Path(r"C:/Users/John/Documents/Codex日报测试/output/pdf/Peter_Liu_Resume_OpenClaw_Console.pdf")
PNG_OUT = Path(r"C:/Users/John/Documents/Codex日报测试/output/pdf/Peter_Liu_Resume_OpenClaw_Console.png")


pdfmetrics.registerFont(TTFont("MSYH", r"C:/Windows/Fonts/msyh.ttc"))
pdfmetrics.registerFont(TTFont("MSYHB", r"C:/Windows/Fonts/msyhbd.ttc"))

W, H = A4
M = 28
LEFT_W = 155
GUTTER = 22
MAIN_X = M + LEFT_W + GUTTER
MAIN_W = W - MAIN_X - M

INK = HexColor("#18212a")
SOFT = HexColor("#4d5b68")
MUTED = HexColor("#788896")
SAGE = HexColor("#6f8a71")
LINE = HexColor("#d9ded8")
BG = HexColor("#f5f2ed")
PAPER = HexColor("#fbfaf7")


def text_width(text: str, font: str, size: float) -> float:
    return pdfmetrics.stringWidth(text, font, size)


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    current = ""
    for char in text:
        if char == " ":
            if current:
                tokens.append(current)
                current = ""
            tokens.append(char)
        elif ord(char) < 128:
            current += char
        else:
            if current:
                tokens.append(current)
                current = ""
            tokens.append(char)
    if current:
        tokens.append(current)
    return tokens


def wrap_text(text: str, font: str, size: float, width: float) -> list[str]:
    lines: list[str] = []
    for para in str(text).split("\n"):
        line = ""
        for token in tokenize(para):
            candidate = line + token
            if text_width(candidate, font, size) <= width:
                line = candidate
                continue
            if line:
                lines.append(line.rstrip())
                line = token.lstrip()
            while text_width(line, font, size) > width and len(line) > 1:
                cut = ""
                rest = line
                for i, char in enumerate(line):
                    if text_width(cut + char, font, size) > width:
                        lines.append(cut.rstrip())
                        rest = line[i:]
                        break
                    cut += char
                line = rest
        if line:
            lines.append(line.rstrip())
    return lines


def draw_text(c: canvas.Canvas, x: float, y: float, text: str, font: str, size: float, color, width: float, leading: float) -> float:
    c.setFont(font, size)
    c.setFillColor(color)
    for line in wrap_text(text, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def heading(c: canvas.Canvas, x: float, y: float, text: str, width: float) -> float:
    c.setFont("MSYHB", 8.6)
    c.setFillColor(SAGE)
    c.drawString(x, y, text.upper())
    c.setStrokeColor(SAGE)
    c.setLineWidth(0.7)
    c.line(x, y - 5, x + width, y - 5)
    return y - 19


def bullet(c: canvas.Canvas, x: float, y: float, text: str, width: float, size: float = 8.1, leading: float = 11.7) -> float:
    c.setFillColor(SAGE)
    c.setFont("MSYHB", size)
    c.drawString(x, y, "•")
    return draw_text(c, x + 10, y, text, "MSYH", size, INK, width - 10, leading)


def build() -> None:
    COPY_OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=A4)
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(PAPER)
    c.rect(M, M, W - 2 * M, H - 2 * M, stroke=0, fill=1)
    c.setFillColor(HexColor("#eef1ec"))
    c.rect(M, M, LEFT_W, H - 2 * M, stroke=0, fill=1)

    c.setFillColor(INK)
    c.setFont("MSYHB", 24)
    c.drawString(MAIN_X, H - 58, "刘沛呈")
    c.setFont("MSYH", 9)
    c.setFillColor(MUTED)
    c.drawString(MAIN_X, H - 74, "PEICHENG (PETER) LIU")
    c.setFont("MSYHB", 11)
    c.setFillColor(SAGE)
    c.drawString(MAIN_X, H - 94, "AI Agent / LLM 应用工程师 · OpenClaw 中控台实践者 · 2025 届")

    lx = M + 16
    ly = H - 62
    c.setFont("MSYHB", 9)
    c.setFillColor(INK)
    c.drawString(lx, ly, "CONTACT")
    ly -= 19
    for label, value in [
        ("EMAIL", "peteliu0522@gmail.com"),
        ("PHONE", "+86 180-9992-8819"),
        ("WECHAT", "PETE6PC"),
        ("PORTFOLIO", "pete6pc.com"),
        ("LOCATION", "上海 / 北京实习"),
    ]:
        c.setFont("MSYHB", 7.2)
        c.setFillColor(SAGE)
        c.drawString(lx, ly, label)
        ly -= 10
        ly = draw_text(c, lx, ly, value, "MSYH", 8.2, INK, LEFT_W - 30, 11.2) - 5

    ly -= 4
    ly = heading(c, lx, ly, "EDUCATION", LEFT_W - 30)
    for title, detail in [
        ("JCU Singapore", "詹姆斯库克大学(新加坡)\n工商管理学士 · 国际商务\nGPA 5.75 / 7.0 · 2024-2025"),
        ("Syracuse University", "雪城大学(美国) · 转学经历"),
        ("Archbishop Ryan HS", "美国费城高中全程\n美国 3 年 + 新加坡 1.5 年"),
    ]:
        c.setFont("MSYHB", 8.4)
        c.setFillColor(INK)
        c.drawString(lx, ly, title)
        ly -= 11
        ly = draw_text(c, lx, ly, detail, "MSYH", 7.5, SOFT, LEFT_W - 30, 10.4) - 5

    ly = heading(c, lx, ly, "TECH STACK", LEFT_W - 30)
    for label, value in [
        ("Agent / 工具", "OpenClaw, Agent Ops\nClaude Code, Cursor"),
        ("前端 / 后端", "React, TypeScript, Express\nNode.js, HTML/CSS/JS"),
        ("数据 / 文件", "SQLite/FTS, JSON, REST API\nPython, PDF/Office tools"),
        ("集成平台", "飞书 Bot, 微信公众号\nTavily Search, Vercel, Git"),
        ("模型 / API", "DeepSeek, Claude, GPT\nGemini, Kimi"),
    ]:
        c.setFont("MSYHB", 7.5)
        c.setFillColor(SAGE)
        c.drawString(lx, ly, label)
        ly -= 9
        ly = draw_text(c, lx, ly, value, "MSYH", 7.15, INK, LEFT_W - 30, 9.6) - 5

    ly = heading(c, lx, ly, "LANGUAGE", LEFT_W - 30)
    draw_text(c, lx, ly, "英语: 工作语言\n中文: 母语", "MSYH", 7.6, INK, LEFT_W - 30, 10.5)

    x = MAIN_X
    y = H - 128
    y = heading(c, x, y, "PROFILE", MAIN_W)
    y = draw_text(
        c,
        x,
        y,
        "2025 届,2025 年 12 月起在北京雅德士实习。围绕风电叶片检测公司的公众号与知识生产场景,独立把「小德」从 AI 内容工作流迭代成可审批、可查库、可排障、可发布的 OpenClaw 中控台。系统把老板近 8 小时人工整理压缩到 30 分钟选题与审核,累计产出 23+ 篇真实公众号文章,并带来公司近年首次央企主动询盘。",
        "MSYH",
        8.4,
        INK,
        MAIN_W,
        12.0,
    )
    y -= 5

    y = heading(c, x, y, "INTERNSHIP", MAIN_W)
    c.setFont("MSYHB", 9.6)
    c.setFillColor(INK)
    c.drawString(x, y, "北京雅德士工程技术咨询服务有限公司")
    c.setFont("MSYH", 8)
    c.setFillColor(MUTED)
    c.drawRightString(x + MAIN_W, y, "2025.12 - 至今")
    y -= 13
    c.setFont("MSYH", 7.9)
    c.setFillColor(SAGE)
    c.drawString(x, y, "实习生 · AI 工作流 / Agent Ops 方向 · 项目代号「小德」")
    y -= 15
    for item in [
        "从 0 到 1 搭建公司公众号 AI 内容生产系统:国际风电资讯搜索、信源评分、选题卡片、改写排版、入库与微信公众号兼容 HTML 产物生成。",
        "设计飞书 Bot + OpenClaw 协作链路:老板 @ 小德触发 Mode A/B,系统返回候选卡片,老板选题后 writer 自动完稿并保存桌面产物。",
        "开发「小德中控台」:React + TypeScript + Express,覆盖总览、内容数据库、工作流控制、小德对话、OpenClaw 运维、发布中心、系统日志 7 个模块。",
        "把生产问题做成系统能力:任务队列、重试/取消/诊断修复、Gateway/RPC/飞书健康检查、假运行检测、日期错乱拦截、字段修复与查重。",
        "解决真实落地坑:DeepSeek 8K 截断、IP 白名单、微信 HTML 白名单、飞书消息长度、重复入库、产物路径追踪与失败发布恢复。",
    ]:
        y = bullet(c, x, y, item, MAIN_W) - 2

    y -= 2
    y = heading(c, x, y, "PROJECT HIGHLIGHTS", MAIN_W)
    for title, desc in [
        ("01 业务规则系统化", "把“信源必须权威、时效不超过窗口、不能编造数据、国际源占比、方向配比、营销词禁用”等要求写成分级评分、黑名单、日期过滤、后处理 check 和 placeholder 机制,降低内容幻觉风险。"),
        ("02 中控台产品化", "把原本分散在命令行、飞书消息和文件夹里的状态收束到一个后台:老板能审批选题和论文,管理员能看任务队列、内容库、发布文件、网络入口和诊断日志。"),
        ("03 真实生产迭代", "v1.0 到 v2.4 共 6 次迭代,每次对应真实问题:从单 Agent 跑通,到 researcher/writer 分工,再到数据库治理、运维面板、失败任务修复和培训手册。"),
    ]:
        c.setFont("MSYHB", 8.6)
        c.setFillColor(INK)
        c.drawString(x, y, title)
        y -= 11
        y = draw_text(c, x, y, desc, "MSYH", 7.85, SOFT, MAIN_W, 11.2) - 5

    strip_y = 98
    c.setFillColor(HexColor("#eef1ec"))
    c.roundRect(x, strip_y, MAIN_W, 58, 5, stroke=0, fill=1)
    metrics = [("87.5%", "效率提升"), ("23+", "真实文章"), ("7", "中控模块"), ("1", "央企询盘")]
    cell = MAIN_W / 4
    for i, (num, label) in enumerate(metrics):
        cx = x + i * cell + 12
        c.setFont("MSYHB", 15)
        c.setFillColor(INK)
        c.drawString(cx, strip_y + 31, num)
        c.setFont("MSYH", 7.4)
        c.setFillColor(SOFT)
        c.drawString(cx, strip_y + 17, label)
        if i:
            c.setStrokeColor(LINE)
            c.line(x + i * cell, strip_y + 11, x + i * cell, strip_y + 47)

    c.setFont("MSYHB", 8.2)
    c.setFillColor(INK)
    c.drawString(x, 74, "其他经历 · 娱乐直播 MCN 机构 内容运营助理(兼职) · 2021")
    draw_text(c, x, 61, "协助多位主播做直播内容策划与排期,监控在线人数、互动率、粉丝增减等数据,形成数据驱动的复盘习惯。", "MSYH", 7.5, SOFT, MAIN_W, 10.5)

    c.setFont("MSYH", 6.8)
    c.setFillColor(MUTED)
    c.drawRightString(W - M, 36, "Portfolio: pete6pc.com · Updated 2026-05-08")

    c.save()
    shutil.copy2(OUT, COPY_OUT)
    pdf = fitz.open(OUT)
    pix = pdf[0].get_pixmap(matrix=fitz.Matrix(1.8, 1.8), alpha=False)
    pix.save(PNG_OUT)
    print(OUT)
    print(COPY_OUT)
    print(PNG_OUT)


if __name__ == "__main__":
    build()
