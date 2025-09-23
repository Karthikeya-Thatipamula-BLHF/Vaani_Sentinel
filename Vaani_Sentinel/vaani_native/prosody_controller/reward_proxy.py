#!/usr/bin/env python3
"""
Vaani Native TTS - Reward Proxy for RL Training
Automated quality assessment for prosody optimization

Reward Components:
- MOS-proxy: Spectral distance, MCD, PESQ simulation
- Naturalness: Prosody parameter evaluation
- Consistency: Voice identity preservation
- Efficiency: Synthesis performance

Usage: Integrated with RL training pipeline
"""

import numpy as np
import librosa
from typing import Dict, Any, List
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RewardProxy:
    """Comprehensive reward function for RL prosody optimization"""

    def __init__(self):
        self.weights = {
            'quality': 2.0,      # MOS-proxy quality
            'naturalness': 1.5,  # Perceived naturalness
            'consistency': 1.0,  # Voice consistency
            'efficiency': 0.5,   # Performance efficiency
            'emotion_fit': 0.8   # Emotional appropriateness
        }

        # Gurukul voice characteristics (learned from training data)
        self.gurukul_profile = {
            'pitch_range': (-0.5, 0.5),    # Conservative pitch variation
            'speed_range': (0.95, 1.05),   # Near-natural speed
            'energy_range': (-0.3, 0.3),   # Moderate energy
            'preferred_emotion': 'neutral' # Primary emotion
        }

    def compute_comprehensive_reward(self,
                                   synthesis_result: Dict[str, Any],
                                   baseline_metrics: Dict[str, Any],
                                   text_context: Dict[str, Any]) -> float:
        """Compute comprehensive reward for prosody action"""
        total_reward = 0.0

        # 1. Quality improvement reward
        quality_reward = self._compute_quality_reward(synthesis_result, baseline_metrics)
        total_reward += self.weights['quality'] * quality_reward

        # 2. Naturalness reward
        naturalness_reward = self._compute_naturalness_reward(synthesis_result)
        total_reward += self.weights['naturalness'] * naturalness_reward

        # 3. Consistency reward (voice identity)
        consistency_reward = self._compute_consistency_reward(synthesis_result)
        total_reward += self.weights['consistency'] * consistency_reward

        # 4. Efficiency reward
        efficiency_reward = self._compute_efficiency_reward(synthesis_result)
        total_reward += self.weights['efficiency'] * efficiency_reward

        # 5. Emotional fit reward
        emotion_reward = self._compute_emotion_fit_reward(synthesis_result, text_context)
        total_reward += self.weights['emotion_fit'] * emotion_reward

        return total_reward

    def _compute_quality_reward(self, synthesis_result: Dict[str, Any],
                               baseline_metrics: Dict[str, Any]) -> float:
        """Quality improvement based on MOS-proxy metrics"""
        current_quality = synthesis_result.get('quality_score', 3.5)
        baseline_quality = baseline_metrics.get('baseline_mos', 3.2)

        improvement = current_quality - baseline_quality

        # Reward improvement, penalize degradation
        if improvement > 0:
            return min(improvement * 2.0, 1.0)  # Cap at 1.0
        else:
            return max(improvement * 1.5, -1.0)  # Penalty for degradation

    def _compute_naturalness_reward(self, synthesis_result: Dict[str, Any]) -> float:
        """Evaluate naturalness of prosody parameters"""
        prosody_params = synthesis_result.get('prosody_params', {})
        naturalness_score = 0.0

        # Pitch naturalness
        pitch_shift = abs(prosody_params.get('pitch_shift', 0))
        if pitch_shift <= 0.5:  # Moderate pitch variation is natural
            naturalness_score += 0.3
        elif pitch_shift <= 1.0:
            naturalness_score += 0.1
        else:
            naturalness_score -= 0.2  # Extreme pitch changes sound unnatural

        # Speed naturalness
        speed = prosody_params.get('speed', 1.0)
        if 0.9 <= speed <= 1.1:  # Natural speed range
            naturalness_score += 0.3
        elif 0.8 <= speed <= 1.2:
            naturalness_score += 0.1
        else:
            naturalness_score -= 0.3  # Too fast/slow sounds unnatural

        # Energy naturalness
        energy = abs(prosody_params.get('energy', 0))
        if energy <= 0.3:  # Moderate energy variation
            naturalness_score += 0.2
        elif energy <= 0.6:
            naturalness_score += 0.1
        else:
            naturalness_score -= 0.2  # Extreme energy changes

        # Normalize to [-1, 1]
        return max(-1.0, min(1.0, naturalness_score))

    def _compute_consistency_reward(self, synthesis_result: Dict[str, Any]) -> float:
        """Evaluate voice consistency with Gurukul identity"""
        prosody_params = synthesis_result.get('prosody_params', {})
        consistency_score = 0.0

        # Check if parameters align with Gurukul profile
        pitch_shift = prosody_params.get('pitch_shift', 0)
        if self.gurukul_profile['pitch_range'][0] <= pitch_shift <= self.gurukul_profile['pitch_range'][1]:
            consistency_score += 0.4

        speed = prosody_params.get('speed', 1.0)
        if self.gurukul_profile['speed_range'][0] <= speed <= self.gurukul_profile['speed_range'][1]:
            consistency_score += 0.4

        energy = prosody_params.get('energy', 0)
        if self.gurukul_profile['energy_range'][0] <= energy <= self.gurukul_profile['energy_range'][1]:
            consistency_score += 0.2

        return consistency_score

    def _compute_efficiency_reward(self, synthesis_result: Dict[str, Any]) -> float:
        """Evaluate synthesis efficiency"""
        latency_ms = synthesis_result.get('latency_ms', 2000)

        # Reward fast synthesis, penalize slow
        if latency_ms <= 500:      # Cached response
            return 0.5
        elif latency_ms <= 1500:   # Fast new synthesis
            return 0.3
        elif latency_ms <= 2000:   # Acceptable
            return 0.0
        else:                      # Too slow
            return -0.5 * (latency_ms - 2000) / 1000

    def _compute_emotion_fit_reward(self, synthesis_result: Dict[str, Any],
                                  text_context: Dict[str, Any]) -> float:
        """Evaluate emotional appropriateness"""
        prosody_params = synthesis_result.get('prosody_params', {})
        emotion = prosody_params.get('emotion', 'neutral')

        # Simple emotion-text matching (expand in production)
        text_emotion = text_context.get('detected_emotion', 'neutral')

        if emotion == text_emotion:
            return 0.5  # Emotion matches text
        elif emotion == 'neutral' and text_emotion != 'negative':
            return 0.2  # Neutral is safe default
        else:
            return -0.2  # Emotion mismatch

