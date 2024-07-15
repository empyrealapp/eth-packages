def tick_from_bitmap(index, num, tick_spacing: int) -> list[int]:
    bin_str = bin(num)[2:][::-1]
    initialized = []
    for idx, val in enumerate(bin_str):
        if val == "1":
            initialized.append(idx)
    return [(index * 256 + i) * tick_spacing for i in initialized]
