from classes import Jogador, Equipe

jogadores = []
equipes = []

while True:
    print("\n======================================")
    print("   CAMPEONATO INTERCLASSE DE E-SPORTS")
    print("1. Cadastrar jogador")
    print("2. Cadastrar equipe")
    print("3. Adicionar jogador a uma equipe")
    print("4. Listar todas as equipes")
    print("5. Listar jogadores de uma equipe")
    print("6. Buscar jogador por nickname")
    print("0. Sair")
    print("======================================")

    try:
        opcao = input("Escolha uma opção: ")

        # IF: verifica se o usuário escolheu opção 1
        if opcao == "1":
            nome = input("Nome do jogador: ")
            nickname = input("Nickname: ")
            turma = input("Turma: ")

            jogador = Jogador(nome, nickname, turma)
            jogadores.append(jogador)

        # IF: opção 2 - cadastrar equipe
        elif opcao == "2":
            nome = input("Nome da equipe: ")
            jogo = input("Jogo: ")

            equipe = Equipe(nome, jogo)
            equipes.append(equipe)

        # IF: opção 3 - adicionar jogador na equipe
        elif opcao == "3":
            nick = input("Nickname do jogador: ")
            nome_equipe = input("Nome da equipe: ")

            jogador_encontrado = None

            # FOR: percorre todos os jogadores cadastrados
            for j in jogadores:
                # IF: verifica se o nickname bate
                if j.nickname == nick:
                    jogador_encontrado = j

            equipe_encontrada = None

            # FOR: percorre todas as equipes cadastradas
            for e in equipes:
                # IF: verifica se o nome da equipe bate
                if e.nome == nome_equipe:
                    equipe_encontrada = e

            # IF: só entra aqui se encontrou jogador E equipe
            if jogador_encontrado and equipe_encontrada:
                sucesso = equipe_encontrada.adicionar_jogador(jogador_encontrado)

                # IF: verifica se conseguiu adicionar
                if sucesso:
                    print("Jogador adicionado à equipe!")
                else:
                    print("A equipe já possui 5 jogadores ou o jogador já está nela!")
            else:
                print("Jogador ou equipe não encontrados.")

        # IF: opção 4 - listar todas as equipes
        elif opcao == "4":
            # FOR: percorre todas as equipes
            for equipe in equipes:
                print(f"\nEquipe: {equipe.nome} | Jogo: {equipe.jogo}")
                equipe.listar_jogadores()

        # IF: opção 5 - listar jogadores de uma equipe específica
        elif opcao == "5":
            nome_equipe = input("Nome da equipe: ")

            # FOR: percorre todas as equipes
            for equipe in equipes:
                # IF: verifica se encontrou a equipe
                if equipe.nome == nome_equipe:
                    print(f"\nEquipe: {equipe.nome}")
                    equipe.listar_jogadores()
                    break
            else:
                print("Equipe não encontrada.")

        # IF: opção 6 - buscar jogador por nickname
        elif opcao == "6":
            nick = input("Digite o nickname: ")
            encontrado = False

            # FOR: percorre todas as equipes
            for equipe in equipes:
                jogador = equipe.buscar_jogador(nick)

                # IF: verifica se encontrou jogador
                if jogador:
                    print(f"O jogador está na equipe {equipe.nome}")
                    encontrado = True

            # IF: se não encontrou em nenhuma equipe
            if not encontrado:
                print("Jogador não encontrado.")

        # IF: opção 0 - sair do programa
        elif opcao == "0":
            break

        # ELSE: qualquer opção inválida
        else:
            print("Opção inválida!")

    except Exception as erro:
        # TRY/EXCEPT: captura qualquer erro inesperado
        print("Ocorreu um erro:", erro)