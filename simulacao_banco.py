# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 10:13:58 2021

@author: Mauro Rebelo
"""

# Simulação da situação do atendimento bancário com fila única e dois atendimentos com processos 
# Markovianos de chegado (M/M/2).
# Baseado no texto de JAIN, B. disponível em: https://towardsdatascience.com/simulating-a-queuing-system-in-python-8a7d1151d485

#%% Setup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import scipy


#%% Classe: Simulação do Banco
# Aqui precisamos entender quais vão ser os atributos importantes e que iremos acompanhar para a execução
# No momento de definir a classe e seus métodos vou comentar a relevancia de cada um deles
# Passagem de tempo na simulação será por eventos (o relógio avança até o momento do evento seguinte e não continuamente)
class Simulation:
    def __init__(self):
        self.clock = 0.00                                                      # momento inicial - relógio em 0.00
        self.num_chegadas = 0                                                  # quantidade de clientes que entraram no banco
        self.n_sistema = 0                                                   # número de pessoas no sistema atualmente
        self.t_saida_cx1 = float('inf')                                        # Momento em que havera uma saida em algum dos caixas
        self.t_saida_cx2 = float('inf')                                        #no momento inicial o bco está vazio e nao podemos ter o prox evento sendo uma saída
        self.t_chegada = self.gen_chegada()                                    # vamos definir um metodo para a proxima chegada
        self.soma_ta_cx1 = 0                                                      # tempo total de atendimento operador 1
        self.soma_ta_cx2 = 0                                                      # tempo total de atendimento operador 2
        self.estado_cx1 =0                                                     # estado do operador 1
        self.estado_cx2 =0                                                     # estado do operador 2
        self.tte = 0.00                                                        # tempo total de espera no sistema
        self.n_cli_em_fila = 0                                                   # num de clientes em fila no estado ATUAL
        self.soma_cli_em_fila = 0                                              # número de clientes que precisou de ficar em fila
        self.saidas_cx1 = 0                                                    # clientes atendidos pelo op 1
        self.saidas_cx2 = 0                                                    # clientes atendidos pelo op 1
        self.desistencias = 0                                                  # clientes que desistiram do atendimento
        self.fila_maxima = 0
    
    # Vamos definir qual é o próximo evento do sistema
    def avanca_relogio(self):
        # o calculo evento seguinte entende que todos os eventos ja tem momentos definidos para ocorrerem
        t_prox_evento = min(self.t_chegada,self.t_saida_cx1,self.t_saida_cx2)
        # atualizacao do tempo de espera
        # A logica é que se duas pessoas esperaram 10 segundos, o tempo de espera do sistema foi de 20 segundos
        self.tte += self.n_cli_em_fila * ( t_prox_evento - self.clock )
        # Atualizar o relogio
        self.clock = t_prox_evento
        
        # Dependendo de qual for o proximo evento, iremos chamar um método diferente
        # Importante notar que existem 3 tipos de evento:
        # Chegada, Fim do atendimento do Op 1 e Fim do atendimento do Op 2
        # Caso 1:  o próximo evento é uma chegada
        if self.t_chegada < self.t_saida_cx1 and self.t_chegada<self.t_saida_cx2:
            self.chegada()
        # Caso 2:  o próximo evento é uma finalizacao em CX1
        elif self.t_saida_cx1 < self.t_chegada and self.t_saida_cx1 < self.t_saida_cx2:
            self.operador1()
        # Caso 3:  o próximo evento é uma finalizacam em CX2
        else:
            self.operador2()

    # Agora iniciaremos a definição dos eventos
    ## Chegada
    def chegada(self):
        self.num_chegadas += 1
        self.n_sistema += 1

        
        # O sistema define se no momento em que o cliente chega, ele fica em fila, é atendido ou desiste da visita
        # Caso 1: Não há ninguém em fila
        if self.n_cli_em_fila == 0:
            # Caso 1.1: Dois operadores ocupados -> fila
            if self.estado_cx1 == 1 and self.estado_cx2 == 1:
                self.n_cli_em_fila += 1
                self.soma_cli_em_fila += 1
                #Atualiza o  momento da proxima chegada:
                self.t_chegada = self.clock + self.gen_chegada()

            # Caso 1.2: Ambos operadores livres
            elif self.estado_cx1 == 0 and self.estado_cx2 == 0:
                # escolhe para onde vai:
                n_escolha =  np.random.choice([0,1])
                if n_escolha == 0: #escolha o op 1
                    self.estado_cx1 = 1
                    self.dep1 = self.gen_ta_cx1()
                    self.soma_ta_cx1 += self.dep1
                    # Atualizar o evento de saída em CX1
                    self.t_saida_cx1 = self.clock + self.dep1
                    #Atualiza o  momento da proxima chegada:
                    self.t_chegada = self.clock+self.gen_chegada()
                else: #escolha o op 2
                    self.estado_cx2 = 1
                    self.dep2 = self.gen_ta_cx2()
                    self.soma_ta_cx2 += self.dep2
                    # Atualizar o evento de saída em CX2
                    self.t_saida_cx2 = self.clock + self.dep2
                    #Atualiza o  momento da proxima chegada:
                    self.t_chegada = self.clock+self.gen_chegada()

            # Caso 3: CX1 livre, CX2 ocupado
            elif self.estado_cx1 == 0 and self.estado_cx2 == 1:
                self.estado_cx1 = 1
                self.dep1 = self.gen_ta_cx1()
                self.soma_ta_cx1 += self.dep1
                # Atualizar o evento de saída em CX1
                self.t_saida_cx1 = self.clock + self.dep1
                #Atualiza o  momento da proxima chegada:
                self.t_chegada = self.clock+self.gen_chegada()

            # Caso 4: CX1 ocupado, CX2 livre
            else:
                self.estado_cx2 = 1
                self.dep2 = self.gen_ta_cx2()
                self.soma_ta_cx2 += self.dep2
                # Atualizar o evento de saída em CX2
                self.t_saida_cx2 = self.clock + self.dep2
                #Atualiza o  momento da proxima chegada:
                self.t_chegada = self.clock+self.gen_chegada()

        #Caso 2: Há de 1 a 3 clientes em fila:
        elif self.n_cli_em_fila >= 1 and self.n_cli_em_fila <= 3:
            self.n_cli_em_fila += 1
            self.soma_cli_em_fila += 1
            self.t_chegada = self.clock + self.gen_chegada()
        
        #Caso 3: Há exatamente 4 clientes na fila
        elif self.n_cli_em_fila == 4:
            #50% de chance de ficar
            fica = np.random.choice([0,1])
            if fica == 1:
                self.n_cli_em_fila += 1
                self.soma_cli_em_fila += 1
                self.t_chegada = self.clock + self.gen_chegada()
            else:
                self.desistencias += 1
                self.t_chegada = self.clock + self.gen_chegada()
        #Caso 4: há 5 ou mais clientes na fila
        else:
            #40% de chance de ficar
            fica = np.random.choice([0,1],p=[0.6,0.4])
            if fica == 1:
                self.n_cli_em_fila += 1
                self.soma_cli_em_fila += 1
                self.t_chegada = self.clock + self.gen_chegada()
            else:
                self.desistencias += 1
                self.t_chegada = self.clock + self.gen_chegada()

        self.fila_maxima = max(self.n_cli_em_fila,self.fila_maxima)
        
    def operador1(self):
        #Finalização do atendimento do operador 1
        self.saidas_cx1 += 1
        if self.n_cli_em_fila > 0:
            self.n_cli_em_fila -= 1
            self.dep1 = self.gen_ta_cx1()
            self.soma_ta_cx1 += self.dep1
            # Atualizar o evento de saída em CX1
            self.t_saida_cx1 = self.clock + self.dep1
        else:
            self.t_saida_cx1 = float('inf')
            self.estado_cx1 = 0

    def operador2(self):
        self.saidas_cx2 += 1
        if self.n_cli_em_fila > 0:
            self.n_cli_em_fila -= 1
            self.dep2 = self.gen_ta_cx2()
            self.soma_ta_cx2 += self.dep2
            # Atualizar o evento de saída em CX1
            self.t_saida_cx2 = self.clock + self.dep1
        else:
            self.t_saida_cx2 = float('inf')
            self.estado_cx2 = 0

    # Geradores de tempos aleatorios
    # Aqui vamos usar tempos exponenciais:
    # f(x) =  lambda * exp(-lambda*x)
    # F(x) = 1 - exp(-lambda*x)
    # F-1(q) = -(1/lambda)*ln(1-q)

    def gen_chegada(self):
        ld = 1/2 #Lambda é o inverso da média
        q = np.random.uniform()
        return -(1/ld) * np.log(1-q)
        
    def gen_ta_cx1(self):
        ld = 1/4 #Lambda é o inverso da média
        q = np.random.uniform()
        return -(1/ld) * np.log(1-q)

    def gen_ta_cx2(self):
        ld = 1/4 #Lambda é o inverso da média
        q = np.random.uniform()
        return -(1/ld) * np.log(1-q)
    
    def __repr__(self):
        # Caso a simulação não tenha sido rodada, retornar vazio
        if self.clock == 0:
            return f'Simulation nao iniciada'
        else:
            # TODO Montar repr
            return f'Simulacao OK'

#%% Rodar a simulação
s = Simulation()
fila_cum = []
espera_cum = []
fila = []
relogio =[]

while s.clock < 6*60:
    s.avanca_relogio()
    relogio.append(s.clock)
    fila_cum.append(s.soma_cli_em_fila)
    fila.append(s.n_cli_em_fila)
    espera_cum.append(s.tte)

print(f'Numero de chegadas: {s.num_chegadas}')

fig,(ax1,ax2,ax3)=plt.subplots(3,1,figsize=(20,10))
ax1.plot(relogio,fila_cum)
ax1.set_title('Fila acumulada')

ax2.plot(relogio,fila,'--x',linewidth=.5)
ax2.set_title('Fila instantânea')

ax3.plot(relogio,espera_cum,'-',linewidth=.5)
ax3.set_title('Tempo de espera acumulado')

plt.show()
print(f'Fila maxima: {s.fila_maxima}')

# %% Stress test

n_rodadas = 1000
filas_maximas = []
ttes = []
fila_media = []

progresso = False

for i in range(n_rodadas):
    sim = Simulation()
    fila_instantanea = []
    while sim.clock < 6*60:
        sim.avanca_relogio()
        fila_instantanea.append(sim.n_cli_em_fila)
    filas_maximas.append(sim.fila_maxima)
    fila_media.append( sum(fila_instantanea)/len(fila_instantanea) )
    ttes.append(sim.tte)
    if progresso:
        if i%10==0:
            print(f'Simulação {i}/{n_rodadas} concluida')
    
print(f'Fila máxima média: {sum(filas_maximas)/len(filas_maximas)}')
print(f'Máxima fila máxima: {max(filas_maximas)}')
print()
print(f'TTE médio: {sum(ttes)/len(ttes):.2f}')
print(f'Máximo TTE: {max(ttes):.2f}')

StressTest = pd.DataFrame({
    'simulacao':range(1,n_rodadas+1),
    'fila_max' : filas_maximas,
    'fila_media': fila_media,
    'tte': ttes
})

fig,ax = plt.subplots(1,2,figsize=(16,9))

fig.suptitle('Stress Test', fontsize=14)

ax[0].scatter(StressTest.tte,StressTest.fila_media)
ax[0].set_xlabel('Tempo Total de Espera')
ax[0].set_ylabel('Fila média')
ax[0].set_title('Fila X TTE')

ax[1].scatter(StressTest.fila_max,StressTest.fila_media)
ax[1].set_xlabel('Fila Máxima')
ax[1].set_ylabel('Fila média')
ax[1].set_title('Fila')


plt.show()
# %%
