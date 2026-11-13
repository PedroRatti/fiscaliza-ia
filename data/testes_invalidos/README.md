# Arquivos inválidos para teste manual

Todos os arquivos desta pasta são intencionalmente inválidos. Envie cada um pela opção
**Enviar arquivo** e confirme que a aplicação mostra uma mensagem compreensível sem interromper o
restante da interface.

| Arquivo | Erro esperado |
| --- | --- |
| `01_csv_sem_coluna_contrato.csv` | coluna obrigatória `contrato` ausente |
| `02_csv_vazio.csv` | CSV sem conteúdo |
| `03_csv_sem_linhas.csv` | planilha sem linhas de dados |
| `04_csv_valor_ausente.csv` | descrição contratada ausente |
| `05_csv_numero_invalido.csv` | quantidade com texto no lugar de número |
| `06_csv_valor_nao_positivo.csv` | preço unitário igual a zero |
| `07_csv_percentual_fora_intervalo.csv` | avanço financeiro acima de 100% |
| `08_csv_data_invalida.csv` | data de medição inválida |
| `09_csv_periodo_invertido.csv` | início previsto posterior ao fim previsto |
| `10_csv_unidade_ausente.csv` | unidade de medida ausente |
| `11_xlsx_sem_coluna_item.xlsx` | coluna obrigatória `item` ausente |
| `12_xlsx_sem_linhas.xlsx` | planilha Excel sem linhas de dados |
| `13_xlsx_corrompido.xlsx` | conteúdo não corresponde a um arquivo Excel |
| `14_extensao_nao_suportada.txt` | extensão não aceita pelo uploader |

O componente de upload pode impedir a seleção do arquivo `.txt`. Esse é o comportamento esperado
da proteção da interface.

