# 📐 ONI Knowledge: Desenho Técnico Mecânico

> **Fonte:** Tutorial YouTube (17J1yiaYP0Y) + [Apostila UFPR](APOSTILA_UFPR_RESUMO.md)
> **Aprendido:** 2026-01-06

> [!NOTE]
> Consulte o resumo detalhado das normas em: [`APOSTILA_UFPR_RESUMO.md`](APOSTILA_UFPR_RESUMO.md)

---

## 🔑 REGRAS PARA TEMPLATES TÉCNICOS

### 1. Tipos de Linhas (NBR 8403)

| Tipo | Estilo | Uso no Template |
|------|--------|-----------------|
| **Contínua** | `────────` | Contornos externos da caixa |
| **Tracejada** | `- - - - -` | Linhas de DOBRA (pliure) |
| **Traço-ponto** | `─ · ─ · ─` | Eixos de simetria, centro de furos |

### 2. Aplicação em CorelDRAW/Photoshop

```
Ao criar template de embalagem:
1. Contornos → Outline.Style = 0 (sólido)
2. Dobras → Outline.Style = 2 (tracejado)  
3. Centros → Outline.Style = 4 (traço-ponto)
```

### 3. Cotas e Dimensões

- **SEMPRE** posicionar cotas FORA do desenho
- Usar linhas de chamada para conectar
- Texto orientado para leitura (horizontal ou 90°)

### 4. Vistas Ortográficas

```
       [SUPERIOR]
           ↓
    [LATERAL] ← [FRONTAL]
```

- Template planificado = Vista SUPERIOR da caixa montada
- Linhas de dobra indicam onde haverá mudança de plano

---

## 🎯 CHECKLIST PRÉ-TEMPLATE

- [ ] Definir unidade de medida (cm/mm)
- [ ] Contornos externos em linha contínua
- [ ] Linhas de dobra em tracejado
- [ ] Adicionar cotas fora do desenho
- [ ] Marcar centros de furos com traço-ponto
- [ ] Verificar alinhamento entre vistas
