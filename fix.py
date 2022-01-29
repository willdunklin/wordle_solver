
with open('log2', 'w') as file:
    with open('log') as log:
        lines = log.readlines()
        for i in range(3**5):
            tmp = i
            filter_str = ''
            for _ in range(5):
                filter_str += '*yg'[tmp%3]
                tmp //= 3

            file.write(filter_str + ' ' + lines[i])