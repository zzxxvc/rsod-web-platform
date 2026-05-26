#!/usr/bin/env python3
"""
数据验证子系统
可扩展的数据质量保障体系
"""

import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

_validators: Dict[str, Callable] = {}


class CheckLevel(Enum):
    """检查结果级别"""

    PASS = "pass"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class CheckResult:
    """单项检查结果"""

    level: CheckLevel
    message: str
    check_name: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckContext:
    """检查上下文 - 验证器的输入数据"""

    annotations_dir: Optional[Path] = None
    images_dir: Optional[Path] = None
    classes: Optional[List[str]] = None
    image_extensions: List[str] = field(
        default_factory=lambda: [".jpg", ".jpeg", ".png"]
    )
    extra: Dict[str, Any] = field(default_factory=dict)


def register_validator(name):
    """验证器装饰器，将函数注册到验证器注册表"""

    def decorator(func):
        _validators[name] = func
        func._validator_name = name
        return func

    return decorator


def list_validators():
    """列出所有已注册的验证器名称"""
    return list(_validators.keys())


def get_validator(name):
    """按名称获取验证器函数"""
    return _validators.get(name)


def run_validators(context, validator_names=None):
    """
    运行验证器

    参数：
        context: 检查上下文
        validator_names: 指定运行的验证器列表，None 表示运行全部

    返回：
        List[CheckResult]: 所有检查结果
    """
    results = []
    names = validator_names if validator_names is not None else list_validators()

    for name in names:
        validator = get_validator(name)
        if validator:
            try:
                check_results = validator(context)
                for r in check_results:
                    if not r.check_name:
                        r.check_name = name
                results.extend(check_results)
            except Exception as e:
                results.append(
                    CheckResult(
                        level=CheckLevel.ERROR,
                        message=f"验证器执行失败: {str(e)}",
                        check_name=name,
                    )
                )

    return results


_LEVEL_ICONS = {
    CheckLevel.PASS: "✅",
    CheckLevel.INFO: "ℹ️ ",
    CheckLevel.WARNING: "⚠️ ",
    CheckLevel.ERROR: "❌",
}


