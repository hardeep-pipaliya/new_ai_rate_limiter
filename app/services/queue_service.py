"""
Queue service for managing message queues
"""
import uuid
from typing import List, Optional, Dict, Any
from app import db
from app.models.queue import Queue
from app.models.provider import Provider
from app.utils.exceptions import QueueNotFoundError, QueueAlreadyExistsError

class QueueService:
    """Service for managing queues"""
    
    @staticmethod
    def create_queue(queue_id: str, providers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a new queue with providers"""
        try:
            # Check if queue already exists
            existing_queue = Queue.query.filter_by(queue_id=queue_id).first()
            if existing_queue:
                raise QueueAlreadyExistsError(f"Queue {queue_id} already exists")
            
            # Create queue
            queue = Queue(queue_id=queue_id)
            db.session.add(queue)
            db.session.flush()  # Get the queue ID
            
            # Create providers
            created_providers = []
            for provider_data in providers:
                provider = Provider(
                    queue_id=queue.queue_id,
                    provider_name=provider_data.get('provider_name'),
                    provider_type=provider_data.get('provider_type'),
                    api_key=provider_data.get('api_key'),
                    limit=provider_data.get('limit', 1000),
                    time_window=provider_data.get('time_window', 3600),
                    config=provider_data.get('config', {})
                )
                db.session.add(provider)
                created_providers.append(provider)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Queue and providers created successfully',
                'queue': queue.to_dict(),
                'providers': [p.to_dict() for p in created_providers]
            }
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def get_queue(queue_id: str) -> Dict[str, Any]:
        """Get queue by ID with providers"""
        queue = Queue.query.filter_by(queue_id=queue_id).first()
        if not queue:
            raise QueueNotFoundError(f"Queue {queue_id} not found")
        
        providers = Provider.query.filter_by(queue_id=queue_id).all()
        
        return {
            'success': True,
            'data': {
                **queue.to_dict(),
                'providers': [p.to_dict() for p in providers]
            }
        }
    
    @staticmethod
    def get_all_queues() -> Dict[str, Any]:
        """Get all queues with their providers"""
        queues = Queue.query.all()
        result = []
        
        for queue in queues:
            providers = Provider.query.filter_by(queue_id=queue.queue_id).all()
            queue_data = queue.to_dict()
            queue_data['providers'] = [p.to_dict() for p in providers]
            result.append(queue_data)
        
        return {
            'data': result
        }
    
    @staticmethod
    def delete_queue(queue_id: str) -> Dict[str, Any]:
        """Delete a queue and all its associated data"""
        queue = Queue.query.filter_by(queue_id=queue_id).first()
        if not queue:
            raise QueueNotFoundError(f"Queue {queue_id} not found")
        
        db.session.delete(queue)
        db.session.commit()
        
        return {
            'success': True,
            'message': f"Queue {queue_id} deleted successfully"
        }
    
    @staticmethod
    def clear_queue(queue_id: str) -> Dict[str, Any]:
        """Clear all messages and stop workers for a queue"""
        queue = Queue.query.filter_by(queue_id=queue_id).first()
        if not queue:
            raise QueueNotFoundError(f"Queue {queue_id} not found")
        
        # Delete all messages
        from app.models.message import Message
        messages_deleted = Message.query.filter_by(queue_id=queue_id).delete()
        
        # Stop all workers
        from app.models.worker import Worker
        workers_stopped = Worker.query.filter_by(queue_id=queue_id).delete()
        
        db.session.commit()
        
        return {
            'success': True,
            'message': f"Queue {queue_id} cleared and all workers stopped and removed messages successfully",
            'queue_stopped': workers_stopped
        } 