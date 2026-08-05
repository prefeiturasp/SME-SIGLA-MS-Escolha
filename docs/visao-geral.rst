Visão geral
===========

O que é este módulo?
--------------------

O **Módulo Escolhas** é o sistema responsável por registrar a **escolha de vaga escolar** feita pelo candidato convocado em um concurso da SME (Secretaria Municipal de Educação de São Paulo).

Em termos simples: depois que o concurso e o processo de convocação existem, o candidato precisa **escolher uma escola** (vaga definitiva ou precária), informar que **não escolheu**, ou ser **reconvocado**. Este módulo guarda essas decisões, as vagas disponíveis por escola e os indicadores usados nos painéis de extração de dados.

Para que serve?
---------------

O sistema permite que a equipe da SME:

- **Cadastre e consulte escolas e DREs** (código EOL, nome oficial, tipo de UE)
- **Parametrize quais tipos de unidade escolar** entram no fluxo de escolha
- **Importe e gerencie lotes de vagas** por processo de convocação (definitivas e precárias)
- **Registre escolhas** de candidatos (escolha, não-escolha ou reconvocação)
- **Acompanhe o histórico** de mudança de situação de cada escolha
- **Extraia indicadores** por ano, processo, DRE e cargo (dashboard / relatórios)
- **Integre com outros módulos** (Candidatos, Concursos, Convocação e SME Integração)

Onde ele se encaixa no ecossistema SIGLA?
-----------------------------------------

Este módulo **não trabalha sozinho**. Ele se integra com outros sistemas:

.. list-table:: Integrações do ecossistema
   :header-rows: 1
   :widths: 30 70

   * - Sistema
     - Papel no processo de escolhas
   * - **API SME Integração**
     - Fonte oficial de DREs e escolas (importação em lote)
   * - **Módulo Candidatos**
     - Identifica o candidato (CPF, nome, processo) na busca e na importação
   * - **Módulo Processos de Concursos**
     - Fornece concursos e nomes de cargos; consome totais de escolhas por cargo
   * - **Módulo Processos de Convocação**
     - Define o processo cujas vagas e escolhas são agrupadas
   * - **Frontend SIGLA**
     - Interface usada pela equipe e pelo fluxo de escolha de vaga

O Módulo Escolhas é a **referência central** de vagas escolares escolhidas e dos indicadores de extração usados pelos demais fluxos do SIGLA.

Exemplo prático do dia a dia
----------------------------

Imagine o seguinte cenário:

1. A SME importa as **escolas e DREs** oficiais (código EOL, tipo de UE).
2. A equipe **habilita os tipos de UE** que entram no fluxo (ex.: EMEF sim, outro tipo não).
3. Um **processo de convocação** envia um lote de vagas por escola e cargo (definitivas e precárias).
4. O candidato convocado **escolhe** uma vaga na escola X, do tipo definitiva.
5. O sistema registra a escolha, grava o **histórico** e **diminui as vagas restantes** daquela escola/cargo.
6. Se o candidato não comparece ou recusa, a situação pode virar **não-escolha** ou **reconvocação**.
7. No painel de extração, a gestão vê quantas escolhas houve no ano, por DRE e por cargo, e compara com as vagas ofertadas.

Fluxo resumido
--------------

.. code-block:: text

   SME Integração  ----->  Importar DREs e escolas
                                    |
                                    v
                           Parametrizar tipos de UE
                           (quais unidades entram no fluxo)
                                    |
                                    v
                           Receber lote de vagas
                           (por processo / cargo / escola)
                                    |
                                    v
                           Candidato escolhe vaga
                           (ou não-escolha / reconvocação)
                                    |
              +---------------------+---------------------+
              |                                           |
              v                                           v
     Histórico + vagas restantes               Extração / dashboard
     (auditoria operacional)                   (por ano, DRE e cargo)
                                                          |
                                                          v
                                               Outros módulos SIGLA
                                               (ex.: concursos)

Tecnologias utilizadas (referência rápida)
------------------------------------------

Para quem precisa de contexto técnico sem entrar no código:

- **Django** — framework web que estrutura o projeto
- **Django REST Framework** — expõe a API consumida pelo frontend
- **PostgreSQL** — banco de dados onde ficam escolas, vagas e escolhas
- **django-auditlog** — registra quem alterou o quê e quando
- **drf-spectacular** — documentação interativa da API (Swagger)
- **sigla-sdk** — correlação de logs, cliente HTTP e autenticação entre microserviços
