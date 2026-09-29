# Metodologia

## Escopo atual

A versão atual do projeto usa dados do **Formulário Cadastral (FCA)** da Comissão de Valores Mobiliários (CVM) para identificar companhias abertas brasileiras a partir do código de negociação.

Essa etapa é cadastral. Ela **não representa, por si só, uma análise de valor da empresa**.

## Princípios para a evolução do projeto

A futura implementação de valuation deverá separar claramente três tipos de informação:

1. **Dados observados**  
   Informações publicadas pelas companhias e pela CVM, como demonstrações financeiras, estrutura de capital e dados cadastrais.

2. **Cálculos derivados**  
   Métricas produzidas a partir dos dados observados, como margens, crescimento, retorno sobre capital, dívida líquida e geração de caixa.

3. **Premissas de valuation**  
   Hipóteses necessárias para estimar valor, como crescimento futuro, reinvestimento, custo de capital e valor terminal.

Essa separação reduz o risco de apresentar uma hipótese como se fosse um dado histórico.

## Etapas planejadas

### Demonstrações financeiras

As séries contábeis deverão ser obtidas, preferencialmente, de bases públicas da CVM, incluindo:

- DFP — Demonstrações Financeiras Padronizadas;
- ITR — Informações Trimestrais.

Os dados deverão ser normalizados antes do cálculo de indicadores.

### Análise operacional e financeira

Antes do valuation, o projeto deverá calcular e exibir métricas que ajudem a entender a empresa, por exemplo:

- evolução da receita;
- margens;
- rentabilidade;
- estrutura de capital;
- endividamento;
- geração de caixa;
- reinvestimento.

### Valuation por fluxo de caixa descontado

A implementação futura poderá seguir a estrutura geral de um DCF:

```text
Valor da firma =
valor presente dos fluxos de caixa esperados
+ valor presente do valor terminal
```

Em uma abordagem por FCFF, o projeto deverá explicitar:

- receita projetada;
- margem operacional;
- impostos;
- reinvestimento;
- FCFF;
- custo médio ponderado de capital (WACC);
- crescimento na perpetuidade ou outra hipótese de valor terminal.

O valor do patrimônio líquido deverá ser derivado do valor da firma por meio dos ajustes financeiros pertinentes, que precisarão ser documentados quando implementados.

## Sensibilidade

Uma estimativa pontual de valor pode transmitir uma precisão que o modelo não possui. Por isso, o roadmap inclui análise de sensibilidade para variáveis relevantes, como:

- custo de capital;
- crescimento de longo prazo;
- margem operacional;
- reinvestimento.

## Referência metodológica

A estrutura conceitual inicial do módulo de valuation considera materiais acadêmicos disponibilizados por **Aswath Damodaran**, professor da NYU Stern School of Business:

- https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valuation/val.htm
- https://pages.stern.nyu.edu/~adamodar/

O uso dessa referência não significa que o projeto já implemente um modelo específico de Damodaran. Cada fórmula e premissa será documentada conforme for incorporada ao código.

## Limitações

O projeto está em desenvolvimento. Enquanto os módulos de demonstrações financeiras e valuation não forem implementados, os resultados exibidos devem ser interpretados apenas como consulta cadastral.

O projeto tem finalidade educacional e acadêmica e não constitui recomendação de investimento.
