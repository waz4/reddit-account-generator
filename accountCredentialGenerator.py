from random import choice, randint
from string import ascii_letters, digits, punctuation

def randomUsername():
    # max lenght is 20 chars
    names = open('resources/names.txt').read().splitlines() # creates a list of names with one line per item
    adjectives = open("resources/adjectives.txt").read().splitlines() # creates a list of adjectives with one line per item

    randomName = choice(names).strip().title()
    randomAdjective = choice(adjectives).strip().lower()
    randomNumber = randint(0, 10)

    randomUsername = randomAdjective + randomName + str(randomNumber)
    return randomUsername[:20]

# type 0 - no punctuation
# type !0 - with punctuation
def randomPassword(passwordLenght: int = 10, type:int = 0):
    
    chars = ascii_letters + digits
    if (type != 0):
        chars += punctuation

    password = ""
    for c in range(passwordLenght):
        password += (choice(chars))

    return password

