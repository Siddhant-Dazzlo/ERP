// Firebase Utilities for Trivanta Edge ERP
// Client-side Firebase operations and data synchronization

class FirebaseUtils {
    constructor() {
        this.initialized = false;
        this.db = null;
        this.storage = null;
        this.firestore = null;
        this.analytics = null;
        
        // Initialize Firebase connection
        this.initializeFirebase();
        
        // Initialize real-time listeners
        this.listeners = new Map();
        this.initializeRealTimeSync();
    }

    // Initialize Firebase connection
    initializeFirebase() {
        try {
            if (window.firebase && window.firebase.db && window.firebase.firestore) {
                this.db = window.firebase.db;
                this.storage = window.firebase.storage;
                this.firestore = window.firebase.firestore;
                this.analytics = window.firebase.analytics;
                this.initialized = true;
                console.log('✅ Firebase initialized successfully');
            } else {
                console.error('❌ Firebase not available');
                this.initialized = false;
            }
        } catch (error) {
            console.error('❌ Firebase initialization failed:', error);
            this.initialized = false;
        }
    }

    // Initialize real-time synchronization
    initializeRealTimeSync() {
        if (!this.initialized) {
            console.warning('⚠️ Firebase not initialized, skipping real-time sync');
            return;
        }
        
        console.log('🔄 Initializing Firebase real-time sync...');
        
        // Set up real-time listeners for all collections
        const collections = ['users', 'clients', 'projects', 'employees', 'attendance', 'leads', 'tasks'];
        
        collections.forEach(collection => {
            this.setupCollectionListener(collection);
        });
    }

