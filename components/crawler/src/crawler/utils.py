from typing import Any, Dict, List


def get_nested(payload: Dict[Any, Any], keys: List[Any], default=None) -> Any:
    item = payload
    for key in keys[:-1]:
        item = item.get(key, {})
    return item.get(keys[-1], default) if keys else item
