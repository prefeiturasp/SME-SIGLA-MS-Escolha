"""Contrato da documentação OpenAPI (Swagger) do microsserviço."""

from io import StringIO

import pytest
from django.core.management import call_command
from drf_spectacular.drainage import GENERATOR_STATS
from drf_spectacular.generators import SchemaGenerator

METODOS_HTTP = {"get", "post", "put", "patch", "delete"}
TEXTOS_PADRAO_DO_GERADOR = (
    "A UUID string identifying",
    "A unique integer value identifying",
    "Which field to use when ordering",
    "A search term",
    "A page number within",
    "Number of results to return",
)

LISTA_SIMPLES = {"200", "403", "500"}
LISTA_PAGINADA = {"200", "403", "404", "500"}
CONSULTA = {"200", "400", "403", "500"}
CRIACAO = {"201", "400", "403", "500"}
LEITURA = {"200", "403", "404", "500"}
GRAVACAO = {"200", "400", "403", "404", "500"}
EXCLUSAO = {"204", "403", "404", "500"}

RESPOSTAS_ESPERADAS = {
    "listar_dres": LISTA_PAGINADA,
    "criar_dre": CRIACAO,
    "detalhar_dre": LEITURA,
    "atualizar_dre": GRAVACAO,
    "atualizar_parcial_dre": GRAVACAO,
    "excluir_dre": EXCLUSAO,
    "listar_escolas": LISTA_PAGINADA,
    "criar_escola": {"400", "403", "500"},
    "detalhar_escola": LEITURA,
    "atualizar_escola": GRAVACAO,
    "atualizar_parcial_escola": GRAVACAO,
    "excluir_escola": EXCLUSAO,
    "listar_parametrizacoes": LISTA_SIMPLES,
    "detalhar_parametrizacao": LEITURA,
    "atualizar_parametrizacao": GRAVACAO,
    "atualizar_parcial_parametrizacao": GRAVACAO,
    "atualizar_parametrizacoes_em_lote": CONSULTA,
    "sincronizar_parametrizacoes": LISTA_SIMPLES,
    "listar_vagas_escolas": CONSULTA,
    "criar_vagas_escolas_em_lote": {"201", "207", "400", "403", "500"},
    "detalhar_vaga_escola": LEITURA,
    "atualizar_vaga_escola": GRAVACAO,
    "atualizar_parcial_vaga_escola": GRAVACAO,
    "excluir_vaga_escola": EXCLUSAO,
    "atualizar_vagas_utilizadas": CONSULTA,
    "incluir_vagas_no_lote": {"201", "207", "400", "403", "404", "500"},
    "listar_vagas_por_cargo_e_escolas": LISTA_SIMPLES,
    "excluir_vagas_por_processo": CONSULTA,
    "listar_escolhas": {"200", "400", "403", "404", "500"},
    "criar_escolha": CRIACAO,
    "detalhar_escolha": LEITURA,
    "atualizar_escolha": GRAVACAO,
    "atualizar_parcial_escolha": GRAVACAO,
    "excluir_escolha": EXCLUSAO,
    "buscar_escolhas_por_candidatos": CONSULTA,
    "agregar_escolhas_por_convocacao": CONSULTA,
    "listar_escolhas_reconvocacao": LISTA_SIMPLES,
    "buscar_candidatos": CONSULTA,
    "contar_escolhas_por_cargo": LISTA_SIMPLES,
    "importar_escolhas_prodam": CRIACAO,
    "extrair_dados_escolhas": CONSULTA,
}
ERRO_INTERNO_COM_CORPO = {"criar_vagas_escolas_em_lote"}

CORPOS_EM_LOTE = {
    "atualizar_parametrizacoes_em_lote": ["usar", "uuid"],
    "atualizar_vagas_utilizadas": ["foi_utilizada", "uuid"],
}
LISTAS_SEM_PAGINACAO = (
    "buscar_escolhas_por_candidatos",
    "listar_escolhas_reconvocacao",
    "buscar_candidatos",
    "listar_vagas_por_cargo_e_escolas",
)

