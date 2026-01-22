#!/usr/bin/env python3
"""
Script to extract dialogues from input JSON and create separate text files for each speaker.
"""

import json
import os
import re
from pathlib import Path


def parse_script_dialogues(script_text):
    """
    Parse the script text and extract dialogues for each speaker.
    
    Returns:
        list: List of tuples (speaker_name, dialogue_text)
    """
    dialogues = []
    
    # Split by newlines and process each line
    lines = script_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Match pattern: SPEAKER: (stage direction) dialogue
        # or SPEAKER: dialogue
        match = re.match(r'^([A-Z]+):\s*(?:\([^)]+\)\s*)?(.*)', line)
        
        if match:
            speaker = match.group(1)
            dialogue = match.group(2).strip()
            
            if dialogue:
                dialogues.append((speaker, dialogue))
    
    return dialogues


def create_dialogue_files(input_json_path, output_folder):
    """
    Read input JSON and create separate dialogue files for each speaker.
    
    Args:
        input_json_path: Path to input JSON file
        output_folder: Folder where dialogue files will be created
    """
    # Create output folder if it doesn't exist
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Read input JSON
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    script = data.get('script', '')
    
    # Parse dialogues
    dialogues = parse_script_dialogues(script)
    
    # Create dialogue files
    for idx, (speaker, dialogue) in enumerate(dialogues, start=1):
        filename = f"dialogue{idx}_{speaker}.txt"
        filepath = output_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(dialogue)
        
        print(f"Created: {filename}")
    
    print(f"\nTotal dialogues extracted: {len(dialogues)}")
    print(f"Output folder: {output_folder}")


def main():
    # Set paths
    script_dir = Path(__file__).parent
    input_json_path = script_dir / "input2.json"
    output_folder = script_dir / "tts_input_json_2"
    
    if not input_json_path.exists():
        print(f"Error: Input file not found: {input_json_path}")
        return
    
    print(f"Reading from: {input_json_path}")
    print(f"Output folder: {output_folder}")
    print("-" * 50)
    
    create_dialogue_files(input_json_path, output_folder)


if __name__ == "__main__":
    main()
