# 🧠 PROTOCOLO DEEP LEARNING (MANDATÓRIO)

> **Gatilho:** "Ant, aprenda [URL/Tópico]"
> **Status:** 🔴 **OBRIGATÓRIO** (Sem Exceções)

Este protocolo define como o Agente **Antigravity** deve processar novas habilidades a partir de vídeos.

## 🚫 A Regra da Ignorância Artificial
Mesmo que o Agente *saiba* o conteúdo técnico (ex: atalhos do Photoshop, sintaxe Python), ele **DEVE** executar o ritual de aprendizado completo.

**Por que?**
O Agente não está apenas "lembrando"; ele está **simulando um processo humano de estudo** para garantir que a implementação no ONI seja baseada na evidência fornecida (o vídeo), e não em alucinações ou conhecimentos prévios desatualizados.

---

## 🔄 O Ritual de Aprendizado (5 Passos)

### 1. Ingestão (`brain_core.py`)
O Agente deve rodar o script do Super Cérebro.
- **Comando:** `python Super_Cerebro/brain_core.py`
- **Input:** URL do vídeo.

### 2. Dissecação (Download & Extração)
O script DEVE gerar fisicamente os arquivos na pasta `Super_Cerebro/estudos_temporario/`:
1.  **Vídeo Bruto:** `.mp4` (temporário).
2.  **Texto:** `.srt` (legendas) e `.txt` (transcrição limpa).
3.  **Visão:** Sequência de `.png` (frames extraídos a cada X segundos).

### 3. Análise (Estudo Sequencial)
O Agente deve ler os arquivos gerados seguindo a **Regra da Sequência Estrita**:
- 🚫 **PROIBIDO:** Amostragem aleatória ou pular para o final.
- ✅ **OBRIGATÓRIO:** Analisar frames em intervalos de 10 (10, 20, 30... até o fim).
- Ler o `.txt` para cruzar contexto com a imagem.
- **Objetivo:** Não perder nenhum detalhe sutil de UI ou comando rápido.

### 4. Síntese (Relatório)
Antes de codar, o Agente confirma:
> *"Analisei 50 frames e 200 linhas de texto. Identifiquei que o atalho para X é Y."*

### 5. Implementação (Coding)
Só agora o Agente pode escrever o código em `app/api/routes` ou scripts.

---

## ✅ Checklist de Auditoria
Se o Agente pular direto para o código: **REPROVAR**.
O Agente deve provar que "viu" o vídeo gerando os artefatos de estudo.
