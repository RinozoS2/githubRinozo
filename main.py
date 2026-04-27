from classes import Jogador,Equipe

jogadores = []
equipes = []

while True:
    print("\nMENU")
    print("1 - Cadastrar jogador")
    print("2 - Cadastrar equipe")
    print("3 - Adicionar jogador em equipe")
    print("4 - Listar equipes e jogadores")
    print("5 - Buscar jogador pelo nickname")
    print("0 - Sair")

    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        nome = input("Nome do jogador: ")
        nickname = input("Nickname: ")
        turma = input("Turma: ")
        jogador = Jogador(nome, nickname, turma)
        jogadores.append(jogador)

    elif opcao == "2":
        nome = input("Nome da equipe: ")
        jogo = input("Jogo: ")
        equipe = Equipe(nome, jogo)
        equipes.append(equipe)

    elif opcao == "3":
        nick = input("Nickname do jogador: ")
        nome_equipe = input("Nome da equipe: ")

        jogador_encontrado = None
        for j in jogadores:
            if j.nickname == nick:
                jogador_encontrado = j

        equipe_encontrada = None
        for e in equipes:
            if e.nome == nome_equipe:
                equipe_encontrada = e

        if jogador_encontrado and equipe_encontrada:
            equipe_encontrada.adicionar_jogador(jogador_encontrado)
            print("Jogador adicionado à equipe!")
        else:
            print("Jogador ou equipe não encontrados.")

    elif opcao == "4":
        for equipe in equipes:
            print(f"\nEquipe: {equipe.nome} | Jogo: {equipe.jogo}")
            equipe.listar_jogadores()

    elif opcao == "5":
        nick = input("Digite o nickname: ")
        encontrado = False
        for equipe in equipes:
            jogador =  equipe.buscar_jogador(nick)
            if jogador:
                print(f"O jogador está na equipe {equipe.nome}")
                encontrado = True

        if not encontrado:
            print("Jogador não encontrado.")

    elif opcao == "0":
        break

    else:
        print("Opção inválida!")