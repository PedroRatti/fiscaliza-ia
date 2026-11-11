# Handoff para o próximo chat do Codex

## Objetivo

Finalizar hoje um projeto de portfólio para candidatura ao programa de trainee Futures da Softplan.
O projeto deve demonstrar integração responsável de IA em um caso de uso compatível com a atuação
da empresa em gestão de obras públicas.

Prazo informado pelo candidato: amanhã às 09h (horário de Brasília).

## Produto escolhido

**FiscalizaIA — Auditoria assistida de medições de obras públicas.**

O sistema recebe uma planilha de medições, aplica regras rastreáveis, prioriza itens de risco e usa
a OpenAI somente para explicar os achados em um parecer. A mensagem central é:

> O sistema não substitui o fiscal nem determina irregularidades. Ele prioriza medições que merecem
> revisão, apresenta evidências e reduz o tempo da conferência inicial.

## Decisões técnicas já tomadas

- Python 3.12.10.
- Streamlit para interface e dashboard.
- pandas para processamento tabular.
- Plotly para gráficos.
- SDK oficial da OpenAI com Responses API para o parecer.
- openpyxl para exportar o relatório.
- pytest e Ruff para testes e qualidade.
- Dados inteiramente sintéticos; nenhum dado da Softplan ou dado pessoal.
- Sem banco de dados, autenticação, Docker, LangChain ou frontend separado neste MVP.
- Cálculos e classificação são determinísticos. A IA não faz cálculos nem decide fraude.

## Estado atual

- Repositório Git local na branch `main`.
- Commit inicial: `b2adb07 feat: cria MVP do FiscalizaIA`.
- Dashboard abre localmente e respondeu HTTP 200.
- Teste automatizado do Streamlit: zero exceções, quatro abas carregadas.
- `pytest`: 4 testes aprovados.
- `ruff check .`: aprovado.
- O repositório não possui `.env`, chave de API ou ambiente virtual.

## O que já está implementado

- Upload de CSV ou XLSX.
- Modo demonstração com planilha sintética.
- Validação das colunas obrigatórias.
- Regra de quantidade acima do contrato sem aditivo.
- Regra de preço unitário divergente.
- Regra de descompasso físico-financeiro.
- Regra de medição fora do cronograma.
- Pontuação de risco por item, limitada a 100.
- Dashboard, filtros e detalhamento das evidências.
- Estimativa de impacto financeiro para priorização.
- Exportação das análises para Excel.
- Integração de parecer via OpenAI, habilitada quando `OPENAI_API_KEY` existe.
- README inicial e arquivo `.env.example`.

## Arquivos principais

- `app.py`: interface Streamlit.
- `src/audit.py`: regras, pontuação e métricas.
- `src/ai.py`: integração OpenAI e instruções do parecer.
- `src/data.py`: importação e exportação.
- `data/medicoes_exemplo.csv`: cenário sintético.
- `tests/test_audit.py`: testes do motor.
- `README.md`: documentação para avaliadores.

## Próximos passos prioritários

1. Criar o ambiente virtual neste diretório e instalar `requirements.txt`.
2. Copiar `.env.example` para `.env`; o usuário deve inserir a chave sem compartilhá-la no chat.
3. Testar uma chamada pequena à OpenAI e confirmar um modelo disponível na conta.
4. Executar o dashboard com a chave e revisar a qualidade do parecer.
5. Implementar a quinta regra planejada: divergência semântica entre descrição contratada e medida,
   preferencialmente com embeddings, se couber no prazo.
6. Melhorar visualmente o dashboard após inspeção no navegador.
7. Adicionar testes de arquivo inválido, datas ausentes e valores extremos.
8. Revisar o README e incluir capturas de tela.
9. Preparar roteiro de vídeo de 2–3 minutos.
10. Usuário grava, publica no YouTube e adiciona o link ao README.
11. Criar repositório remoto no GitHub e enviar a branch `main`, somente quando o usuário autorizar.

## Comandos de retomada no Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

Validação:

```powershell
pytest
ruff check .
```

## Cuidados obrigatórios

- Nunca solicitar que o usuário cole a chave da OpenAI no chat.
- Nunca commitar `.env`; ele já está no `.gitignore`.
- Manter revisão humana explícita e evitar linguagem que conclua fraude.
- Não enviar dados pessoais ou documentos reais para a API durante a demonstração.
- Não publicar no GitHub ou YouTube sem ação/autorização expressa do usuário.
- Preservar o escopo de MVP por causa do prazo.

## Contexto do processo seletivo

O Futures valoriza mais o projeto e o raciocínio do candidato do que a instituição de ensino. A
apresentação deve enfatizar problema, justificativa para IA, decisões, resultados, limitações,
ética, transparência e impacto. O programa é focado em aplicações práticas de IA, protagonismo,
método, comunicação e impacto no setor público.

