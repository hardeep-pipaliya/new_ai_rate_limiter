"""
Queue routes for managing message queues
"""
from flask import Blueprint, request, jsonify
from app.services.queue_service import QueueService
from app.utils.exceptions import QueueNotFoundError, QueueAlreadyExistsError

queue_bp = Blueprint('queue', __name__)

@queue_bp.route('/queues/', methods=['GET'])
def get_queues():
    """Get all queues"""
    try:
        result = QueueService.get_all_queues()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500

@queue_bp.route('/queue/<queue_id>', methods=['GET'])
def get_queue(queue_id):
    """Get queue by ID"""
    try:
        result = QueueService.get_queue(queue_id)
        return jsonify(result), 200
    except QueueNotFoundError as e:
        return jsonify({'message': str(e), 'success': False}), 404
    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500

@queue_bp.route('/queue/create', methods=['POST'])
def create_queue():
    """Create a new queue with providers"""
    try:
        data = request.get_json()
        queue_id = data.get('queue_id')
        providers = data.get('providers', [])
        
        if not queue_id:
            return jsonify({'message': 'queue_id is required', 'success': False}), 400
        
        if not providers:
            return jsonify({'message': 'providers list is required', 'success': False}), 400
        
        result = QueueService.create_queue(queue_id, providers)
        return jsonify(result), 201
    except QueueAlreadyExistsError as e:
        return jsonify({'message': str(e), 'success': False}), 400
    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500

@queue_bp.route('/queue/delete/<queue_id>', methods=['DELETE'])
def delete_queue(queue_id):
    """Delete a queue"""
    try:
        result = QueueService.delete_queue(queue_id)
        return jsonify(result), 200
    except QueueNotFoundError as e:
        return jsonify({'message': str(e), 'success': False}), 404
    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500

@queue_bp.route('/queue/clear/<queue_id>', methods=['POST'])
def clear_queue(queue_id):
    """Clear all messages and stop workers for a queue"""
    try:
        result = QueueService.clear_queue(queue_id)
        return jsonify(result), 200
    except QueueNotFoundError as e:
        return jsonify({'message': str(e), 'success': False}), 404
    except Exception as e:
        return jsonify({'message': str(e), 'success': False}), 500 