import os
import sys
import unittest


DIRETORIO_PROJETO = os.path.dirname(os.path.abspath(__file__))
if DIRETORIO_PROJETO not in sys.path:
    sys.path.insert(0, DIRETORIO_PROJETO)

from TrabalhoDeJogo import Player


class TestDamageAnimation(unittest.TestCase):
    def setUp(self):
        os.chdir(DIRETORIO_PROJETO)
        self.jogador = Player()

    def test_damage_animation_returns_to_normal_movement(self):
        self.jogador.iniciar_animacao_dano()

        self.assertTrue(self.jogador.animacao_dano_ativa)
        self.assertEqual(
            self.jogador.texture,
            self.jogador.texturas_dano[0],
        )

        self.jogador.update(0.9)

        self.assertFalse(self.jogador.animacao_dano_ativa)
        self.assertEqual(self.jogador.texture, self.jogador.texture_parado)
        self.assertEqual(self.jogador.change_x, 0)
        self.assertEqual(self.jogador.change_y, 0)


if __name__ == "__main__":
    unittest.main()