TIPOS_JSON = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "object": dict,
    "array": list,
}

COMPONENTES_TESTE = {
    "Situacao": {"type": "string", "enum": ["ABERTO", "FECHADO"]},
    "Item": {
        "type": "object",
        "properties": {
            "uuid": {"type": "string", "readOnly": True},
            "nome": {"type": "string"},
            "vagas": {"type": "integer"},
            "situacao": {
                "allOf": [{"$ref": "#/components/schemas/Situacao"}],
                "description": "Situação do item.",
            },
            "observacao": {"type": "string", "nullable": True},
        },
        "required": ["uuid", "nome", "situacao"],
    },
}
REF_ITEM = {"$ref": "#/components/schemas/Item"}
ITEM_VALIDO = {"uuid": "u", "nome": "n", "situacao": "ABERTO"}


def _sem_pendencias(pendencias):
    assert not pendencias, "\n" + "\n".join(pendencias)


def _corpos_json(operacao):
    """Devolve (origem, conteúdo JSON, é requisição) de cada corpo."""
    corpos = []
    requisicao = (
        operacao.get("requestBody", {})
        .get("content", {})
        .get("application/json")
    )
    if requisicao:
        corpos.append(("requisição", requisicao, True))
    for codigo, resposta in operacao["responses"].items():
        conteudo = resposta.get("content", {}).get("application/json")
        if conteudo:
            corpos.append((f"resposta {codigo}", conteudo, False))
    return corpos


def _violacoes(valor, esquema, componentes, caminho="$", *, requisicao=False):
    """Lista o que impede ``valor`` de seguir ``esquema`` (OpenAPI 3.0)."""
    if "$ref" in esquema:
        alvo = componentes[esquema["$ref"].rsplit("/", 1)[-1]]
        return _violacoes(
            valor, alvo, componentes, caminho, requisicao=requisicao
        )
    if "oneOf" in esquema:
        tentativas = [
            _violacoes(
                valor, alternativa, componentes, caminho, requisicao=requisicao
            )
            for alternativa in esquema["oneOf"]
        ]
        if any(not tentativa for tentativa in tentativas):
            return []
        return [f"{caminho}: não segue nenhuma alternativa de oneOf"]
    if valor is None and esquema.get("nullable"):
        return []
    if "allOf" in esquema:
        return [
            violacao
            for parte in esquema["allOf"]
            for violacao in _violacoes(
                valor, parte, componentes, caminho, requisicao=requisicao
            )
        ]
    if "enum" in esquema:
        if valor in esquema["enum"]:
            return []
        return [f"{caminho}: {valor!r} fora do enum {esquema['enum']}"]
    if valor is None:
        return [f"{caminho}: nulo não permitido"]
    tipo = esquema.get("type")
    if tipo is None:
        return []
    booleano_indevido = isinstance(valor, bool) and tipo != "boolean"
    if booleano_indevido or not isinstance(valor, TIPOS_JSON[tipo]):
        return [f"{caminho}: esperado {tipo}, veio {type(valor).__name__}"]
    if tipo == "array":
        return [
            violacao
            for indice, item in enumerate(valor)
            for violacao in _violacoes(
                item,
                esquema.get("items", {}),
                componentes,
                f"{caminho}[{indice}]",
                requisicao=requisicao,
            )
        ]
    propriedades = esquema.get("properties")
    adicionais = esquema.get("additionalProperties")
    chaves_dinamicas = isinstance(adicionais, dict)
    if tipo != "object" or (propriedades is None and not chaves_dinamicas):
        return []
    propriedades = propriedades or {}
    somente_leitura = {
        nome for nome, campo in propriedades.items() if campo.get("readOnly")
    }
    obrigatorios = set(esquema.get("required", []))
    if requisicao:
        obrigatorios -= somente_leitura
    violacoes = [
        f"{caminho}.{nome}: obrigatório ausente"
        for nome in sorted(obrigatorios - set(valor))
    ]
    for nome in sorted(set(valor) - set(propriedades)):
        if chaves_dinamicas:
            violacoes += _violacoes(
                valor[nome],
                adicionais,
                componentes,
                f"{caminho}.{nome}",
                requisicao=requisicao,
            )
        elif adicionais is not True:
            violacoes.append(f"{caminho}.{nome}: campo fora do modelo")
    for nome in sorted(set(valor) & set(propriedades)):
        violacoes += _violacoes(
            valor[nome],
            propriedades[nome],
            componentes,
            f"{caminho}.{nome}",
            requisicao=requisicao,
        )
    return violacoes


