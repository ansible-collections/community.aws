# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Union


def rename_dict_keys(src: Union[dict, list, str], old_key: str, new_key: str) -> dict:
    result = None
    if isinstance(src, dict):
        result = {}
        for key, value in src.items():
            result_key = new_key if key == old_key else key
            if isinstance(value, dict):
                result[result_key] = rename_dict_keys(value, old_key, new_key)
            elif isinstance(value, list):
                result[result_key] = [rename_dict_keys(i, old_key, new_key) for i in value]
            else:
                result[result_key] = value
    elif isinstance(src, list):
        result = [rename_dict_keys(k, old_key, new_key) for k in src]
    else:
        result = src
    return result
