# Relatório de Auditoria de Código - Repositório tamireslaeao-prog/ONI_V30

**Autor:** Manus AI
**Data:** 28 de Janeiro de 2026
**Escopo:** Análise completa do código-fonte, estrutura, dependências e documentação do repositório `ONI_V30`.

---

## 1. Resumo Executivo

O repositório `ONI_V30` representa um sistema de automação de desktop altamente complexo e ambicioso, denominado **Omega Neural Interface (ONI)**. A arquitetura é modular, baseada em um servidor **FastAPI** e módulos de automação específicos para aplicações criativas (Photoshop, Blender, After Effects) e sistema operacional (Windows).

A auditoria identificou que o projeto está em um estado de **transição arquitetural** e **maturação de protocolo**, com uma forte ênfase em **auto-cura (self-healing)** e **memória cognitiva**.

| Categoria | Status | Impacto |
| :--- | :--- | :--- |
| **Hardcoded (Caminhos/Versões)** | **CRÍTICO** | Alta dependência de ambiente Windows específico, dificultando portabilidade e manutenção. |
| **Inconsistências de Arquitetura** | **ALTO** | Coexistência de lógica de automação robusta (Onihand/ArtMaster) com métodos fracos (`pyautogui` direto), e desalinhamento de versões. |
| **Segurança e Privacidade** | **MÉDIO** | Exposição de caminhos de rede e coleta de IP público. Risco de `Race Condition` no `Sentinel`. |
| **Qualidade de Código/Testes** | **MÉDIO** | Falta de testes unitários significativos e redundância em dependências. |

---

## 2. Análise de Arquitetura e Inconsistências

O sistema ONI é construído em torno de um servidor **FastAPI** (`app/main.py`) que expõe uma série de endpoints REST para controle de automação e serviços cognitivos.

### 2.1. Inconsistências de Versão

O projeto apresenta uma inconsistência crítica em sua auto-identificação, o que pode levar a confusão e erros de integração:

| Arquivo | Versão Declarada | Observação |
| :--- | :--- | :--- |
| `app/core/config.py` | `25.1.0` | **ONI V25.1 - Soul Binding Consolidado** |
| `MASTER.md` | `25.1` | **SISTEMA UNIFICADO & OPERACIONAL** |
| `Modules/Oni_Engine/oni_video_brain.py` | `23.0` | Módulo central de vídeo está desatualizado. |
| `Modules/Windows/ONI.Windows.psm1` | `1.0` | Módulo PowerShell principal desatualizado. |
| `Modules/Windows/ONI.Windows.v2.psm1` | `2.0.0` | Coexistência de v1 e v2 do módulo Windows. |
| `Modules/Blender/ONI_Blender_Bridge.py` | `2.0.0` | Versão do Add-on Blender. |

**Recomendação:** Centralizar a versão em um único local (`app/core/config.py`) e usar essa variável em todos os módulos e documentações.

### 2.2. Duplicação e Inconsistência de Lógica de Automação

O sistema possui serviços avançados de **Grounding Visual** (`UITarsProvider`, `OnihandService`, `ArtMaster`) que utilizam modelos de visão para localizar elementos com precisão. No entanto, a rota `/api/task/execute` em `app/api/routes/oni/task.py` ignora essa lógica e usa o módulo básico `pyautogui` diretamente [1].

```python
# app/api/routes/oni/task.py (Lógica Fraca)
elif action_type == "click":
    pyautogui.click(params.get("x", 0), params.get("y", 0))
# ...
# app/api/routes/onihand.py (Lógica Robusta)
result = await service.act(request.instruction) # Usa Grounding Visual
```

**Inconsistência:** A rota de execução de tarefas mais genérica (`/task/execute`) utiliza o método menos confiável e mais propenso a falhas de coordenadas fixas, enquanto a rota `onihand` utiliza a inteligência visual do sistema.

**Melhoria:** A rota `/task/execute` deve ser refatorada para utilizar o `OnihandService` para todas as ações de interação, garantindo que o **Axioma 6** (`Coordenadas de canvas_limits > valores hardcoded`) seja respeitado.

### 2.3. Dependências Redundantes

O arquivo `requirements.txt` lista a dependência `easyocr>=1.7.0` duas vezes, o que, embora não seja um erro funcional, indica falta de limpeza e manutenção no arquivo.

---

## 3. Hardcoded e Configuração

A principal falha de arquitetura do projeto reside na quantidade de valores fixos (hardcoded) que comprometem a portabilidade e a segurança.