@pytest.fixture(scope="module")
def schema():
    """Gera o schema OpenAPI completo a partir das rotas reais."""
    return SchemaGenerator().get_schema(request=None, public=True)


@pytest.fixture(scope="module")
def operacoes(schema):
    """Reúne (rótulo, operação) de todas as operações do schema."""
    return [
        (f"{metodo.upper()} {caminho}", operacao)
        for caminho, item in schema["paths"].items()
        for metodo, operacao in item.items()
        if metodo in METODOS_HTTP
    ]


@pytest.fixture(scope="module")
def por_identificador(operacoes):
    """Indexa as operações pelo ``operationId``."""
    return {operacao["operationId"]: operacao for _, operacao in operacoes}


@pytest.mark.parametrize(
    ("valor", "requisicao", "esperado"),
    [
        (ITEM_VALIDO, False, []),
        ({"nome": "n", "situacao": "ABERTO"}, True, []),
        (
            {"nome": "n", "situacao": "ABERTO"},
            False,
            ["$.uuid: obrigatório ausente"],
        ),
        (
            {**ITEM_VALIDO, "situacao": "X"},
            False,
            ["$.situacao: 'X' fora do enum ['ABERTO', 'FECHADO']"],
        ),
        (
            {**ITEM_VALIDO, "vagas": "3"},
            False,
            ["$.vagas: esperado integer, veio str"],
        ),
        (
            {**ITEM_VALIDO, "vagas": True},
            False,
            ["$.vagas: esperado integer, veio bool"],
        ),
        (
            {**ITEM_VALIDO, "extra": 1},
            False,
            ["$.extra: campo fora do modelo"],
        ),
        (
            {**ITEM_VALIDO, "nome": None},
            False,
            ["$.nome: nulo não permitido"],
        ),
        ({**ITEM_VALIDO, "observacao": None}, False, []),
    ],
)
def test_violacoes_apontam_divergencia_entre_exemplo_e_modelo(
    valor, requisicao, esperado
):
    """Exemplo fora do modelo é apontado com o caminho do campo."""
    assert (
        _violacoes(valor, REF_ITEM, COMPONENTES_TESTE, requisicao=requisicao)
        == esperado
    )


def test_violacoes_percorrem_listas_e_alternativas():
    """Itens de lista e alternativas de ``oneOf`` também são conferidos."""
    lista = {"type": "array", "items": REF_ITEM}
    alternativas = {"oneOf": [REF_ITEM, lista]}

    assert _violacoes([ITEM_VALIDO], alternativas, COMPONENTES_TESTE) == []
    assert _violacoes(
        [ITEM_VALIDO, {**ITEM_VALIDO, "vagas": 1.5}],
        lista,
        COMPONENTES_TESTE,
    ) == ["$[1].vagas: esperado integer, veio float"]
    assert _violacoes("texto", alternativas, COMPONENTES_TESTE) == [
        "$: não segue nenhuma alternativa de oneOf"
    ]


