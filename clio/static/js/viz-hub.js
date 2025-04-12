/**
 * Visualization Hub Core Module
 * 
 * This is the main module that manages the visualization hub interface,
 * handles visualization switching, and common functionality like UI interactions.
 */

// Main VizHub object
const VizHub = {
    // Current state
    currentViz: 'system-relationships',
    data: {}, // Stores data for different visualizations
    visualizations: {}, // References to loaded visualization modules
    
    // Initialization
    init: function() {
        this.setupEventListeners();
        this.loadVisualizationModule('system-relationships');
    },
    
    // Set up all UI interactions
    setupEventListeners: function() {
        // Visualization selector dropdown
        const vizSelectorButton = document.getElementById('vizSelectorButton');
        const vizSelectorMenu = document.getElementById('vizSelectorMenu');
        
        // Toggle dropdown
        vizSelectorButton.addEventListener('click', function() {
            vizSelectorMenu.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!vizSelectorButton.contains(e.target) && !vizSelectorMenu.contains(e.target)) {
                vizSelectorMenu.classList.remove('active');
            }
        });
        
        // Visualization selection
        document.querySelectorAll('.viz-selector-item').forEach(item => {
            item.addEventListener('click', () => {
                const vizType = item.getAttribute('data-viz');
                const vizName = item.getAttribute('data-name');
                
                // Update UI
                document.querySelectorAll('.viz-selector-item').forEach(i => {
                    i.classList.remove('active');
                });
                item.classList.add('active');
                
                // Update current visualization name
                document.getElementById('currentVizName').textContent = vizName;
                
                // Close dropdown
                vizSelectorMenu.classList.remove('active');
                
                // Load the visualization
                this.loadVisualizationModule(vizType);
            });
        });
        
        // Export button
        const exportButton = document.getElementById('exportButton');
        const exportMenu = document.getElementById('exportMenu');
        
        // Toggle export menu
        exportButton.addEventListener('click', function(e) {
            e.stopPropagation();
            exportMenu.classList.toggle('active');
        });
        
        // Close export menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!exportButton.contains(e.target) && !exportMenu.contains(e.target)) {
                exportMenu.classList.remove('active');
            }
        });
        
        // Export options
        document.querySelectorAll('.viz-export-item').forEach(item => {
            item.addEventListener('click', e => {
                e.preventDefault();
                const format = item.getAttribute('data-format');
                this.exportVisualization(format);
                exportMenu.classList.remove('active');
            });
        });
        
        // Optimal layout button
        document.getElementById('optimalLayoutButton').addEventListener('click', () => {
            if (this.currentVisualization && typeof this.currentVisualization.optimizeLayout === 'function') {
                this.currentVisualization.optimizeLayout();
            }
        });
        
        // Reset button
        document.getElementById('resetButton').addEventListener('click', () => {
            // Clear search
            document.getElementById('searchInput').value = '';
            
            if (this.currentVisualization && typeof this.currentVisualization.reset === 'function') {
                this.currentVisualization.reset();
            }
        });
        
        // Zoom controls
        document.getElementById('zoomInButton').addEventListener('click', () => {
            if (this.currentVisualization && typeof this.currentVisualization.zoomIn === 'function') {
                this.currentVisualization.zoomIn();
            }
        });
        
        document.getElementById('zoomOutButton').addEventListener('click', () => {
            if (this.currentVisualization && typeof this.currentVisualization.zoomOut === 'function') {
                this.currentVisualization.zoomOut();
            }
        });
        
        document.getElementById('centerButton').addEventListener('click', () => {
            if (this.currentVisualization && typeof this.currentVisualization.centerView === 'function') {
                this.currentVisualization.centerView();
            }
        });
        
        document.getElementById('fullscreenButton').addEventListener('click', () => {
            if (this.currentVisualization && typeof this.currentVisualization.toggleFullscreen === 'function') {
                this.currentVisualization.toggleFullscreen();
            }
        });
        
        // Window resize event for responsive behavior
        window.addEventListener('resize', () => {
            if (this.currentVisualization && typeof this.currentVisualization.handleResize === 'function') {
                this.currentVisualization.handleResize();
            }
        });
        
        // Fullscreen change event
        document.addEventListener('fullscreenchange', () => {
            if (this.currentVisualization && typeof this.currentVisualization.handleFullscreenChange === 'function') {
                this.currentVisualization.handleFullscreenChange();
            }
        });
        
        // Set up search functionality
        document.getElementById('searchInput').addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            if (this.currentVisualization && typeof this.currentVisualization.handleSearch === 'function') {
                this.currentVisualization.handleSearch(searchTerm);
            }
        });
    },
    
    // Load a specific visualization module dynamically
    loadVisualizationModule: function(vizType) {
        // Show loading overlay
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        // Clear the current visualization
        this.clearVisualization();
        
        // Update current visualization
        this.currentViz = vizType;
        
        // Update dynamic filters based on visualization type
        this.updateDynamicFilters(vizType);
        
        // Module path pattern - adjust based on your actual structure
        const modulePath = `/static/js/visualizations/${vizType}.js`;
        
        // If we've already loaded this module, use it
        if (this.visualizations[vizType]) {
            this.initializeVisualization(vizType);
            return;
        }
        
        // Otherwise, dynamically load the JavaScript file
        const script = document.createElement('script');
        script.src = modulePath;
        script.onload = () => {
            // If we have a successful load but no module is found, show error
            if (!window[this.getModuleName(vizType)]) {
                this.showLoadError(vizType, 'Module not found after loading');
                return;
            }
            
            // Store reference to the module
            this.visualizations[vizType] = window[this.getModuleName(vizType)];
            
            // Initialize the visualization
            this.initializeVisualization(vizType);
        };
        
        script.onerror = () => {
            // Handle loading error
            this.showLoadError(vizType, 'Failed to load visualization module');
        };
        
        document.head.appendChild(script);
    },
    
    // Get module name from viz type (e.g., 'system-relationships' -> 'SystemRelationshipsViz')
    getModuleName: function(vizType) {
        return vizType.split('-').map(part => 
            part.charAt(0).toUpperCase() + part.slice(1)
        ).join('') + 'Viz';
    },
    
    // Initialize the visualization after module is loaded
    initializeVisualization: function(vizType) {
        if (!this.visualizations[vizType]) {
            // Placeholder or "coming soon" for visualizations without modules
            document.getElementById('loadingOverlay').style.display = 'none';
            document.getElementById('vizDiagram').innerHTML = `
                <div class="viz-no-data">
                    <h3 class="text-lg font-medium text-blue-800">${this.formatVizName(vizType)}</h3>
                    <p class="mt-2 text-gray-600">This visualization is coming soon. Please select a different visualization.</p>
                </div>
            `;
            return;
        }
        
        // Store reference to current visualization
        this.currentVisualization = this.visualizations[vizType];
        
        // Initialize the visualization
        this.currentVisualization.initialize(this);
    },
    
    // Format visualization type for display
    formatVizName: function(vizType) {
        return vizType.split('-').map(part => 
            part.charAt(0).toUpperCase() + part.slice(1)
        ).join(' ');
    },
    
    // Clear current visualization
    clearVisualization: function() {
        // Clear diagram container
        const diagram = document.getElementById('vizDiagram');
        diagram.innerHTML = '';
        
        // Clear legend
        document.getElementById('vizLegend').innerHTML = '';
        
        // Hide info panel
        document.getElementById('infoPanel').style.display = 'none';
        
        // Hide mini map
        const miniMap = document.getElementById('miniMap');
        miniMap.innerHTML = '';
        miniMap.style.display = 'none';
    },
    
    // Show error when visualization fails to load
    showLoadError: function(vizType, errorMessage) {
        document.getElementById('loadingOverlay').style.display = 'none';
        document.getElementById('vizDiagram').innerHTML = `
            <div class="viz-no-data">
                <h3 class="text-lg font-medium text-red-800">Error Loading ${this.formatVizName(vizType)}</h3>
                <p class="mt-2 text-red-600">${errorMessage}</p>
            </div>
        `;
    },
    
    // Update filters based on visualization type
    updateDynamicFilters: function(vizType) {
        const filterContainer = document.getElementById('vizFilters');
        filterContainer.innerHTML = '';
        
        // Add filters based on visualization type
        switch(vizType) {
            case 'system-relationships':
                this.addCategoryFilter(filterContainer);
                this.addStatusFilter(filterContainer);
                this.addSSOFilter(filterContainer);
                this.addHostFilter(filterContainer);
                break;
            case 'system-script-relationships':
                this.addSystemFilter(filterContainer, 'System');
                this.addLanguageFilter(filterContainer);
                break;
            case 'host-script-relationships':
                this.addHostSystemFilter(filterContainer);
                this.addLanguageFilter(filterContainer);
                this.addScheduleFilter(filterContainer);
                break;
            case 'workflow-plan-timeline':
                this.addStatusFilter(filterContainer, 'Status');
                this.addDateRangeFilter(filterContainer);
                break;
            case 'initiative-dependencies':
                this.addStatusFilter(filterContainer, 'Initiative Status');
                this.addPriorityFilter(filterContainer);
                break;
            default:
                // Default - no filters
                break;
        }
    },
    
    // Filter creation helpers
    addCategoryFilter: function(container, label = 'Category') {
        const filterDiv = document.createElement('div');
        filterDiv.className = 'viz-filter';
        filterDiv.innerHTML = `
            <span class="viz-filter-label">${label}</span>
            <select class="viz-filter-select" id="categoryFilter">
                <option value="">All Categories</option>
                <!-- Categories will be loaded dynamically -->
            </select>
        `;
        container.appendChild(filterDiv);
    },
    
    addStatusFilter: function(container, label = 'Status') {
        const filterDiv = document.createElement('div');
        filterDiv.className = 'viz-filter';
        filterDiv.innerHTML = `
            <span class="viz-filter-label">${label}</span>
            <select class="viz-filter-select" id="statusFilter">
                <option value="">All Statuses</option>
                <!-- Statuses will be loaded dynamically -->
            </select>
        `;
        container.appendChild(filterDiv);
    },
    
    addSSOFilter: function(container) {
        const filterDiv = document.createElement('div');
        filterDiv.className = 'viz-filter';
        filterDiv.innerHTML = `
            <span class="viz-filter-label">SSO</span>
            <select class="viz-filter-select" id="ssoFilter">
                <option value="">All</option>
                <option value="none">None</option>
                <!-- SSO options will be loaded dynamically -->
            </select>
        `;
        container.appendChild(filterDiv);
    },
    
    addHostFilter: function(container) {
        const filterDiv = document.createElement('div');
        filterDiv.className = 'viz-filter';
        filterDiv.innerHTML = `
            <span class="viz-filter-label">Hosting</span>
            <select class="viz-filter-select" id="hostFilter">
                <option value="">All</option>
                <option value="none">None</option>
                <!-- Host options will be loaded dynamically -->
            </select>
        `;
        container.appendChild(filterDiv);
    },
    
    addLanguageFilter: function(container) {
        const filterDiv = document.createElement('div');
        filterDiv.className = 'viz-filter';
        filterDiv.innerHTML = `
            <span class="viz-filter-label">Language</span>
            <select class="viz-filter-select" id="languageFilter">
                <option value="">All Languages</option>
                <!-- Languages will be loaded dynamically -->
            </select>
        `;
        container.appendChild(filterDiv);
    },
    
    addSystemFilter: function(container, label = 'System') {
        const filterDiv = document.createElement('div');
        filterDiv.className = 'viz-filter';
        filterDiv.innerHTML = `
            <span class="viz-filter-label">${label}</span>
            <select class="viz-filter-select" id="systemFilter">
                <option value="">Any System</option>
                <!-- Systems will be loaded dynamically -->
            </select>
        `;
        container.appendChild(filterDiv);
    },
    
    addHostSystemFilter: function(container) {
        const filterDiv = document.createElement('div');
        filterDiv.className = 'viz-filter';
        filterDiv.innerHTML = `
            <span class="viz-filter-label">Host System</span>
            <select class="viz-filter-select" id="hostSystemFilter">
                <option value="">Any Host</option>
                <!-- Host systems will be loaded dynamically -->
            </select>
        `;
        container.appendChild(filterDiv);
    },
    
    addScheduleFilter: function(container) {
        const filterDiv = document.createElement('div');
        filterDiv.className = 'viz-filter';
        filterDiv.innerHTML = `
            <span class="viz-filter-label">Schedule Method</span>
            <select class="viz-filter-select" id="scheduleFilter">
                <option value="">All Methods</option>
                <option value="cron">Cron</option>
                <option value="task_scheduler">Task Scheduler</option>
                <option value="jenkins">Jenkins</option>
                <option value="airflow">Airflow</option>
                <option value="manual">Manual</option>
                <option value="other">Other</option>
            </select>
        `;
        container.appendChild(filterDiv);
    },
    
    addPriorityFilter: function(container) {
        const filterDiv = document.createElement('div');
        filterDiv.className = 'viz-filter';
        filterDiv.innerHTML = `
            <span class="viz-filter-label">Priority</span>
            <select class="viz-filter-select" id="priorityFilter">
                <option value="">All Priorities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
            </select>
        `;
        container.appendChild(filterDiv);
    },
    
    addDateRangeFilter: function(container) {
        const filterDiv = document.createElement('div');
        filterDiv.className = 'viz-filter';
        filterDiv.innerHTML = `
            <span class="viz-filter-label">From</span>
            <input type="date" class="viz-filter-select" id="dateFromFilter">
        `;
        container.appendChild(filterDiv);
        
        const filterDivTo = document.createElement('div');
        filterDivTo.className = 'viz-filter';
        filterDivTo.innerHTML = `
            <span class="viz-filter-label">To</span>
            <input type="date" class="viz-filter-select" id="dateToFilter">
        `;
        container.appendChild(filterDivTo);
    },
    
    // Export functions
    exportVisualization: function(format) {
        if (!this.currentVisualization) return;
        
        switch(format) {
            case 'svg':
                this.currentVisualization.exportSVG && this.currentVisualization.exportSVG();
                break;
            case 'png':
                this.currentVisualization.exportPNG && this.currentVisualization.exportPNG();
                break;
            case 'json':
                this.currentVisualization.exportJSON && this.currentVisualization.exportJSON();
                break;
        }
    }
};

// Initialize on DOM content loaded
document.addEventListener('DOMContentLoaded', function() {
    VizHub.init();
});