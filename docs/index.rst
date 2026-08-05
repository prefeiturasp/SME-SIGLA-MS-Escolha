Documentação — Módulo Escolhas
==============================

Bem-vindo à documentação do **módulo de Escolhas** da SIGLA (SME/PMSP).

Este material foi escrito para facilitar o entendimento de **gestores, analistas de negócio e novos desenvolvedores** — com linguagem clara, exemplos do dia a dia e foco no *porquê* de cada parte do sistema.

.. toctree::
   :maxdepth: 2
   :caption: Conteúdo

   visao-geral
   regras-negocio
   estrutura-projeto

Como gerar o HTML
-----------------

Com o ambiente virtual ativo e as dependências de desenvolvimento instaladas:

.. code-block:: bash

   make docs

Ou diretamente:

.. code-block:: bash

   sphinx-build -b html docs/ docs/_build/html

O site gerado ficará em ``docs/_build/html/index.html``.