    // Set up real-time listener for a collection
    setupCollectionListener(collectionName) {
        if (!this.initialized) {
            console.warning(`⚠️ Firebase not initialized, skipping listener for ${collectionName}`);
            return;
        }
        
        try {
            const q = this.firestore.query(
                this.firestore.collection(this.db, collectionName),
                this.firestore.orderBy(this.db, 'created_at', 'desc')
            );

            const unsubscribe = this.firestore.onSnapshot(q, (snapshot) => {
                const changes = snapshot.docChanges();
                
                changes.forEach((change) => {
                    const docData = { id: change.doc.id, ...change.doc.data() };
                    
                    if (change.type === 'added') {
                        this.handleDocumentAdded(collectionName, docData);
                    } else if (change.type === 'modified') {
                        this.handleDocumentModified(collectionName, docData);
                    } else if (change.type === 'removed') {
                        this.handleDocumentRemoved(collectionName, docData.id);
                    }
                });
                
                // Update UI with real-time data
                this.updateUIWithRealTimeData(collectionName, snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() })));
                
            }, (error) => {
                console.error(`❌ Error listening to ${collectionName}:`, error);
                // Try to reinitialize Firebase on error
                setTimeout(() => this.initializeFirebase(), 5000);
            });

            this.listeners.set(collectionName, unsubscribe);
            console.log(`✅ Listener set up for ${collectionName}`);
            
        } catch (error) {
            console.error(`❌ Error setting up listener for ${collectionName}:`, error);
        }
    }

    // Handle document added
    handleDocumentAdded(collectionName, docData) {
        console.log(`📄 Document added to ${collectionName}:`, docData);
        
        // Trigger custom event for UI updates
        const event = new CustomEvent('firebase-document-added', {
            detail: { collection: collectionName, data: docData }
        });
        document.dispatchEvent(event);
    }

    // Handle document modified
    handleDocumentModified(collectionName, docData) {
        console.log(`✏️ Document modified in ${collectionName}:`, docData);
        
        // Trigger custom event for UI updates
        const event = new CustomEvent('firebase-document-modified', {
            detail: { collection: collectionName, data: docData }
        });
        document.dispatchEvent(event);
    }

    // Handle document removed
    handleDocumentRemoved(collectionName, docId) {
        console.log(`🗑️ Document removed from ${collectionName}:`, docId);
        
        // Trigger custom event for UI updates
        const event = new CustomEvent('firebase-document-removed', {
            detail: { collection: collectionName, id: docId }
        });
        document.dispatchEvent(event);
    }

    // Update UI with real-time data
    updateUIWithRealTimeData(collectionName, documents) {
        try {
            // Update dashboard metrics if on dashboard page
            if (window.location.pathname.includes('/dashboard')) {
                this.updateDashboardMetrics(collectionName, documents);
            }
            
            // Update data tables if they exist
            this.updateDataTables(collectionName, documents);
            
            // Update charts if they exist
            this.updateCharts(collectionName, documents);
        } catch (error) {
            console.error(`❌ Error updating UI for ${collectionName}:`, error);
        }
    }

    // Update dashboard metrics
    updateDashboardMetrics(collectionName, documents) {
        const metrics = {
            'projects': 'total_projects',
            'clients': 'total_clients',
            'employees': 'total_employees',
            'leads': 'total_leads'
        };

        if (metrics[collectionName]) {
            const metricElement = document.getElementById(metrics[collectionName]);
            if (metricElement) {
                metricElement.textContent = documents.length;
            }
        }
    }

    // Update data tables
    updateDataTables(collectionName, documents) {
        const tableId = `${collectionName}-table`;
        const table = document.getElementById(tableId);
        
        if (table) {
            this.refreshTableData(table, documents);
        }
    }

    // Update charts
    updateCharts(collectionName, documents) {
        try {
            // Update project progress chart
            if (collectionName === 'projects' && window.projectProgressChart) {
                this.updateProjectProgressChart(documents);
            }
            
            // Update team performance chart
            if (collectionName === 'employees' && window.teamPerformanceChart) {
                this.updateTeamPerformanceChart(documents);
            }
        } catch (error) {
            console.error(`❌ Error updating charts for ${collectionName}:`, error);
        }
    }

    // Refresh table data
    refreshTableData(table, documents) {
        try {
            const tbody = table.querySelector('tbody');
            if (!tbody) return;

            tbody.innerHTML = '';
            
            documents.forEach(doc => {
                const row = this.createTableRow(doc);
                tbody.appendChild(row);
            });
        } catch (error) {
            console.error('❌ Error refreshing table data:', error);
        }
    }

    // Create table row
    createTableRow(doc) {
        try {
            const row = document.createElement('tr');
            row.setAttribute('data-id', doc.id);
            
            // Add data attributes for easy access
            Object.keys(doc).forEach(key => {
                row.setAttribute(`data-${key}`, doc[key]);
            });
            
            // Generate row content based on document type
            const cells = this.generateTableCells(doc);
            cells.forEach(cell => row.appendChild(cell));
            
            return row;
        } catch (error) {
            console.error('❌ Error creating table row:', error);
            return document.createElement('tr');
        }
    }

    // Generate table cells based on document type
    generateTableCells(doc) {
        const cells = [];
        
        try {
            // Common fields
            if (doc.name) {
                const nameCell = document.createElement('td');
                nameCell.textContent = doc.name;
                cells.push(nameCell);
            }
            
            if (doc.email) {
                const emailCell = document.createElement('td');
                emailCell.textContent = doc.email;
                cells.push(emailCell);
            }
            
            if (doc.status) {
                const statusCell = document.createElement('td');
                const badge = document.createElement('span');
                badge.className = `badge bg-${this.getStatusColor(doc.status)}`;
                badge.textContent = doc.status;
                statusCell.appendChild(badge);
                cells.push(statusCell);
            }
            
            if (doc.created_at) {
                const dateCell = document.createElement('td');
                dateCell.textContent = new Date(doc.created_at).toLocaleDateString();
                cells.push(dateCell);
            }
            
            // Action buttons
            const actionCell = document.createElement('td');
            actionCell.innerHTML = this.generateActionButtons(doc);
            cells.push(actionCell);
            
        } catch (error) {
            console.error('❌ Error generating table cells:', error);
        }
        
        return cells;
    }

    // Get status color for badges
    getStatusColor(status) {
        const colors = {
            'active': 'success',
            'pending': 'warning',
            'completed': 'success',
            'in_progress': 'info',
            'cancelled': 'danger',
            'new': 'primary',
            'contacted': 'info',
            'qualified': 'success',
            'lost': 'danger'
        };
        return colors[status] || 'secondary';
    }

    // Generate action buttons
    generateActionButtons(doc) {
        return `
            <button class="btn btn-sm btn-outline-primary me-1" onclick="editDocument('${doc.id}')">
                <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteDocument('${doc.id}')">
                <i class="bi bi-trash"></i>
            </button>
        `;
    }

    // Update project progress chart
    updateProjectProgressChart(projects) {
        try {
            if (!window.projectProgressChart) return;
            
            const completedProjects = projects.filter(p => p.status === 'completed').length;
            const activeProjects = projects.filter(p => p.status === 'in_progress').length;
            const pendingProjects = projects.filter(p => p.status === 'pending').length;
            
            window.projectProgressChart.data.datasets[0].data = [completedProjects, activeProjects, pendingProjects];
            window.projectProgressChart.update();
        } catch (error) {
            console.error('❌ Error updating project progress chart:', error);
        }
    }

    // Update team performance chart
    updateTeamPerformanceChart(employees) {
        try {
            if (!window.teamPerformanceChart) return;
            
            const totalEmployees = employees.length;
            const excellent = Math.floor(totalEmployees * 0.3);
            const good = Math.floor(totalEmployees * 0.5);
            const average = Math.floor(totalEmployees * 0.15);
            const needsImprovement = Math.max(0, totalEmployees - excellent - good - average);
            
            window.teamPerformanceChart.data.datasets[0].data = [excellent, good, average, needsImprovement];
            window.teamPerformanceChart.update();
        } catch (error) {
            console.error('❌ Error updating team performance chart:', error);
        }
    }

    // CRUD Operations
    async createDocument(collectionName, data) {
        if (!this.initialized) {
            throw new Error('Firebase not initialized');
        }
        
        try {
            const docRef = await this.firestore.addDoc(
                this.firestore.collection(this.db, collectionName),
                {
                    ...data,
                    created_at: new Date().toISOString(),
                    updated_at: new Date().toISOString()
                }
            );
            
            console.log(`✅ Document created with ID: ${docRef.id}`);
            return docRef.id;
            
        } catch (error) {
            console.error('❌ Error creating document:', error);
            throw error;
        }
    }

    async updateDocument(collectionName, docId, data) {
        if (!this.initialized) {
            throw new Error('Firebase not initialized');
        }
        
        try {
            const docRef = this.firestore.doc(this.db, collectionName, docId);
            await this.firestore.updateDoc(docRef, {
                ...data,
                updated_at: new Date().toISOString()
            });
            
            console.log(`✅ Document updated: ${docId}`);
            return true;
            
        } catch (error) {
            console.error('❌ Error updating document:', error);
            throw error;
        }
    }

    async deleteDocument(collectionName, docId) {
        if (!this.initialized) {
            throw new Error('Firebase not initialized');
        }
        
        try {
            const docRef = this.firestore.doc(this.db, collectionName, docId);
            await this.firestore.deleteDoc(docRef);
            
            console.log(`✅ Document deleted: ${docId}`);
            return true;
            
        } catch (error) {
            console.error('❌ Error deleting document:', error);
            throw error;
        }
    }

    async getDocuments(collectionName, filters = null) {
        if (!this.initialized) {
            throw new Error('Firebase not initialized');
        }
        
        try {
            let q = this.firestore.collection(this.db, collectionName);
            
            if (filters) {
                Object.keys(filters).forEach(key => {
                    q = this.firestore.query(q, this.firestore.where(this.db, key, '==', filters[key]));
                });
            }
            
            const querySnapshot = await this.firestore.getDocs(q);
            return querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
            
        } catch (error) {
            console.error('❌ Error getting documents:', error);
            throw error;
        }
    }

    // File upload to Firebase Storage
    async uploadFile(file, destinationPath, metadata = {}) {
        if (!this.initialized) {
            throw new Error('Firebase not initialized');
        }
        
        try {
            const storageRef = this.storage.ref(this.storage, destinationPath);
            const snapshot = await this.storage.uploadBytes(storageRef, file, metadata);
            const downloadURL = await this.storage.getDownloadURL(snapshot.ref);
            
            console.log('✅ File uploaded successfully:', downloadURL);
            return downloadURL;
            
        } catch (error) {
            console.error('❌ Error uploading file:', error);
            throw error;
        }
    }

    // Check Firebase status
    isReady() {
        return this.initialized && this.db && this.firestore;
    }

    // Reinitialize Firebase
    async reinitialize() {
        console.log('🔄 Reinitializing Firebase...');
        this.cleanup();
        this.initializeFirebase();
        
        if (this.initialized) {
            this.initializeRealTimeSync();
        }
    }

    // Cleanup listeners
    cleanup() {
        try {
            this.listeners.forEach((unsubscribe, collectionName) => {
                unsubscribe();
                console.log(`🧹 Listener for ${collectionName} cleaned up`);
            });
            this.listeners.clear();
        } catch (error) {
            console.error('❌ Error during cleanup:', error);
        }
    }
}

// Initialize Firebase utilities when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        if (window.firebase) {
            window.firebaseUtils = new FirebaseUtils();
            console.log('✅ Firebase utilities initialized');
        } else {
            console.error('❌ Firebase not available');
        }
    } catch (error) {
        console.error('❌ Error initializing Firebase utilities:', error);
    }
});

// Global functions for table actions
window.editDocument = function(docId) {
    try {
        console.log('✏️ Edit document:', docId);
        // Implement edit functionality
        // You can add your edit logic here
    } catch (error) {
        console.error('❌ Error editing document:', error);
    }
};

window.deleteDocument = function(docId) {
    try {
        if (confirm('Are you sure you want to delete this item?')) {
            console.log('🗑️ Delete document:', docId);
            // Implement delete functionality
            // You can add your delete logic here
        }
    } catch (error) {
        console.error('❌ Error deleting document:', error);
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FirebaseUtils;
}
