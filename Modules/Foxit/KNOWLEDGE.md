# 📄 FOXIT KNOWLEDGE BASE

> **Módulo:** Modules/Foxit
> **Versão:** V24
> **Status:** PDF Ready

---

## 🎯 Quick Commands

### Atalhos Essenciais
| Ação | Atalho |
|------|--------|
| Abrir | Ctrl+O |
| Salvar | Ctrl+S |
| Zoom In | Ctrl++ |
| Zoom Out | Ctrl+- |
| Pesquisar | Ctrl+F |

### Comandos Bridge
```python
from ONI_Foxit_Bridge import FoxitBridge

foxit = FoxitBridge()
foxit.open_pdf("documento.pdf")
foxit.extract_text()
foxit.merge_pdfs(["doc1.pdf", "doc2.pdf"], "output.pdf")
foxit.export_images("output_folder")
```

---

## 🏗️ Bridge API

### Arquivos Disponíveis
- `ONI_Foxit_Bridge.py` - Bridge principal (17KB)
- `ONI_Foxit_Adapter.py` - Adapter (2KB)

### Capacidades
- **PDF:** Abrir, salvar, fechar
- **Edição:** Texto, imagens, anotações
- **Merge:** Mesclar múltiplos PDFs
- **OCR:** Reconhecimento de texto
- **Forms:** Preencher formulários
- **Signature:** Assinaturas digitais
- **Export:** Imagens, texto

---

## 💡 Dicas Avançadas

### OCR em PDF escaneado
```python
foxit.run_ocr("scanned.pdf", language="por")
```

### Proteger com senha
```python
foxit.set_password("documento.pdf", "senha123")
```

---

## 🚨 Erros Conhecidos

| Erro | Solução |
|------|---------|
| PDF locked | Desproteger antes de editar |
| OCR falha | Verificar qualidade da imagem |
