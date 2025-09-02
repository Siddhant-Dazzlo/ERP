# Firebase Configuration for Trivanta Edge ERP
# Complete Firebase integration with Firestore and Storage

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, storage
from firebase_admin import auth as firebase_auth
from google.cloud.firestore import Client as FirestoreClient
from google.cloud.storage import Client as StorageClient
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirebaseConfig:
    """Firebase configuration and connection management"""
    
    def __init__(self):
        self.config = {
            "apiKey": "AIzaSyBwceYbtCryrZcTYvK38GtUNjEnvTVfqXQ",
            "authDomain": "trivanta-erp.firebaseapp.com",
            "projectId": "trivanta-erp",
            "storageBucket": "trivanta-erp.firebasestorage.app",
            "messagingSenderId": "1086746404611",
            "appId": "1:1086746404611:web:f1b58ca02ab6496cc46b36",
            "measurementId": "G-7NG8G150T9"
        }
        self.initialized = False
        self.db = None
        self.storage_client = None
        self.bucket = None
        
    def initialize(self):
        """Initialize Firebase connection"""
        try:
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                logger.info("Firebase already initialized")
                self.initialized = True
                return True
            
            # Try to get service account credentials
            cred = None
            
            # Method 1: Try environment variable
            if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                try:
                    cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
                    logger.info("Using service account from environment variable")
                except Exception as e:
                    logger.warning(f"Failed to load service account from environment: {e}")
            
            # Method 2: Try default credentials
            if not cred:
                try:
                    cred = credentials.ApplicationDefault()
                    logger.info("Using application default credentials")
                except Exception as e:
                    logger.warning(f"Failed to load application default credentials: {e}")
            
            # Method 3: Try to find service account in common locations
            if not cred:
                service_account_paths = [
                    'service-account-key.json',
                    'firebase-service-account.json',
                    'trivanta-erp-firebase-adminsdk.json',
                    os.path.expanduser('~/.config/firebase/service-account.json')
                ]
                
                for path in service_account_paths:
                    if os.path.exists(path):
                        try:
                            cred = credentials.Certificate(path)
                            logger.info(f"Using service account from: {path}")
                            break
                        except Exception as e:
                            logger.warning(f"Failed to load service account from {path}: {e}")
            
            # If no credentials found, use anonymous auth (limited functionality)
            if not cred:
                logger.warning("No service account credentials found, using limited Firebase functionality")
                # Try to initialize with project ID only
                try:
                    firebase_admin.initialize_app({
                        'projectId': self.config['projectId'],
                        'storageBucket': self.config['storageBucket']
                    })
                    logger.info("Firebase initialized with limited functionality")
                except Exception as e:
                    logger.error(f"Failed to initialize Firebase even with limited functionality: {e}")
                    return False
            else:
                # Initialize with full credentials
                firebase_admin.initialize_app(cred, {
                    'storageBucket': self.config['storageBucket']
                })
                logger.info("Firebase initialized with full credentials")
            
            # Initialize Firestore
            try:
                self.db = firestore.client()
                logger.info("Firestore client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Firestore: {e}")
                self.db = None
            
            # Initialize Storage
            try:
                self.storage_client = StorageClient()
                self.bucket = self.storage_client.bucket(self.config['storageBucket'])
                logger.info("Storage client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Storage: {e}")
                self.storage_client = None
                self.bucket = None
            
            self.initialized = True
            logger.info("Firebase initialization completed")
            return True
            
        except Exception as e:
            logger.error(f"Firebase initialization failed: {e}")
            self.initialized = False
            return False
    
    def is_ready(self) -> bool:
        """Check if Firebase is ready for use"""
        return self.initialized and self.db is not None
    
    def get_config(self) -> Dict[str, Any]:
        """Get Firebase configuration"""
        return self.config.copy()
    
    def get_firestore_client(self) -> FirestoreClient:
        """Get Firestore client"""
        if not self.is_ready():
            self.initialize()
        return self.db
    
    def get_storage_client(self) -> StorageClient:
        """Get Storage client"""
        if not self.is_ready():
            self.initialize()
        return self.storage_client
    
    def get_storage_bucket(self):
        """Get Storage bucket"""
        if not self.is_ready():
            self.initialize()
        return self.bucket

