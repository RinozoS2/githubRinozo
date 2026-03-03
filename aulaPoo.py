import random

# Sorteia o número
valor_sorteado = random.randint(10, 15)

# Primeira tentativa
valor_usuario = int(input("Digite um valor entre 10 e 15: "))

# Loop principal
while valor_usuario != valor_sorteado:
    # Verifica se o número está no intervalo
    if valor_usuario < 10 or valor_usuario > 15:
        print("Ei, o número deve ser entre 10 e 15")
    else:
        print("Não foi dessa vez. Tente novamente!")
        print(f"sorteado anterior {valor_sorteado}")
        valor_sorteado = random.randint(10, 15)

    
    valor_usuario = int(input("Digite seu novo palpite: "))

# Se saiu do loop, acertou
print(f"\nParabéns, você ganhou! O valor sorteado realmente foi: {valor_sorteado}")