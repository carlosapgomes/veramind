# Modelo Conceitual do VeraBrain

[English](./verabrain-concept-model.md)

## Propósito

Este documento registra o modelo conceitual inicial do VeraBrain como um
second brain e sistema pessoal de conhecimento.

O objetivo é esclarecer o que pertence ao core do VeraBrain, o que
pertence a camadas opcionais de workflow e onde comportamentos inspirados
em GTD se encaixam.

## Posicionamento

O VeraBrain não deve ser enquadrado como:

- apenas um gerenciador de tarefas
- apenas um sistema de notas
- apenas um storage de memória para um agente
- apenas uma implementação de GTD

O VeraBrain deve ser enquadrado como:

- um sistema pessoal de memória e conhecimento
- uma camada de second brain que ajuda a capturar, organizar, relacionar
  e recuperar contexto durável
- uma camada opcional de execução para transformar open loops em ação

## Visão Arquitetural

O VeraBrain deve ser modelado em três camadas:

1. `Core de second brain`
2. `Sistema pessoal de conhecimento`
3. `Workflows de execução`

A ideia central é que execução é importante, mas deve ficar sobre o
modelo de conhecimento em vez de defini-lo.

## 1. Core de Second Brain

Este é o centro de gravidade mínimo do VeraBrain.

Ele deve ser responsável por:

- memória pessoal durável
- retrieval contextual
- relações semânticas entre itens
- fatos de identidade e preferências
- continuidade entre projetos e tópicos ao longo do tempo

Essa camada responde perguntas como:

- O que o sistema deve lembrar sobre o usuário ao longo do tempo?
- Que contexto deve ser fácil de recuperar depois?
- Que relações existem entre projetos, pessoas, tópicos e decisões?

### Objetos centrais

- `Memory`
  - fatos duráveis sobre o usuário, preferências, decisões, hábitos e
    contexto ativo
- `KnowledgeItem`
  - notas, documentos, trechos, capturas, resumos, referências e
    artefatos de pesquisa
- `Link`
  - relação semântica entre dois itens, como `supports`, `relates_to`,
    `contradicts`, `belongs_to` ou `derived_from`
- `Source`
  - metadado de origem de um item capturado, como URL, arquivo local,
    conversa, mensagem ou entrada manual

### Responsabilidades centrais

- capturar
- classificar
- enriquecer
- armazenar
- relacionar
- recuperar
- resumir

## 2. Sistema Pessoal de Conhecimento

Essa camada fica acima do core de memória e foca em gerenciar um corpus
mais amplo de conhecimento pessoal.

Ela deve incluir:

- notas
- capturas de pesquisa
- ADRs e decisões
- snippets
- bookmarks e capturas web
- transcrições
- documentos de apoio

### Conceitos de organização do PKS

- `Project`
  - um resultado de múltiplas etapas com relevância ativa ou histórica
- `Area`
  - um domínio persistente de responsabilidade como saúde, finanças,
    carreira, família ou trabalho em produto
- `Topic`
  - um tema ou conceito que pode atravessar múltiplos projetos e notas
- `Decision`
  - uma conclusão durável com racional e consequências
- `Reference`
  - informação útil que não é acionável sozinha, mas deve ser
    recuperável depois

### Princípio de design do PKS

O PKS deve otimizar para:

- captura fácil
- retrieval com baixo atrito
- linking significativo
- estruturação gradual

Ele não deve exigir que o usuário classifique tudo completamente logo no
início.

## 3. Workflows de Execução

Execução deve ser modelada como uma camada separada que usa as mesmas
estruturas subjacentes de memória e conhecimento.

Essa camada deve incluir:

- tarefas
- próximas ações
- lembretes
- itens waiting-for
- processamento de inbox
- revisões
- checklists

### Objetos de execução

- `InboxItem`
  - entrada ainda não processada e que precisa ser clarificada
- `Task`
  - item de ação concreto
- `OpenLoop`
  - algo não resolvido que pode ou não já ser uma tarefa explícita
- `Review`
  - processo recorrente ou ad hoc de reavaliação do estado

## Onde o GTD se Encaixa

GTD deve ser tratado como uma metodologia opcional de execução, e não
como a identidade central do VeraBrain.

Isso significa que o VeraBrain deve suportar capacidades inspiradas em
GTD, como:

- captura em inbox
- clarificação
- próximas ações
- acompanhamento de projetos
- waiting-for
- someday/maybe
- revisão semanal

Mas o modelo de dados não deve ser rigidamente codificado em torno de
GTD como único workflow válido.

### Postura recomendada

- `Core de second brain`: obrigatório
- `Sistema pessoal de conhecimento`: obrigatório
- `Camada de tarefas e revisão`: recomendada
- `Convenções de workflow GTD`: opcionais, mas de primeira classe

## Boundary Entre Conhecimento e Execução

A distinção a seguir deve permanecer explícita:

- Conhecimento responde: o que eu sei, o que aconteceu, o que importa e
  como as coisas se conectam?
- Execução responde: o que devo fazer agora, do que estou esperando
  retorno e o que precisa ser revisado?

Isso evita colapsar o VeraBrain em:

- um sistema puro de notas sem modelo de ação
- um sistema puro de tarefas com contexto fraco e memória pobre

## Entidades Iniciais Sugeridas

O primeiro conjunto conceitual de entidades deve ser:

- `Memory`
- `KnowledgeItem`
- `Project`
- `Area`
- `Task`
- `OpenLoop`
- `Decision`
- `Source`
- `Link`
- `Review`

Esse conjunto é intencionalmente amplo o suficiente para suportar PKM e
execução sem exigir uma implementação completa de GTD desde o primeiro
dia.

## Non-Goals Iniciais

Neste estágio, o VeraBrain não deve assumir:

- uma implementação completa de GTD antes que o modelo central de
  memória exista
- uma taxonomia rígida apenas de PARA ou apenas de GTD
- uma UI pesada de produtividade como primeiro marco
- que todo item capturado precise virar tarefa
- que todo pensamento em aberto precise ser formalizado imediatamente

## Implicação de Direção de Produto

O enquadramento provável de produto é:

> VeraBrain é um sistema pessoal de memória e conhecimento com
> workflows opcionais de execução, incluindo camadas de tarefas e
> revisão inspiradas em GTD.

Esse enquadramento mantém o sistema amplo o suficiente para suportar:

- casos de uso de second brain
- gestão pessoal de conhecimento
- continuidade entre projetos
- gestão de ação
- views futuras específicas de metodologia sem travar a arquitetura cedo
