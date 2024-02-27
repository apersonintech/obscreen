
def str_to_enum(str_val: str, enum_class):
    for enum_item in enum_class:
        if enum_item.value == str_val:
            return enum_item
    raise ValueError(f"{str_val} is not a valid {enum_class.__name__} item")
