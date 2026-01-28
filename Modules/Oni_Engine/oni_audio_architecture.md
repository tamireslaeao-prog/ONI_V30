# 🎹 ONI AUDIO ARCHITECTURE: ROADMAP TO SUPREMACY

Atualmente, estamos no **Nível 1 (FFmpeg Filters)**. É funcional, mas é como "pintar com luvas de boxe". Para evoluir, precisamos de precisão cirúrgica.

## 📊 Níveis de Evolução

### Nível 1: FFmpeg Synthesizer (Atual) ✅
*   **Tecnologia:** `lavfi` (filter graphs).
*   **Prós:** Rápido, zero dependências extras.
*   **Contras:** 
    *   Sintaxe hostil (`sine=f=440...`).
    *   Sem ADSR (Attack, Decay, Sustain, Release) real = som de "beep" artificial.
    *   Difícil de sequenciar melodias complexas.

### Nível 2: ONI Audio Engine (Python/Numpy) 🚀 [RECOMENDADO]
*   **Tecnologia:** `numpy` + `scipy.io.wavfile`.
*   **Conceito:** Gerar áudio manipulando arrays matemáticos puros.
*   **Capacidades:**
    *   **Síntese FM:** Sons metálicos, sinos, baixos profundos (como o Yamaha DX7).
    *   **Envelopes:** Controle total de volume (fade-in/fade-out suaves).
    *   **Sequencer:** Escrever música usando Listas/Arrays Python (`[C4, E4, G4]`).
    *   **Sampling:** Carregar `.wav` reais (Bateria de verdade) e mixar via código.

### Nível 3: GenAI Audio (MusicGen/AudioCraft) 🤖
*   **Tecnologia:** Modelos de Deep Learning (Meta/Google).
*   **Prós:** Realismo absoluto.
*   **Contras:** Requer GPU massiva, instalação pesada, lento para gerar.

---

## 🛠️ Proposta de Próximo Passo: "ONI DSP"

Criar um módulo Python (`oni_dsp.py`) que atue como uma DAW (Digital Audio Workstation) sem interface:

```python
# Exemplo do que poderemos fazer:
synth = OniSynth()
track1 = synth.add_track("Bass")
track1.add_notes("C2", length=0.5, velocity=0.8)
track1.set_instrument("fm_bass")

track2 = synth.add_track("Drums")
track2.load_sample("kick.wav")
track2.sequence("x...x...x...")

synth.render("saida_profissional.wav")
```

**Veredito:** Devemos construir o **Nível 2 (Python DSP)**. Isso nos dá poder infinito de criação sem depender de "caixas pretas" de IA ou limitações do FFmpeg.
