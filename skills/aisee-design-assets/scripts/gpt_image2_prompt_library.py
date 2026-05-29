#!/usr/bin/env python3
"""Build and query the built-in GPT Image 2 Chinese prompt library.

The library keeps only Chinese-language prompt entries. It does not translate
non-Chinese prompts into Chinese.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape
from xml.etree import ElementTree as ET
from typing import Iterable


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
LIB_ROOT = SKILL_ROOT / "prompt-library" / "gpt-image-2"
CATALOG_DIR = LIB_ROOT / "catalogs"
RAW_DIR = LIB_ROOT / "raw-index"

YOUMIND_README_ZH = "https://raw.githubusercontent.com/YouMind-OpenLab/awesome-gpt-image-2/main/README_zh.md"
YOUMIND_PROMPTS_SITEMAP = "https://youmind.com/sitemaps/prompts/sitemap.xml"
YOUMIND_REPO = "https://github.com/YouMind-OpenLab/awesome-gpt-image-2"
YOUMIND_LICENSE = "CC BY 4.0"
YOUMIND_LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"

EVOLINK_CASES_API = "https://api.github.com/repos/EvoLinkAI/awesome-gpt-image-2-API-and-Prompts/contents/cases?ref=main"
EVOLINK_REPO = "https://github.com/EvoLinkAI/awesome-gpt-image-2-API-and-Prompts"
EVOLINK_LICENSE = "CC0 1.0"
EVOLINK_LICENSE_URL = "https://creativecommons.org/publicdomain/zero/1.0/"

MIN_CJK_RATIO = 0.08
MIN_CJK_CHARS = 12

INTENT_PROFILES = {
    "ui": ["ui", "界面", "网页", "移动端", "app", "设计系统", "截图", "控件", "社交媒体"],
    "poster": ["海报", "poster", "封面", "flyer", "广告", "宣传", "主视觉"],
    "ecommerce": ["电商", "商品", "产品", "主图", "卖点", "详情页", "直播"],
    "infographic": ["信息图", "图解", "拆解", "流程", "时间轴", "diagram", "chart"],
    "character": ["角色", "人物", "头像", "肖像", "设定", "三视图", "表情"],
    "social": ["小红书", "抖音", "视频号", "社交", "朋友圈", "帖子", "截图"],
    "asset": ["素材", "图标", "背景", "插画", "游戏", "贴纸", "卡牌"],
    "style": ["风格", "复古", "水彩", "像素", "赛博", "电影感", "3d", "手绘"],
}


@dataclass
class PromptRecord:
    id: str
    source_project: str
    source_file: str
    source_url: str
    license: str
    license_url: str
    title: str
    category: str
    original_language: str
    prompt_language: str
    author: str
    author_url: str
    original_post_url: str
    published_at: str
    preview_image_url: str
    try_url: str
    prompt_text: str
    prompt_hash: str
    cjk_ratio: float
    variables: str
    tags: str
    risk_notes: str
    attribution_text: str


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "aisee-design-assets-prompt-library"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


def fetch_web_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 aisee-design-assets"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


def fetch_json(url: str) -> object:
    return json.loads(fetch_text(url))


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def decode_js_string(value: str) -> str:
    decoded = value
    for _ in range(3):
        try:
            next_decoded = json.loads(f'"{decoded}"')
        except json.JSONDecodeError:
            break
        if next_decoded == decoded:
            break
        decoded = next_decoded
    return decoded.replace(r"\"", '"').replace(r"\n", "\n")


def strip_markdown_link(value: str) -> tuple[str, str]:
    match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", value)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return re.sub(r"[*_`]", "", value).strip(), ""


def extract_first_code_block(text: str) -> str:
    code = re.search(r"```(?:[a-zA-Z0-9_-]+)?\n(.*?)\n```", text, re.S)
    return code.group(1).strip() if code else ""


def cjk_stats(text: str) -> tuple[int, float]:
    visible = [ch for ch in text if not ch.isspace()]
    if not visible:
        return 0, 0.0
    cjk = sum(1 for ch in visible if "\u4e00" <= ch <= "\u9fff")
    return cjk, cjk / len(visible)


def has_non_chinese_script(text: str) -> bool:
    return bool(re.search(r"[\u3040-\u30ff\uac00-\ud7af]", text))


def is_chinese_prompt(prompt: str) -> bool:
    count, ratio = cjk_stats(prompt)
    return count >= MIN_CJK_CHARS and ratio >= MIN_CJK_RATIO and not has_non_chinese_script(prompt)


def prompt_hash(prompt: str) -> str:
    normalized = re.sub(r"\s+", " ", prompt).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def extract_variables(prompt: str) -> str:
    names = re.findall(r'\{argument name="([^"]+)"', prompt)
    names.extend(re.findall(r"\[([a-zA-Z][a-zA-Z0-9 _-]{1,48})\]", prompt))
    names.extend(re.findall(r"（这里?[^）]{1,40}）", prompt))
    unique = []
    for name in names:
        clean = normalize_text(name)
        if clean and clean not in unique:
            unique.append(clean)
    return "; ".join(unique)


def infer_tags(title: str, category: str, prompt: str) -> str:
    text = f"{title}\n{category}\n{prompt}".lower()
    tags = []
    for intent, keywords in INTENT_PROFILES.items():
        if any(keyword.lower() in text for keyword in keywords):
            tags.append(intent)
    return "; ".join(tags)


def detect_risks(prompt: str, title: str) -> str:
    text = f"{title}\n{prompt}".lower()
    risks = []
    brand_terms = [
        "meta quest",
        "spacex",
        "apple",
        "iphone",
        "gta",
        "persona",
        "evangelion",
        "皮克斯",
        "圣斗士",
        "新世纪福音战士",
        "刘亦菲",
        "小红书",
        "抖音",
    ]
    public_figure_terms = ["elon musk", "tim cook", "特朗普", "川普", "拜登", "马斯克"]
    if any(term.lower() in text for term in brand_terms):
        risks.append("可能包含品牌/IP引用")
    if any(term.lower() in text for term in public_figure_terms):
        risks.append("可能包含公众人物/肖像引用")
    if "logo" in text or "水印" in text:
        risks.append("可能涉及Logo/标识")
    return "; ".join(risks)


def parse_detail_line(block: str, label: str) -> tuple[str, str]:
    match = re.search(rf"- \*\*{re.escape(label)}:\*\* (.+)", block)
    if not match:
        return "", ""
    return strip_markdown_link(match.group(1))


def parse_youmind_zh() -> tuple[list[PromptRecord], list[dict]]:
    """Parse YouMind zh README, but keep only entries marked as original zh."""
    text = fetch_text(YOUMIND_README_ZH)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / "youmind-readme-zh.md").write_text(text, encoding="utf-8")

    records: list[PromptRecord] = []
    excluded: list[dict] = []
    blocks = re.split(r"(?=^### No\. \d+: )", text, flags=re.M)
    for block in blocks:
        heading = re.match(r"^### No\. (\d+): (.+)$", block, flags=re.M)
        if not heading:
            continue
        number = heading.group(1)
        full_title = heading.group(2).strip()
        category, title = ("精选提示词", full_title)
        if " - " in full_title:
            category, title = full_title.split(" - ", 1)

        language_badge = re.search(r"!\[Language-([A-Z-]+)\]", block)
        detail_language, _ = parse_detail_line(block, "多语言")
        original_language = (detail_language or (language_badge.group(1).lower() if language_badge else "")).lower()
        if original_language != "zh":
            continue

        prompt_marker = block.find("#### 📝 提示词")
        prompt = extract_first_code_block(block[prompt_marker:] if prompt_marker >= 0 else block)
        if not prompt:
            continue

        cjk_count, ratio = cjk_stats(prompt)
        if not is_chinese_prompt(prompt):
            excluded.append(
                {
                    "source_project": "YouMind-OpenLab/awesome-gpt-image-2",
                    "source_file": "README_zh.md",
                    "source_item": f"No. {number}",
                    "title": title,
                    "original_language": original_language,
                    "cjk_chars": cjk_count,
                    "cjk_ratio": round(ratio, 4),
                    "reason": "元数据为中文但正文中文比例不足",
                }
            )
            continue

        author, author_url = parse_detail_line(block, "作者")
        _, original_post_url = parse_detail_line(block, "来源")
        published_at, _ = parse_detail_line(block, "发布时间")
        preview = ""
        image_match = re.search(r'<img src="([^"]+)"', block)
        if image_match:
            preview = image_match.group(1)
        try_url = ""
        try_match = re.search(r"\*\*\[👉 .*?\]\((https://youmind\.com/[^)]+)\)\*\*", block)
        if try_match:
            try_url = try_match.group(1)

        hash_value = prompt_hash(prompt)
        source_url = try_url or f"{YOUMIND_REPO}/blob/main/README_zh.md"
        records.append(
            PromptRecord(
                id=f"youmind-zh-{number.zfill(5)}-{hash_value[:8]}",
                source_project="YouMind-OpenLab/awesome-gpt-image-2",
                source_file="README_zh.md",
                source_url=source_url,
                license=YOUMIND_LICENSE,
                license_url=YOUMIND_LICENSE_URL,
                title=title,
                category=category,
                original_language="zh",
                prompt_language="zh",
                author=author,
                author_url=author_url,
                original_post_url=original_post_url,
                published_at=published_at,
                preview_image_url=preview,
                try_url=try_url,
                prompt_text=prompt,
                prompt_hash=hash_value,
                cjk_ratio=round(ratio, 4),
                variables=extract_variables(prompt),
                tags=infer_tags(title, category, prompt),
                risk_notes=detect_risks(prompt, title),
                attribution_text=f"{title} - {author or 'unknown'} - {YOUMIND_LICENSE} - {source_url}",
            )
        )
    return records, excluded


def discover_youmind_prompt_urls(limit: int = 0) -> list[str]:
    cache_path = RAW_DIR / "youmind-sitemap-zh-cn-urls.jsonl"
    try:
        xml = fetch_web_text(YOUMIND_PROMPTS_SITEMAP)
        urls = re.findall(r"<loc>(https://youmind\.com/zh-CN/prompts/[^<]+)</loc>", xml)
    except Exception:
        if not cache_path.exists():
            raise
        urls = [json.loads(line)["url"] for line in cache_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    seen = set()
    unique = []
    for url in urls:
        slug = url.rsplit("/", 1)[-1]
        prompt_id = slug.rsplit("-", 1)[-1]
        if prompt_id in seen:
            continue
        seen.add(prompt_id)
        unique.append(url)
        if limit and len(unique) >= limit:
            break
    return unique


def parse_youmind_detail_url(url: str) -> tuple[PromptRecord | None, dict | None]:
    slug = url.rsplit("/", 1)[-1]
    prompt_id = slug.rsplit("-", 1)[-1]
    try:
        text = fetch_web_text(url)
    except Exception as exc:
        return None, {
            "source_project": "YouMind web detail",
            "source_file": "sitemap detail",
            "source_item": prompt_id,
            "title": slug,
            "original_language": "",
            "cjk_chars": 0,
            "cjk_ratio": 0,
            "reason": f"详情页抓取失败: {exc}",
        }

    prompt_match = re.search(
        rf'\{{\\"content\\":\\"(.*?)\\",\\"promptId\\":{re.escape(prompt_id)},\\"collection\\":\\"prompts\\",\\"translatedContent\\":',
        text,
        re.S,
    )
    language_match = re.search(
        rf'\\"promptId\\":{re.escape(prompt_id)}.*?\\"originalLanguage\\":\\"([^\\"]+)\\"',
        text,
        re.S,
    )
    if not prompt_match:
        return None, {
            "source_project": "YouMind web detail",
            "source_file": "sitemap detail",
            "source_item": prompt_id,
            "title": slug,
            "original_language": language_match.group(1) if language_match else "",
            "cjk_chars": 0,
            "cjk_ratio": 0,
            "reason": "详情页未解析到原始 content",
        }

    prompt = decode_js_string(prompt_match.group(1)).strip()
    original_language = language_match.group(1) if language_match else ""
    cjk_count, ratio = cjk_stats(prompt)
    title = slug
    title_match = re.search(r"<title>(.*?) - GPT Image 2 AI Prompt(?: for ([^|<]+))? \| YouMind</title>", text)
    category = "YouMind detail"
    if title_match:
        title = title_match.group(1).strip()
        if title_match.group(2):
            category = title_match.group(2).strip()
    media = ""
    media_match = re.search(r'\\"images\\":\[\\"([^\\"]+)\\"', text)
    if media_match:
        media = decode_js_string(media_match.group(1))
    source_link = ""
    source_match = re.search(r'\\"sourceLink\\":\\"([^\\"]+)\\"', text)
    if source_match:
        source_link = decode_js_string(source_match.group(1))
    author = ""
    author_url = ""
    author_match = re.search(r'\\"author\\":\{\\"name\\":\\"([^\\"]*)\\",\\"link\\":\\"([^\\"]*)\\"\}', text)
    if author_match:
        author = decode_js_string(author_match.group(1))
        author_url = decode_js_string(author_match.group(2))
    published_at = ""
    published_match = re.search(r'\\"sourcePublishedAt\\":\\"([^\\"]+)\\"', text)
    if published_match:
        published_at = published_match.group(1)

    if original_language != "zh" or not is_chinese_prompt(prompt):
        return None, {
            "source_project": "YouMind web detail",
            "source_file": "sitemap detail",
            "source_item": prompt_id,
            "title": title,
            "original_language": original_language,
            "cjk_chars": cjk_count,
            "cjk_ratio": round(ratio, 4),
            "reason": "详情页原始语言不是中文或正文中文比例不足",
        }

    hash_value = prompt_hash(prompt)
    return PromptRecord(
        id=f"youmind-detail-zh-{prompt_id}-{hash_value[:8]}",
        source_project="YouMind web detail",
        source_file="sitemap detail",
        source_url=url,
        license=YOUMIND_LICENSE,
        license_url=YOUMIND_LICENSE_URL,
        title=title,
        category=category,
        original_language="zh",
        prompt_language="zh",
        author=author,
        author_url=author_url,
        original_post_url=source_link,
        published_at=published_at,
        preview_image_url=media,
        try_url=url,
        prompt_text=prompt,
        prompt_hash=hash_value,
        cjk_ratio=round(ratio, 4),
        variables=extract_variables(prompt),
        tags=infer_tags(title, category, prompt),
        risk_notes=detect_risks(prompt, title),
        attribution_text=f"{title} - {author or 'unknown'} - {YOUMIND_LICENSE} - {url}",
    ), None


def parse_youmind_details(limit: int = 0, workers: int = 4) -> tuple[list[PromptRecord], list[dict]]:
    urls = discover_youmind_prompt_urls(limit)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl(RAW_DIR / "youmind-sitemap-zh-cn-urls.jsonl", ({"url": url} for url in urls))
    records: list[PromptRecord] = []
    excluded: list[dict] = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        future_map = {executor.submit(parse_youmind_detail_url, url): url for url in urls}
        for future in as_completed(future_map):
            record, exclusion = future.result()
            if record:
                records.append(record)
            if exclusion:
                excluded.append(exclusion)
    records.sort(key=lambda item: item.id)
    excluded.sort(key=lambda item: (item.get("reason", ""), item.get("source_item", "")))
    return records, excluded


def evolink_case_files() -> list[dict]:
    items = fetch_json(EVOLINK_CASES_API)
    if not isinstance(items, list):
        return []
    # Use the canonical markdown files. Prompt bodies are not translated there;
    # Chinese prompts remain Chinese and non-Chinese prompts remain non-Chinese.
    localized_suffixes = ("_de.md", "_es.md", "_fr.md", "_ja.md", "_ko.md", "_pt.md", "_ru.md", "_tr.md", "_zh-CN.md", "_zh-TW.md")
    return [
        item
        for item in items
        if isinstance(item, dict)
        and item.get("type") == "file"
        and str(item.get("name", "")).endswith(".md")
        and not str(item.get("name", "")).endswith(localized_suffixes)
    ]


def parse_evolink() -> tuple[list[PromptRecord], list[dict]]:
    records: list[PromptRecord] = []
    excluded: list[dict] = []
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for item in evolink_case_files():
        name = item["name"]
        url = item["download_url"]
        text = fetch_text(url)
        (RAW_DIR / name).write_text(text, encoding="utf-8")
        category = name.removesuffix(".md")
        blocks = re.split(r"(?=^### Case \d+: )", text, flags=re.M)
        for block in blocks:
            heading = re.match(r"^### Case (\d+): \[([^\]]+)\]\(([^)]+)\)(?: \(by \[([^\]]+)\]\(([^)]+)\)\))?", block, flags=re.M)
            if not heading:
                continue
            case_no = heading.group(1)
            title = heading.group(2).strip()
            original_post_url = heading.group(3).strip()
            author = (heading.group(4) or "").strip()
            author_url = (heading.group(5) or "").strip()
            marker = block.find("**Prompt:**")
            prompt = extract_first_code_block(block[marker:] if marker >= 0 else block)
            if not prompt:
                continue
            cjk_count, ratio = cjk_stats(prompt)
            if not is_chinese_prompt(prompt):
                excluded.append(
                    {
                        "source_project": "EvoLinkAI/awesome-gpt-image-2-API-and-Prompts",
                        "source_file": f"cases/{name}",
                        "source_item": f"Case {case_no}",
                        "title": title,
                        "original_language": "unknown",
                        "cjk_chars": cjk_count,
                        "cjk_ratio": round(ratio, 4),
                        "reason": "prompt正文不是中文或中文比例不足",
                    }
                )
                continue
            preview = ""
            image_match = re.search(r'<img src="([^"]+)"', block)
            if image_match:
                preview = image_match.group(1)
            hash_value = prompt_hash(prompt)
            source_url = item.get("html_url", url)
            records.append(
                PromptRecord(
                    id=f"evolink-{category}-zh-{case_no.zfill(3)}-{hash_value[:8]}",
                    source_project="EvoLinkAI/awesome-gpt-image-2-API-and-Prompts",
                    source_file=f"cases/{name}",
                    source_url=source_url,
                    license=EVOLINK_LICENSE,
                    license_url=EVOLINK_LICENSE_URL,
                    title=title,
                    category=category,
                    original_language="zh",
                    prompt_language="zh",
                    author=author,
                    author_url=author_url,
                    original_post_url=original_post_url,
                    published_at="",
                    preview_image_url=preview,
                    try_url="",
                    prompt_text=prompt,
                    prompt_hash=hash_value,
                    cjk_ratio=round(ratio, 4),
                    variables=extract_variables(prompt),
                    tags=infer_tags(title, category, prompt),
                    risk_notes=detect_risks(prompt, title),
                    attribution_text=f"{title} - {author or 'unknown'} - {EVOLINK_LICENSE} - {source_url}",
                )
            )
    return records, excluded


def dedupe(records: Iterable[PromptRecord]) -> tuple[list[PromptRecord], list[dict]]:
    kept: list[PromptRecord] = []
    seen: dict[str, PromptRecord] = {}
    duplicates: list[dict] = []
    for record in records:
        if record.prompt_hash in seen:
            duplicates.append(
                {
                    "id": record.id,
                    "duplicate_of": seen[record.prompt_hash].id,
                    "title": record.title,
                    "source_project": record.source_project,
                    "source_file": record.source_file,
                    "prompt_hash": record.prompt_hash,
                    "reason": "prompt_hash重复",
                }
            )
            continue
        seen[record.prompt_hash] = record
        kept.append(record)
    return kept, duplicates


def write_jsonl(path: Path, rows: Iterable[object]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def catalog_row(record: PromptRecord) -> dict[str, str]:
    return {
        "来源": record.source_project,
        "分类": record.category,
        "标题": record.title,
        "详细提示词": record.prompt_text,
        "来源链接": record.source_url,
        "许可证": record.license,
        "风险备注": record.risk_notes,
    }


def write_csv(path: Path, rows: list[PromptRecord]) -> None:
    fields = ["来源", "分类", "标题", "详细提示词", "来源链接", "许可证", "风险备注"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(catalog_row(row))


def column_name(index: int) -> str:
    name = ""
    index += 1
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def write_xlsx(path: Path, rows: list[PromptRecord]) -> None:
    fields = ["来源", "分类", "标题", "详细提示词", "来源链接", "许可证", "风险备注"]
    table = [fields] + [[catalog_row(row)[field] for field in fields] for row in rows]
    sheet_rows = []
    for r_idx, row in enumerate(table, start=1):
        cells = []
        for c_idx, value in enumerate(row):
            ref = f"{column_name(c_idx)}{r_idx}"
            safe = escape(str(value), {'"': "&quot;"})
            cells.append(f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{safe}</t></is></c>')
        sheet_rows.append(f'<row r="{r_idx}">{"".join(cells)}</row>')
    widths = [24, 18, 36, 96, 48, 14, 36]
    cols = "".join(f'<col min="{i}" max="{i}" width="{width}" customWidth="1"/>' for i, width in enumerate(widths, start=1))
    sheet_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>
  <cols>{cols}</cols>
  <sheetData>{"".join(sheet_rows)}</sheetData>
</worksheet>'''
    workbook_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="中文提示词" sheetId="1" r:id="rId1"/></sheets>
</workbook>'''
    rels_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>'''
    workbook_rels_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>'''
    content_types_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>'''
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", rels_xml)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def read_xlsx_rows(path: Path) -> list[dict[str, str]]:
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as zf:
        sheet_xml = zf.read("xl/worksheets/sheet1.xml")
    root = ET.fromstring(sheet_xml)
    rows: list[list[str]] = []
    for row in root.findall(".//x:sheetData/x:row", ns):
        values = []
        for cell in row.findall("x:c", ns):
            text = cell.find("x:is/x:t", ns)
            values.append(text.text if text is not None and text.text is not None else "")
        rows.append(values)
    if not rows:
        return []
    headers = rows[0]
    return [dict(zip(headers, row)) for row in rows[1:]]


def score_excel_row(row: dict[str, str], query: str) -> int:
    text = "\n".join(str(row.get(key, "")) for key in ("来源", "分类", "标题", "详细提示词", "风险备注")).lower()
    score = 0
    for token in re.split(r"\s+", query.strip().lower()):
        if token and token in text:
            score += 2
    if not row.get("风险备注"):
        score += 1
    return score


def read_excel_catalog(args: argparse.Namespace) -> int:
    path = Path(args.path) if args.path else CATALOG_DIR / "prompts.xlsx"
    if not path.exists():
        raise SystemExit(f"Excel catalog not found: {path}. Run `build` or `repair-local` first.")

    rows = read_xlsx_rows(path)
    if args.source:
        rows = [row for row in rows if args.source.lower() in row.get("来源", "").lower()]
    if args.category:
        rows = [row for row in rows if args.category.lower() in row.get("分类", "").lower()]
    if args.no_risk:
        rows = [row for row in rows if not row.get("风险备注")]
    if args.query:
        rows = [row for row in rows if score_excel_row(row, args.query) > 0]
        rows.sort(key=lambda row: score_excel_row(row, args.query), reverse=True)

    rows = rows[: args.limit]
    if args.format == "json":
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0

    for idx, row in enumerate(rows, 1):
        print(f"## {idx}. {row.get('标题', '')}")
        print(f"- 来源: {row.get('来源', '')}")
        print(f"- 分类: {row.get('分类', '')}")
        print(f"- 来源链接: {row.get('来源链接', '')}")
        print(f"- 许可证: {row.get('许可证', '')}")
        if row.get("风险备注"):
            print(f"- 风险: {row.get('风险备注', '')}")
        print("")
        print("```")
        print(row.get("详细提示词", ""))
        print("```")
        print("")
    return 0


def write_sources_md(records: list[PromptRecord], excluded: list[dict], duplicates: list[dict], youmind_source: str) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    by_source: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for record in records:
        by_source[record.source_project] = by_source.get(record.source_project, 0) + 1
        by_category[record.category] = by_category.get(record.category, 0) + 1
    lines = [
        "# GPT Image 2 中文原始提示词库",
        "",
        f"- 更新时间：{now}",
        f"- 主库条目：{len(records)}",
        f"- 中文筛选：只保留原始语言为中文或 prompt 正文本身为中文的条目；不翻译非中文 prompt。",
        f"- YouMind 抓取模式：{youmind_source}",
        "- 完整性：当前 catalog 是离线库；使用 sitemap detail 模式时覆盖公开 sitemap 可发现的 YouMind detail 页，不等同于授权 CMS 全量。",
        f"- 已排除非中文/低中文比例条目：{len(excluded)}",
        f"- 已排除重复条目：{len(duplicates)}",
        "",
        "## 来源",
        "",
        f"- YouMind-OpenLab/awesome-gpt-image-2：{YOUMIND_REPO}，许可证 {YOUMIND_LICENSE}；README 模式仅保留元数据 `多语言: zh` 的条目，README 不是全量来源。",
        f"- EvoLinkAI/awesome-gpt-image-2-API-and-Prompts：{EVOLINK_REPO}，许可证 {EVOLINK_LICENSE}，从 canonical cases 中保留中文 prompt 正文。",
        f"- YouMind prompts sitemap：{YOUMIND_PROMPTS_SITEMAP}，用于发现网页图库候选 detail URL；detail 页可解析原始语言，但全量抓取需节流并遵守站点 robots。",
        "",
        "## 输出文件",
        "",
        "- `catalogs/prompts.jsonl`：skill 脚本按意图检索的主数据。",
        "- `catalogs/prompts.csv`：精简字段表格，便于外部表格工具使用。",
        "- `catalogs/prompts.xlsx`：精简字段 Excel，列为来源、分类、标题、详细提示词、来源链接、许可证、风险备注。",
        "- `catalogs/excluded.jsonl`：因非中文、低中文比例或重复被排除的条目。",
        "- `raw-index/`：导入时读取的原始 Markdown 快照。",
        "",
        "## 来源统计",
        "",
        "| 来源 | 条目数 |",
        "|------|--------|",
    ]
    for source, count in sorted(by_source.items()):
        lines.append(f"| {source} | {count} |")
    lines.extend(["", "## 分类统计", "", "| 分类 | 条目数 |", "|------|--------|"])
    for category, count in sorted(by_category.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {category} | {count} |")
    lines.extend(
        [
            "",
            "## 使用约束",
            "",
            "- 不把非中文 prompt 翻译后入库。",
            "- 使用当前离线库时注意来源模式；如果需要 YouMind CMS 真正全量，需接入授权 CMS API。",
            "- CC BY 4.0 来源在复用、改写或对外分发时必须保留署名、来源链接和许可证链接。",
            "- `risk_notes` 标记品牌、IP、公众人物或 Logo 风险；这些条目不应默认用于商用生成。",
            "- 预览图片只保存 URL，不复制图片文件；如需图片资产，应单独确认授权和用途。",
            "",
        ]
    )
    (LIB_ROOT / "sources.md").write_text("\n".join(lines), encoding="utf-8")


def build_catalog(args: argparse.Namespace) -> int:
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if args.youmind_source == "sitemap":
        youmind_records, youmind_excluded = parse_youmind_details(args.youmind_limit, args.youmind_workers)
    elif args.youmind_source == "readme":
        youmind_records, youmind_excluded = parse_youmind_zh()
    else:
        youmind_records, youmind_excluded = [], []
    evolink_records, evolink_excluded = parse_evolink()
    records, duplicates = dedupe([*youmind_records, *evolink_records])
    excluded = [*youmind_excluded, *evolink_excluded, *duplicates]
    records.sort(key=lambda item: (item.source_project, item.category, item.title, item.id))
    write_jsonl(CATALOG_DIR / "prompts.jsonl", (asdict(row) for row in records))
    write_csv(CATALOG_DIR / "prompts.csv", records)
    write_xlsx(CATALOG_DIR / "prompts.xlsx", records)
    write_jsonl(CATALOG_DIR / "excluded.jsonl", excluded)
    write_sources_md(records, excluded, duplicates, args.youmind_source)
    source_counts: dict[str, int] = {}
    for record in records:
        source_counts[record.source_project] = source_counts.get(record.source_project, 0) + 1
    summary = {
        "records": len(records),
        "excluded": len(excluded),
        "duplicates": len(duplicates),
        "pre_dedupe": {
            "youmind_kept": len(youmind_records),
            "evolink_kept": len(evolink_records),
        },
        "source_counts": source_counts,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": "keep only Chinese-language prompt entries; do not translate non-Chinese prompts",
        "youmind_source": args.youmind_source,
        "youmind_limit": args.youmind_limit,
        "completeness": "offline catalog; sitemap mode covers public sitemap detail pages, not authorized CMS full export",
    }
    (CATALOG_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def load_records() -> list[dict]:
    path = CATALOG_DIR / "prompts.jsonl"
    if not path.exists():
        raise SystemExit(f"Prompt catalog not found: {path}. Run `build` first.")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def score_record(record: dict, query: str, intent: str) -> int:
    text = "\n".join(
        str(record.get(key, ""))
        for key in ("title", "category", "tags", "variables", "risk_notes", "prompt_text")
    ).lower()
    score = 0
    if intent:
        for keyword in INTENT_PROFILES.get(intent, [intent]):
            if keyword.lower() in text:
                score += 4
    for token in re.split(r"\s+", query.strip().lower()):
        if token and token in text:
            score += 2
    if not record.get("risk_notes"):
        score += 1
    return score


def search_catalog(args: argparse.Namespace) -> int:
    records = load_records()
    if args.intent:
        records = [row for row in records if score_record(row, "", args.intent) > 0]
    if args.category:
        records = [row for row in records if args.category.lower() in row.get("category", "").lower()]
    if args.no_risk:
        records = [row for row in records if not row.get("risk_notes")]
    if args.query:
        records = [row for row in records if score_record(row, args.query, "") > 0]
    records.sort(key=lambda row: score_record(row, args.query or "", args.intent or ""), reverse=True)
    records = records[: args.limit]
    if args.format == "json":
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return 0
    for idx, row in enumerate(records, 1):
        print(f"## {idx}. {row['title']}")
        print(f"- ID: {row['id']}")
        print(f"- 分类: {row['category']}")
        print(f"- 标签: {row.get('tags', '')}")
        print(f"- 来源: {row['source_project']} / {row['source_url']}")
        print(f"- 许可证: {row['license']}")
        if row.get("risk_notes"):
            print(f"- 风险: {row['risk_notes']}")
        if row.get("variables"):
            print(f"- 变量: {row['variables']}")
        print("")
        print("```")
        print(row["prompt_text"])
        print("```")
        print("")
    return 0


def list_categories(_: argparse.Namespace) -> int:
    records = load_records()
    counts: dict[str, int] = {}
    for row in records:
        counts[row["category"]] = counts.get(row["category"], 0) + 1
    for category, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"{count}\t{category}")
    return 0


def repair_local_catalog(_: argparse.Namespace) -> int:
    records = []
    dropped = []
    for row in load_records():
        row["prompt_text"] = decode_js_string(row["prompt_text"])
        cjk_count, ratio = cjk_stats(row["prompt_text"])
        if not is_chinese_prompt(row["prompt_text"]):
            dropped.append(
                {
                    "source_project": row.get("source_project", ""),
                    "source_file": row.get("source_file", ""),
                    "source_item": row.get("id", ""),
                    "title": row.get("title", ""),
                    "original_language": row.get("original_language", ""),
                    "cjk_chars": cjk_count,
                    "cjk_ratio": round(ratio, 4),
                    "reason": "本地修复时排除：正文含日文假名/韩文或中文比例不足",
                }
            )
            continue
        row["prompt_hash"] = prompt_hash(row["prompt_text"])
        row["variables"] = extract_variables(row["prompt_text"])
        row["tags"] = infer_tags(row["title"], row["category"], row["prompt_text"])
        row["risk_notes"] = detect_risks(row["prompt_text"], row["title"])
        records.append(PromptRecord(**row))
    records, duplicates = dedupe(records)
    existing_excluded = []
    excluded_path = CATALOG_DIR / "excluded.jsonl"
    if excluded_path.exists():
        existing_excluded = [json.loads(line) for line in excluded_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    write_jsonl(CATALOG_DIR / "prompts.jsonl", (asdict(row) for row in records))
    write_csv(CATALOG_DIR / "prompts.csv", records)
    write_xlsx(CATALOG_DIR / "prompts.xlsx", records)
    write_jsonl(excluded_path, [*existing_excluded, *dropped, *duplicates])
    source_counts: dict[str, int] = {}
    for record in records:
        source_counts[record.source_project] = source_counts.get(record.source_project, 0) + 1
    summary = {
        "records": len(records),
        "excluded": len(existing_excluded) + len(dropped) + len(duplicates),
        "duplicates": len(duplicates),
        "source_counts": source_counts,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": "keep only Chinese-language prompt entries; reject Japanese kana and Korean Hangul; do not translate non-Chinese prompts",
        "youmind_source": "sitemap",
        "completeness": "offline catalog; sitemap mode covers public sitemap detail pages, not authorized CMS full export",
    }
    (CATALOG_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_sources_md(records, [*existing_excluded, *dropped, *duplicates], duplicates, "sitemap")
    print(json.dumps({"records": len(records), "dropped_during_repair": len(dropped), "deduped_during_repair": len(duplicates)}, ensure_ascii=False, indent=2))
    return 0


def discover_youmindsitemap(args: argparse.Namespace) -> int:
    xml = fetch_web_text(YOUMIND_PROMPTS_SITEMAP)
    urls = re.findall(r"<loc>(.*?)</loc>", xml)
    localized_prefixes = "zh-CN|zh-TW|ja-JP|ko-KR|th-TH|vi-VN|hi-IN|es-ES|es-419|de-DE|fr-FR|it-IT|pt-BR|pt-PT|tr-TR"
    unique: dict[str, dict] = {}
    for url in urls:
        match = re.search(rf"/(?:({localized_prefixes})/)?prompts/([^/<]+)$", url)
        if not match:
            continue
        locale = match.group(1) or "en"
        slug = match.group(2)
        if slug not in unique:
            unique[slug] = {"slug": slug, "urls": {}}
        unique[slug]["urls"][locale] = url

    rows = list(unique.values())
    rows.sort(key=lambda item: item["slug"])
    returned = rows[: args.limit] if args.limit else rows

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        write_jsonl(out, returned)

    print(json.dumps(
        {
            "sitemap": YOUMIND_PROMPTS_SITEMAP,
            "unique_prompts": len(unique),
            "returned": len(returned),
            "output": args.output or "",
            "note": "Use detail pages to determine original language; do not infer original language from zh-CN URLs.",
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="Fetch sources and rebuild the local prompt catalog.")
    build.add_argument("--youmind-source", choices=["sitemap", "readme", "none"], default="sitemap", help="How to import YouMind records.")
    build.add_argument("--youmind-limit", type=int, default=0, help="Limit YouMind detail pages in sitemap mode; 0 means all.")
    build.add_argument("--youmind-workers", type=int, default=4, help="Concurrent workers for YouMind detail pages.")
    search = sub.add_parser("search", help="Read the local prompt catalog by intent, category, and query.")
    search.add_argument("--intent", choices=sorted(INTENT_PROFILES), help="Intent profile to match.")
    search.add_argument("--category", help="Substring match on source category.")
    search.add_argument("--query", help="Free text query.")
    search.add_argument("--limit", type=int, default=5)
    search.add_argument("--no-risk", action="store_true", help="Exclude records with risk_notes.")
    search.add_argument("--format", choices=["markdown", "json"], default="markdown")
    read_excel = sub.add_parser("read-excel", help="Read and filter the generated prompts.xlsx without opening Excel.")
    read_excel.add_argument("--path", help="Optional xlsx path. Defaults to the built-in prompt catalog.")
    read_excel.add_argument("--source", help="Substring match on source.")
    read_excel.add_argument("--category", help="Substring match on category.")
    read_excel.add_argument("--query", help="Free text query on source/category/title/prompt/risk.")
    read_excel.add_argument("--limit", type=int, default=5)
    read_excel.add_argument("--no-risk", action="store_true", help="Exclude records with risk notes.")
    read_excel.add_argument("--format", choices=["markdown", "json"], default="markdown")
    sub.add_parser("categories", help="List categories in the local prompt catalog.")
    sub.add_parser("repair-local", help="Repair local catalog text decoding and regenerate CSV/XLSX without network.")
    discover = sub.add_parser("discover-youmind-sitemap", help="Discover YouMind prompt detail URLs from the public sitemap.")
    discover.add_argument("--limit", type=int, default=0, help="Limit returned rows; 0 means all.")
    discover.add_argument("--output", help="Optional JSONL output path.")
    args = parser.parse_args(argv)
    if args.command == "build":
        return build_catalog(args)
    if args.command == "search":
        return search_catalog(args)
    if args.command == "read-excel":
        return read_excel_catalog(args)
    if args.command == "categories":
        return list_categories(args)
    if args.command == "repair-local":
        return repair_local_catalog(args)
    if args.command == "discover-youmind-sitemap":
        return discover_youmindsitemap(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
