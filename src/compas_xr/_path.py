from typing import Union


def normalize_path(path: Union[str, list[str], tuple[str, ...]]) -> str:
    """Normalize a slash-delimited cloud path.

    Parameters
    ----------
    path
        Path as a slash-delimited string or as path segments.

    Returns
    -------
    str
        Normalized path with single slashes and no leading/trailing slash.
    """
    if isinstance(path, str):
        raw_parts = path.strip("/").split("/")
    elif isinstance(path, (list, tuple)):
        raw_parts = path
    else:
        raise TypeError("path must be a string, list, or tuple")

    parts = []
    for part in raw_parts:
        if not isinstance(part, str):
            raise TypeError("all path parts must be strings")
        stripped = part.strip("/")
        if stripped:
            parts.append(stripped)

    return "/".join(parts)


def path_to_parts(path: Union[str, list[str], tuple[str, ...]]) -> list[str]:
    """Convert a path string or path parts to normalized path segments."""
    normalized = normalize_path(path)
    if not normalized:
        return []
    return normalized.split("/")


def validate_reference_parts(parts: Union[list[str], tuple[str, ...]], invalid_chars: Union[set[str], None] = None) -> None:
    """Validate normalized path segments for cloud references.

    Parameters
    ----------
    parts
        Normalized path segments.
    invalid_chars
        Characters that are not allowed in each path segment.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If the path is empty or contains invalid characters.
    """
    if not parts:
        raise ValueError("path must not be empty")

    invalid_chars = invalid_chars or set()
    for part in parts:
        if any(char in part for char in invalid_chars):
            raise ValueError("invalid path segment '{}': contains one of {}".format(part, " ".join(sorted(invalid_chars))))
        if any(ord(char) < 32 or ord(char) == 127 for char in part):
            raise ValueError("invalid path segment '{}': contains control characters".format(part))


def validate_reference_path(path: Union[str, list[str], tuple[str, ...]], invalid_chars: Union[set[str], None] = None) -> list[str]:
    """Normalize and validate a cloud reference path.

    Parameters
    ----------
    path
        Path as a slash-delimited string or as path segments.
    invalid_chars
        Characters that are not allowed in each path segment.

    Returns
    -------
    list[str]
        Normalized and validated path segments.

    Raises
    ------
    ValueError
        If the path is empty or contains invalid characters.
    """
    parts = path_to_parts(path)
    validate_reference_parts(parts, invalid_chars=invalid_chars)
    return parts
