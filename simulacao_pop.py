# Modelo de crescimento da população de uma cidade

import pandas as pd
import random
import numpy as np
# import itertools
from matplotlib import pyplot as plt
from copy import deepcopy

random.seed(42)

# Parametros da simulacao
populacaoInicial = 50
tempoSimulacao = 300 #anos
mortalidadeInfantil = 1 #%
idadeFertil = (15,45)
idadeProdutiva = (16,65)
ataqueDoencas = 1 #percentual da populacao morto anualmente por doencas



class Pessoa:
    def __init__(self, idade) -> None:
        self.sexo = random.randint(0,1)
        self.idade = idade
        self.produtividade = abs(random.gauss(2,1))
        self.idade_morte = abs(random.gauss(70,5))

    def __repr__(self):
        genero = {1:'masc', 0:'fem'}
        return f'''Pessoa(sexo: {genero[self.sexo]},idade: {self.idade}, produtividade anual: {self.produtividade}, idade morte: {self.idade_morte})\n'''
    

# Inicializar a populacao
populacao = []
for i in range(populacaoInicial):
    populacao.append(Pessoa(idade=random.randint(0,80)))
# Realizar incremento populacional
# Considerando que 20% das mulheres tem filhos a cada ano
taxa_natalidade = 10

def incremento_pop(populacaoCidade):
    populacao = populacaoCidade.copy()
    hc = 0
    nasc = 0
    for pessoa in populacao:
        if pessoa.sexo == 0 and pessoa.idade >= idadeFertil[0] and pessoa.idade<=idadeFertil[1] and random.randint(0,100)<=taxa_natalidade:
            # Mulher tem filho
            n_filhos_gestacao = 1
            nasc += n_filhos_gestacao
            filho = Pessoa(0)
            # O filho sobrevive?
            sorteio_mortalidade_infantil = random.randint(0,100)
            if sorteio_mortalidade_infantil >=  mortalidadeInfantil:
                #Vive
                populacao.append(filho)
            else:
                hc+=1
    print(f'Nascimentos:{nasc}\tMortos ao nascer: {hc}\tIncremento: {nasc-hc}')        
    return populacao, nasc-hc

# Remover as pessoas que chegaram na idade prevista para morte
def mortos_velhice(populacaoCidade):
    
    # populacao = populacaoCidade.copy()
    sobreviventes = []
    hc=0
    for pessoa in populacaoCidade:
        if pessoa.idade <= pessoa.idade_morte:
            sobreviventes.append(pessoa)
        else:
            hc+=1
    # print(f'Mortos por idade: {hc}')
    return (sobreviventes, hc)
    
def mortos_doenca(populacaoCidade):
    
    sobreviventes = []
    hc = 0
    
    for pessoa in populacaoCidade:
        if random.randint(0,100)>=ataqueDoencas:
            sobreviventes.append(pessoa)
        else:
            hc += 1
    # print(f'Mortos por saude: {hc}')
    return sobreviventes,hc

def envelhece_pop(populacaoCidade):
    populacao = deepcopy(populacaoCidade)
    for pessoa in populacao:
        pessoa.idade += 1
    return populacao

def mortos_falta_comida(populacaoCidade):
    capacidade_produtiva = sum([ pessoa.produtividade for pessoa in populacaoCidade if pessoa.idade >=idadeProdutiva[0] and pessoa.idade<=idadeProdutiva[1] ])
    
    mortos_inanicao = len(populacaoCidade) - int(round(capacidade_produtiva,0))
    if mortos_inanicao > 0:
    
        indices_mortos = np.random.randint(0,len(populacaoCidade),mortos_inanicao)
        sobreviventes = [ p for i,p in enumerate(populacaoCidade) if i not in indices_mortos  ]
    else:
        sobreviventes = deepcopy(populacaoCidade)
    # print(f'Populacao: {len(populacaoCidade)}    Cap. Produtiva: {round(capacidade_produtiva,0)}    Sobreviventes: {len(sobreviventes)}')
    
    return sobreviventes, len(populacaoCidade) - len(sobreviventes)
    


