import math

# Tabela de valores de rotação para cada passo do processamento
rotate_by = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
             5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20,
             4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
             6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21]

# Tabela de constantes para cada passo do processamento, calculada usando a função seno
constants = [int(abs(math.sin(i + 1)) * 4294967296) & 0xFFFFFFFF for i in range(64)]

# Função para realizar o padding da mensagem
def pad(msg):
    msg_len_in_bits = (8 * len(msg)) & 0xffffffffffffffff
    msg.append(0x80) # Adiciona 1 bit seguido por 0 bits até o comprimento ser congruente a 448 (mod 512)

    while len(msg) % 64 != 56:
        msg.append(0)

    # Adiciona o comprimento original da mensagem como um inteiro de 64 bits (little-endian)
    msg += msg_len_in_bits.to_bytes(8, byteorder='little')

    return msg

# Buffer inicial do MD5, conforme especificado na RFC
init_MDBuffer = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]

# Função de rotação à esquerda
def leftRotate(x, amount):
    x &= 0xFFFFFFFF
    return (x << amount | x >> (32 - amount)) & 0xFFFFFFFF

# Função para processar a mensagem em blocos de 512 bits (64 bytes)
def processMessage(msg):
    init_temp = init_MDBuffer[:] # Cria uma cópia do buffer inicial para preservar os valores originais

    # Processa a mensagem em blocos de 512 bits
    for offset in range(0, len(msg), 64):
        A, B, C, D = init_temp
        block = msg[offset: offset + 64] # Cria um bloco de 512 bits para ser processado

        # Processa cada bloco de 512 bits em 64 passos
        for i in range(64):
            if i < 16:
                func = lambda b, c, d: (b & c) | (~b & d)
                index_func = lambda i: i
            elif i < 32:
                func = lambda b, c, d: (d & b) | (~d & c)
                index_func = lambda i: (5 * i + 1) % 16
            elif i < 48:
                func = lambda b, c, d: b ^ c ^ d
                index_func = lambda i: (3 * i + 5) % 16
            else:
                func = lambda b, c, d: c ^ (b | ~d)
                index_func = lambda i: (7 * i) % 16

            F = func(B, C, D)
            G = index_func(i)
            to_rotate = A + F + constants[i] + int.from_bytes(block[4 * G: 4 * G + 4], byteorder='little')
            newB = (B + leftRotate(to_rotate, rotate_by[i])) & 0xFFFFFFFF

            A, B, C, D = D, newB, B, C

        # Adiciona o resultado final da etapa ao estado inicial do buffer
        for i, val in enumerate([A, B, C, D]):
            init_temp[i] += val
            init_temp[i] &= 0xFFFFFFFF

    # Retorna a soma dos buffers finais como o digest
    return sum(buffer_content << (32 * i) for i, buffer_content in enumerate(init_temp))

# Função para converter o digest para um valor hexadecimal
def MD_to_hex(digest):
    raw = digest.to_bytes(16, byteorder='little')
    return '{:032x}'.format(int.from_bytes(raw, byteorder='big'))

# Função principal que calcula o hash MD5 de uma mensagem
def md5(msg):
    msg = bytearray(msg, 'ascii') # Converte a mensagem em uma sequência de bytes
    msg = pad(msg)
    processed_msg = processMessage(msg) # Processa a mensagem para obter o hash
    message_hash = MD_to_hex(processed_msg) # Converte o digest para hexadecimal
    
    return message_hash

import hashlib

# Testes
print("=== Testando MD5 com a hashlib ===")
print(hashlib.md5("teste".encode('utf-8')).hexdigest(), "\n")

print("=== Testando MD5 com meu algoritmo ===")
hashdoAluno = md5('teste')
print(hashdoAluno)