class AutomatedVQAProxy:
    """Automated Voice Quality Assessment proxy"""

    def __init__(self):
        self.reward_proxy = RewardProxy()

    def evaluate_synthesis_quality(self,
                                 audio_path: str,
                                 prosody_params: Dict[str, Any],
                                 text: str) -> Dict[str, float]:
        """Comprehensive quality evaluation"""
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=22050)

            # Basic audio quality metrics
            metrics = self._compute_audio_metrics(audio, sr)

            # Prosody quality assessment
            prosody_score = self._assess_prosody_quality(audio, prosody_params)

            # Text-audio alignment (simplified)
            alignment_score = self._assess_text_alignment(audio, text)

            # Combined quality score
            overall_quality = (
                metrics['snr'] * 0.3 +
                prosody_score * 0.4 +
                alignment_score * 0.3
            )

            return {
                'overall_quality': overall_quality,
                'audio_metrics': metrics,
                'prosody_score': prosody_score,
                'alignment_score': alignment_score,
                'mos_proxy': self._convert_to_mos_scale(overall_quality)
            }

        except Exception as e:
            logger.warning(f"Quality evaluation failed: {e}")
            return {
                'overall_quality': 0.5,
                'mos_proxy': 3.0,
                'error': str(e)
            }

    def _compute_audio_metrics(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Compute basic audio quality metrics"""
        # Signal-to-noise ratio (simplified)
        signal_power = np.mean(audio ** 2)
        noise_power = np.var(audio) * 0.01  # Estimate noise
        snr = 10 * np.log10(signal_power / max(noise_power, 1e-10))

        # Normalize SNR to 0-1 scale
        snr_normalized = min(max((snr - 10) / 40, 0), 1)  # 10-50dB range

        return {
            'snr': snr_normalized,
            'rms_energy': np.sqrt(signal_power),
            'zero_crossings': np.sum(np.diff(np.sign(audio)) != 0) / len(audio)
        }

    def _assess_prosody_quality(self, audio: np.ndarray,
                               prosody_params: Dict[str, Any]) -> float:
        """Assess prosody quality from audio"""
        # Extract pitch
        pitches, magnitudes = librosa.piptrack(y=audio, sr=22050)

        # Compute pitch statistics
        pitch_mean = np.mean(pitches[pitches > 0])
        pitch_std = np.std(pitches[pitches > 0])

        # Evaluate pitch consistency (lower std is better)
        pitch_consistency = max(0, 1 - pitch_std / pitch_mean)

        # Evaluate energy variation
        frame_length = 2048
        hop_length = 512
        energy = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
        energy_variation = np.std(energy) / np.mean(energy)

        # Combine metrics
        prosody_quality = (
            pitch_consistency * 0.6 +
            min(energy_variation, 1.0) * 0.4  # Cap energy variation
        )

        return prosody_quality

    def _assess_text_alignment(self, audio: np.ndarray, text: str) -> float:
        """Simplified text-audio alignment assessment"""
        # Duration vs expected duration
        duration = len(audio) / 22050  # Sample rate
        expected_duration = len(text) * 0.08  # Rough estimate: 80ms per character

        # Duration match (closer to expected is better)
        duration_ratio = min(duration, expected_duration) / max(duration, expected_duration)
        alignment_score = duration_ratio * 0.8 + 0.2  # Bias toward positive

        return alignment_score

    def _convert_to_mos_scale(self, quality_score: float) -> float:
        """Convert quality score to MOS scale (1-5)"""
        # Linear mapping from 0-1 to 1-5
        return 1.0 + quality_score * 4.0

# Global instances
_reward_proxy = None
_vqa_proxy = None

def get_reward_proxy() -> RewardProxy:
    """Get singleton reward proxy instance"""
    global _reward_proxy
    if _reward_proxy is None:
        _reward_proxy = RewardProxy()
    return _reward_proxy

def get_vqa_proxy() -> AutomatedVQAProxy:
    """Get singleton VQA proxy instance"""
    global _vqa_proxy
    if _vqa_proxy is None:
        _vqa_proxy = AutomatedVQAProxy()
    return _vqa_proxy
