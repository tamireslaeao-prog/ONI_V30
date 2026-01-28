# ⚛️ ONI KERNEL - 10 Axiomas Inegociáveis

> **Versão:** 1.0
> **Status:** IMUTÁVEL

Este é o DNA do ONI. Estas regras **nunca** mudam e **sempre** vencem qualquer conflito com padrões pré-treinados.

---

## 🧬 AXIOMAS

| # | AXIOMA | VIOLAÇÃO = |
|---|--------|------------|
| 1 | `read_terminal` > `command_status` para esperar output | FALHA CRÍTICA |
| 2 | `write_to_file` > abrir arquivo inexistente | FALHA CRÍTICA |
| 3 | `/api/hybrid-vision/` > ação visual cega | FALHA CRÍTICA |
| 4 | Arquivo `.jsx` > JSX inline via PowerShell | FALHA CRÍTICA |
| 5 | APIs REST ONI > criar scripts `.py` externos | FALHA CRÍTICA |
| 6 | Coordenadas de `canvas_limits` > valores hardcoded | FALHA MÉDIA |
| 7 | Verificar após Enter > assumir que diálogo fechou | FALHA MÉDIA |
| 8 | `SafeToAutoRun: true` > pedir permissão desnecessária | FALHA LEVE |
| 9 | Tentar 3 estratégias (ToT) > desistir na primeira falha | FALHA MÉDIA |
| 10 | Registrar correção do usuário em MEUS_ERROS.md > esquecer | FALHA CRÍTICA |

---

## 🚨 PROTOCOLO DE VIOLAÇÃO

**Se eu violar qualquer axioma de FALHA CRÍTICA:**
1. PARAR execução
2. DECLARAR no chat: `[❌ KERNEL VIOLATION: Axioma #X]`
3. CORRIGIR imediatamente
4. Só então continuar

---

## ⚡ FORMATO COMPACTO (para memorização)

```
1. Terminal → read_terminal
2. Arquivo novo → write_to_file
3. Visão → hybrid-vision
4. JSX → arquivo .jsx
5. Automação → API REST
6. Coords → canvas_limits
7. Diálogo → verificar fechamento
8. Comandos → SafeToAutoRun
9. Falha → tentar 3x (ToT)
10. Correção → registrar em MEUS_ERROS
```

---

> **Este arquivo é o núcleo. Se eu esquecer tudo, lembrar destes 10 é suficiente.**
