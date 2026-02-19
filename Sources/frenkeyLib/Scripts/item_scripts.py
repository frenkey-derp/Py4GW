
def get_true_identifier_with_hex(runtime_identifier: int) -> tuple[int, str]:
    value = (runtime_identifier >> 4) & 0x3FF
    return value, hex(value)

print("ItemHandling", f"{get_true_identifier_with_hex(9224)}")