def test_violacoes_conferem_chaves_dinamicas():
    """Chaves fora de ``properties`` seguem ``additionalProperties``."""
    mapa = {"type": "object", "additionalProperties": REF_ITEM}
    misto = {
        "type": "object",
        "properties": {"fixo": {"type": "integer"}},
        "additionalProperties": REF_ITEM,
    }
    aberto = {
        "type": "object",
        "properties": {"fixo": {"type": "integer"}},
        "additionalProperties": True,
    }

    assert _violacoes({"a": ITEM_VALIDO}, mapa, COMPONENTES_TESTE) == []
    assert _violacoes(
        {"a": {**ITEM_VALIDO, "vagas": "3"}}, mapa, COMPONENTES_TESTE
    ) == ["$.a.vagas: esperado integer, veio str"]
    assert (
        _violacoes({"fixo": 1, "2025": ITEM_VALIDO}, misto, COMPONENTES_TESTE)
        == []
    )
    assert _violacoes({"fixo": 1, "2025": 5}, misto, COMPONENTES_TESTE) == [
        "$.2025: esperado object, veio int"
    ]
    assert _violacoes({"fixo": 1, "outro": 5}, aberto, COMPONENTES_TESTE) == []


def test_tamanho_de_pagina_documentado_e_o_real():
    """O tamanho de página citado na documentação é o da paginação."""
    from core.openapi import TAMANHO_PAGINA_PADRAO
    from core.utils import DEFAULT_PAGE_SIZE

    assert TAMANHO_PAGINA_PADRAO == DEFAULT_PAGE_SIZE


def test_schema_valido_sem_avisos():
    """Toda view é introspectável e o documento é OpenAPI válido."""
    GENERATOR_STATS.reset()
    call_command(
        "spectacular", "--validate", "--fail-on-warn", stdout=StringIO()
    )


def test_inventario_de_operacoes(operacoes):
    """Todo endpoint exposto está no inventário documentado."""
    identificadores = sorted(
        operacao["operationId"] for _, operacao in operacoes
    )
    assert identificadores == sorted(RESPOSTAS_ESPERADAS)


def test_operacao_tem_resumo_descricao_e_tag(schema, operacoes):
    """Toda operação tem resumo, descrição e uma tag declarada."""
    tags_declaradas = {tag["name"] for tag in schema.get("tags", [])}
    pendencias = []
    for rotulo, operacao in operacoes:
        tags = operacao.get("tags", [])
        if not operacao.get("summary"):
            pendencias.append(f"{rotulo}: sem resumo")
        if not operacao.get("description"):
            pendencias.append(f"{rotulo}: sem descrição")
        if len(tags) != 1 or tags[0] not in tags_declaradas:
            pendencias.append(f"{rotulo}: tag não declarada {tags}")
    _sem_pendencias(pendencias)


def test_parametros_tem_tipo_e_descricao(operacoes):
    """Todo parâmetro de rota e de query tem tipo e descrição própria."""
    pendencias = []
    for rotulo, operacao in operacoes:
        for parametro in operacao.get("parameters", []):
            nome = f"{rotulo} › {parametro['in']} {parametro['name']}"
            descricao = parametro.get("description", "")
            if not descricao:
                pendencias.append(f"{nome}: sem descrição")
            elif descricao.startswith(TEXTOS_PADRAO_DO_GERADOR):
                pendencias.append(f"{nome}: texto padrão do gerador")
            if "type" not in parametro.get("schema", {}):
                pendencias.append(f"{nome}: sem tipo")
    _sem_pendencias(pendencias)


def test_campos_dos_modelos_tem_descricao(schema):
    """Todo campo de todo modelo de request e response tem descrição."""
    pendencias = [
        f"{nome}.{campo}"
        for nome, componente in schema["components"]["schemas"].items()
        for campo, definicao in componente.get("properties", {}).items()
        if not definicao.get("description")
    ]
    _sem_pendencias(pendencias)


def test_modelos_tem_descricao_para_quem_consome(schema):
    """Todo modelo é descrito sem expor termos de implementação."""
    pendencias = []
    for nome, componente in schema["components"]["schemas"].items():
        if "properties" not in componente:
            continue
        descricao = componente.get("description", "")
        if not descricao:
            pendencias.append(f"{nome}: sem descrição")
        elif "serializer" in descricao.lower():
            pendencias.append(f"{nome}: cita implementação ({descricao})")
    _sem_pendencias(pendencias)


