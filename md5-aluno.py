import math

# Tabela de valores de rotacao
valores_rotacao = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
             5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20,
             4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
             6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21]

# Tabela de constantes
# constantes = [int(abs(math.sin(i + 1)) * 4294967296) & 0xFFFFFFFF for i in range(64)]
constantes = []
for i in range(64):
    valor = abs(math.sin(i + 1)) * 4294967296
    valor_int = int(valor) & 0xFFFFFFFF
    constantes.append(valor_int)

# Passo 1: Acrescentar bits de preenchimento
def preencher(msg):
    tamanho_msg_bits = (8 * len(msg)) & 0xffffffffffffffff
    msg.append(0x80)

    while len(msg) % 64 != 56:
        msg.append(0)

    # Passo 2: Acrescentar comprimento
    msg += tamanho_msg_bits.to_bytes(8, byteorder='little')

    return msg

# Passo 3: Inicializar MD Buffer
buffer_inicial_MD = [0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476]

# Função de rotação à esquerda
def rotacaoEsquerda(x, valor):
    x &= 0xFFFFFFFF
    return (x << valor | x >> (32 - valor)) & 0xFFFFFFFF

# Passo 4: Processar mensagem
def processarMensagem(msg):
    buffer_temp = buffer_inicial_MD[:]

    for deslocamento in range(0, len(msg), 64):
        A, B, C, D = buffer_temp
        bloco = msg[deslocamento: deslocamento + 64]

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
            rotacionar = A + F + constantes[i] + int.from_bytes(bloco[4 * G: 4 * G + 4], byteorder='little')
            novoB = (B + rotacaoEsquerda(rotacionar, valores_rotacao[i])) & 0xFFFFFFFF

            A, B, C, D = D, novoB, B, C

        for i, val in enumerate([A, B, C, D]):
            buffer_temp[i] += val
            buffer_temp[i] &= 0xFFFFFFFF

    return sum(conteudo_buffer << (32 * i) for i, conteudo_buffer in enumerate(buffer_temp))

# Funcao para converter o digest para um valor hexadecimal
def MD_para_hexa(digest):
    valorBruto = digest.to_bytes(16, byteorder='little')
    return '{:032x}'.format(int.from_bytes(valorBruto, byteorder='big'))

# Funcao principal que calcula o hash MD5 de uma mensagem
def hashMD5Aluno(msg):
    msg = bytearray(msg, 'ascii')
    msg = preencher(msg)
    msg_processada = processarMensagem(msg)
    hash_mensagem = MD_para_hexa(msg_processada)
    
    return hash_mensagem

# Testes
import hashlib

print("=== MD5 hashlib ===")
print(hashlib.md5("teste".encode('utf-8')).hexdigest(), "\n")

print("=== MD5 aluno ===")
hashdoAluno = hashMD5Aluno("teste")
print(hashdoAluno)