import os
import uuid
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from werkzeug.utils import secure_filename
from flask import current_app, request
import mimetypes
import hashlib

class FileManager:
    def __init__(self, upload_folder: str = None):
        self.upload_folder = upload_folder or current_app.config.get('UPLOAD_FOLDER', 'uploads')
        self.allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', 
                                                        {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'})
        self.max_file_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16MB default
        
        # Ensure upload directory exists
        os.makedirs(self.upload_folder, exist_ok=True)
        
        # Create subdirectories for different file types
        self.subdirs = {
            'documents': os.path.join(self.upload_folder, 'documents'),
            'images': os.path.join(self.upload_folder, 'images'),
            'reports': os.path.join(self.upload_folder, 'reports'),
            'backups': os.path.join(self.upload_folder, 'backups'),
            'temp': os.path.join(self.upload_folder, 'temp')
        }
        
        for subdir in self.subdirs.values():
            os.makedirs(subdir, exist_ok=True)
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def get_file_category(self, filename: str) -> str:
        """Determine file category based on extension"""
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        image_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'webp'}
        document_extensions = {'pdf', 'doc', 'docx', 'txt', 'rtf'}
        spreadsheet_extensions = {'xls', 'xlsx', 'csv'}
        
        if ext in image_extensions:
            return 'images'
        elif ext in document_extensions:
            return 'documents'
        elif ext in spreadsheet_extensions:
            return 'documents'
        else:
            return 'documents'
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate unique filename to prevent conflicts"""
        name, ext = os.path.splitext(original_filename)
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{name}_{timestamp}_{unique_id}{ext}"
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def upload_file(self, file, category: str = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Upload a file and return file information"""
        if file is None:
            raise ValueError("No file provided")
        
        if not self.allowed_file(file.filename):
            raise ValueError(f"File type not allowed. Allowed types: {', '.join(self.allowed_extensions)}")
        
        if file.content_length and file.content_length > self.max_file_size:
            raise ValueError(f"File too large. Maximum size: {self.max_file_size / (1024*1024)}MB")
        
        # Generate secure filename
        original_filename = secure_filename(file.filename)
        unique_filename = self.generate_unique_filename(original_filename)
        
        # Determine category
        if category is None:
            category = self.get_file_category(original_filename)
        
        # Create file path
        file_path = os.path.join(self.subdirs[category], unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Calculate file hash
        file_hash = self.calculate_file_hash(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Create file record
        file_record = {
            'id': str(uuid.uuid4()),
            'original_filename': original_filename,
            'filename': unique_filename,
            'file_path': file_path,
            'file_hash': file_hash,
            'file_size': file_size,
            'mime_type': mime_type,
            'category': category,
            'uploaded_at': datetime.now().isoformat(),
            'uploaded_by': request.form.get('user_id') if request.form else None,
            'metadata': metadata or {}
        }
        
        return file_record
    
    def upload_multiple_files(self, files: List, category: str = None, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Upload multiple files"""
        uploaded_files = []
        
        for file in files:
            try:
                file_record = self.upload_file(file, category, metadata)
                uploaded_files.append(file_record)
            except Exception as e:
                current_app.logger.error(f"Failed to upload file {file.filename}: {str(e)}")
                uploaded_files.append({
                    'error': str(e),
                    'original_filename': file.filename
                })
        
        return uploaded_files
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get information about a file"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        return {
            'file_path': file_path,
            'file_size': stat.st_size,
            'mime_type': mime_type,
            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'file_hash': self.calculate_file_hash(file_path)
        }
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Failed to delete file {file_path}: {str(e)}")
            return False
    
    def move_file(self, source_path: str, destination_path: str) -> bool:
        """Move a file to a new location"""
        try:
            if os.path.exists(source_path):
                shutil.move(source_path, destination_path)
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Failed to move file {source_path}: {str(e)}")
            return False
    
    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """Copy a file to a new location"""
        try:
            if os.path.exists(source_path):
                shutil.copy2(source_path, destination_path)
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Failed to copy file {source_path}: {str(e)}")
            return False
    
    def get_directory_size(self, directory: str) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except Exception as e:
            current_app.logger.error(f"Failed to calculate directory size: {str(e)}")
        
        return total_size
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """Clean up temporary files older than specified hours"""
        temp_dir = self.subdirs['temp']
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        deleted_count = 0
        
        try:
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    file_time = os.path.getmtime(file_path)
                    if file_time < cutoff_time:
                        if self.delete_file(file_path):
                            deleted_count += 1
        except Exception as e:
            current_app.logger.error(f"Failed to cleanup temp files: {str(e)}")
        
        return deleted_count
    
    def create_backup(self, source_path: str, backup_name: str = None) -> Optional[str]:
        """Create a backup of a file"""
        try:
            if not os.path.exists(source_path):
                return None
            
            if backup_name is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"backup_{timestamp}_{os.path.basename(source_path)}"
            
            backup_path = os.path.join(self.subdirs['backups'], backup_name)
            shutil.copy2(source_path, backup_path)
            
            return backup_path
        except Exception as e:
            current_app.logger.error(f"Failed to create backup: {str(e)}")
            return None
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        stats = {
            'total_size': 0,
            'file_count': 0,
            'category_stats': {}
        }
        
        for category, directory in self.subdirs.items():
            if os.path.exists(directory):
                category_size = self.get_directory_size(directory)
                category_files = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
                
                stats['total_size'] += category_size
                stats['file_count'] += category_files
                stats['category_stats'][category] = {
                    'size': category_size,
                    'file_count': category_files
                }
        
        return stats

# Initialize file manager lazily to avoid app context issues
file_manager = None

def get_file_manager():
    global file_manager
    if file_manager is None:
        file_manager = FileManager()
    return file_manager
