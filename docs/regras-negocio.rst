Regras de negócio
=================

Esta seção descreve as **regras que o sistema aplica** — ou seja, o que pode e o que não pode acontecer no cadastro de escolas, vagas e escolhas.

Escola e DRE
------------

O que é
~~~~~~~

Uma **DRE** (Diretoria Regional de Educação) agrupa escolas de uma região. Uma **escola** é a unidade escolar identificada principalmente pelo **código EOL**.

Cada escola guarda, entre outros dados:

- Código EOL
- Nome oficial
- Tipo de UE (tipo de unidade escolar)
- DRE vinculada
- Bairro, logradouro e demais dados cadastrais

Regras importantes
~~~~~~~~~~~~~~~~~~

- O **código EOL** identifica a escola na importação de vagas e na integração.
- A listagem de escolas da API considera apenas tipos de UE **habilitados** na parametrização.
- Se nenhum tipo de UE estiver com ``usar=True``, a listagem de escolas **fica vazia**.
- É possível filtrar escolas pelo nome oficial e pelo código da DRE.

Parametrização de tipo de UE
----------------------------

O que é
~~~~~~~

A **parametrização** controla quais **tipos de unidade escolar** entram no fluxo de escolha (ex.: EMEF, EMEI).

Cada registro guarda:

- Tipo de UE (único)
- Flag **usar** (sim / não)

Regras importantes
~~~~~~~~~~~~~~~~~~

- Novos tipos de UE surgem a partir das escolas cadastradas (sincronização).
- A criação avulsa via ``POST /parametrizacao/`` **não é permitida**.
- A atualização em lote altera só o campo ``usar``.
- Tipos com ``usar=False`` **não aparecem** na listagem de escolas e **bloqueiam** a criação de vagas daquele tipo.

Vagas das escolas
-----------------

O que é
~~~~~~~

Uma **vaga de escola** representa a oferta de um **cargo** em uma **escola**, dentro de um **lote de processo** de convocação.

Cada registro guarda:

- Escola e lote (processo / concurso)
- Código e descrição do cargo
- Vagas **definitivas** e **precárias** (ofertadas, utilizadas e restantes)
- Se a vaga está **checada** e se já foi utilizada

O **lote** agrupa as vagas de um mesmo ``processo_uuid`` (e opcionalmente um concurso).

Regras importantes
~~~~~~~~~~~~~~~~~~

- Na criação em lote, a escola é localizada pelo **código EOL** (com zeros à esquerda, 6 dígitos).
- Se a escola não existir, aquele item falha e os demais podem seguir.
- Se o tipo de UE da escola estiver **desabilitado**, a criação do lote é **bloqueada**.
- A listagem por processo usa o **lote mais recente** daquele ``processo_uuid``.
- Só entram na listagem agregada as vagas com ``esta_checada=True``.
- Se houver quantidades **utilizadas** preenchidas, os totais da listagem usam utilizadas; senão, usam as ofertadas.
- É possível incluir mais vagas em um lote existente, atualizar utilizadas e excluir lotes (e vagas em cascata) por processo.

Escolha
-------

O que é
~~~~~~~

Uma **escolha** registra a decisão do candidato em relação a uma vaga escolar de um concurso/processo.

Cada registro guarda:

- UUID do candidato
- UUID do concurso
- Situação
- Tipo de vaga (definitiva ou precária)
- Se é retardatário
- Vaga da escola (quando houver)

Situações da escolha
~~~~~~~~~~~~~~~~~~~~

.. list-table:: Situações da escolha
   :header-rows: 1
   :widths: 25 75

   * - Situação
     - Significado
   * - **Escolha**
     - O candidato escolheu uma vaga escolar
   * - **Não-escolha**
     - O candidato não escolheu vaga naquele momento
   * - **Reconvocação**
     - O candidato volta ao fluxo para nova oportunidade de escolha

Tipos de vaga
~~~~~~~~~~~~~

.. list-table:: Tipos de vaga
   :header-rows: 1
   :widths: 25 75

   * - Tipo
     - Significado
   * - **Definitiva**
     - Vaga permanente da unidade
   * - **Precária**
     - Vaga temporária / precária da unidade

Regras importantes sobre escolha
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Ao **criar** uma escolha com situação **escolha** e tipo de vaga preenchido, o sistema **decrementa as vagas restantes** (definitivas ou precárias), sem ficar negativo.
- Toda criação ou mudança de situação gera um registro de **histórico**.
- A reconvocação lista candidatos em situação de reconvocação para um concurso.
- A importação Prodam localiza o candidato por CPF e a vaga por código EOL + código do cargo.
- Se o candidato ou a vaga não forem encontrados na importação, o item é reportado como erro e os demais podem seguir.
- O agrupamento por cargo conta apenas escolhas na situação **escolha**.

Histórico
---------

Cada alteração relevante de situação fica no **histórico da escolha** (situação anterior → situação nova). Isso permite auditar o caminho do candidato sem depender só do estado atual.

Extração de dados
-----------------

A **extração de dados** monta indicadores de escolhas para relatórios e painéis.

Como funciona
~~~~~~~~~~~~~

1. O usuário (ou o frontend) informa, opcionalmente:

   - Um **concurso** (``concurso_uuid``)
   - Uma lista de **filtros** ``{ano, processo_uuids}``

2. Com filtros, o resultado vem **separado por ano**, com:

   - Totais por situação (escolha / reconvocação / não-escolha)
   - Indicadores por DRE (escolhas e vagas ofertadas)
   - Metadados de ``concurso_uuid`` e ``filtros``

3. Sem filtros, o resultado é um único bloco agregado na raiz.

4. Sempre há:

   - ``dres_concursos`` — detalhe por concurso, DRE e cargo
   - ``ultima_escolha_em`` — data/hora da última escolha com vaga no escopo

Com ``processo_uuids``, escolhas **com vaga** entram pelo processo do lote; escolhas **sem vaga** usam o ano de ``criado_em``. Assim a extração alinha ao ano do processo de convocação, como candidatos e vagas.

Auditoria
---------

Alterações em escolas, parametrizações, vagas e escolhas são **registradas automaticamente** (quem alterou, quando e o que mudou), além do histórico operacional da escolha.
