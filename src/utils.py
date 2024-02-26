
def str_to_enum(strval: str, enum_class):
    for enum_item in enum_class:
        if enum_item.value == strval:
            return enum_item
    raise ValueError(f"{strval} is not a valid {enum_class.__name__} item")
