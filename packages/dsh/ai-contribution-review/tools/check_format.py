#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验本 skill 是否符合 DeepSeek Harness（dsh）的 skill 规范。

规范来源：deepseek-ai/deepseek-harness 仓库 `docs/subsystems/skills.zh.md`
（发布站点：https://deepseek-harness.github.io/deepseek-harness/）。

被检查的规则：
  1. 名称 kebab-case：^[a-z0-9]+(?:-[a-z0-9]+)*$
  2. 目录包布局 `<root>/<name>/SKILL.md`，目录名须与 frontmatter 的 name 一致
  3. frontmatter 必填 name、description
  4. 可选键仅限 whenToUse、metadata、disable-model-invocation、user-invocable
  5. disable-model-invocation 与 user-invocable 若出现必须为布尔值，否则整条 skill 被丢弃
  6. 不支持嵌套发现：root 下超过一层的 SKILL.md 不会被扫描
  7. 正文须含四个必需部分：When to use / Steps / Constraints / Acceptance

用法：
    python tools/check_format.py [bundle_dir]      # 默认检查本文件所在 bundle
"""

import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_KEYS = {"name", "description"}
OPTIONAL_KEYS = {"whenToUse", "metadata", "disable-model-invocation", "user-invocable"}
BOOLEAN_KEYS = {"disable-model-invocation", "user-invocable"}
REQUIRED_SECTIONS = ["when to use", "steps", "constraints", "acceptance"]


def _stdout_utf8():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def parse_frontmatter(text):
    """极简 YAML 解析：只取顶层标量与 metadata 块，避免引入依赖。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None, 0
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, None, 0

    data = {}
    current = None
    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith(("  ", "\t")) and current == "metadata":
            k, _, v = raw.strip().partition(":")
            data.setdefault("metadata", {})[k.strip()] = v.strip().strip('"').strip("'")
            continue
        key, _, value = raw.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if value == "":
            current = key
            data[key] = {} if key == "metadata" else None
        else:
            current = None
            data[key] = value.strip('"').strip("'")
    return data, lines[end + 1:], end + 1


def truthy(value):
    return str(value).strip().lower() in {"true", "yes", "1"}


def check(bundle):
    errors, warnings = [], []
    skill = bundle / "SKILL.md"

    if not skill.exists():
        return [f"目录包缺少 SKILL.md：{skill}"], []

    fm, body_lines, offset = parse_frontmatter(skill.read_text(encoding="utf-8"))
    if fm is None:
        return ["SKILL.md 缺少 frontmatter（应以 --- 开始并以 --- 结束）"], []

    # 1 & 3 & 4
    for key in REQUIRED_KEYS:
        if not fm.get(key):
            errors.append(f"frontmatter 缺少必填项 {key}")
    unknown = set(fm) - REQUIRED_KEYS - OPTIONAL_KEYS
    if unknown:
        warnings.append(f"出现规范未列出的键：{sorted(unknown)}（dsh 未定义，可能被忽略）")

    name = str(fm.get("name") or "")
    if name and not NAME_RE.match(name):
        errors.append(f"name 不是 kebab-case：{name!r}（须匹配 {NAME_RE.pattern}）")

    # 2
    if name and bundle.name != name:
        errors.append(f"目录名 {bundle.name!r} 与 frontmatter name {name!r} 不一致；"
                      f"目录包须为 <root>/<name>/SKILL.md")

    # 5
    for key in BOOLEAN_KEYS:
        if key in fm:
            val = str(fm[key]).strip().lower()
            if val not in {"true", "false"}:
                errors.append(f"{key} 的值 {fm[key]!r} 不是布尔值；规范规定非布尔值会整条丢弃该 skill")

    # 6：正常布局是 <root>/<name>/SKILL.md（相对路径 2 段）；更深的不会被扫描
    root = bundle.parent
    for p in root.rglob("SKILL.md"):
        rel = p.relative_to(root)
        if len(rel.parts) > 2:
            errors.append(f"存在嵌套 SKILL.md（不会被发现）：{rel}")

    # 7
    body = "\n".join(body_lines)
    headings = [h.strip().lower() for h in re.findall(r"^#{2,3}\s+(.+)$", body, re.M)]
    for section in REQUIRED_SECTIONS:
        if not any(h.startswith(section) or section in h for h in headings):
            errors.append(f"正文缺少必需部分：{section}")

    # 额外体检
    desc = str(fm.get("description") or "")
    if len(desc) < 20:
        warnings.append("description 过短；模型目录只读 name + description，会难以触发")
    if len(desc) > 500:
        warnings.append(f"description 长 {len(desc)} 字符，建议压到 500 以内")
    if len(body_lines) > 400:
        warnings.append(f"正文 {len(body_lines)} 行，官方指南建议保持精简，细节放 references/")

    return errors, warnings


def main():
    _stdout_utf8()
    bundle = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    print(f"检查 {bundle}")
    errors, warnings = check(bundle)
    for w in warnings:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  ERROR {e}")
    if not errors:
        print("  ✓ 符合 dsh skill 规范")
    print()
    print("通过" if not errors else "未通过")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
