from typing import Any, Dict, List


def merge_lists_in_dict(
    old: Dict[Any, List[Any]], new: Dict[Any, List[Any]]
) -> Dict[Any, List[Any]]:
    for key, l_value in new.items():
        if key in old:
            old[key].extend(l_value)
        else:
            old[key] = l_value

    return old


def compare_lists_in_dict(
    old: Dict[Any, List[Any]], new: Dict[Any, List[Any]]
) -> Dict[Any, List[Any]]:
    diff = {}
    for key, l_value in new.items():
        if key not in old:
            diff[key] = l_value
        else:
            list_diff = list(set(l_value) - set(old[key]))
            if list_diff:
                diff[key] = list_diff
    return diff


def to_message(hotel_name: str, availrooms: Dict[Any, List[Any]]):
    message= f"【{hotel_name}】\n"
    for key, l_value in availrooms.items():
        str_value = ", ".join(l_value)
        message += key + ":  " + str_value + "\n\n"
    return message.strip()