### 3.1. Caminhos Absolutos do Windows

O sistema está profundamente acoplado a um ambiente Windows específico, utilizando caminhos absolutos que deveriam ser configuráveis ou descobertos dinamicamente:

| Arquivo | Caminho Hardcoded | Impacto |
| :--- | :--- | :--- |
| `Modules/Oni_Engine/config.py` | `data/bin/ffmpeg/bin/ffmpeg.exe` | Embora relativo ao projeto, usa `.exe` e assume estrutura de binários Windows. |
| `Modules/AfterEffects/oni_ae_bridge.py` | `C:\Program Files\Adobe\Adobe After Effects 2025\Support Files\AfterFX.exe` | Caminho fixo para o executável do After Effects. |
| `Modules/Photoshop/ONI_Photoshop_Bridge.py` | `C:\Program Files\Adobe\Adobe Photoshop 2026\Photoshop.exe` | Caminho fixo para o executável do Photoshop. |
| `Modules/Core/Scripts/Resolve-AppPaths.ps1` | `C:\Program Files\Blender Foundation`, `C:\Program Files\Adobe` | Embora tente descobrir a versão mais recente, o caminho base é fixo. |
| `memo/ASSETS_MAP.md` | `D:\DESIGN`, `D:\ATOM` | Caminhos de rede/disco fixos para ativos criativos. |

**Melhoria:** Implementar um serviço de descoberta de caminhos (como o `Resolve-AppPaths.ps1`, mas mais robusto e centralizado) que armazene os caminhos em um arquivo de configuração (e.g., `.env` ou `session.json`) e não no código-fonte.

### 3.2. Configuração de Rede e Endpoints

Endereços de rede e portas são fixos em vários serviços:

| Arquivo | Valor Hardcoded | Contexto |
| :--- | :--- | :--- |
| `Modules/Blender/ONI_Blender_Bridge.py` | `PORT = 8081`, `HOST = '127.0.0.1'` | Comunicação com o Blender Bridge. |
| `app/services/blender_service.py` | `self.port = 8081`, `self.host = '127.0.0.1'` | Cliente do Blender Bridge. |
| `Modules/Super_Cerebro/VideoKnowledge/config.py` | `API_BASE = "http://localhost:8000"` | Endpoint do servidor ONI. |

**Melhoria:** Todos os endpoints e portas devem ser configuráveis via `app/core/config.py` (usando `pydantic-settings`) e carregados via variáveis de ambiente.

### 3.3. Hardcoded de Modelos LLM

Os provedores de LLM (`zai_provider.py`, `mistral_provider.py`) definem modelos padrão fixos como *fallback* se as variáveis de ambiente não estiverem presentes:

```python
# app/infrastructure/llm/zai_provider.py
self._model = model or os.getenv("ZAI_MODEL", "glm-4.6v-flash")
# app/infrastructure/llm/mistral_provider.py
self._model = model or os.getenv("MISTRAL_MODEL", "mistral-small-latest")
```

**Melhoria:** Embora o uso de variáveis de ambiente seja a prática correta, o valor padrão fixo deve ser movido para a classe `LLMSettings` em `app/core/config.py`, permitindo que o LLM principal seja configurado centralmente.

---

## 4. Erros, Inconsistências e Vulnerabilidades

### 4.1. Falha na Estratégia de Testes

A auditoria revelou que os arquivos de teste existentes são ineficazes. Por exemplo, `Modules/Blender/Library/test_skill.py` contém apenas `print('I am a skill')`.

**Impacto:** A falta de testes unitários e de integração adequados para módulos complexos (como `OniDSP`, `VideoBrain` e os *bridges* de aplicação) aumenta o risco de regressão e dificulta a manutenção.

### 4.2. Risco de Vazamento de Segredos

Embora não haja chaves de API hardcoded diretamente no código-fonte, a lógica de carregamento de chaves de API (e.g., `STABILITY_API_KEY`, `NANO_API_KEY`) em `Modules/Photoshop/VectorFactory/nanobanana_gen.py` depende de um parser `.env` simples e não centralizado.

**Vulnerabilidade:** A ausência de um arquivo `.gitignore` no repositório (embora o `.env` não esteja presente) é um risco. Se um desenvolvedor criar um `.env` e esquecer de adicioná-lo ao `.gitignore`, as chaves podem ser acidentalmente comitadas.

**Melhoria:** Criar um `.gitignore` robusto que exclua `.env`, `__pycache__`, `server.log`, `data/memory/` e outros arquivos gerados.

