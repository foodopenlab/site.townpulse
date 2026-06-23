from __future__ import annotations

import re

_VILLAGE_CODE = re.compile(r"^\d{10}$")


def validate_village_code(code: str) -> str:
    if not _VILLAGE_CODE.match(code):
        raise ValueError(f"invalid village_code: {code}")
    return code
