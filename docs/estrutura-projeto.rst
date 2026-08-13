Estrutura do projeto
====================

Esta seção explica **cada pasta do repositório** e o papel de cada módulo dentro de ``apps/``.

Visão da árvore principal
-------------------------

.. code-block:: text

   ms-escolha/
   ├── apps/              # Módulos de negócio (Django apps)
   ├── config/            # Configurações do projeto Django
   ├── docs/              # Documentação Sphinx (este material)
   ├── requirements/      # Dependências Python por ambiente
   ├── manage.py          # Ponto de entrada do Django
   ├── Dockerfile         # Imagem Docker da API
   ├── docker-compose.yml # Ambiente local (API + banco)
   └── Makefile           # Comandos úteis de desenvolvimento

Pasta ``apps/``
---------------

É onde ficam os **módulos de negócio**. Cada subpasta é um "app" Django com responsabilidade bem definida. As tabelas históricas permanecem no app Django ``escolhas`` (migrations e nomes de tabela inalterados).

``apps/core/``
~~~~~~~~~~~~~~

**O que faz:** Fornece a base comum usada por todos os outros apps.

**Para que serve:** Evita repetir código. Todo modelo do sistema herda de ``BaseModel``, que já traz:

- Identificador único (UUID)
- Data de criação
- Data da última atualização
- Campo de histórico de auditoria

Também disponibiliza a paginação padrão das listagens da API (formato SIGLA com ``links``, ``count``, ``page``, ``page_size`` e ``results``).

**Analogia:** É a "ficha padrão" que todo cadastro do sistema usa — como um formulário com campos obrigatórios no topo.

``apps/escola/``
~~~~~~~~~~~~~~~~

**O que faz:** Gerencia **DREs** e **escolas**.

**Para que serve:**

- Criar, listar, editar e excluir DREs e escolas
- Filtrar escolas por tipo de UE habilitado e por nome
- Importar cadastro oficial via SME Integração (comandos de management)

**Principais partes internas:**

.. list-table:: Módulos do app escola
   :header-rows: 1
   :widths: 35 65

   * - Subpasta / arquivo
     - Função
   * - ``models/``
     - Modelos ``Dre`` e ``Escola``
   * - ``api/views/``
     - Endpoints REST de DRE e escola
   * - ``repository.py``
     - Acesso ao banco (consultas usadas por outros apps)
   * - ``services/``
     - Integração com a SME Integração
   * - ``management/commands/``
     - Importar / atualizar DREs e escolas
   * - ``tests/``
     - Testes automatizados do app

**Exemplo:** A tela de escolha lista escolas ativas; se o tipo de UE estiver desligado na parametrização, a escola não aparece.

``apps/parametrizacao/``
~~~~~~~~~~~~~~~~~~~~~~~~

**O que faz:** Controla quais **tipos de UE** entram no fluxo.

**Para que serve:**

- Listar e atualizar o flag ``usar``
- Sincronizar tipos a partir das escolas
- Atualizar vários tipos de uma vez (bulk)

**Principais partes internas:**

.. list-table:: Módulos do app parametrizacao
   :header-rows: 1
   :widths: 35 65

   * - Subpasta / arquivo
     - Função
   * - ``models.py``
     - Modelo ``Parametrizacao``
   * - ``api/views.py``
     - Endpoints de listagem, sync e bulk
   * - ``repository.py``
     - Consultas e persistência
   * - ``serializers.py``
     - Validação e conversão dos dados da API

**Exemplo:** A gestão desmarca um tipo de UE; novas vagas desse tipo passam a ser recusadas.

``apps/vagas_escolas/``
~~~~~~~~~~~~~~~~~~~~~~~

**O que faz:** Gerencia **lotes de vagas** por processo e as vagas de cada escola/cargo.

**Para que serve:**

- Criar lote de vagas de um processo
- Incluir vagas em lote existente
- Atualizar quantidades utilizadas
- Listar vagas checadas com totais e DREs
- Excluir lotes de um processo

**Principais partes internas:**

.. list-table:: Módulos do app vagas_escolas
   :header-rows: 1
   :widths: 35 65

   * - Subpasta / arquivo
     - Função
   * - ``models/``
     - Modelos ``VagasEscolas`` e ``VagasEscolasLote``
   * - ``api/views.py``
     - Endpoints REST de vagas e ações (inclusão, utilizadas, exclusão)
   * - ``services/``
     - Regras de criação em lote e bloqueio por tipo de UE
   * - ``repository.py``
     - Consultas, agregações e persistência
   * - ``serializers.py``
     - Validação e conversão dos dados da API

**Exemplo:** O processo envia um lote; a listagem ``GET /vagas-escolas/?processo_uuid=...`` mostra só o lote mais recente, com totais de vagas e DREs.

``apps/escolhas/``
~~~~~~~~~~~~~~~~~~

**O que faz:** É o **coração** do microserviço. Registra escolhas, histórico e a extração de dados.

**Para que serve:**

- CRUD de escolhas
- Busca, reconvocação e importação Prodam
- Agrupar escolhas por cargo
- Montar extração de indicadores (ano / processo / DRE / cargo)

**Principais partes internas:**

.. list-table:: Módulos do app escolhas
   :header-rows: 1
   :widths: 35 65

   * - Subpasta / arquivo
     - Função
   * - ``models/``
     - Modelos ``Escolha`` e ``HistoricoEscolha``
   * - ``api/views/``
     - Endpoints REST de escolha e extração
   * - ``services/``
     - Extração e clientes HTTP (Candidatos / Concursos)
   * - ``repository.py``
     - Consultas, agregações e persistência
   * - ``serializers/``
     - Validação e conversão dos dados da API
   * - ``signals.py``
     - Histórico e decremento de vagas restantes
   * - ``constants.py``
     - Situações e tipos de vaga
   * - ``tests/``
     - Testes automatizados do app