### 4.3. Risco de `Race Condition` no Sentinel

O `ProcessSentinel` (`app/core/process_sentinel.py`) é um componente de segurança crítica que monitora e encerra processos de automação órfãos.

**Vulnerabilidade:** A função `emergency_purge_automation()` é chamada em `app/infrastructure/monitoring/exception_handlers.py` em caso de erro crítico. Essa função chama `scan_and_purge(force_all_targets=True)`, que encerra **todos** os processos listados em `TARGET_PROCESS_NAMES` (`powershell.exe`, `acad.exe`, `excel.exe`, etc.) independentemente da idade.

O `ERR-016` registrado em `memo/CORE/MEUS_ERROS.md` confirma o problema:

> **ERR-016: Sentinel Emergency Purge Mata Tudo**
> **Sintoma:** Ao reiniciar servidor, TODAS as janelas fecham (VS Code, Photoshop, tudo)

**Melhoria:** O `Sentinel` deve ser refatorado para rastrear processos **somente** se eles foram explicitamente iniciados pelo ONI (via PID ou um identificador de contexto) e não confiar apenas no nome do executável. A purga de emergência deve ser limitada aos processos rastreados.

### 4.4. Preocupação com Privacidade (Harvester)

O script `ONI_Windows_Harvester.ps1` coleta o endereço IP público do sistema usando um serviço externo (`https://api.ipify.org`).

**Preocupação:** A coleta de dados de rede e sistema deve ser justificada. Se o IP público não for essencial para a função do ONI, essa chamada deve ser removida ou tornada opcional, pois expõe o usuário a um terceiro.

---

## 5. Melhorias Propostas e Refatoração

As seguintes melhorias são sugeridas para aumentar a robustez, segurança e manutenibilidade do projeto:

| Área | Recomendação | Detalhes |
| :--- | :--- | :--- |
| **Arquitetura** | **Unificar a Lógica de Automação** | Refatorar `/api/task/execute` para usar o `OnihandService` ou `ArtMaster` em vez de `pyautogui` direto, garantindo que todas as ações de interação utilizem o *grounding visual* avançado. |
| **Configuração** | **Centralizar Caminhos** | Criar um serviço de configuração de caminhos que descubra dinamicamente os executáveis de aplicações criativas (Photoshop, Blender) e armazene-os em `session.json` ou `.env`. Eliminar caminhos absolutos do código-fonte. |
| **Segurança** | **Reforçar o Sentinel** | Modificar `ProcessSentinel` para rastrear processos por PID e contexto, e não apenas por nome. Limitar a purga de emergência a processos explicitamente rastreados pelo ONI. |
| **Segurança** | **Criar `.gitignore`** | Adicionar um arquivo `.gitignore` que exclua explicitamente `.env`, `__pycache__`, `data/memory/`, `server.log` e outros arquivos gerados ou sensíveis. |
| **Qualidade** | **Implementar Testes Unitários** | Criar um diretório `tests/` na raiz e adicionar testes unitários reais para módulos críticos como `OniDSP`, `VideoBrain`, `BlenderService` e `ProcessSentinel`. |
| **Qualidade** | **Limpeza de Dependências** | Remover a entrada duplicada de `easyocr>=1.7.0` do `requirements.txt`. |
| **Documentação** | **Consolidar Versão** | Garantir que todos os arquivos de documentação e código reflitam a versão atual do projeto (V25.1). |

---

## 6. Conclusão

O projeto ONI é um *framework* de automação de desktop de ponta, com mecanismos sofisticados de auto-cura e memória cognitiva. No entanto, sua maturidade é comprometida por uma forte dependência de caminhos absolutos do Windows e inconsistências na aplicação de sua própria lógica de automação avançada.

A refatoração focada na **desacoplagem do ambiente** (eliminando hardcoded de caminhos) e no **reforço da segurança** (melhorando o `Sentinel` e a gestão de segredos) é o próximo passo crucial para transformar o ONI em um sistema robusto e portátil.

---
## Referências

[1] `app/api/routes/oni/task.py` - Rota de execução de tarefas.
[2] `app/core/process_sentinel.py` - Implementação do Process Sentinel.
[3] `memo/CORE/MEUS_ERROS.md` - Registro de erros do agente.
[4] `Modules/Photoshop/ONI_Photoshop_Bridge.py` - Bridge do Photoshop com caminhos hardcoded.
[5] `Modules/Super_Cerebro/VideoKnowledge/processor.py` - Módulo de processamento de vídeo.
