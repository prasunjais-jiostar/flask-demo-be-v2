from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)


@app.route('/generate-script', methods=['POST'])
def generate_script():
    """
    Endpoint to generate a script.
    Currently returns a hardcoded success response.
    """
    return jsonify({
        'status': 'success',
        'message': 'Script generated successfully',
        'data': {
            'script_id': 'script_12345',
            'script_content': 'This is a sample generated script',
            'timestamp': datetime.now().isoformat()
        }
    }), 200


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