class FirebaseDataManager:
    """Firebase data management operations"""
    
    def __init__(self, firebase_config: FirebaseConfig):
        self.config = firebase_config
        self.db = None
        self.bucket = None
        
    def initialize(self):
        """Initialize Firebase data manager"""
        if not self.config.is_ready():
            self.config.initialize()
        self.db = self.config.get_firestore_client()
        self.bucket = self.config.get_storage_bucket()
        
    def create_collection(self, collection_name: str, data: Dict[str, Any]) -> str:
        """Create a new document in a collection"""
        if not self.db:
            self.initialize()
        
        try:
            doc_ref = self.db.collection(collection_name).add(data)
            logger.info(f"Document created in {collection_name} with ID: {doc_ref[1].id}")
            return doc_ref[1].id
        except Exception as e:
            logger.error(f"Error creating document in {collection_name}: {e}")
            raise
    
    def get_document(self, collection_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        if not self.db:
            self.initialize()
        
        try:
            doc = self.db.collection(collection_name).document(doc_id).get()
            if doc.exists:
                return {'id': doc.id, **doc.to_dict()}
            return None
        except Exception as e:
            logger.error(f"Error getting document {doc_id} from {collection_name}: {e}")
            return None
    
    def get_collection(self, collection_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get all documents from a collection with optional filters"""
        if not self.db:
            self.initialize()
        
        try:
            query = self.db.collection(collection_name)
            
            # Apply filters if provided
            if filters:
                for field, value in filters.items():
                    if isinstance(value, dict):
                        for op, op_value in value.items():
                            if op == '==':
                                query = query.where(field, '==', op_value)
                            elif op == '>':
                                query = query.where(field, '>', op_value)
                            elif op == '<':
                                query = query.where(field, '<', op_value)
                            elif op == '>=':
                                query = query.where(field, '>=', op_value)
                            elif op == '<=':
                                query = query.where(field, '<=', op_value)
                            elif op == 'in':
                                query = query.where(field, 'in', op_value)
                    else:
                        query = query.where(field, '==', value)
            
            docs = query.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
            
        except Exception as e:
            logger.error(f"Error getting collection {collection_name}: {e}")
            return []
    
    def update_document(self, collection_name: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Update a document"""
        if not self.db:
            self.initialize()
        
        try:
            self.db.collection(collection_name).document(doc_id).update(data)
            logger.info(f"Document {doc_id} updated in {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error updating document {doc_id} in {collection_name}: {e}")
            return False
    
    def delete_document(self, collection_name: str, doc_id: str) -> bool:
        """Delete a document"""
        if not self.db:
            self.initialize()
        
        try:
            self.db.collection(collection_name).document(doc_id).delete()
            logger.info(f"Document {doc_id} deleted from {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id} from {collection_name}: {e}")
            return False
    
    def upload_file(self, file_path: str, destination_blob_name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Upload a file to Firebase Storage"""
        if not self.bucket:
            self.initialize()
        
        try:
            blob = self.bucket.blob(destination_blob_name)
            
            # Set metadata if provided
            if metadata:
                blob.metadata = metadata
            
            blob.upload_from_filename(file_path)
            logger.info(f"File uploaded to {destination_blob_name}")
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Error uploading file {file_path}: {e}")
            raise
    
    def download_file(self, source_blob_name: str, destination_file_name: str) -> bool:
        """Download a file from Firebase Storage"""
        if not self.bucket:
            self.initialize()
        
        try:
            blob = self.bucket.blob(source_blob_name)
            blob.download_to_filename(destination_file_name)
            logger.info(f"File downloaded from {source_blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading file {source_blob_name}: {e}")
            return False
    
    def delete_file(self, blob_name: str) -> bool:
        """Delete a file from Firebase Storage"""
        if not self.bucket:
            self.initialize()
        
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            logger.info(f"File {blob_name} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {blob_name}: {e}")
            return False
    
    def migrate_from_local(self, local_data: Dict[str, Any]) -> bool:
        """Migrate data from local storage to Firebase"""
        if not self.db:
            self.initialize()
        
        try:
            for collection_name, documents in local_data.items():
                if collection_name in ['users', 'clients', 'projects', 'employees', 'attendance', 'leads', 'tasks']:
                    for doc in documents:
                        # Remove the id field as Firebase will generate it
                        doc_data = {k: v for k, v in doc.items() if k != 'id'}
                        self.create_collection(collection_name, doc_data)
            
            logger.info("Data migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Data migration failed: {e}")
            return False

# Global Firebase instances
firebase_config = FirebaseConfig()
firebase_data_manager = FirebaseDataManager(firebase_config)

def get_firebase_config() -> FirebaseConfig:
    """Get global Firebase configuration instance"""
    return firebase_config

def get_firebase_data_manager() -> FirebaseDataManager:
    """Get global Firebase data manager instance"""
    return firebase_data_manager

