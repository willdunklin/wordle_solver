from turtle import end_fill


dictionary = open('dictionary.txt').readlines()
# print(dictionary)
x=len(dictionary)
print(x)

word5 = []
for word in dictionary:
    if len(word) == 5:
        word5.append(word)

print(word5)