def read_txt_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

commander_names_suggestions = read_txt_file('commander_names.txt')

print(commander_names_suggestions)