**Exemplo:** O frontend envia ``POST /extracao-dados/`` com concurso e filtros por ano/processo; o app devolve totais por situação e indicadores por DRE.

Pasta ``config/``
-----------------

**O que faz:** Configurações centrais do projeto Django.

**Para que serve:**

.. list-table:: Arquivos de configuração
   :header-rows: 1
   :widths: 25 75

   * - Arquivo
     - Função
   * - ``settings.py``
     - Banco de dados, apps instalados, CORS, URLs de integração, API keys
   * - ``settings_test.py``
     - Configuração usada pelos testes automatizados
   * - ``urls.py``
     - Rotas da API (``/api/v1/``), admin, healthcheck e Swagger
   * - ``wsgi.py``
     - Ponto de entrada para servidores de produção

**Exemplo:** As variáveis ``API_KEY``, ``CANDIDATOS_API_URL`` e ``CONCURSOS_API_URL`` em ``settings.py`` dizem ao sistema como autenticar e onde buscar candidatos e concursos.

Pasta ``requirements/``
-----------------------

**O que faz:** Lista as **dependências Python** do projeto, separadas por ambiente.

**Para que serve:**

.. list-table:: Arquivos de dependências
   :header-rows: 1
   :widths: 25 75

   * - Arquivo
     - Conteúdo
   * - ``base.txt``
     - Dependências essenciais (Django, DRF, PostgreSQL, auditlog, SDK)
   * - ``local.txt``
     - Desenvolvimento (testes, lint, Sphinx, debug toolbar)
   * - ``production.txt``
     - Produção (gunicorn)

Pasta ``docs/``
---------------

**O que faz:** Contém esta documentação em formato reStructuredText (``.rst``) e a configuração do Sphinx.

**Para que serve:** Gerar o site HTML de documentação com ``make docs`` ou ``sphinx-build``.

Arquivos na raiz
----------------

.. list-table:: Arquivos na raiz do projeto
   :header-rows: 1
   :widths: 25 75

   * - Arquivo
     - Função
   * - ``manage.py``
     - Comando Django (migrações, servidor, superusuário, importações)
   * - ``docker-compose.yml``
     - Sobe API e PostgreSQL juntos
   * - ``Dockerfile``
     - Constrói a imagem Docker da API
   * - ``Makefile``
     - Atalhos: testes, lint, migrações, pre-commit e documentação
   * - ``README.md``
     - Visão técnica rápida e instruções de execução
   * - ``.pre-commit-config.yaml``
     - Hooks de qualidade (black, ruff, mypy)

API — endpoints principais (referência)
---------------------------------------

Para consulta rápida, os principais caminhos da API (prefixo ``/api/v1/``):

**DREs e escolas**

- ``GET /dres/`` — Listar DREs
- ``POST /dres/`` — Criar DRE
- ``GET /dres/{uuid}/`` — Detalhes
- ``GET /escolas/`` — Listar escolas (tipos de UE habilitados)
- ``POST /escolas/`` — Criar escola
- ``GET /escolas/{uuid}/`` — Detalhes

**Parametrização**

- ``GET /parametrizacao/`` — Listar tipos de UE
- ``PATCH /parametrizacao/{uuid}/`` — Atualizar um tipo
- ``POST /parametrizacao/sync/`` — Criar tipos faltantes a partir das escolas
- ``PATCH /parametrizacao/bulk/`` — Atualizar ``usar`` em lote

**Vagas das escolas**

- ``GET /vagas-escolas/`` — Listar vagas checadas (totais e DREs; filtro por ``processo_uuid``)
- ``POST /vagas-escolas/`` — Criar lote de vagas
- ``POST /vagas-escolas/inclusao/`` — Incluir vagas em lote existente
- ``PATCH /vagas-escolas/utilizadas/`` — Atualizar quantidades utilizadas
- ``GET /vagas-escolas/por-cargo-e-escolas/`` — Filtrar por cargo e EOLs
- ``DELETE /vagas-escolas/por-processo/`` — Excluir lotes do processo

**Escolhas**

- ``GET /escolhas/`` — Listar escolhas
- ``POST /escolhas/`` — Criar escolha
- ``GET /escolhas/{uuid}/`` — Detalhes
- ``POST /escolhas/busca/`` — Busca avançada
- ``GET /escolhas/reconvocacao/`` — Listar reconvocações
- ``GET /escolhas/buscar-candidatos/`` — Consultar candidatos no MS-Candidatos
- ``GET /escolhas/agrupar-por-cargo/`` — Totais de escolhas por cargo
- ``POST /escolhas/importacao-prodam/`` — Importar escolhas da Prodam

**Extração de dados**

- ``POST /extracao-dados/`` — Indicadores agregados (concurso, anos e processos)

A documentação interativa da API (Swagger) está disponível em ``/api/docs/`` quando o servidor está rodando.

Comandos úteis de management
----------------------------

.. list-table:: Comandos Django
   :header-rows: 1
   :widths: 40 60

   * - Comando
     - Finalidade
   * - ``criar_dres``
     - Importa / cria DREs a partir da SME Integração
   * - ``criar_escolas``
     - Importa / cria escolas a partir da SME Integração
   * - ``criar_dres_escolas``
     - Importa DREs e escolas em sequência
   * - ``atualizar_codigo_integracao_escolas``
     - Atualiza o código de integração das escolas
