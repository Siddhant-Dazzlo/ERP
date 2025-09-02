from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request, session
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import threading
import time

class WebSocketManager:
    def __init__(self, app=None):
        self.socketio = SocketIO()
        self.connected_users = {}  # {user_id: {'sid': sid, 'role': role, 'rooms': []}}
        self.notification_queue = []
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
        self._register_events()
    
    def _register_events(self):
        """Register WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            user_id = request.args.get('user_id')
            role = request.args.get('role')
            
            if user_id and role:
                self.connected_users[user_id] = {
                    'sid': request.sid,
                    'role': role,
                    'rooms': [],
                    'connected_at': datetime.now().isoformat()
                }
                
                # Join role-specific room
                join_room(f"role_{role}")
                self.connected_users[user_id]['rooms'].append(f"role_{role}")
                
                # Join user-specific room
                join_room(f"user_{user_id}")
                self.connected_users[user_id]['rooms'].append(f"user_{user_id}")
                
                # Send connection confirmation
                emit('connected', {
                    'user_id': user_id,
                    'role': role,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Send pending notifications
                self._send_pending_notifications(user_id)
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            user_id = None
            for uid, data in self.connected_users.items():
                if data['sid'] == request.sid:
                    user_id = uid
                    break
            
            if user_id:
                del self.connected_users[user_id]
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            """Handle room joining"""
            room = data.get('room')
            user_id = data.get('user_id')
            
            if room and user_id and user_id in self.connected_users:
                join_room(room)
                self.connected_users[user_id]['rooms'].append(room)
                emit('room_joined', {'room': room})
        
        @self.socketio.on('leave_room')
        def handle_leave_room(data):
            """Handle room leaving"""
            room = data.get('room')
            user_id = data.get('user_id')
            
            if room and user_id and user_id in self.connected_users:
                leave_room(room)
                if room in self.connected_users[user_id]['rooms']:
                    self.connected_users[user_id]['rooms'].remove(room)
                emit('room_left', {'room': room})
        
        @self.socketio.on('send_message')
        def handle_send_message(data):
            """Handle real-time messaging"""
            message = data.get('message')
            room = data.get('room')
            user_id = data.get('user_id')
            
            if message and room and user_id:
                message_data = {
                    'message': message,
                    'user_id': user_id,
                    'timestamp': datetime.now().isoformat(),
                    'type': 'chat'
                }
                
                emit('new_message', message_data, room=room)
        
        @self.socketio.on('typing')
        def handle_typing(data):
            """Handle typing indicators"""
            room = data.get('room')
            user_id = data.get('user_id')
            is_typing = data.get('is_typing', False)
            
            if room and user_id:
                emit('user_typing', {
                    'user_id': user_id,
                    'is_typing': is_typing
                }, room=room, include_self=False)
    
    def send_notification(self, user_id: str, notification: Dict[str, Any]):
        """Send notification to specific user"""
        if user_id in self.connected_users:
            emit('notification', notification, room=f"user_{user_id}")
        else:
            # Queue notification for when user connects
            self.notification_queue.append({
                'user_id': user_id,
                'notification': notification,
                'timestamp': datetime.now().isoformat()
            })
    
    def send_notification_to_role(self, role: str, notification: Dict[str, Any]):
        """Send notification to all users with specific role"""
        emit('notification', notification, room=f"role_{role}")
    
    def send_notification_to_room(self, room: str, notification: Dict[str, Any]):
        """Send notification to specific room"""
        emit('notification', notification, room=room)
    
    def broadcast_notification(self, notification: Dict[str, Any]):
        """Broadcast notification to all connected users"""
        emit('notification', notification, broadcast=True)
    
    def send_real_time_update(self, update_type: str, data: Dict[str, Any], 
                            target: str = None, target_type: str = 'user'):
        """Send real-time updates"""
        update_data = {
            'type': update_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        if target:
            if target_type == 'user':
                self.send_notification(target, update_data)
            elif target_type == 'role':
                self.send_notification_to_role(target, update_data)
            elif target_type == 'room':
                self.send_notification_to_room(target, update_data)
        else:
            self.broadcast_notification(update_data)
    
    def send_project_update(self, project_id: str, update_type: str, project_data: Dict[str, Any]):
        """Send project-related updates"""
        update_data = {
            'type': 'project_update',
            'project_id': project_id,
            'update_type': update_type,
            'project_data': project_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to project room
        self.send_notification_to_room(f"project_{project_id}", update_data)
        
        # Send to managers
        self.send_notification_to_role('manager', update_data)
    
    def send_attendance_update(self, attendance_data: Dict[str, Any]):
        """Send attendance updates"""
        update_data = {
            'type': 'attendance_update',
            'data': attendance_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to managers
        self.send_notification_to_role('manager', update_data)
    
    def send_lead_update(self, lead_id: str, update_type: str, lead_data: Dict[str, Any]):
        """Send lead-related updates"""
        update_data = {
            'type': 'lead_update',
            'lead_id': lead_id,
            'update_type': update_type,
            'lead_data': lead_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to sales team
        self.send_notification_to_role('employee', update_data)
        self.send_notification_to_role('manager', update_data)
    
    def send_system_alert(self, alert_type: str, message: str, severity: str = 'info'):
        """Send system alerts"""
        alert_data = {
            'type': 'system_alert',
            'alert_type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to admins
        self.send_notification_to_role('admin', alert_data)
        
        # Send to managers for high severity alerts
        if severity in ['warning', 'error', 'critical']:
            self.send_notification_to_role('manager', alert_data)
    
    def send_analytics_update(self, analytics_data: Dict[str, Any]):
        """Send analytics updates"""
        update_data = {
            'type': 'analytics_update',
            'data': analytics_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to admins and managers
        self.send_notification_to_role('admin', update_data)
        self.send_notification_to_role('manager', update_data)
    
    def _send_pending_notifications(self, user_id: str):
        """Send pending notifications to newly connected user"""
        pending = [n for n in self.notification_queue if n['user_id'] == user_id]
        
        for notification in pending:
            self.send_notification(user_id, notification['notification'])
        
        # Remove sent notifications from queue
        self.notification_queue = [n for n in self.notification_queue if n['user_id'] != user_id]
    
    def get_connected_users(self) -> Dict[str, Any]:
        """Get information about connected users"""
        return {
            'total_connected': len(self.connected_users),
            'users_by_role': self._get_users_by_role(),
            'active_rooms': self._get_active_rooms()
        }
    
    def _get_users_by_role(self) -> Dict[str, int]:
        """Get count of connected users by role"""
        role_counts = {}
        for user_data in self.connected_users.values():
            role = user_data['role']
            role_counts[role] = role_counts.get(role, 0) + 1
        return role_counts
    
    def _get_active_rooms(self) -> List[str]:
        """Get list of active rooms"""
        rooms = set()
        for user_data in self.connected_users.values():
            rooms.update(user_data['rooms'])
        return list(rooms)
    
    def cleanup_old_notifications(self, max_age_hours: int = 24):
        """Clean up old notifications from queue"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        self.notification_queue = [
            n for n in self.notification_queue 
            if datetime.fromisoformat(n['timestamp']).timestamp() > cutoff_time
        ]
    
    def run_background_tasks(self):
        """Run background tasks for WebSocket management"""
        def cleanup_task():
            while True:
                time.sleep(3600)  # Run every hour
                self.cleanup_old_notifications()
        
        cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
        cleanup_thread.start()

# Initialize WebSocket manager
websocket_manager = WebSocketManager()

