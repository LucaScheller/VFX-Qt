def blend(value_a, value_b, factor):
    return value_b * factor + value_a * (1 - factor)

def fit(value, old_min, old_max, new_min, new_max):
    return new_min + (((value-old_min)/(old_max-old_min)) * (new_max-new_min))