# Random Simulations
Esse repositório tem como intenção centralizar os códigos de simulação de fiz ao longo do tempo tanto em projetos sem importância alguma como em momentos de estudo para entender o processo de simulação em Python.

Não deve ser entendido como um projeto fechado e com finalidade definida, mas como um compilado de experimentações.

# Experiências
## Estimar Pi
Por meio de cálculo de probabilidades e com a lei forte de grandes números, são gerados pontos aleatórios com o intuito de se estimar o valor da constante real $\pi$.

Para isso, é imaginado o seguinte cenário: um círculo inscrito em um quadrado de lado $\ell=1$. Ao se escolher um ponto aleatório interno ao quadrado, a probabilidade de ele estar também interno ao círculo é de 
$$P = \frac{\pi}{4}$$

Estimamos o valor de $P$ como o número de pontos internos ao círculo dividido pelo número total de pontos, assim:
$$\frac{N_{\text{pontos internos}}}{N_{\text{pontos totais}}} \approx \frac{\pi}{4}$$
$$\pi \approx 4\times \frac{N_{\text{pontos internos}}}{N_{\text{pontos totais}}}$$

## Simulação Banco
Abordagem clássica de simulação em ambiente de atendimento de clientes sujeitos a tempos de distribuição <i>exponencial</i> com uso de geração de números pseudo-aleatórios.

## Simulação Pop
Abordagem de simulação sobre uma população residente em uma determinada região. Considera-se uma taxa de crescimento dependente do número de mulheres e de mortalidade dependente de uma distribuição normal das idades