def _safe_print(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        print(text.encode(encoding, errors="replace").decode(encoding))


class DataValidator:
    """数据验证器，执行验证并生成报告"""

    def __init__(self, context: CheckContext, validator_names=None):
        self.context = context
        self.validator_names = validator_names

    def validate(self) -> List[CheckResult]:
        return run_validators(self.context, self.validator_names)

    def validate_and_report(self) -> bool:
        """执行验证并打印报告，无 ERROR 时返回 True"""
        results = self.validate()
        self._print_report(results)
        return not any(r.level == CheckLevel.ERROR for r in results)

    def _print_report(self, results: List[CheckResult]):
        _safe_print("\n" + "=" * 60)
        _safe_print("数据验证报告")
        _safe_print("=" * 60 + "\n")

        for r in results:
            icon = _LEVEL_ICONS.get(r.level, "")
            name = r.check_name or "unknown"
            _safe_print(f"{icon} [{r.level.value.upper()}] {name}: {r.message}")
            if r.details:
                for key, value in r.details.items():
                    _safe_print(f"   {key}: {value}")

        error_count = sum(1 for r in results if r.level == CheckLevel.ERROR)
        warning_count = sum(1 for r in results if r.level == CheckLevel.WARNING)

        _safe_print("\n" + "-" * 60)
        _safe_print(f"总计: {len(results)} 项检查")
        _safe_print(f"  错误: {error_count}")
        _safe_print(f"  警告: {warning_count}")
        _safe_print("-" * 60 + "\n")


@register_validator("directories_exist")
def check_directories(ctx):
    """检查必要目录是否存在"""
    results = []

    if ctx.annotations_dir:
        if ctx.annotations_dir.exists():
            results.append(
                CheckResult(
                    level=CheckLevel.PASS,
                    message=f"标注目录存在: {ctx.annotations_dir}",
                )
            )
        else:
            results.append(
                CheckResult(
                    level=CheckLevel.ERROR,
                    message=f"标注目录不存在: {ctx.annotations_dir}",
                )
            )

    if ctx.images_dir:
        if ctx.images_dir.exists():
            results.append(
                CheckResult(
                    level=CheckLevel.PASS,
                    message=f"图片目录存在: {ctx.images_dir}",
                )
            )
        else:
            results.append(
                CheckResult(
                    level=CheckLevel.ERROR,
                    message=f"图片目录不存在: {ctx.images_dir}",
                )
            )

    return results


@register_validator("annotation_files")
def check_annotation_files(ctx):
    """检查标注文件"""
    results = []

    if not ctx.annotations_dir or not ctx.annotations_dir.exists():
        return results

    xml_files = list(ctx.annotations_dir.glob("*.xml"))

    if len(xml_files) == 0:
        results.append(
            CheckResult(
                level=CheckLevel.ERROR,
                message="未找到任何 XML 标注文件",
            )
        )
    else:
        results.append(
            CheckResult(
                level=CheckLevel.PASS,
                message=f"找到 {len(xml_files)} 个 XML 标注文件",
                details={"count": len(xml_files)},
            )
        )

    return results


@register_validator("image_annotation_match")
def check_image_annotation_match(ctx):
    """检查图片和标注文件是否匹配"""
    results = []

    if not ctx.annotations_dir or not ctx.images_dir:
        return results
    if not ctx.annotations_dir.exists() or not ctx.images_dir.exists():
        return results

    xml_files = {f.stem for f in ctx.annotations_dir.glob("*.xml")}

    image_files = set()
    for ext in ctx.image_extensions:
        image_files.update({f.stem for f in ctx.images_dir.glob(f"*{ext}")})

    missing_images = xml_files - image_files
    if missing_images:
        results.append(
            CheckResult(
                level=CheckLevel.WARNING,
                message=f"{len(missing_images)} 个标注文件缺少对应图片",
                details={"missing": list(missing_images)[:10]},
            )
        )

    missing_annotations = image_files - xml_files
    if missing_annotations:
        results.append(
            CheckResult(
                level=CheckLevel.WARNING,
                message=f"{len(missing_annotations)} 个图片缺少对应标注",
                details={"missing": list(missing_annotations)[:10]},
            )
        )

    if not missing_images and not missing_annotations:
        results.append(
            CheckResult(
                level=CheckLevel.PASS,
                message=f"图片和标注文件完全匹配，共 {len(xml_files & image_files)} 对",
            )
        )

    return results


@register_validator("class_validation")
def check_classes(ctx):
    """检查标注中的类别是否有效"""
    results = []

    if not ctx.annotations_dir or not ctx.classes:
        return results
    if not ctx.annotations_dir.exists():
        return results

    classes_set = set(ctx.classes)
    found_classes = set()
    unknown_classes = set()
    invalid_files = []

    for xml_file in list(ctx.annotations_dir.glob("*.xml"))[:100]:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for obj in root.findall("object"):
                name_elem = obj.find("name")
                if name_elem is not None:
                    class_name = name_elem.text
                    found_classes.add(class_name)
                    if class_name not in classes_set:
                        unknown_classes.add(class_name)
        except Exception:
            invalid_files.append(xml_file.name)

    if found_classes:
        results.append(
            CheckResult(
                level=CheckLevel.INFO,
                message=f"数据集中发现的类别: {sorted(found_classes)}",
            )
        )

    if unknown_classes:
        results.append(
            CheckResult(
                level=CheckLevel.WARNING,
                message=f"发现未知类别: {sorted(unknown_classes)}",
            )
        )

    if invalid_files:
        results.append(
            CheckResult(
                level=CheckLevel.WARNING,
                message=f"无法解析的 XML 文件: {len(invalid_files)} 个",
            )
        )

    if not unknown_classes and not invalid_files and found_classes:
        results.append(
            CheckResult(
                level=CheckLevel.PASS,
                message="类别验证通过",
            )
        )

    return results
