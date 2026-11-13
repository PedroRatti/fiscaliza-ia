# Estratégia de testes

## Objetivo

Os testes devem demonstrar que o motor é determinístico, que entradas inválidas falham de forma
compreensível e que a interface continua utilizável sem serviços externos.

## Pirâmide de testes

1. **Unitários:** regras, pontuação, métricas e funções de transformação.
2. **Integração local:** leitura de CSV/XLSX, exportação e composição entre módulos.
3. **Interface:** carregamento do Streamlit e fluxos essenciais usando dados sintéticos.
4. **Teste manual externo:** geração de parecer com uma chave local, sem dados reais.

A maior parte da cobertura deve ficar nos dois primeiros níveis. Testes automatizados não devem
chamar a OpenAI.

## Casos mínimos para regras de auditoria

Cada regra deve cobrir:

- caso que dispara o alerta;
- caso que não dispara;
- valor exatamente no limite;
- valor logo acima ou abaixo do limite;
- campos ausentes, inválidos ou extremos relevantes;
- unidade de medida presente e preservada nas evidências.

Além disso, devem existir testes para:

- colunas obrigatórias ausentes;
- datas inválidas ou ausentes;
- valores numéricos nulos, textuais, negativos ou iguais a zero;
- limite de 100 pontos;
- conjunto sem alertas;
- leitura de CSV e XLSX;
- formato não suportado;
- exportação das duas planilhas esperadas;
- IA indisponível e falhas simuladas da API;
- cliente de IA injetado sem chave ou acesso à rede;
- carregamento das quatro abas do Streamlit.

## Comandos de validação

Com o ambiente virtual ativo:

```powershell
python -m pytest -q
python -m ruff check .
```

Para validar o carregamento básico da interface:

```powershell
python -c "from streamlit.testing.v1 import AppTest; app = AppTest.from_file('app.py'); app.run(); assert not app.exception"
```

Quando a alteração afetar a experiência visual, execute também:

```powershell
streamlit run app.py
```

e confira manualmente os fluxos de demonstração, upload, filtros, detalhes e download.

## Teste manual da OpenAI

O teste real da integração é opcional para desenvolvimento comum e obrigatório antes de uma
demonstração que dependa do parecer. Ele deve:

- usar chave somente no `.env` local;
- utilizar exclusivamente os dados sintéticos do projeto;
- confirmar que o modelo configurado está disponível;
- verificar se o texto não afirma fraude ou irregularidade;
- verificar se o parecer se limita aos alertas fornecidos;
- confirmar que erros da API aparecem de forma compreensível.

Nunca registre a chave, o conteúdo do `.env` ou respostas que contenham dados sensíveis.

## Critério de conclusão

Uma tarefa está pronta quando os testes relevantes e o Ruff passam, a documentação afetada foi
atualizada e qualquer verificação não executada foi explicitamente informada.

