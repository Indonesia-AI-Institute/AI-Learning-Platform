"""
LLM Providers Auto Loader

Tujuan:
- Auto discover semua provider module
- Auto import supaya registry register jalan
- Zero manual import provider

Pattern:
Drop file provider baru → langsung aktif
"""

import pkgutil
import importlib
from pathlib import Path


def auto_import_providers():
    """
    Auto import semua module dalam folder providers.
    """

    package_dir = Path(__file__).parent
    package_name = __name__

    for module_info in pkgutil.iter_modules([str(package_dir)]):
        module_name = module_info.name

        if module_name.startswith("_"):
            continue

        full_module_name = f"{package_name}.{module_name}"

        importlib.import_module(full_module_name)


# Auto run saat package di import
auto_import_providers()
