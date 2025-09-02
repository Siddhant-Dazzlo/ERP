# Firebase Storage Service for Trivanta Edge ERP
# Handles file uploads, downloads, and storage management

import os
import mimetypes
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, BinaryIO
import logging
from google.cloud import storage
from google.cloud.storage import Blob
from utils.firebase_config import get_firebase_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirebaseStorageService:
    """Firebase Storage service for file management"""
    
    def __init__(self):
        self.config = get_firebase_config()
        self.storage_client = None
        self.bucket = None
        self.initialized = False
        
    def initialize(self):
        """Initialize Firebase Storage service"""
        try:
            if not self.config.is_ready():
                self.config.initialize()
            
            self.storage_client = self.config.get_storage_client()
            self.bucket = self.config.get_storage_bucket()
            self.initialized = True
            
            logger.info("Firebase Storage service initialized successfully")
            
        except Exception as e:
            logger.error(f"Firebase Storage initialization failed: {e}")
            self.initialized = False
    
    def is_ready(self) -> bool:
        """Check if Firebase Storage is ready"""
        return self.initialized and self.storage_client is not None and self.bucket is not None
    
    def upload_file(self, file_path: str, destination_blob_name: str, 
                   metadata: Optional[Dict[str, Any]] = None, 
                   content_type: Optional[str] = None) -> Optional[str]:
        """Upload a file to Firebase Storage"""
        if not self.is_ready():
            self.initialize()
        
        try:
            # Create blob
            blob = self.bucket.blob(destination_blob_name)
            
            # Set metadata
            if metadata:
                blob.metadata = metadata
            
            # Set content type
            if content_type:
                blob.content_type = content_type
            else:
                # Auto-detect content type
                content_type, _ = mimetypes.guess_type(file_path)
                if content_type:
                    blob.content_type = content_type
            
            # Upload file
            blob.upload_from_filename(file_path)
            
            # Make blob publicly readable
            blob.make_public()
            
            logger.info(f"File uploaded successfully: {destination_blob_name}")
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Error uploading file {file_path}: {e}")
            return None
    
    def upload_file_object(self, file_object: BinaryIO, destination_blob_name: str,
                          metadata: Optional[Dict[str, Any]] = None,
                          content_type: Optional[str] = None) -> Optional[str]:
        """Upload a file object to Firebase Storage"""
        if not self.is_ready():
            self.initialize()
        
        try:
            # Create blob
            blob = self.bucket.blob(destination_blob_name)
            
            # Set metadata
            if metadata:
                blob.metadata = metadata
            
            # Set content type
            if content_type:
                blob.content_type = content_type
            
            # Upload file object
            blob.upload_from_file(file_object)
            
            # Make blob publicly readable
            blob.make_public()
            
            logger.info(f"File object uploaded successfully: {destination_blob_name}")
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Error uploading file object {destination_blob_name}: {e}")
            return None
    
    def download_file(self, source_blob_name: str, destination_file_name: str) -> bool:
        """Download a file from Firebase Storage"""
        if not self.is_ready():
            self.initialize()
        
        try:
            blob = self.bucket.blob(source_blob_name)
            blob.download_to_filename(destination_file_name)
            
            logger.info(f"File downloaded successfully: {source_blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading file {source_blob_name}: {e}")
            return False
    
    def get_file_url(self, blob_name: str, expires_in: int = 3600) -> Optional[str]:
        """Get signed URL for file access"""
        if not self.is_ready():
            self.initialize()
        
        try:
            blob = self.bucket.blob(blob_name)
            
            # Generate signed URL
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.utcnow() + timedelta(seconds=expires_in),
                method="GET"
            )
            
            logger.info(f"Signed URL generated for: {blob_name}")
            return url
            
        except Exception as e:
            logger.error(f"Error generating signed URL for {blob_name}: {e}")
            return None
    
    def delete_file(self, blob_name: str) -> bool:
        """Delete a file from Firebase Storage"""
        if not self.is_ready():
            self.initialize()
        
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            
            logger.info(f"File deleted successfully: {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {blob_name}: {e}")
            return False
    
    def list_files(self, prefix: str = "", delimiter: str = "/") -> List[Dict[str, Any]]:
        """List files in Firebase Storage"""
        if not self.is_ready():
            self.initialize()
        
        try:
            blobs = self.bucket.list_blobs(prefix=prefix, delimiter=delimiter)
            
            files = []
            for blob in blobs:
                file_info = {
                    'name': blob.name,
                    'size': blob.size,
                    'content_type': blob.content_type,
                    'created': blob.time_created,
                    'updated': blob.updated,
                    'metadata': blob.metadata or {},
                    'public_url': blob.public_url
                }
                files.append(file_info)
            
            logger.info(f"Listed {len(files)} files from Firebase Storage")
            return files
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def get_file_metadata(self, blob_name: str) -> Optional[Dict[str, Any]]:
        """Get file metadata"""
        if not self.is_ready():
            self.initialize()
        
        try:
            blob = self.bucket.blob(blob_name)
            blob.reload()  # Refresh metadata
            
            metadata = {
                'name': blob.name,
                'size': blob.size,
                'content_type': blob.content_type,
                'created': blob.time_created,
                'updated': blob.updated,
                'metadata': blob.metadata or {},
                'public_url': blob.public_url,
                'bucket': blob.bucket.name
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting file metadata for {blob_name}: {e}")
            return None
    
    def update_file_metadata(self, blob_name: str, metadata: Dict[str, Any]) -> bool:
        """Update file metadata"""
        if not self.is_ready():
            self.initialize()
        
        try:
            blob = self.bucket.blob(blob_name)
            blob.metadata = metadata
            blob.patch()
            
            logger.info(f"File metadata updated for: {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating file metadata for {blob_name}: {e}")
            return False
    
    def copy_file(self, source_blob_name: str, destination_blob_name: str) -> bool:
        """Copy a file within Firebase Storage"""
        if not self.is_ready():
            self.initialize()
        
        try:
            source_blob = self.bucket.blob(source_blob_name)
            destination_blob = self.bucket.blob(destination_blob_name)
            
            # Copy the blob
            self.bucket.copy_blob(source_blob, self.bucket, destination_blob_name)
            
            logger.info(f"File copied from {source_blob_name} to {destination_blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error copying file from {source_blob_name} to {destination_blob_name}: {e}")
            return False
    
    def move_file(self, source_blob_name: str, destination_blob_name: str) -> bool:
        """Move a file within Firebase Storage"""
        if not self.is_ready():
            self.initialize()
        
        try:
            # Copy the file
            if self.copy_file(source_blob_name, destination_blob_name):
                # Delete the original
                if self.delete_file(source_blob_name):
                    logger.info(f"File moved from {source_blob_name} to {destination_blob_name}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error moving file from {source_blob_name} to {destination_blob_name}: {e}")
            return False
    
    def create_folder(self, folder_name: str) -> bool:
        """Create a folder in Firebase Storage (by creating an empty blob)"""
        if not self.is_ready():
            self.initialize()
        
        try:
            # Ensure folder name ends with /
            if not folder_name.endswith('/'):
                folder_name += '/'
            
            # Create an empty blob to represent the folder
            blob = self.bucket.blob(folder_name)
            blob.upload_from_string('', content_type='application/x-directory')
            
            logger.info(f"Folder created: {folder_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating folder {folder_name}: {e}")
            return False
    
    def delete_folder(self, folder_name: str) -> bool:
        """Delete a folder and all its contents"""
        if not self.is_ready():
            self.initialize()
        
        try:
            # Ensure folder name ends with /
            if not folder_name.endswith('/'):
                folder_name += '/'
            
            # List all blobs in the folder
            blobs = self.bucket.list_blobs(prefix=folder_name)
            
            # Delete all blobs in the folder
            for blob in blobs:
                blob.delete()
            
            logger.info(f"Folder deleted: {folder_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting folder {folder_name}: {e}")
            return False
    
    def get_storage_usage(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        if not self.is_ready():
            self.initialize()
        
        try:
            blobs = list(self.bucket.list_blobs())
            
            total_size = sum(blob.size for blob in blobs)
            total_files = len(blobs)
            
            # Group by content type
            content_types = {}
            for blob in blobs:
                content_type = blob.content_type or 'unknown'
                if content_type not in content_types:
                    content_types[content_type] = {'count': 0, 'size': 0}
                content_types[content_type]['count'] += 1
                content_types[content_type]['size'] += blob.size
            
            usage_stats = {
                'total_size': total_size,
                'total_files': total_files,
                'content_types': content_types,
                'bucket_name': self.bucket.name
            }
            
            logger.info(f"Storage usage stats retrieved: {total_files} files, {total_size} bytes")
            return usage_stats
            
        except Exception as e:
            logger.error(f"Error getting storage usage: {e}")
            return {}
    
    def cleanup_old_files(self, days_old: int = 30) -> int:
        """Clean up files older than specified days"""
        if not self.is_ready():
            self.initialize()
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            blobs = self.bucket.list_blobs()
            
            deleted_count = 0
            for blob in blobs:
                if blob.time_created and blob.time_created < cutoff_date:
                    blob.delete()
                    deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")
            return 0

# Global Firebase Storage service instance
firebase_storage_service = FirebaseStorageService()

def get_firebase_storage_service() -> FirebaseStorageService:
    """Get global Firebase Storage service instance"""
    return firebase_storage_service
