"""
Validation utilities for tracker API responses and markdown parsing.

Provides safe validation of tracker responses and markdown data using
Pydantic models to prevent crashes from malformed data.
"""

import logging
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def validate_response(
    data: Any,
    model: Type[T],
    context: str = "response"
) -> Optional[T]:
    """Safely validate data against Pydantic model.

    Args:
        data: Raw data to validate (dict, list, etc.)
        model: Pydantic model class to validate against
        context: Description of data being validated (for logging)

    Returns:
        Validated model instance, or None if validation failed
    """
    try:
        return model.parse_obj(data)
    except ValidationError as e:
        logger.error(f"❌ Validation error in {context}: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error validating {context}: {e}")
        return None


def validate_list(
    data: Any,
    model: Type[T],
    context: str = "list"
) -> List[T]:
    """Safely validate list of items against Pydantic model.

    Args:
        data: Raw list data to validate
        model: Pydantic model class for each item
        context: Description of data being validated (for logging)

    Returns:
        List of validated model instances (empty list if validation fails)
    """
    if not isinstance(data, list):
        logger.error(f"❌ Expected list in {context}, got {type(data)}")
        return []

    validated_items: List[T] = []
    for i, item in enumerate(data):
        validated = validate_response(item, model, f"{context}[{i}]")
        if validated:
            validated_items.append(validated)
        else:
            logger.warning(f"⚠️ Skipped invalid item {i} in {context}")

    return validated_items


def safe_json_parse(data: str) -> Dict[str, Any]:
    """Safely parse JSON string.

    Args:
        data: JSON string to parse

    Returns:
        Parsed dict, or empty dict if parsing fails
    """
    try:
        import json
        return json.loads(data)
    except Exception as e:
        logger.error(f"❌ Failed to parse JSON: {e}")
        return {}
