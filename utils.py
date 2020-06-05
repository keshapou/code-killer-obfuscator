import random

def filter_dictionary(d, val):
    names = []
    for name in d:
        if val == d[name]:
            names.append(name)

    return names

def rand_count(a, b, max_count=99999):
    """Рандомно выбирает число от a до b, учитывая максимальное количество"""
    a = min(max_count, a)
    b = min(max_count, b)

    if a >= b:
        return b
    return random.randint(a, b)

def rand_indexes_revert(max_size, count):
    if count >= max_size:
        return [i for i in range(max_size - 1, -1, -1)]

    res = [rand_count(0, max_size - 1) for i in range(max_size)]
    res.sort()
    res.reverse()
    return res