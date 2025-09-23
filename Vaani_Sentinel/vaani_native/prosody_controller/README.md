# Vaani Native TTS Prosody Controller Directory
# Day 3: RL-driven prosody control for expressive speech
# - policy.py: Discrete Q-learning policy for prosody actions
# - train_policy.py: RL training loop with automated reward proxy
# - reward_proxy.py: MOS-proxy quality assessment (spectral distance + heuristics)
# Action space: pitch_shift ∈ {-1,0,1}, speed ∈ {0.9,1.0,1.1}, energy ∈ {-1,0,1}, emotion ∈ {neutral, warm}
