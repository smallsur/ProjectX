

def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    # join意为用指定的字符连接生成一个新字符串
    return ', '.join(L)
