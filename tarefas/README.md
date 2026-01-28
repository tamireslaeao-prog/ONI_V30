# Sistema de Tarefas ONI (ONI Tasks System)

Este diretório contém fluxos de trabalho automatizados e portáteis. Cada pasta numerada representa uma "Máquina" capaz de executar uma tarefa complexa de ponta a ponta.

## Estrutura Padrão (The Standard)

Cada tarefa deve seguir rigosamente esta estrutura para garantir portabilidade:

```text
NN_NOME_DA_TAREFA/
├── run.py              # Ponto de entrada ÚNICO. Execute isso para rodar.
├── manual.md           # Instruções de uso para o humano.
├── input/              # ONDE O USUÁRIO coloca os arquivos (texto, fotos).
├── output/             # ONDE O SISTEMA entrega o resultado final.
├── assets/             # Arquivos estáticos (CSS, Logos, Fontes) - NÃO MEXER.
└── modules/            # Scripts Python auxiliares (Logic Core) - NÃO MEXER.
```

## Regras de Ouro (Portabilidade)

1.  **Caminhos Relativos:** NUNCA use `C:\Users\...` nos scripts.
    *   Use `os.path.dirname(__file__)` para descobrir onde o script está.
    *   Construa caminhos dinamicamente: `os.path.join(BASE_DIR, 'input', 'foto.jpg')`.
2.  **Input/Output Isolados:** O script só deve ler de `input/` e escrever em `output/`.
3.  **Configuração Zero:** O usuário não deve precisar instalar nada além do ambiente `venv` padrão do ONI.

## Como Usar

1.  Entre na pasta da tarefa desejada.
2.  Coloque os arquivos necessários na pasta `input/` (conforme o `manual.md`).
3.  Execute `python run.py`.
4.  Pegue o resultado na pasta `output/`.
