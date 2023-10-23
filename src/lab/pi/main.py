def get_binary(char='-'):


    # Get the Unicode code point of the character
    unicode_code_point = ord(char)

    # Convert the code point to binary
    binary_representation = bin(unicode_code_point)

    # The binary representation will have a '0b' prefix, so you can remove it if needed
    binary_representation = binary_representation[2:]

    return f" '{char}' -> {binary_representation}"

alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


for letter in alphabet:
    print(get_binary(letter))


