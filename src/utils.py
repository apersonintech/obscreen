
def str_to_enum(str_val: str, enum_class):
    for enum_item in enum_class:
        if enum_item.value == str_val:
            return enum_item
    raise ValueError(f"{str_val} is not a valid {enum_class.__name__} item")

def get_ip_address():
    try:
        result = subprocess.run(
            ["ip", "-4", "route", "get", "8.8.8.8"],
            capture_output=True,
            text=True
        )
        ip_address = result.stdout.split()[6]
        return ip_address
    except Exception as e:
        print(f"Error obtaining IP address: {e}")
        return 'Unknown'