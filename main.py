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
    """Initialize the database with Script and Dialogue tables."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create Script table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Script (
            script_id TEXT PRIMARY KEY
        )
    ''')
    
    # Create Dialogue table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Dialogue (
            dialogue_id TEXT PRIMARY KEY,
            speaker TEXT NOT NULL,
            dialogue TEXT NOT NULL,
            sequence INTEGER NOT NULL,
            script_id TEXT NOT NULL,
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
        
        # Generate script_id
        script_id = str(uuid.uuid4())
        
        # Save to database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Insert script
        cursor.execute('INSERT INTO Script (script_id) VALUES (?)', (script_id,))
        
        # Insert dialogues with sequence numbers
        for idx, (speaker, dialogue_text) in enumerate(dialogues, start=1):
            dialogue_id = str(uuid.uuid4())
            cursor.execute(
                'INSERT INTO Dialogue (dialogue_id, speaker, dialogue, sequence, script_id) VALUES (?, ?, ?, ?, ?)',
                (dialogue_id, speaker, dialogue_text, idx, script_id)
            )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Script generated and saved successfully',
            'script': script_text,
            'data': {
                'script_id': script_id,
                'timestamp': datetime.now().isoformat()
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
    Currently returns a hardcoded success response.
    """
    return jsonify({
        'status': 'success',
        'message': 'Video generation triggered successfully',
        'data': {
            'job_id': 'job_67890',
            'video_id': 'video_abcde',
            'status': 'processing',
            'timestamp': datetime.now().isoformat()
        }
    }), 200


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
