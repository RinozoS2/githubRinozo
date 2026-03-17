def verificar_par(x):        
    vef = True
    if(x % 2 == 0):
        return vef
    else:
        vef = False
        return vef
    
x1 = int(input("Digite um número: "))

if(verificar_par(x1)):
    print("Número par")
else:
    print("Número impar")