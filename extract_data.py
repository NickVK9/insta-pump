clear_list = []
with open('users.txt', 'r', encoding="utf8") as file:
    for line in file:
        if 'Фото профиля ' in line:
            a = line.split('Фото профиля ')
            a = a[1]
            clear_list.append(a.replace('\n', ''))

with open('users_for_test.txt', 'w') as file2:
    for i in clear_list:
        file2.write(i+'\n')
