# FiscalizaIA

Auditoria assistida de medições de obras públicas. O sistema aplica regras rastreáveis para
priorizar medições que merecem revisão e usa IA generativa apenas para explicar os achados.

> O FiscalizaIA não determina fraude ou irregularidade e não substitui o fiscal. Ele organiza
> evidências e reduz o esforço da triagem inicial.

## Problema

A conferência de medições exige comparar quantidades, preços, cronograma e avanço físico-financeiro.
Em carteiras grandes, casos relevantes podem ficar escondidos entre centenas de linhas.

## Solução

O MVP aceita CSV ou XLSX e identifica:

1. quantidade acumulada acima da quantidade contratual vigente;
2. preço unitário divergente;
3. descompasso entre avanço físico e financeiro;
4. medição fora do período previsto.

Cada achado contém evidência, gravidade, pontuação, impacto potencial e recomendação. A OpenAI
transforma esses dados estruturados em um parecer objetivo, sempre sujeito à revisão humana.

Antes da auditoria, a entrada é validada para impedir resultados silenciosamente incorretos. A
planilha deve conter valores completos, unidade de medida, números positivos para quantidades e
preços, percentuais entre 0 e 100, datas válidas e um período previsto coerente. Quantidades e
preços contratuais devem refletir a versão vigente do contrato, incluindo alterações autorizadas.

### Formato de entrada

Cada linha representa um item de serviço medido. As quantidades contratada e acumulada usam a
mesma `unidade_medida`, como `m`, `m2`, `m3`, `t`, `un` ou `servico`. O MVP não recebe o histórico
dos aditivos: os campos contratuais devem trazer os valores vigentes na data da medição.

O campo `preco_unitario_medido` representa o preço unitário aplicado no boletim de medição, não o
custo interno da empresa executora.

## Arquitetura

```text
Planilha → validação → regras determinísticas → risco e evidências → dashboard
                                                          └→ OpenAI → parecer
```

- **Python + pandas:** processamento e regras de auditoria.
- **Streamlit + Plotly:** aplicação e visualização.
- **OpenAI Responses API:** explicação dos alertas.
- **pytest:** testes do domínio, arquivos, integração de IA, interface e arquitetura.

O código é separado em três camadas: domínio determinístico (`src/domain/`), integrações externas
(`src/infrastructure/`) e apresentação Streamlit (`src/presentation/`). O `app.py` apenas compõe o
fluxo entre elas.

As responsabilidades dos módulos, a direção das dependências e as regras permanentes para agentes
estão documentadas em [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) e [`AGENTS.md`](AGENTS.md).
A estratégia e os critérios de validação estão em [`docs/TESTING.md`](docs/TESTING.md).

## Como executar

Requer Python 3.12 ou superior.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

A aplicação funciona sem IA. Para habilitar o parecer:

```powershell
Copy-Item .env.example .env
```

Edite `.env` e preencha `OPENAI_API_KEY`. Nunca publique esse arquivo.

## Testes

```powershell
pytest
ruff check .
```

## Dados

`data/medicoes_exemplo.csv` contém dados inteiramente sintéticos, preparados para demonstrar casos
normais e alertas. `data/medicoes_teste_alternativo.xlsx` oferece um segundo cenário para upload
manual. Os arquivos de `data/testes_invalidos/` permitem verificar as mensagens de validação.

O repositório não contém dados da Softplan, contratos reais nem dados pessoais.

## Limitações e próximos passos

- As regras não cobrem toda a legislação ou todos os tipos de contrato.
- A estimativa financeira serve para priorização, não para comprovar dano.
- A versão futura pode incluir trilha de auditoria, perfis de acesso, comparação semântica de
  descrições, histórico de aditivos e integração com documentos contratuais.

## Vídeo

[Assistir à demonstração do FiscalizaIA no YouTube](https://www.youtube.com/watch?v=jtZN4ZqGTx4).
