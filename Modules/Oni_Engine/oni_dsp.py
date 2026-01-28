
"""
ONI V25.1 - AUDIO DSP ENGINE
Module: OniDSP
Status: Core Active
"""
import numpy as np
import scipy.io.wavfile as wavfile
from scipy import signal
from typing import List, Dict, Optional

class OniDSP:
    """
    Motor DSP aprimorado com síntese avançada.
    Melhorias: mais formas de onda, efeitos (reverb, chorus), 
    síntese FM, melhor ADSR.
    """
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def note_to_freq(self, note: str) -> float:
        """Converte nota musical para frequência (A4 = 440Hz)."""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        if len(note) == 3:  # C#3
            octave = int(note[2])
            key = notes.index(note[:2])
        else:  # C3
            octave = int(note[1])
            key = notes.index(note[0])
        
        semitone = key + (octave * 12)
        midi = semitone + 12
        return 440.0 * (2.0 ** ((midi - 69) / 12.0))
    
    def generate_wave(
        self, 
        freq: float, 
        duration: float, 
        wave_type: str = 'sine',
        phase: float = 0.0
    ) -> np.ndarray:
        """
        Gera forma de onda.
        Suporta: sine, square, saw, triangle, noise, pulse
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        
        if wave_type == 'sine':
            return np.sin(2 * np.pi * freq * t + phase)
        
        elif wave_type == 'square':
            return signal.square(2 * np.pi * freq * t + phase)
        
        elif wave_type == 'saw':
            return signal.sawtooth(2 * np.pi * freq * t + phase)
        
        elif wave_type == 'triangle':
            return signal.sawtooth(2 * np.pi * freq * t + phase, width=0.5)
        
        elif wave_type == 'noise':
            return np.random.uniform(-1, 1, len(t))
        
        elif wave_type == 'pulse':
            # Pulse wave with variable width
            return signal.square(2 * np.pi * freq * t + phase) * 0.5 + 0.5
        
        return np.zeros_like(t)
    
    def apply_adsr(
        self, 
        wave: np.ndarray,
        attack: float = 0.01,
        decay: float = 0.1,
        sustain: float = 0.7,
        release: float = 0.2
    ) -> np.ndarray:
        """Envelope ADSR aprimorado com curvas exponenciais."""
        n_samples = len(wave)
        sr = self.sample_rate
        
        # Calculate raw sample counts
        a_samples = int(attack * sr)
        d_samples = int(decay * sr)
        r_samples = int(release * sr)
        
        # Clamp to ensure they fit in the wave
        # Prioritize Attack > Release > Decay > Sustain
        if a_samples >= n_samples:
            a_samples = n_samples
            d_samples = 0
            s_samples = 0
            r_samples = 0
        elif a_samples + r_samples >= n_samples:
            r_samples = n_samples - a_samples
            d_samples = 0
            s_samples = 0
        else:
            # Remaining space for decay and sustain
            remaining = n_samples - a_samples - r_samples
            if d_samples > remaining:
                d_samples = remaining
                s_samples = 0
            else:
                s_samples = remaining - d_samples
        
        envelope = np.zeros(n_samples)
        current_idx = 0
        
        # Attack (exponencial)
        if a_samples > 0:
            envelope[:a_samples] = 1 - np.exp(-5 * np.linspace(0, 1, a_samples))
            current_idx += a_samples
        
        # Decay
        if d_samples > 0:
            end = current_idx + d_samples
            envelope[current_idx:end] = np.linspace(1.0, sustain, d_samples)
            current_idx = end
        
        # Sustain
        if s_samples > 0:
            end = current_idx + s_samples
            envelope[current_idx:end] = sustain
            current_idx = end
        
        # Release (exponencial)
        if r_samples > 0:
            # Release goes from sustain level to 0
            # If no sustain phase (s_samples=0), it might go from decay end level, which is sustain value anyway
            envelope[current_idx:] = sustain * np.exp(-5 * np.linspace(0, 1, r_samples))
        
        return wave * envelope
    
    def apply_reverb(
        self, 
        wave: np.ndarray, 
        room_size: float = 0.5,
        wet: float = 0.3
    ) -> np.ndarray:
        """Adiciona reverberação simples (delay-based)."""
        delay_samples = int(0.05 * self.sample_rate * room_size)
        decay = 0.5
        
        output = np.copy(wave)
        delayed = np.zeros_like(wave)
        
        # Múltiplas reflexões
        for i in range(4):
            current_delay = delay_samples * (i + 1)
            if current_delay < len(wave):
                delayed[current_delay:] += wave[:-current_delay] * (decay ** (i + 1))
        
        return (wave * (1 - wet)) + (delayed * wet)
    
    def apply_distortion(
        self, 
        wave: np.ndarray,
        gain: float = 10.0,
        mix: float = 1.0
    ) -> np.ndarray:
        """Distorção com soft clipping."""
        distorted = np.tanh(wave * gain) * 0.8
        return (distorted * mix) + (wave * (1 - mix))
    
    def render_composition(
        self, 
        tracks: List[Dict],
        output_path: str
    ) -> str:
        """
        Renderiza composição multi-track.
        
        tracks = [
            {
                "note": "C4",
                "duration": 1.0,
                "start": 0.0,
                "wave_type": "sine",
                "volume": 0.5,
                "effects": ["reverb", "distortion"]
            },
            ...
        ]
        """
        # Calcular duração total
        total_duration = max(
            (t["start"] + t["duration"]) for t in tracks
        )
        
        # Buffer mestre
        master_buffer = np.zeros(int(total_duration * self.sample_rate))
        
        print(f"[OniDSP] Renderizando {len(tracks)} tracks...")
        
        for track in tracks:
            freq = self.note_to_freq(track["note"])
            wave = self.generate_wave(
                freq, 
                track["duration"],
                track.get("wave_type", "sine")
            )
            
            # Aplicar ADSR
            wave = self.apply_adsr(wave)
            
            # Aplicar efeitos
            for effect in track.get("effects", []):
                if effect == "reverb":
                    wave = self.apply_reverb(wave)
                elif effect == "distortion":
                    wave = self.apply_distortion(wave, gain=track.get("gain", 10.0))
            
            # Aplicar volume
            wave *= track.get("volume", 0.5)
            
            # Adicionar ao buffer mestre
            start_idx = int(track["start"] * self.sample_rate)
            end_idx = start_idx + len(wave)
            
            if end_idx > len(master_buffer):
                master_buffer = np.pad(
                    master_buffer, 
                    (0, end_idx - len(master_buffer))
                )
            
            master_buffer[start_idx:end_idx] += wave
        
        # Normalizar
        max_val = np.max(np.abs(master_buffer))
        if max_val > 1.0:
            master_buffer /= max_val
        
        # Salvar
        scaled = np.int16(master_buffer * 32767)
        wavfile.write(output_path, self.sample_rate, scaled)
        
        print(f"[OniDSP] Salvo em: {output_path}")
        return output_path

    def render_sequence(self, sequence: List[tuple], output_path: str) -> str:
        """
        Legacy adapter for backward compatibility.
        Converts (note, duration) list to composition tracks.
        """
        print("[OniDSP] Using legacy render_sequence adapter...")
        tracks = []
        current_time = 0.0
        
        for note, duration in sequence:
            if note == 'REST':
                current_time += duration
                continue
                
            tracks.append({
                "note": note,
                "duration": duration,
                "start": current_time,
                "wave_type": "sine",
                "volume": 0.5,
                "effects": ["reverb"]
            })
            current_time += duration
            
        return self.render_composition(tracks, output_path)
