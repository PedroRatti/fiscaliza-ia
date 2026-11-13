# Arquitetura do FiscalizaIA

## Visão geral

O FiscalizaIA usa uma arquitetura em camadas enxuta. O domínio determinístico permanece isolado de
frameworks, arquivos, rede e IA generativa.

```text
                     +--------------------+
                     |       app.py       |
                     | composição do fluxo|
                     +---------+----------+
                               |
             +-----------------+-----------------+
             |                                   |
             v                                   v
 +----------------------+             +----------------------+
 | src/presentation/    |             | src/infrastructure/  |
 | Streamlit e Plotly   |             | arquivos e OpenAI    |
 +----------+-----------+             +----------+-----------+
            |                                    |
            +----------------+-------------------+
                             |
                             v
                  +----------------------+
                  |     src/domain/      |
                  | regras determinísticas|
                  +----------------------+
```

## Regra de dependência

As dependências apontam para o domínio:

```text
app.py -----------> presentation
  |                      |
  +--> infrastructure ---+--> domain
  +--------------------------> domain
```

- `src/domain/` não importa Streamlit, Plotly, OpenAI nem módulos de infraestrutura.
- `src/infrastructure/` pode usar contratos e validações do domínio.
- `src/presentation/` pode consumir domínio e infraestrutura para apresentar o fluxo ao usuário.
- `app.py` é o composition root e conecta as camadas.

## Domínio

### `src/domain/models.py`

- Define o modelo imutável `Alert`.
- Não possui dependências externas.

### `src/domain/validation.py`

- Define o contrato das colunas de entrada.
- Valida completude, unidade de medida, tipos, intervalos e datas.
- Reúne erros para evitar resultados silenciosamente incorretos.

### `src/domain/rules.py`

- Contém uma função pura para cada regra de auditoria.
- Mantém o registro simples `AUDIT_RULES`.
- Cada regra retorna um `Alert` ou `None`.

### `src/domain/audit.py`

- Valida a entrada.
- Executa o registro de regras para cada item.
- Converte os alertas em estrutura tabular.

### `src/domain/metrics.py`

- Agrega pontuação e nível de risco.
- Limita a pontuação a 100.
- Calcula métricas determinísticas do portfólio.

## Infraestrutura

### `src/infrastructure/files.py`

- Lê CSV e XLSX.
- Traduz falhas de arquivo em mensagens compreensíveis.
- Exporta resumo e alertas para Excel.

### `src/infrastructure/openai_report.py`

- Isola configuração e chamada à OpenAI.
- Envia somente métricas e alertas previamente calculados.
- Aceita um cliente injetado para testes sem chave e sem rede.
- Não altera pontuação, severidade, evidência ou impacto.

## Apresentação

### `src/presentation/layout.py`

- Configura a página, estilos, cabeçalho e barra lateral.

### `src/presentation/dashboard.py`

- Renderiza métricas, gráficos e itens priorizados.

### `src/presentation/alerts.py`

- Renderiza filtros, evidências e recomendações dos alertas.

### `src/presentation/report.py`

- Controla a interação visual para gerar e baixar o parecer assistido.

### `src/presentation/export.py`

- Exibe dados analisados e disponibiliza o relatório Excel.

## Utilitários compartilhados

### `src/formatting.py`

- Centraliza formatações puras usadas pelo domínio e pela apresentação.
- Não depende de frameworks ou serviços externos.

## Invariantes

- O mesmo conjunto de dados e a mesma versão das regras produzem os mesmos alertas.
- A ausência da OpenAI não impede análise, dashboard ou exportação.
- Um alerta é evidência para priorização, não conclusão de irregularidade.
- O impacto financeiro é uma estimativa, não comprovação de dano.
- O usuário consegue rastrear cada alerta até uma regra e uma linha de entrada.
- Quantidades contratada e acumulada usam a mesma unidade de medida por item.
- Quantidades e preços contratuais representam a base vigente, após alterações autorizadas.

## Evolução da arquitetura

Novas regras devem ser funções puras adicionadas a `src/domain/rules.py` e ao registro
`AUDIT_RULES`, acompanhadas de casos positivo, negativo e de limite.

Crie uma nova abstração apenas diante de uma necessidade concreta, como múltiplas implementações,
repetição estável ou dificuldade comprovada de teste. Não crie repositórios, serviços, fábricas ou
classes-base apenas para aparentar sofisticação.

Mudanças duradouras com alternativas relevantes devem receber um registro em `docs/adr/` com
contexto, decisão, consequências e alternativas descartadas.

