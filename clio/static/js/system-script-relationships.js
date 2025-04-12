/**
 * System-Script Relationships Visualization
 * 
 * This module implements an interactive diagram showing the relationships
 * between systems and scripts, how they interact, and their dependencies.
 */

 const SystemScriptRelationshipsViz = {
    // State variables
    data: null,
    simulation: null,
    zoomInstance: null,
    parent: null, // Reference to the parent VizHub object
    
    // Initialize the visualization
    initialize: function(parentHub) {
        this.parent = parentHub;
        
        // Fetch data
        this.fetchData()
            .then(data => {
                // Store the data
                this.data = data;
                
                // Initialize the diagram
                this.createVisualization(data);
                
                // Update the legend
                this.updateLegend(data);
                
                // Populate filter dropdowns
                this.populateFilters(data);
                
                // Hide loading overlay
                document.getElementById('loadingOverlay').style.display = 'none';
            })
            .catch(error => {
                console.error("Error loading system-script relationship data:", error);
                document.getElementById('loadingOverlay').style.display = 'none';
                document.getElementById('vizDiagram').innerHTML = `
                    <div class="viz-no-data">
                        <h3 class="text-lg font-medium text-red-800">Error Loading Data</h3>
                        <p class="mt-2 text-red-600">${error.message || "Could not load data. Please try again later."}</p>
                    </div>
                `;
            });
    },
    
    // Fetch data from server
    fetchData: function() {
        // Use our API endpoint
        return fetch("/api/visualizations/system-script-relationships/")
            .then(response => response.json());
    },
    
    // Create the main visualization
    createVisualization: function(data) {
        // TODO: Implement the visualization with D3.js
        
        // For now, just show a placeholder message
        document.getElementById('vizDiagram').innerHTML = `
            <div class="viz-no-data">
                <h3 class="text-lg font-medium text-blue-800">System-Script Relationships</h3>
                <p class="mt-2 text-gray-600">This visualization will show how scripts and systems interact with each other.</p>
                <p class="mt-2 text-gray-600">Features to be implemented:</p>
                <ul class="list-disc pl-5 mt-2 text-gray-600 text-left">
                    <li>Bipartite graph showing systems and scripts as different node types</li>
                    <li>Connection types showing input/output/utility relationships</li>
                    <li>Filters for script languages and systems</li>
                    <li>Interactive selection and highlighting</li>
                </ul>
            </div>
        `;
    },
    
    // Update the legend
    updateLegend: function(data) {
        const legendContainer = document.getElementById('vizLegend');
        legendContainer.innerHTML = '';
        
        // Add placeholder legend items
        const legendItems = [
            { color: '#3b82f6', label: 'System' },
            { color: '#10b981', label: 'Script' },
            { color: '#6366f1', label: 'Input Relationship' },
            { color: '#f59e0b', label: 'Output Relationship' },
            { color: '#8b5cf6', label: 'Utility Relationship' }
        ];
        
        legendItems.forEach(item => {
            const legendItem = document.createElement('div');
            legendItem.className = 'legend-item';
            legendItem.innerHTML = `
                <div class="legend-color" style="background-color: ${item.color};"></div>
                <span>${item.label}</span>
            `;
            legendContainer.appendChild(legendItem);
        });
    },
    
    // Populate filters
    populateFilters: function(data) {
        // System filter
        const systemFilter = document.getElementById('systemFilter');
        if (systemFilter) {
            // Add placeholder options
            systemFilter.innerHTML = `
                <option value="">Any System</option>
                <option value="1">System 1</option>
                <option value="2">System 2</option>
                <option value="3">System 3</option>
            `;
        }
        
        // Language filter
        const languageFilter = document.getElementById('languageFilter');
        if (languageFilter) {
            // Add placeholder options
            languageFilter.innerHTML = `
                <option value="">All Languages</option>
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="sql">SQL</option>
            `;
        }
    },
    
    // Handle search input
    handleSearch: function(searchTerm) {
        console.log("Searching for:", searchTerm);
        // Would implement actual search when visualization is complete
    },
    
    // Reset the visualization
    reset: function() {
        console.log("Resetting visualization");
        // Would implement actual reset when visualization is complete
    },
    
    // Optimize the layout
    optimizeLayout: function() {
        console.log("Optimizing layout");
        // Would implement layout optimization when visualization is complete
    },
    
    // Zoom functions
    zoomIn: function() {
        console.log("Zoom in");
        // Would implement when visualization is complete
    },
    
    zoomOut: function() {
        console.log("Zoom out");
        // Would implement when visualization is complete
    },
    
    centerView: function() {
        console.log("Center view");
        // Would implement when visualization is complete
    },
    
    // Toggle fullscreen mode
    toggleFullscreen: function() {
        const diagramContainer = document.getElementById('vizDiagram');
        
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else if (diagramContainer.requestFullscreen) {
            diagramContainer.requestFullscreen();
        } else if (diagramContainer.webkitRequestFullscreen) {
            diagramContainer.webkitRequestFullscreen();
        } else if (diagramContainer.msRequestFullscreen) {
            diagramContainer.msRequestFullscreen();
        }
    },
    
    // Handle fullscreen change event
    handleFullscreenChange: function() {
        // Update visualization for fullscreen if needed
    },
    
    // Handle window resize
    handleResize: function() {
        // Update visualization for new size if needed
    },
    
    // Export functions - placeholders for now
    exportSVG: function() {
        alert("SVG export not yet implemented for this visualization");
    },
    
    exportPNG: function() {
        alert("PNG export not yet implemented for this visualization");
    },
    
    exportJSON: function() {
        alert("JSON export not yet implemented for this visualization");
    }
};