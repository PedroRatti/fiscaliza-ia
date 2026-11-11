# FiscalizaIA

Auditoria assistida de medições de obras públicas. O sistema aplica regras rastreáveis para
priorizar medições que merecem revisão e usa IA generativa apenas para explicar os achados.

> O FiscalizaIA não determina fraude ou irregularidade e não substitui o fiscal. Ele organiza
> evidências e reduz o esforço da triagem inicial.

## Problema

A conferência de medições exige comparar quantidades, preços, cronograma e avanço físico-financeiro.
Em carteiras grandes, casos relevantes podem ficar escondidos entre centenas de linhas.

## Solução

O MVP aceita CSV ou Excel e identifica:

1. quantidade acumulada acima do contrato sem aditivo informado;
2. preço unitário divergente;
3. descompasso entre avanço físico e financeiro;
4. medição fora do período previsto.

Cada achado contém evidência, gravidade, pontuação, impacto potencial e recomendação. A OpenAI
transforma esses dados estruturados em um parecer objetivo, sempre sujeito à revisão humana.

## Arquitetura

```text
Planilha → validação → regras determinísticas → risco e evidências → dashboard
                                                          └→ OpenAI → parecer
```

- **Python + pandas:** processamento e regras de auditoria.
- **Streamlit + Plotly:** aplicação e visualização.
- **OpenAI Responses API:** explicação dos alertas.
- **pytest:** testes do motor de regras.

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
normais e alertas. O repositório não contém dados da Softplan nem dados pessoais.

## Limitações e próximos passos

- As regras não cobrem toda a legislação ou todos os tipos de contrato.
- A estimativa financeira serve para priorização, não para comprovar dano.
- A versão futura pode incluir trilha de auditoria, perfis de acesso, comparação semântica de
  descrições e integração com documentos contratuais.

## Vídeo

Link da demonstração: **a adicionar**.

