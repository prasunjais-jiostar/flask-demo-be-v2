# -*- coding: utf-8 -*-
"""
chatterbox_tts.py: Text-to-Speech utility using Chatterbox AI

This utility provides TTS functionality using the Chatterbox AI API for generating
audio narration from text sequences. It supports voice cloning and multiple language options.

Created at 29/10/2025
"""

from __future__ import annotations

import logging
import os
import typing
import warnings

import torch

# Configure logging
logger = logging.getLogger(__name__)


class ChatterboxTTS:
    """
    Text-to-Speech utility using ResembleAI's Chatterbox multilingual TTS model.
    """

    def __init__(self):
        """Initialize Chatterbox TTS with model loading."""
        self.model = None
        self.config = None
        self.device = None
        self.load_chatterbox()

    def load_chatterbox(self):
        """Load ResembleAI's Chatterbox multilingual TTS model."""
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning)
                warnings.filterwarnings("ignore", message=".*torch_dtype.*deprecated.*")
                from chatterbox.mtl_tts import ChatterboxMultilingualTTS

            logger.info("Loading ResembleAI's Chatterbox multilingual TTS model...")
            logger.info(
                "This may take a while on first run as models are downloaded..."
            )

            # Enhanced CUDA detection for optimal device selection
            cuda_available = torch.cuda.is_available()

            if cuda_available:
                current_device = torch.cuda.current_device()
                gpu_memory = (
                    torch.cuda.get_device_properties(current_device).total_memory
                    / 1024**3
                )  # GB
                logger.info(
                    f"CUDA detected: Using GPU {current_device} with {gpu_memory:.1f}GB memory"
                )
                device = "cuda"
            else:
                logger.info("CUDA not available - loading model in CPU mode")
                device = "cpu"

            # Suppress warnings during model loading
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning)
                warnings.filterwarnings("ignore", message=".*attention mask.*")
                warnings.filterwarnings("ignore", message=".*pad token.*")

                # Load Chatterbox model with proper device management
                logger.info(f"Loading Chatterbox model on {device}...")

                # Set environment variable to force CPU mapping for CUDA checkpoints
                import os

                old_cuda_visible_devices = os.environ.get("CUDA_VISIBLE_DEVICES")

                try:
                    if device == "cpu":
                        # Force CPU loading by temporarily hiding CUDA devices
                        os.environ["CUDA_VISIBLE_DEVICES"] = ""

                        # Also monkey patch torch.load to always use CPU mapping
                        original_load = torch.load

                        def cpu_load(*args, **kwargs):
                            kwargs["map_location"] = "cpu"
                            return original_load(*args, **kwargs)

                        torch.load = cpu_load

                        try:
                            multilingual_model = (
                                ChatterboxMultilingualTTS.from_pretrained(device=device)
                            )
                        finally:
                            # Restore original torch.load
                            torch.load = original_load
                    else:
                        multilingual_model = ChatterboxMultilingualTTS.from_pretrained(
                            device=device
                        )

                finally:
                    # Restore original CUDA_VISIBLE_DEVICES
                    if old_cuda_visible_devices is not None:
                        os.environ["CUDA_VISIBLE_DEVICES"] = old_cuda_visible_devices
                    elif "CUDA_VISIBLE_DEVICES" in os.environ:
                        del os.environ["CUDA_VISIBLE_DEVICES"]

            # Define supported languages for Chatterbox (23 languages)
            chatterbox_config = {
                "supported_languages": {
                    "english": "en",
                    "spanish": "es",
                    "french": "fr",
                    "german": "de",
                    "italian": "it",
                    "portuguese": "pt",
                    "polish": "pl",
                    "turkish": "tr",
                    "russian": "ru",
                    "dutch": "nl",
                    "czech": "cs",
                    "arabic": "ar",
                    "chinese": "zh",
                    "japanese": "ja",
                    "hungarian": "hu",
                    "korean": "ko",
                    "hindi": "hi",
                    "finnish": "fi",
                    "vietnamese": "vi",
                    "ukrainian": "uk",
                    "greek": "el",
                    "bulgarian": "bg",
                    "croatian": "hr",
                },
                "default_language": "en",
                "sampling_rate": getattr(
                    multilingual_model, "sr", 24000
                ),  # Default to 24kHz
            }

            self.model = multilingual_model
            self.config = chatterbox_config
            self.device = device

            logger.info(f"Chatterbox model loaded successfully on {device}")
            logger.info(
                f"Supported languages: {', '.join(list(chatterbox_config['supported_languages'].keys())[:10])}... (23 total)"
            )

        except Exception as e:
            logger.error(f"Failed to load Chatterbox model: {e}")
            raise RuntimeError(f"Could not load Chatterbox model: {e}")

    def generate_audio(
        self,
        text: str,
        output_path: str,
        language: typing.Optional[str] = None,
        voice_clone_path: typing.Optional[str] = None,
    ) -> float:
        """Generate audio using ResembleAI's Chatterbox multilingual TTS model.

        Args:
            text: Text to convert to speech
            output_path: Path where the audio file will be saved
            language: Language code (e.g., 'hindi', 'english', 'spanish') or None for auto-detection
            voice_clone_path: Path to reference audio file for voice cloning (optional)

        Returns:
            Duration of generated audio in seconds
        """
        try:
            import torchaudio as ta

            if self.model is None:
                raise RuntimeError("Chatterbox model not loaded")

            # Voice cloning validation
            if voice_clone_path:
                if not os.path.exists(voice_clone_path):
                    raise FileNotFoundError(
                        f"Voice clone audio file not found: {voice_clone_path}"
                    )
                logger.info(
                    f"🎭 Voice cloning enabled with reference: {os.path.basename(voice_clone_path)}"
                )

            if not language:
                raise RuntimeError("Language must be specified for Chatterbox TTS")

            # Try to find language code
            language_lower = language.lower()
            if language_lower in self.config["supported_languages"]:
                language_id = self.config["supported_languages"][language_lower]
            elif language_lower in self.config["supported_languages"].values():
                language_id = language_lower
            else:
                logger.warning(
                    f"Unknown language '{language}', using default: {self.config['default_language']}"
                )
                language_id = self.config["default_language"]

            logger.info(f"Using language: {language_id} for text: {text[:50]}...")

            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # Generate audio with Chatterbox
            logger.info("Generating audio with Chatterbox multilingual TTS...")
            if voice_clone_path:
                logger.info(
                    f"Using voice cloning with reference: {os.path.basename(voice_clone_path)}"
                )
                wav_output = self.model.generate(
                    text=text,
                    language_id=language_id,
                    audio_prompt_path=voice_clone_path,  # Voice cloning reference
                )
            else:
                wav_output = self.model.generate(text, language_id=language_id)

            if wav_output is None or len(wav_output) == 0:
                raise RuntimeError("No audio generated by Chatterbox model")

            # Save audio file using torchaudio
            ta.save(output_path, wav_output, self.model.sr)

            # Calculate duration
            duration = (
                len(wav_output[0]) / self.model.sr
                if len(wav_output.shape) > 1
                else len(wav_output) / self.model.sr
            )

            # Verify audio quality
            max_amplitude = wav_output.abs().max().item()
            if max_amplitude < 0.001:
                logger.warning("Generated audio appears to be silent or very quiet")
                raise RuntimeError("Generated audio is silent")

            logger.info(
                f"Chatterbox generated audio of {duration:.2f} seconds with max amplitude {max_amplitude:.4f}"
            )
            return duration

        except Exception as e:
            logger.error(f"Chatterbox generation failed: {e}")
            raise