def test_codigos_de_resposta(operacoes):
    """Cada operação documenta exatamente os códigos HTTP que retorna."""
    pendencias = []
    for rotulo, operacao in operacoes:
        esperados = RESPOSTAS_ESPERADAS.get(operacao["operationId"], set())
        obtidos = set(operacao["responses"])
        if obtidos != esperados:
            pendencias.append(
                f"{rotulo}: {sorted(obtidos)} != {sorted(esperados)}"
            )
    _sem_pendencias(pendencias)


def test_respostas_tem_descricao_e_modelo(operacoes):
    """Toda resposta é descrita e traz modelo, salvo 204 e 500 genérico."""
    pendencias = []
    for rotulo, operacao in operacoes:
        for codigo, resposta in operacao["responses"].items():
            if not resposta.get("description"):
                pendencias.append(f"{rotulo} [{codigo}]: sem descrição")
            sem_corpo = codigo == "204" or (
                codigo == "500"
                and operacao["operationId"] not in ERRO_INTERNO_COM_CORPO
            )
            conteudo = resposta.get("content", {}).get("application/json")
            if sem_corpo and conteudo:
                pendencias.append(f"{rotulo} [{codigo}]: modelo inesperado")
            if not sem_corpo and "schema" not in (conteudo or {}):
                pendencias.append(f"{rotulo} [{codigo}]: sem modelo")
    _sem_pendencias(pendencias)


def test_corpos_tem_exemplos(operacoes):
    """Todo corpo de requisição e de resposta traz ao menos um exemplo."""
    pendencias = [
        f"{rotulo} › {origem}: sem exemplo"
        for rotulo, operacao in operacoes
        for origem, conteudo, _ in _corpos_json(operacao)
        if not conteudo.get("examples")
    ]
    _sem_pendencias(pendencias)


def test_exemplos_seguem_os_modelos(schema, operacoes):
    """Os exemplos publicados obedecem ao modelo que ilustram."""
    componentes = schema["components"]["schemas"]
    exemplos = [
        (f"{rotulo} › {origem} › {nome}", exemplo, conteudo, requisicao)
        for rotulo, operacao in operacoes
        for origem, conteudo, requisicao in _corpos_json(operacao)
        for nome, exemplo in conteudo.get("examples", {}).items()
    ]
    assert exemplos, "nenhum exemplo publicado"
    pendencias = [
        f"{rotulo} › {violacao}"
        for rotulo, exemplo, conteudo, requisicao in exemplos
        for violacao in _violacoes(
            exemplo["value"],
            conteudo["schema"],
            componentes,
            requisicao=requisicao,
        )
    ]
    _sem_pendencias(pendencias)


@pytest.mark.parametrize(
    ("identificador", "obrigatorios"), sorted(CORPOS_EM_LOTE.items())
)
def test_corpo_em_lote_e_lista_com_campos_obrigatorios(
    schema, por_identificador, identificador, obrigatorios
):
    """PATCH em lote recebe uma lista e mantém os campos obrigatórios."""
    corpo = por_identificador[identificador]["requestBody"]
    esquema = corpo["content"]["application/json"]["schema"]
    item = esquema["items"]["$ref"].rsplit("/", 1)[-1]

    assert esquema["type"] == "array"
    assert corpo.get("required") is True
    assert schema["components"]["schemas"][item]["required"] == obrigatorios


@pytest.mark.parametrize("identificador", LISTAS_SEM_PAGINACAO)
def test_acao_de_lista_simples_nao_publica_pagina(
    por_identificador, identificador
):
    """Ação que devolve lista simples não é descrita como página."""
    resposta = por_identificador[identificador]["responses"]["200"]
    esquema = resposta["content"]["application/json"]["schema"]

    assert esquema["type"] == "array"
