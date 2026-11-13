# Instruções para agentes

Este arquivo define as regras permanentes para qualquer agente de IA que analise ou altere este
repositório. Leia também `README.md`, `docs/ARCHITECTURE.md` e `docs/TESTING.md` antes de mudanças
que afetem comportamento.

## Objetivo do produto

O FiscalizaIA é um MVP de apoio à fiscalização de medições de obras públicas. O sistema prioriza
itens para revisão humana por meio de regras explícitas e usa IA generativa somente para explicar
os alertas calculados.

O sistema não determina fraude, irregularidade, aprovação de medição ou responsabilidade de
pessoas. Preserve essa linguagem na interface, na documentação e nos pareceres.

## Princípios de implementação

- Prefira a solução mais simples que satisfaça o requisito atual (KISS e YAGNI).
- Evite duplicação de regras de negócio, mas não crie abstrações apenas para eliminar poucas linhas
  semelhantes. Aplique DRY quando houver um conceito único e estável.
- Use nomes que expressem intenção e mantenha funções pequenas, coesas e com uma responsabilidade
  clara.
- Separe regra de negócio, entrada e saída de dados, integração externa e apresentação.
- Prefira funções puras no motor de auditoria. Efeitos externos devem ficar nas bordas do sistema.
- Não esconda regras de negócio em callbacks da interface ou prompts de IA.
- Adicione comentários apenas para explicar decisões, restrições ou motivos não evidentes. Não
  descreva literalmente o que o código já mostra.
- Preserve o estilo e a estrutura existentes quando forem adequados. Refatore somente dentro do
  escopo solicitado ou quando isso for necessário para uma mudança segura.

## SOLID no contexto deste projeto

- **Responsabilidade única:** cada módulo e função deve ter um motivo principal para mudar.
  `src/domain/` contém regras e métricas; `src/infrastructure/` trata arquivos e OpenAI;
  `src/presentation/` renderiza a interface; `app.py` compõe o fluxo.
- **Aberto/fechado:** novas regras devem poder ser adicionadas sem alterar contratos públicos
  desnecessariamente. Não introduza um framework de regras antes de existir complexidade que o
  justifique.
- **Substituição de Liskov:** se abstrações ou implementações alternativas forem criadas, preserve
  as entradas, saídas, exceções e garantias esperadas por quem as utiliza.
- **Segregação de interfaces:** funções e protocolos devem pedir somente os dados e capacidades que
  realmente usam. Evite objetos de contexto genéricos ou dependências excessivas.
- **Inversão de dependência:** lógica determinística não deve depender de Streamlit ou do SDK da
  OpenAI. Integrações externas devem ser isoladas e, quando necessário, injetáveis nos testes.

SOLID é uma ferramenta de decisão, não uma meta de quantidade de classes. Para este MVP funcional,
funções simples e módulos coesos são preferíveis a hierarquias e camadas artificiais.

## Regras arquiteturais obrigatórias

- Cálculos, pontuação, classificação e estimativas devem ser determinísticos e testáveis sem rede.
- A OpenAI pode receber apenas métricas e alertas já calculados; nunca deve calcular risco ou decidir
  se houve fraude ou irregularidade.
- A aplicação deve funcionar sem `OPENAI_API_KEY`. Somente a geração do parecer pode ficar
  indisponível.
- Não envie dados pessoais, documentos reais ou segredos para serviços externos nos testes e na
  demonstração.
- Toda nova regra de auditoria deve produzir, quando aplicável: identificador estável, título,
  severidade, pontos, evidência, impacto estimado e recomendação.
- Pontuações agregadas devem permanecer limitadas a 100 e manter significado documentado.
- Erros de entrada devem resultar em mensagens compreensíveis e não em resultados silenciosamente
  incorretos.
- Não adicione banco de dados, autenticação, Docker, framework de agentes, frontend separado ou
  outra infraestrutura sem uma necessidade aprovada para o escopo.
- `src/domain/` não pode importar `src/presentation/` ou `src/infrastructure/`.
- `src/presentation/` e `src/infrastructure/` podem depender do domínio; dependências no sentido
  inverso são proibidas.

Consulte `docs/ARCHITECTURE.md` para dependências permitidas e responsabilidades dos módulos.

## Qualidade do código Python

- Mantenha compatibilidade com Python 3.12 ou superior.
- Use type hints em novas funções públicas e em código onde eles eliminem ambiguidade.
- Prefira `pathlib.Path` para caminhos e context managers para recursos.
- Capture exceções específicas nas camadas internas. Na interface, traduza falhas esperadas em
  mensagens úteis sem expor chave, payload sensível ou stack trace ao usuário.
- Não use estado global mutável para regras ou resultados.
- Não faça chamadas de rede durante importação de módulos.
- Mantenha dependências mínimas e registre qualquer nova dependência em `requirements.txt` com uma
  justificativa clara.
- Ruff é a fonte de verdade para lint e formatação configurada no projeto.

## Testes e definição de pronto

- Mudança de comportamento exige teste que falhe antes da correção e passe depois dela.
- Nova regra precisa de casos positivo, negativo e de limite.
- Correção de bug precisa de teste de regressão.
- Testes não podem depender de rede, horário instável, chave real ou dados pessoais.
- Integrações externas devem ser simuladas nos testes automatizados. Um teste real com a OpenAI é
  manual e opcional, executado apenas quando houver credencial local.
- Antes de considerar uma alteração pronta, execute os comandos de `docs/TESTING.md` aplicáveis.
- Se algum comando não puder ser executado, informe exatamente qual e por quê; não declare a
  validação concluída.

## Segurança, privacidade e Git

- Nunca leia, imprima, registre, copie ou versione valores de `.env` ou chaves de API.
- Use somente `.env.example` com valores vazios ou fictícios.
- Não altere nem descarte mudanças existentes do usuário sem autorização.
- Não publique, faça push, crie repositório remoto ou exponha dados sem solicitação explícita.
- Dados de demonstração devem ser claramente sintéticos.

## Documentação

- Atualize `README.md` quando mudar instalação, uso ou comportamento visível.
- Atualize `docs/ARCHITECTURE.md` quando mudar responsabilidades ou dependências entre módulos.
- Registre decisões arquiteturais relevantes em `docs/adr/` quando elas tiverem alternativas e
  consequências duradouras.
- Não versione arquivos temporários de handoff. Estado transitório deve ficar fora da documentação
  pública e não substitui estas regras nem a documentação estável.

## Ao concluir uma tarefa

Informe de forma objetiva:

1. o que foi alterado;
2. quais decisões ou limitações são relevantes;
3. quais verificações foram executadas e seus resultados;
4. o que não pôde ser verificado.

