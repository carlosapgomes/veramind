# ADR-0003: Revisar o stack de implementação para um VeraBrain centrado no Hermes

[English](./ADR-0003-python-first-hermes-stack.md)

## Status

Accepted

## Contexto

A ADR-0001 estabeleceu um stack TypeScript-first quando o VeraBrain ainda
era concebido como uma implementação standalone de agente com runtime
próprio.

Essa premissa mudou após a análise do Hermes e a decisão na ADR-0002 de
reposicionar o VeraBrain como uma arquitetura de extensão centrada no
Hermes.

Sob essa nova direção, a primeira implementação não otimiza mais para um
runtime customizado em TypeScript. Ela passa a otimizar para:

- integração com Hermes Agent
- entrega MCP-first
- possível integração futura via plugin nativo do Hermes
- experimentação com baixo atrito no mesmo ecossistema que o Hermes já
  usa

O repositório já contém um scaffold inicial em TypeScript e esses
artefatos continuam úteis para bootstrap do projeto e validação de
processo, mas eles não representam mais a direção preferencial de
implementação do produto.

## Decisão

Adotar uma direção Python-first para a primeira versão do VeraBrain
centrada no Hermes.

A direção revisada de stack passa a ser:

- Python 3.11+ como linguagem principal de implementação
- `uv` como gerenciador preferencial de ambiente e pacotes Python
- Hermes Agent como runtime shell
- MCP como principal superfície inicial de integração
- um adaptador fino opcional de plugin do Hermes posteriormente, caso a
  superfície nativa de extensão amadureça o suficiente

O scaffold existente em TypeScript/Node permanece no repositório como
artefato legado de fundação e pode continuar sustentando os checks
locais atuais até que um scaffold Python o substitua.

## Alternativas consideradas

1. Manter TypeScript como linguagem principal de implementação apesar do
   pivot para Hermes
2. Usar uma arquitetura híbrida desde o primeiro slice de implementação
3. Adiar a revisão de stack até depois do desenho da arquitetura de
   adapters

## Consequências

- Positivas:
  - alinha a linguagem de implementação com a direção atual do produto,
    centrada no Hermes
  - reduz atrito para integração via MCP e futuro trabalho com plugin
    fino
  - mantém o foco arquitetural no core do VeraBrain, em vez de gastar
    energia cedo demais conciliando dois stacks principais
  - torna os próximos slices de design mais honestos sobre o caminho de
    entrega pretendido
- Negativas/Trade-offs:
  - enfraquece a direção original TypeScript/pi-mono registrada na
    ADR-0001
  - deixa o repositório em um estado temporariamente misto enquanto o
    scaffold TypeScript e a direção Python-first coexistem
  - pode exigir migração ou substituição do tooling local de qualidade
    em slices posteriores

## Notas

Essa decisão muda a direção preferencial de implementação, não o
princípio arquitetural central da ADR-0002. O VeraBrain continua
devendo ser estruturado como:

- uma camada central de domínio
- um adaptador MCP
- um adaptador opcional futuro de plugin do Hermes

Essa separação mantém futuras mudanças de stack ou integração mais
baratas.
