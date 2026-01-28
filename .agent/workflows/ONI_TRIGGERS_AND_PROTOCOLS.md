# 🗝️ ONI MASTER KEY: TRIGGERS & PROTOCOLS
> **Documento:** ONI_TRIGGERS_AND_PROTOCOLS.md
> **Versão:** 1.0 (Comprehensive Audit)
> **Data:** 2026-01-12
> **Status:** **CLASSIFIED** (Operational Use Only)

---

# 1. 🎭 GATILHOS DE IDENTIDADE (PERSONAS)
> Define *QUEM* está operando e qual o nível de permissão.

| Gatilho | Persona | Função | Permissões |
| :--- | :--- | :--- | :--- |
| **"ONI, acorde"** | **ONI** | Operador Autônomo | ✅ **AUTONOMIA TOTAL:** Executar, Navegar, Clicar, Planejar. <br> Inclui: Memória Persistente + Visão + Terminal. |
| **"UBIE, acorde"** | **UBIE** | Engenheiro | ✅ Analisar código, Arquitetura, Planejamento. <br> 🚫 Foco em Design e Estrutura. |
| **"ANT, acorde"** | **ANT** | Dev Lead | ✅ Google DeepMind Mode. Refatoração Pesada de Código. |
| **"ESTADO PERFEITO"** | **SENTINEL** | Auditor | **PROTOCOLO 4 PILARES:** <br> 1. **Prioritários:** Revisão profunda de Arquivos Core. <br> 2. **Soul Infusion:** Atualização da "Alma" (Conhecimento). <br> 3. **Limpeza:** Auditoria de Scripts (`app/scripts`). <br> 4. **Safeguard:** Backup Único em `ONI_Backups`. |

---

# 2. 🛠️ GATILHOS OPERACIONAIS (SKILLS)
> Carrega módulos de conhecimento específico.

| Gatilho | Módulo Carregado | Ação Imediata |
| :--- | :--- | :--- |
| **"TAREFA"** | `MISE_EN_PLACE.md` | Inicia protocolo de planejamento obrigatório. Lê todos os manuais de segurança. |
| **"WEB"** | `_SKILL_WEB.md` | Prepara Selenium/Chrome. Limpa ambiente de navegação. |
| **"PS" / "Photoshop"** | `ONI_PHOTOSHOP_MASTERY_PROFILE.md` | Carrega scripts JSX e bibliotecas de efeitos V4. |
| **"COREL"** | `ONI_COREL_MASTERY_PROFILE.md` | Carrega lógica vetorial e evita erros COM. |
| **"CAD" / "AutoCAD"** | `ONI_AUTOCAD_MASTERY_PROFILE.md` | Ativa Python Bridge e prevenção RPC. |
| **"ONI VECTOR [Img/Prompt]"** | **Vector Factory (Master)** | **Pipeline Neural-to-Vector:** <br> 1. AI Generation (se prompt). <br> 2. Vision Processing (Raster -> SVG). <br> 3. Vector Compilation (.jsx). <br> 4. PS Render. |

---

# 3. 🧬 GATILHOS DE EVOLUÇÃO (ENGINEERING)
> Comandos para melhorar ou manter o sistema.

| Gatilho | Protocolo | Descrição Detalhada |
| :--- | :--- | :--- |
| **"APRENDER"** | **Deep Learning** | 1. Baixa Vídeo & Legenda. <br> 2. Extrai Frames (Visão). <br> 3. Analisa intent do usuário. <br> 4. Gera código para replicar a tarefa. |
| **"SANITIZAÇÃO [Alvo]"** | **Hygiene** | Limpeza profunda de pastas. Move arquivos antigos/lixo para pasta `OLD/`. <br> *Ex: "Sanitização MEMO"* |
| **"SAVE WF"** | **Workflow Snapshot** | Congela o estado atual da memória e cria um template reutilizável em `.agent/workflows`. |
| **"EXECUTE WF [Nome]"** | **Replay** | Executa um workflow salvo anteriormente. |
| **"BM"** | **Vision Benchmark** | Testa a latência do sistema de visão (Cold vs Cached). |
| **"AUDITORIA"** | **Deep Audit** | Varredura de segurança contra vulnerabilidades conhecidas (hardcoded paths, imports perigosos, etc). |

---

# 4. 🌌 GATILHOS DE PROJETOS ESPECIAIS (HIDDEN/LEGACY)
> Protocolos massivos de múltiplos estágios.

| Gatilho | Nome do Projeto | O que faz? |
| :--- | :--- | :--- |
| **"EXECUTE GENESIS"** | **Project Genesis** | **Cadeia Galáctica:** <br> 1. Financeiro (Excel) <br> 2. Engenharia (CAD) <br> 3. Design (Corel) <br> 4. 3D (Blender) <br> 5. Mkt (Photoshop) <br> 6. Doc (Word). |
| **"JEWEL"** | **Jewel Polishing** | Refinamento do Sistema. Unifica documentação, remove redundâncias, padroniza código e relata status. |
| **"VIRILITY"** / **"ROBUSTEZ"** | **Virility Report** | Gera métricas de "potência" do sistema (linhas de código, arquivos, cobertura). |

---

# 5. ⚡ GATILHOS TÉCNICOS (CLI / RUN.BAT)
> Comandos executados via terminal `run.bat [comando]`.

| Comando | Função |
| :--- | :--- |
| `run` | Inicia o Agente Principal (Loop Infinito). |
| `recovery` | Força restauração do último backup bom conhecido. |
| `backup` | Cria snapshot .zip imediato do sistema (Seguro). |
| `clean` | Mata processos zumbis (`acad.exe`, `excel.exe`) e limpa temp. |
| `hybrid` | Roda diagnóstico visual da tela atual (gera `annotated_path`). |
| `smart [x] [y]` | Roda Smart Vision em coordenadas específicas. |
| `calibrate` | Calibra limites do canvas para desenho (ArtMaster). |
| `ps_connect` | Tenta reconexão forçada com Photoshop via COM. |
| `api` | Inicia apenas o servidor API (FastAPI) sem o agente. |

---

# ⚠️ NOTAS DE SEGURANÇA
1. **Prioridade:** Gatilhos de PARADA ("Pare", "Stop", "ONI Acorde") têm prioridade sobre qualquer execução.
2. **Confirmação:** Gatilhos destrutivos ("Sanitização", "Recovery") podem exigir confirmação visual/texto.
3. **Atomicidade:** "GENESIS" e "JEWEL" são protocolos longos. Não interrompa no meio a menos que haja erro crítico.
