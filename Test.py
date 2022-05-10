with open('objects_not_found.txt') as f:
    # if file not exists, create it
    lines = f.readlines()


# remove \n from the end of each line
lines = [line.rstrip('\n') for line in lines]

print(lines)