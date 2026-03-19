# ADR-0002: Posicionar o VeraBrain como extensão do Hermes

[English](./ADR-0002-verabrain-as-hermes-extension.md)

## Status

Accepted

## Contexto

O VeraBrain foi inicialmente concebido como um sistema de agente
pessoal standalone, com seu próprio runtime, camada de memória, camada
de ferramentas e sistema de conhecimento.

Após analisar o Hermes Agent, ficou claro que ele já fornece uma grande
parte da infraestrutura que o VeraBrain precisaria construir do zero:

- loop de agente e runtime de tool calling
- interfaces de terminal e mensageria
- registry de tools e sistema de plugins
- suporte a MCP para ecossistemas externos de ferramentas
- memória persistente limitada via `MEMORY.md` e `USER.md`
- recall de sessões via SQLite + `session_search`
- memória procedural via skills
- modelagem opcional do usuário entre sessões via Honcho

Ao mesmo tempo, o Hermes não cobre integralmente o caso de uso pretendido
para o VeraBrain. A memória embutida dele é intencionalmente limitada e
orientada ao prompt, enquanto a capacidade desejada para o VeraBrain se
aproxima mais de um second brain e de um sistema pessoal de
conhecimento, com retrieval mais rico, objetos de conhecimento duráveis
e um corpus mais amplo que memória curada para prompt.

## Decisão

Reposicionar o VeraBrain de uma implementação standalone de agente para
uma arquitetura de extensão centrada no Hermes.

A direção padrão passa a ser:

- Hermes Agent como runtime e shell principal do agente
- VeraBrain como subsistema complementar de second brain e conhecimento
  pessoal
- um servidor MCP como principal superfície de integração entre Hermes
  e VeraBrain
- um plugin fino opcional do Hermes para melhorias de UX, setup ou
  skills empacotadas quando necessário

A lógica de negócio do VeraBrain deve permanecer fora da camada de
integração. O MCP é o adaptador inicial, não o centro arquitetural do
sistema.

O VeraBrain deve complementar a memória do Hermes, e não substituí-la:

- a memória nativa do Hermes permanece como camada quente, limitada e
  injetada no prompt
- as skills do Hermes permanecem como memória procedural
- o session search do Hermes permanece como recall de transcrições
- o Honcho permanece como modelagem opcional do usuário
- o VeraBrain passa a ser a camada de conhecimento pessoal de longo
  prazo e second brain

## Alternativas consideradas

1. Continuar construindo o VeraBrain como agente standalone do zero
2. Construir o VeraBrain apenas como plugin nativo do Hermes
3. Construir o VeraBrain como subsistema MCP-first com uma camada fina
   opcional de plugin

## Consequências

- Positivas:
  - evita reconstruir infraestrutura de agente que o Hermes já entrega
  - acelera o tempo até um sistema pessoal utilizável
  - preserva uma separação conceitual limpa entre memória quente e
    conhecimento de longo prazo
  - mantém o VeraBrain reutilizável fora do Hermes ao centralizar a
    integração em MCP
  - reduz acoplamento com internals não documentados do Hermes em
    comparação com uma abordagem puramente plugin
  - preserva um caminho de migração de baixo atrito da integração via
    MCP para um plugin nativo ou integração via hooks no futuro
- Negativas/Trade-offs:
  - desloca o centro de implementação da direção originalmente
    TypeScript-first para um ecossistema Hermes/Python
  - introduz dependência da evolução do projeto Hermes e de seus pontos
    de extensão
  - ainda pode exigir uma fina camada de compatibilidade se hooks de
    plugin do Hermes forem necessários além do registro de tools
  - exige cuidado de UX para que memória do Hermes, Honcho, skills e
    VeraBrain não se sobreponham de forma confusa

## Notas

O sistema de plugins do Hermes é maduro o suficiente para adicionar
tools, mas os hooks de ciclo de vida documentados parecem mais amplos do
que os hooks atualmente invocados no runtime. Isso torna o MCP a
superfície primária de integração mais segura para a primeira versão do
VeraBrain sobre o Hermes.

Para preservar flexibilidade de migração no futuro, o VeraBrain deve ser
separado em camadas:

- um core de memória e conhecimento que seja dono dos modelos de dados,
  persistência, classificação, retrieval e ranking
- um adaptador MCP fino que exponha essas capacidades como tools
- um adaptador opcional fino de plugin do Hermes para integração direta
  futura

Com essa estrutura, uma migração posterior de uma integração MCP-first
para uma integração nativa por plugin ou hooks deve exigir apenas a
troca da camada adaptadora, e não a reescrita do core do VeraBrain.
