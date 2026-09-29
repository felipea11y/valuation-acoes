# Valuation de Ações Brasileiras

Aplicação em **Python + Streamlit** para consulta de companhias abertas brasileiras a partir de dados públicos da **Comissão de Valores Mobiliários (CVM)**.

O projeto está em desenvolvimento e tem como objetivo evoluir de uma camada de identificação cadastral para uma ferramenta acadêmica de **análise fundamentalista e valuation**.

> **Status atual:** protótipo funcional para identificação de companhias pelo ticker e leitura inicial de DFP/ITR.  
> **Ainda não implementado:** cálculo de valor intrínseco, fluxo de caixa descontado, múltiplos ou recomendação de investimento.

## O que já funciona

- consulta do conjunto de dados do Formulário Cadastral (FCA) da CVM;
- busca de companhia por ticker, como `WEGE3` e `PETR4`;
- exibição do nome empresarial e CNPJ;
- cache da base consultada para reduzir downloads repetidos;
- interface web simples com Streamlit;
- tratamento básico de erros de rede e leitura dos dados;
- carregamento de DRE, balanço patrimonial ativo/passivo a partir de DFP ou ITR;
- filtro das demonstrações pelo CNPJ identificado a partir do ticker;
- indicadores descritivos da DRE: receita, resultado bruto, resultado operacional, lucro líquido e margens;
- séries históricas anuais com crescimento de receita/lucro e CAGR.

## Fonte dos dados

A identificação dos valores mobiliários é baseada no conjunto **Formulário Cadastral (FCA)** disponibilizado no Portal de Dados Abertos da CVM.

Documentação oficial:

- https://dados.cvm.gov.br/dataset/cia_aberta-doc-fca
- https://www.gov.br/cvm/pt-br/acesso-a-informacao-cvm/dados-abertos

A disponibilidade, estrutura e atualização dos arquivos são de responsabilidade da fonte oficial.

## Roadmap

### 1. Cadastro e identificação — em desenvolvimento
- [x] consulta ao FCA;
- [x] busca por ticker;
- [x] identificação de empresa e CNPJ;
- [ ] melhorar tratamento de múltiplos registros por ticker;
- [ ] adicionar informações cadastrais relevantes.

### 2. Demonstrações financeiras
- [x] integrar Demonstrações Financeiras Padronizadas (DFP);
- [x] integrar Informações Trimestrais (ITR);
- [ ] organizar DRE, balanço patrimonial e demonstração de fluxo de caixa;
- [x] padronizar séries históricas iniciais de DRE para análise.

### 3. Análise fundamentalista
- [x] receita e margens;
- [x] crescimento por série histórica;
- [ ] dívida e estrutura de capital;
- [ ] rentabilidade;
- [ ] geração de caixa;
- [ ] indicadores por ação.

### 4. Valuation
- [x] infraestrutura matemática inicial de FCFF/WACC;
- [x] horizonte explícito padrão de 5 anos, parametrizável;
- [ ] projeção completa de FCFF;
- [ ] custo de capital com parâmetros de mercado;
- [ ] valor terminal;
- [ ] análise de sensibilidade;
- [ ] comparação por múltiplos.

A metodologia de valuation será documentada antes de sua implementação. Como referência acadêmica inicial, o projeto considera os materiais públicos de valuation do professor **Aswath Damodaran**, da NYU Stern:

- https://pages.stern.nyu.edu/~adamodar/New_Home_Page/valuation/val.htm

Veja também [docs/METODOLOGIA.md](docs/METODOLOGIA.md).

## Tecnologias

- Python
- Streamlit
- Pandas
- Requests
- dados abertos da CVM

## Como executar

Recomenda-se utilizar um ambiente virtual.

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute:

```bash
streamlit run app.py
```

## Estrutura do projeto

```text
valuation-acoes/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── src/
│   ├── cvm_data.py
│   ├── indicadores.py
│   └── valuation.py
├── tests/
│   ├── test_cvm_data.py
│   ├── test_indicadores.py
│   └── test_valuation.py
└── docs/
    └── METODOLOGIA.md
```

## Objetivo acadêmico

O projeto busca combinar programação, dados públicos do mercado de capitais e conceitos de finanças corporativas em uma aplicação reproduzível. O foco é tornar explícitas as etapas entre **dados contábeis**, **hipóteses econômicas** e **estimativas de valor**.

Quando o módulo de valuation for implementado, premissas como crescimento, margem, reinvestimento, custo de capital e valor terminal deverão aparecer de forma transparente e separada dos dados observados.

## Aviso

Este projeto possui finalidade **educacional e acadêmica**. As informações apresentadas não constituem recomendação de compra, venda ou manutenção de valores mobiliários.

## Autor

Desenvolvido por [felipea11y](https://github.com/felipea11y).
