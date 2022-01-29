words = list(open('words.txt'))
words = [word.strip().lower() for word in words]

freq = list(open('freq100k.txt', encoding='utf8'))
freq = [word.strip().lower() for word in freq]

print(len(words))
print(len(freq))

with open('final.txt', 'w') as file:
    listed = []
    for word in freq:
        if word in words and word not in listed:
            file.writelines(word + '\n')
            listed.append(word)

    for word in words:
        if word not in listed:
            file.writelines(word + '\n')