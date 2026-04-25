secret = [0, 1, 0, 1]

def all_possible_secrets():

    all = []
    current=[0,0,0,0]
    for w in range(2):
        current[0] = w
        for x in range(2):
            current[1] = x
            for y in range(2):
                current[2] = y
                for z in range(2):
                    current[3] = z
                    all += [current[:]]
    return all

def optimal_all():

    all = [[w,x,y,z] for w in range(2) for x in range(2) for y in range(2) for z in range(2)]
    return all

def secret_checker(input):
    if input == [0, 1, 0, 1]:
        return True
    return False

def main():
    result = secret_checker(secret)
    print(result)
    all = optimal_all()
    print(all)

if __name__ == "__main__":
    main()