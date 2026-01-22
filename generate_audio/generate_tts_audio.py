#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_tts_audio.py: Script to generate TTS audio from text files

This script reads text from text files in a folder and generates audio using ChatterboxTTS.
It can process multiple files in parallel.

Usage:
    python3 scripts/generate_tts_audio.py --input-folder <path> --output-folder <path> [--voice-clone <path>] [--language <lang>] [--max-workers <num>]

Example:
python3 generate_tts_audio.py \
    --input-folder ./tts_input_json_2 \
    --output-folder ./tts_output_json_2/R1 \
    --voice-clone /Users/rohit.dharrao/Desktop/hs/experimentation/short_story/output_from_metadata/Abhira_Armaans_Bittersweet_Dream_R1_merged_v6-1_P10_R2_T2/audio_clips/sequence_000_audio.wav \
    --language english \
    --max-workers 2

python3 generate_tts_audio.py \
    --input-folder ./tts_input_json_2_hindi \
    --output-folder ./tts_output_json_2_hindi/R2 \
    --voice-clone /Users/rohit.dharrao/Desktop/hs/experimentation/short_story/output_from_metadata/Abhira_Armaans_Bittersweet_Dream_R1_merged_v6-1_P10_R2_T2/audio_clips/sequence_000_audio.wav \
    --language hindi \
    --max-workers 1
"""

import argparse
import logging
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

# Add parent directory to path to import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.chatterbox_tts import ChatterboxTTS

# Maximum number of parallel workers for audio generation
MAX_PARALLEL_WORKERS = 4

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def process_single_file(text_file_path, output_folder, voice_clone_path, language):
    """
    Process a single text file and generate audio.
    Each process loads its own ChatterboxTTS instance for true parallelization.
    
    Args:
        text_file_path: Path to the input text file
        output_folder: Path to the output folder
        voice_clone_path: Path to voice clone reference audio (or None)
        language: Language for TTS
        
    Returns:
        Tuple of (success, text_file_path, output_path, duration, error_message)
    """
    # Configure logging for this process
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    text_file = Path(text_file_path)
    
    try:
        # Read text from file
        logger.info(f"Processing: {text_file.name}")
        with open(text_file, "r", encoding="utf-8") as f:
            text = f.read().strip()
        
        if not text:
            logger.warning(f"Skipping empty file: {text_file.name}")
            return (False, text_file_path, None, 0, "Empty file")
        
        # Generate output path with same name but .wav extension
        output_filename = text_file.stem + ".wav"
        output_path = os.path.join(output_folder, output_filename)
        
        # Load ChatterboxTTS in this process
        logger.info(f"Loading ChatterboxTTS for {text_file.name}...")
        chatterbox_tts = ChatterboxTTS()
        
        # Generate audio (each process has its own model, so no contention)
        logger.info(f"Generating audio for: {text_file.name}")
        duration = chatterbox_tts.generate_audio(
            text=text,
            output_path=output_path,
            language=language,
            voice_clone_path=voice_clone_path
        )
        
        logger.info(f"✅ Completed: {text_file.name} -> {output_filename} ({duration:.2f}s)")
        return (True, text_file_path, output_path, duration, None)
        
    except Exception as e:
        error_msg = f"Failed to process {text_file.name}: {str(e)}"
        logger.error(error_msg)
        return (False, text_file_path, None, 0, error_msg)


def main():
    """Main function to generate TTS audio from text files in a folder."""
    parser = argparse.ArgumentParser(
        description="Generate TTS audio from text files using ChatterboxTTS (with parallel processing)"
    )
    parser.add_argument(
        "--input-folder",
        required=True,
        help="Path to folder containing .txt files to convert to speech"
    )
    parser.add_argument(
        "--output-folder",
        required=True,
        help="Path to folder where audio files will be saved"
    )
    parser.add_argument(
        "--voice-clone",
        default="",
        help="Path to reference audio file for voice cloning (optional)"
    )
    parser.add_argument(
        "--language",
        default="hindi",
        help="Language for TTS generation (default: hindi)"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=MAX_PARALLEL_WORKERS,
        help=f"Maximum number of parallel workers (default: {MAX_PARALLEL_WORKERS})"
    )

    args = parser.parse_args()

    # Validate input folder exists
    input_folder = Path(args.input_folder)
    if not input_folder.exists():
        logger.error(f"Input folder not found: {args.input_folder}")
        sys.exit(1)
    
    if not input_folder.is_dir():
        logger.error(f"Input path is not a folder: {args.input_folder}")
        sys.exit(1)

    # Find all .txt files in input folder
    txt_files = list(input_folder.glob("*.txt"))
    if not txt_files:
        logger.error(f"No .txt files found in: {args.input_folder}")
        sys.exit(1)
    
    logger.info(f"Found {len(txt_files)} text file(s) to process")

    # Validate voice clone path if provided
    voice_clone_path = args.voice_clone if args.voice_clone else None
    if voice_clone_path and not os.path.exists(voice_clone_path):
        logger.error(f"Voice clone audio file not found: {voice_clone_path}")
        sys.exit(1)

    # Create output directory
    output_folder = Path(args.output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output folder: {args.output_folder}")

    # Process files in parallel using multiprocessing
    # Each process loads its own model instance for true parallelization
    logger.info(f"Starting parallel processing with {args.max_workers} worker(s)...")
    logger.info(f"Language: {args.language}")
    if voice_clone_path:
        logger.info(f"Voice cloning: {voice_clone_path}")
    logger.info("Note: Each worker process will load its own ChatterboxTTS model")
    
    results = []
    with ProcessPoolExecutor(max_workers=args.max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(
                process_single_file,
                str(txt_file),
                str(output_folder),
                voice_clone_path,
                args.language
            ): txt_file
            for txt_file in txt_files
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_file):
            txt_file = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Unexpected error processing {txt_file.name}: {e}")
                results.append((False, str(txt_file), None, 0, str(e)))
    
    # Print summary
    successful = [r for r in results if r[0]]
    failed = [r for r in results if not r[0]]
    
    logger.info("\n" + "=" * 70)
    logger.info("PROCESSING SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total files: {len(results)}")
    logger.info(f"Successful: {len(successful)}")
    logger.info(f"Failed: {len(failed)}")
    
    if successful:
        total_duration = sum(r[3] for r in successful)
        logger.info(f"Total audio duration: {total_duration:.2f} seconds")
        logger.info("\nSuccessful files:")
        for _, input_path, output_path, duration, _ in successful:
            logger.info(f"  ✅ {Path(input_path).name} -> {Path(output_path).name} ({duration:.2f}s)")
    
    if failed:
        logger.info("\nFailed files:")
        for _, input_path, _, _, error in failed:
            logger.info(f"  ❌ {Path(input_path).name}: {error}")
    
    logger.info("=" * 70)
    
    # Exit with error code if any files failed
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