# Inicializar a populacao
populacao = []
for i in range(populacaoInicial):
    populacao.append(Pessoa(idade=random.randint(0,80)))
populacao


n_interacao = 0
# print(populacao)
historico_pop = []
hc_velhice = [] 
hc_doenca =[]
hc_inani = []
cresc_pop = []
n_mulheres = []
n_mulheres_ferteis = []


while n_interacao < tempoSimulacao and len(populacao)>0:
    print(f'Iteracao {n_interacao}')
    historico_pop.append(len(populacao))
    
    populacao,cresc = incremento_pop(populacao)
    populacao,mv = mortos_velhice(populacao)
    populacao,md = mortos_doenca(populacao)
    populacao,mi = mortos_falta_comida(populacao)
    populacao = envelhece_pop(populacao)
    
    n_interacao += 1
    
    cresc_pop.append(cresc)
    hc_velhice.append(mv)
    hc_doenca.append(md)
    hc_inani.append(mi)    
    
    mulheres = [ i for i in populacao if i.sexo==0 ]
    mulheres_ferteis = [ i for i in mulheres if i.idade >= idadeFertil[0] and i.idade<=idadeFertil[1] ]
    n_mulheres.append(len(mulheres))
    n_mulheres_ferteis.append(len(mulheres_ferteis))
    
    
    # print(populacao)
    print('Populacao: ',len(populacao))

historico_pop = np.array(historico_pop)
cresc_pop = np.array(cresc_pop)
hc_velhice = np.array(hc_velhice)
hc_doenca = np.array(hc_doenca)
hc_inani = np.array(hc_inani)

df = pd.DataFrame(
    {'Populacao':historico_pop,
     
     'Nascimentos (liq)':cresc_pop,
     'Mortos velhice':hc_velhice,
     'Mortos doenca':hc_doenca,
     'Mortos fome':hc_inani }
    )
df['saldo'] = df.iloc[:,0] + df.iloc[:,1] - df.iloc[:,2] -df.iloc[:,3] - df.iloc[:,4]

fig,ax = plt.subplots(figsize=(15,8),dpi=100)
eixox = np.array(range(n_interacao))

ax.plot(eixox,historico_pop,'.-')
ax.set_title(f'Pop ini {populacaoInicial} - Idade Prod {idadeProdutiva} - Natalidade {taxa_natalidade}')

barras = False

if barras:

    wd = 0.15
    
    # ax.bar(eixox , historico_pop, width=wd)
    
    ax.bar(eixox+wd , historico_pop+cresc_pop, width=wd,color='#00B050')
    ax.bar(eixox+wd , historico_pop, width=wd,color='white')
    
    folga = 0
    ax.bar(eixox+2*wd+folga , historico_pop + cresc_pop, width=wd,color='#C00000',label='mortos por idade')
    ax.bar(eixox+2*wd+folga , historico_pop + cresc_pop - hc_velhice, width=wd,color='white')
    
    ax.bar(eixox+3*wd+folga , historico_pop + cresc_pop - hc_velhice, width=wd,color='#ED7D31',label='mortos por doenca')
    ax.bar(eixox+3*wd+folga , historico_pop + cresc_pop - hc_velhice - hc_doenca, width=wd,color='white')
    
    ax.bar(eixox+4*wd+folga , historico_pop + cresc_pop - hc_velhice - hc_doenca, width=wd,color='#FFC000',label='mortos por fome')
    ax.bar(eixox+4*wd+folga , historico_pop + cresc_pop - hc_velhice - hc_doenca - hc_inani, width=wd,color='white')
    ax.legend()


ax.set_ylim((0,historico_pop.max()+.1*historico_pop.max()))
# ax.set_xticks(range(n_interacao))
ax.set_ylabel('População')
