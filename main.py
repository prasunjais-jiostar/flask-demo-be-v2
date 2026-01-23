from flask import Flask, jsonify, request
from datetime import datetime
import requests
import sqlite3
import uuid
from utils.generate_dialogue_files import parse_script_dialogues

app = Flask(__name__)

# Database setup
DATABASE = 'scripts.db'

def init_db():
    """Initialize the database with Script, Dialogue, and Video tables."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create Script table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Script (
            script_id TEXT PRIMARY KEY,
            location TEXT NOT NULL
        )
    ''')
    
    # Create Dialogue table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Dialogue (
            dialogue_id TEXT PRIMARY KEY,
            speaker TEXT NOT NULL,
            dialogue TEXT NOT NULL,
            sequence INTEGER NOT NULL,
            output_audio_path TEXT,
            output_video_path TEXT,
            script_id TEXT NOT NULL,
            FOREIGN KEY (script_id) REFERENCES Script(script_id)
        )
    ''')
    
    # Create Video table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Video (
            video_id TEXT PRIMARY KEY,
            script_id TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL,
            output_final_video_path TEXT,
            FOREIGN KEY (script_id) REFERENCES Script(script_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()


@app.route('/generate-script', methods=['POST'])
def generate_script():
    """
    Endpoint to generate a script by calling external API,
    parsing the response, and saving to database.
    """
    try:
        # Get request data
        request_data = request.get_json()
        
        # Only forward Cookie and Content-Type headers
        headers = {}
        if 'Cookie' in request.headers:
            headers['Cookie'] = request.headers['Cookie']
        if 'Content-Type' in request.headers:
            headers['Content-Type'] = request.headers['Content-Type']
        else:
            headers['Content-Type'] = 'application/json'
        
        # Call external API
        external_url = 'https://script-kiosk.emergent.host/api/generate-script'
        
        response = requests.post(external_url, json=request_data, headers=headers)
        response.raise_for_status()
        
        # Get script from response
        response_data = response.json()
        script_text = response_data.get('script', '')
        
        if not script_text:
            return jsonify({
                'status': 'error',
                'message': 'No script found in response'
            }), 400
        
        # Parse dialogues using the utility function
        dialogues = parse_script_dialogues(script_text)
        
        # Get location (set) from request
        location = request_data.get('set', '')
        
        # Generate script_id
        script_id = str(uuid.uuid4())
        
        # Save to database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Insert script with location
        cursor.execute('INSERT INTO Script (script_id, location) VALUES (?, ?)', (script_id, location))
        
        # Insert dialogues with sequence numbers
        for idx, (speaker, dialogue_text) in enumerate(dialogues, start=1):
            dialogue_id = str(uuid.uuid4())
            cursor.execute(
                'INSERT INTO Dialogue (dialogue_id, speaker, dialogue, sequence, output_audio_path, output_video_path, script_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (dialogue_id, speaker, dialogue_text, idx, '', '', script_id)
            )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Script generated and saved successfully',
            'script': script_text,
            'data': {
                'script_id': script_id
            }
        }), 200
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to call external API: {str(e)}'
        }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }), 500


@app.route('/trigger-video-gen', methods=['POST'])
def trigger_video_gen():
    """
    Endpoint to trigger video generation.
    Creates a Video entry with pending status or returns existing entry.
    """
    try:
        # Get request data
        request_data = request.get_json()
        script_id = request_data.get('script_id')
        
        if not script_id:
            return jsonify({
                'status': 'error',
                'message': 'script_id is required'
            }), 400
        
        # Verify script exists
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT script_id FROM Script WHERE script_id = ?', (script_id,))
        script = cursor.fetchone()
        
        if not script:
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Script not found'
            }), 404
        
        # Check if video entry already exists for this script
        cursor.execute('SELECT video_id, status, output_final_video_path FROM Video WHERE script_id = ?', (script_id,))
        existing_video = cursor.fetchone()
        
        if existing_video:
            conn.close()
            return jsonify({
                'status': 'success',
                'message': 'Video entry already exists for this script',
                'data': {
                    'video_id': existing_video[0],
                    'script_id': script_id,
                    'video_processing_status': existing_video[1]
                }
            }), 200
        
        # Generate video_id
        video_id = str(uuid.uuid4())
        
        # Insert video entry with pending status
        cursor.execute(
            'INSERT INTO Video (video_id, script_id, status, output_final_video_path) VALUES (?, ?, ?, ?)',
            (video_id, script_id, 'pending', '')
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Video generation triggered successfully',
            'data': {
                'video_id': video_id,
                'script_id': script_id,
                'video_processing_status': 'pending'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }), 500


@app.route('/get-job-status', methods=['GET'])
def get_job_status():
    """
    Endpoint to get job status.
    Currently returns a hardcoded success response.
    """
    job_id = request.args.get('job_id', 'job_67890')

    return jsonify({
        'status': 'success',
        'message': 'Job status retrieved successfully',
        'data': {
            'job_id': job_id,
            'status': 'completed',
            'progress': 100,
            'result': 'Video generation completed successfully',
            'timestamp': datetime.now().isoformat()
        }
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200


if __name__ == '__main__':
    # For production, use a proper WSGI server like gunicorn
    # This is just for development
    app.run(host='0.0.0.0', port=8000, debug=False)
