# Metodologia

## Escopo atual

O projeto usa dados públicos da **Comissão de Valores Mobiliários (CVM)** para identificar companhias abertas, ler demonstrações financeiras estruturadas e produzir indicadores históricos descritivos.

O módulo de valuation está sendo construído de forma incremental e metodologicamente explícita.

## Separação de informações

O projeto separa três tipos de informação:

1. **Dados observados**  
   Informações publicadas pelas companhias e pela CVM.

2. **Cálculos derivados**  
   Métricas calculadas a partir dos dados observados, como margens, crescimento histórico e, futuramente, reinvestimento e retorno sobre capital.

3. **Premissas de valuation**  
   Hipóteses necessárias para projetar resultados futuros, como crescimento, margens futuras, custo de capital e valor terminal.

Uma premissa nunca deve ser apresentada como se fosse um dado observado.

## Método principal de valuation

Foi definido como método principal inicial o **FCFF — Free Cash Flow to the Firm**, com desconto pelo **WACC — Weighted Average Cost of Capital**.

O objetivo do FCFF é estimar fluxos disponíveis a todos os provedores de capital da empresa, antes da remuneração específica de credores e acionistas.

A estrutura conceitual adotada é:

```text
NOPAT = EBIT × (1 - alíquota de imposto)

FCFF =
NOPAT
+ Depreciação e amortização
- CAPEX
- Variação do capital de giro
```

O valor presente dos FCFFs explícitos é calculado por:

```text
VP(FCFF_t) = FCFF_t / (1 + WACC)^t
```

O WACC é estruturado como:

```text
WACC =
(E / (D + E)) × Ke
+ (D / (D + E)) × Kd × (1 - T)
```

onde:

- `E` = valor de mercado do patrimônio;
- `D` = valor da dívida;
- `Ke` = custo do capital próprio;
- `Kd` = custo da dívida antes de impostos;
- `T` = alíquota de imposto.

Após estimar o **Enterprise Value**, a ponte inicial para o valor do patrimônio é:

```text
Equity Value =
Enterprise Value
+ Caixa e equivalentes
- Dívida bruta
+ Outros ajustes financeiros explicitamente identificados
```

Essa fórmula não implica que todos os possíveis ajustes de valuation já estejam implementados. Participações não controladoras, ativos não operacionais, passivos de pensão e outros itens deverão ser avaliados separadamente quando aplicáveis.

## O que já pode ser implementado sem premissas adicionais

A infraestrutura matemática pode incluir:

- cálculo de NOPAT;
- cálculo de FCFF;
- cálculo de WACC;
- desconto de fluxos explícitos;
- ponte entre Enterprise Value e Equity Value;
- validações matemáticas;
- testes automatizados.

## Decisões ainda pendentes

A projeção completa permanece bloqueada até definição explícita de:

- horizonte de projeção;
- metodologia para crescimento futuro;
- metodologia para margens futuras;
- reinvestimento e capital de giro;
- taxa livre de risco;
- beta;
- prêmio de risco de mercado;
- eventual prêmio de risco-país;
- custo da dívida;
- alíquota de imposto usada no valuation;
- pesos de dívida e patrimônio;
- metodologia de valor terminal;
- moeda e consistência nominal/real.

O crescimento histórico observado não será automaticamente usado como crescimento futuro.

## Séries históricas

DFP e ITR são utilizadas para análise histórica. As DFPs anuais são usadas na série histórica de receita, lucro e margens.

CAGR é uma métrica histórica. Ele não representa, por si só, uma projeção.

## Sensibilidade

Uma estimativa pontual de valor pode transmitir precisão excessiva. O roadmap prevê análise de sensibilidade para variáveis como:

- custo de capital;
- crescimento de longo prazo;
- margem operacional;
- reinvestimento.

## Referência metodológica

A estrutura conceitual inicial considera materiais acadêmicos disponibilizados por **Aswath Damodaran**, professor da NYU Stern School of Business:

- https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valuation/val.htm
- https://pages.stern.nyu.edu/~adamodar/

A referência orienta conceitos gerais. Cada fórmula, fonte de dados e premissa adotada pelo projeto deve permanecer documentada explicitamente.

## Limitações

O projeto ainda não possui um DCF completo nem gera estimativa de valor intrínseco. A infraestrutura de FCFF/WACC não deve ser interpretada como recomendação de investimento.

O projeto tem finalidade educacional e acadêmica.
