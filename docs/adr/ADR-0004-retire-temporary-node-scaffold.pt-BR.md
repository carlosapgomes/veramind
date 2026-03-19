# ADR-0004: Retirar o scaffold temporário de TypeScript e Node do repositório

[English](./ADR-0004-retire-temporary-node-scaffold.md)

## Status

Accepted

## Contexto

A ADR-0003 manteve o scaffold existente de TypeScript e Node no
repositório como um artefato temporário de transição enquanto a direção
Python-first centrada no Hermes ainda estava sendo estabelecida.

Essa condição de transição não se sustenta mais:

- o esqueleto do pacote Python agora existe em `src/verabrain`
- o quality gate do repositório já pode rodar via `uv`
- as verificações de limites arquiteturais agora existem em Python

Manter o scaffold temporário de Node depois disso deixaria o
repositório com duas fundações concorrentes e continuaria sinalizando
que o caminho antigo standalone ainda está ativo.

## Decisão

Retirar o scaffold temporário de TypeScript e Node do repositório.

Isso inclui:

- remover o módulo de limites arquiteturais em TypeScript e seus testes
- remover `package.json`, `package-lock.json`, `tsconfig.json`,
  `vitest.config.ts` e a configuração de lint específica de Node
- substituir os comandos de qualidade baseados em Node por comandos em
  Python e `uv`
- mover a validação e formatação de markdown para ferramentas Python
  gerenciadas por `uv`

A direção Hermes-centered e Python-first da ADR-0003 continua em vigor.
Esta ADR apenas encerra o período de coexistência temporária.

## Alternativas consideradas

1. Manter indefinidamente o scaffold temporário de Node
2. Manter o Node apenas para ferramentas de repositório como validação
   de markdown
3. Retirar o scaffold e atualizar o repositório para uma fundação
   apenas em Python

## Consequências

- Positivas:
  - remove a ambiguidade de stack misto do repositório
  - simplifica o quality gate e o onboarding de contribuidores
  - faz o estado do repositório refletir a direção de produto aceita
  - reduz a manutenção de testes de limites e tooling duplicados
- Negativas/Trade-offs:
  - remove o antigo caminho de fallback baseado em Node
  - exige equivalentes em Python para ferramentas do repositório como
    validação de markdown
  - faz qualquer uso futuro de TypeScript voltar como reintrodução
    deliberada, não como um padrão remanescente

## Notas

Esta decisão não muda o princípio arquitetural da ADR-0002 nem a
direção Hermes-centered e Python-first da ADR-0003. Ela apenas retira o
scaffold temporário do repositório que existia durante a transição.
