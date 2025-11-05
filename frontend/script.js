// Furniture Detection System - Frontend JavaScript

class FurnitureDetectionApp {
    constructor() {
        this.apiBaseUrl = window.location.origin;
        this.initializeElements();
        this.setupEventListeners();
        this.setupDragAndDrop();
    }

    initializeElements() {
        // Get DOM elements
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.resultsSection = document.getElementById('resultsSection');
        this.loadingSection = document.getElementById('loadingSection');
        this.errorSection = document.getElementById('errorSection');
        this.originalImage = document.getElementById('originalImage');
        this.resultImage = document.getElementById('resultImage');
        this.imageInfo = document.getElementById('imageInfo');
        this.processingTime = document.getElementById('processingTime');
        this.summaryContent = document.getElementById('summaryContent');
        this.errorMessage = document.getElementById('errorMessage');
    }

    setupEventListeners() {
        // File input change event
        this.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });

        // Upload area click event
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });
    }

    setupDragAndDrop() {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, () => {
                this.uploadArea.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, () => {
                this.uploadArea.classList.remove('dragover');
            }, false);
        });

        // Handle dropped files
        this.uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        }, false);
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    async handleFileUpload(file) {
        // Validate file type
        if (!this.isValidImageFile(file)) {
            this.showError('Please upload a valid image file (JPG, JPEG, PNG)');
            return;
        }

        // Validate file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            this.showError('File size too large. Please upload an image smaller than 10MB');
            return;
        }

        try {
            // Show loading state
            this.showLoading();

            // Display original image
            this.displayOriginalImage(file);

            // Upload and process image
            const startTime = Date.now();
            const result = await this.uploadImage(file);
            const processingTime = Date.now() - startTime;

            // Display results
            this.displayResults(result, processingTime);

        } catch (error) {
            console.error('Upload error:', error);
            this.showError(error.message || 'Failed to process image. Please try again.');
        }
    }

    isValidImageFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        return validTypes.includes(file.type);
    }

    displayOriginalImage(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.originalImage.src = e.target.result;
            
            // Display image info
            const sizeInMB = (file.size / (1024 * 1024)).toFixed(2);
            this.imageInfo.innerHTML = `
                <strong>File:</strong> ${file.name}<br>
                <strong>Size:</strong> ${sizeInMB} MB<br>
                <strong>Type:</strong> ${file.type}
            `;
        };
        reader.readAsDataURL(file);
    }

    async uploadImage(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${this.apiBaseUrl}/api/upload/detect`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    displayResults(result, processingTime) {
        try {
            // Display processing time
            this.processingTime.innerHTML = `
                <strong>Processing Time:</strong> ${processingTime}ms<br>
                <strong>Status:</strong> ${result.status || 'Completed'}
            `;

            // Display result image if available
            if (result.result_image) {
                this.resultImage.src = `data:image/jpeg;base64,${result.result_image}`;
            } else {
                // If no result image, show original
                this.resultImage.src = this.originalImage.src;
            }

            // Display detection summary
            this.displayDetectionSummary(result.detections || []);

            // Show results section
            this.showResults();

        } catch (error) {
            console.error('Error displaying results:', error);
            this.showError('Error displaying results. Please try again.');
        }
    }

    displayDetectionSummary(detections) {
        if (!detections || detections.length === 0) {
            this.summaryContent.innerHTML = `
                <div class="no-detections">
                    <i class="fas fa-search"></i>
                    <h4>No Furniture Detected</h4>
                    <p>Try uploading an image with visible furniture items like chairs, tables, sofas, or beds.</p>
                </div>
            `;
            return;
        }

        // Filter for furniture-related detections
        const furnitureClasses = ['chair', 'couch', 'bed', 'dining table', 'toilet', 'sofa', 'furniture'];
        const furnitureDetections = detections.filter(detection => 
            furnitureClasses.some(furniture => 
                detection.class_name.toLowerCase().includes(furniture.toLowerCase())
            )
        );

        if (furnitureDetections.length === 0) {
            this.summaryContent.innerHTML = `
                <div class="no-detections">
                    <i class="fas fa-couch"></i>
                    <h4>No Furniture Items Found</h4>
                    <p>Detected ${detections.length} object(s), but none were furniture items.</p>
                </div>
            `;
            return;
        }

        // Create detection items
        let summaryHTML = `
            <div style="margin-bottom: 20px;">
                <strong>Found ${furnitureDetections.length} furniture item(s):</strong>
            </div>
        `;

        furnitureDetections.forEach((detection, index) => {
            const confidence = (detection.confidence * 100).toFixed(1);
            summaryHTML += `
                <div class="detection-item">
                    <div class="detection-name">
                        <i class="fas fa-couch" style="margin-right: 8px; color: #27ae60;"></i>
                        ${detection.class_name}
                    </div>
                    <div class="detection-confidence">${confidence}%</div>
                </div>
            `;
        });

        // Add statistics
        const avgConfidence = furnitureDetections.reduce((sum, d) => sum + d.confidence, 0) / furnitureDetections.length;
        const maxConfidence = Math.max(...furnitureDetections.map(d => d.confidence));

        summaryHTML += `
            <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; text-align: center;">
                    <div>
                        <div style="font-size: 1.2rem; font-weight: bold; color: #27ae60;">${furnitureDetections.length}</div>
                        <div style="font-size: 0.9rem; color: #7f8c8d;">Total Items</div>
                    </div>
                    <div>
                        <div style="font-size: 1.2rem; font-weight: bold; color: #3498db;">${(avgConfidence * 100).toFixed(1)}%</div>
                        <div style="font-size: 0.9rem; color: #7f8c8d;">Avg Confidence</div>
                    </div>
                    <div>
                        <div style="font-size: 1.2rem; font-weight: bold; color: #e67e22;">${(maxConfidence * 100).toFixed(1)}%</div>
                        <div style="font-size: 0.9rem; color: #7f8c8d;">Best Match</div>
                    </div>
                </div>
            </div>
        `;

        this.summaryContent.innerHTML = summaryHTML;
    }

    showLoading() {
        this.hideAllSections();
        this.loadingSection.style.display = 'block';
    }

    showResults() {
        this.hideAllSections();
        this.resultsSection.style.display = 'block';
    }

    showError(message) {
        this.hideAllSections();
        this.errorMessage.textContent = message;
        this.errorSection.style.display = 'block';
    }

    hideAllSections() {
        this.resultsSection.style.display = 'none';
        this.loadingSection.style.display = 'none';
        this.errorSection.style.display = 'none';
    }
}

// Global function for retry button
function resetUpload() {
    app.hideAllSections();
    document.getElementById('fileInput').value = '';
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new FurnitureDetectionApp();
    
    // Add some console info for debugging
    console.log('🪑 Furniture Detection System Loaded');
    console.log('API Base URL:', window.location.origin);
});

// Add some utility functions for debugging
window.debugApp = {
    testAPI: async () => {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            console.log('API Health Check:', data);
            return data;
        } catch (error) {
            console.error('API Test Failed:', error);
            return error;
        }
    },
    
    getModelInfo: async () => {
        try {
            const response = await fetch('/api/model-info');
            const data = await response.json();
            console.log('Model Info:', data);
            return data;
        } catch (error) {
            console.error('Model Info Failed:', error);
            return error;
        }
    }
};