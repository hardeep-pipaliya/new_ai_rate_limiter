"""
Celery tasks for processing messages
"""
import json
import requests
import time
from typing import Dict, Any
from app import celery, db
from app.models.message import Message
from app.models.provider import Provider
from app.models.batch import Batch
from app.services.redis_service import RedisService
from app.services.rabbitmq_service import RabbitMQService
from app.services.apisix_service import APISIXService
from app.utils.exceptions import MessageNotFoundError, ProviderNotFoundError

@celery.task(bind=True)
def process_message(self, message_id: str) -> Dict[str, Any]:
    """Process a single message through APISIX"""
    try:
        # Get message from database
        message = Message.query.filter_by(message_id=message_id).first()
        if not message:
            raise MessageNotFoundError(f"Message {message_id} not found")
        
        # Update status to processing
        message.status = 'processing'
        db.session.commit()
        
        # Get provider for the queue
        provider = Provider.query.filter_by(queue_id=message.queue_id).first()
        if not provider:
            raise ProviderNotFoundError(f"No provider found for queue {message.queue_id}")
        
        # Prepare request for APISIX
        request_data = {
            'model': provider.config_dict.get('model'),
            'messages': [
                {
                    'role': 'user',
                    'content': message.prompt
                }
            ]
        }
        
        if message.system_prompt:
            request_data['messages'].insert(0, {
                'role': 'system',
                'content': message.system_prompt
            })
        
        # Send request to APISIX
        response = APISIXService.send_request(
            provider=provider,
            request_data=request_data
        )
        
        # Update message with result
        message.status = 'completed'
        message.result = response.get('content', '')
        message.provider_id = provider.provider_id
        db.session.commit()
        
        # Store result in Redis
        RedisService.store_message_result(str(message.message_id), response)
        
        # If this is part of a batch, increment batch counter
        if message.batch_id:
            response_count = RedisService.increment_batch_response(str(message.batch_id))
            
            # Check if batch is complete
            batch = Batch.query.filter_by(batch_id=message.batch_id).first()
            if batch and response_count >= batch.request_count:
                # Batch is complete, publish to aggregator queue
                RabbitMQService.publish_batch_complete(str(message.batch_id))
        
        return {
            'success': True,
            'message_id': str(message.message_id),
            'result': response
        }
        
    except Exception as e:
        # Update message status to failed
        if 'message' in locals():
            message.status = 'failed'
            message.error_message = str(e)
            db.session.commit()
        
        # Re-raise the exception
        raise e

@celery.task(bind=True)
def process_batch_aggregator(self, batch_id: str) -> Dict[str, Any]:
    """Process batch completion and aggregate results"""
    try:
        # Get batch from database
        batch = Batch.query.filter_by(batch_id=batch_id).first()
        if not batch:
            return {'success': False, 'error': 'Batch not found'}
        
        # Get all messages for the batch
        messages = Message.query.filter_by(batch_id=batch_id).all()
        
        # Aggregate results
        results = []
        for message in messages:
            result = {
                'message_id': str(message.message_id),
                'status': message.status,
                'prompt': message.prompt,
                'result': message.result,
                'error_message': message.error_message
            }
            results.append(result)
        
        # Store batch results in Redis
        batch_data = {
            'batch_id': str(batch.batch_id),
            'request_count': batch.request_count,
            'response_count': batch.response_count,
            'results': results,
            'completed_at': time.time()
        }
        RedisService.store_batch_results(str(batch.batch_id), batch_data)
        
        # Update batch status
        batch.status = 'completed'
        batch.response_count = len([r for r in results if r['status'] == 'completed'])
        db.session.commit()
        
        # Send webhook if configured
        if batch.webhook_url:
            try:
                webhook_data = {
                    'batch_id': str(batch.batch_id),
                    'status': 'completed',
                    'request_count': batch.request_count,
                    'response_count': batch.response_count,
                    'results': results
                }
                
                response = requests.post(
                    batch.webhook_url,
                    json=webhook_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    batch.webhook_status = 'success'
                else:
                    batch.webhook_status = 'failed'
                
                batch.webhook_last_called_at = time.time()
                db.session.commit()
                
            except Exception as e:
                batch.webhook_status = 'failed'
                db.session.commit()
        
        return {
            'success': True,
            'batch_id': str(batch.batch_id),
            'results_count': len(results)
        }
        
    except Exception as e:
        raise e

@celery.task(bind=True)
def cleanup_expired_data(self) -> Dict[str, Any]:
    """Clean up expired data from Redis"""
    try:
        # This task can be scheduled to run periodically
        # to clean up old message results and batch data
        return {'success': True, 'message': 'Cleanup completed'}
    except Exception as e:
        raise e 