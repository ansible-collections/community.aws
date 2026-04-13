# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import annotations

from typing import Union


def is_dict_subset(
    expected: Union[dict, list[dict]],
    existing: Union[dict, list[dict]],
    list_sort_key: Union[str, None] = None,
) -> bool:
    """Check that all keys in *expected* match the corresponding values in *existing*.

    Recurses into nested dicts and compares lists element-wise so that extra
    keys present only in *existing* (e.g. defaults populated by AWS) do not
    cause a false mismatch.

    Lists of dicts are sorted by *list_sort_key* (when provided and every
    element in both lists is a dict containing that key) before comparison so
    that order differences do not cause false mismatches.

    Raises ValueError if *expected* or *existing* is not a dict or list.
    """
    if not isinstance(expected, (dict, list)) or not isinstance(existing, (dict, list)):
        raise ValueError(
            f"is_dict_subset expects dict or list[dict] arguments, "
            f"got {type(expected).__name__} and {type(existing).__name__}"
        )
    return _is_subset(expected, existing, list_sort_key=list_sort_key)


def _is_subset(expected, existing, list_sort_key=None):
    """Recursive implementation of is_dict_subset."""
    if isinstance(expected, dict) and isinstance(existing, dict):
        for key, value in expected.items():
            if key not in existing:
                return False
            if not _is_subset(value, existing[key], list_sort_key=list_sort_key):
                return False
        return True
    if isinstance(expected, list) and isinstance(existing, list):
        if len(expected) != len(existing):
            return False
        exp = expected
        ext = existing
        if (
            list_sort_key
            and exp
            and all(isinstance(i, dict) and list_sort_key in i for i in exp)
            and all(isinstance(i, dict) and list_sort_key in i for i in ext)
        ):
            exp = sorted(exp, key=lambda d: d[list_sort_key])
            ext = sorted(ext, key=lambda d: d[list_sort_key])
        return all(_is_subset(e, a, list_sort_key=list_sort_key) for e, a in zip(exp, ext))
    return expected == existing
