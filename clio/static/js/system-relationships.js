/**
 * System Relationships Visualization
 * 
 * This module implements the interactive system relationships diagram
 * showing connections between systems with force-directed layout.
 */

 const SystemRelationshipsViz = {
    // State variables
    data: null,
    simulation: null,
    zoomInstance: null,
    parent: null, // Reference to the parent VizHub object
    
    // Initialize the visualization
    initialize: function(parentHub) {
        this.parent = parentHub;
        
        // Fetch data and create visualization
        fetch("/systems/relationship_data/")
            .then(response => response.json())
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
                console.error("Error loading relationship data:", error);
                document.getElementById('loadingOverlay').style.display = 'none';
                document.getElementById('vizDiagram').innerHTML = `
                    <div class="viz-no-data">
                        <h3 class="text-lg font-medium text-red-800">Error Loading Data</h3>
                        <p class="mt-2 text-red-600">${error.message || "Could not load relationship data. Please try again later."}</p>
                    </div>
                `;
            });
    },
    
    // Create the main visualization
    createVisualization: function(data) {
        const container = document.getElementById('vizDiagram');
        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight || 700;
        
        // Show mini map for this visualization
        document.getElementById('miniMap').style.display = 'block';
        
        // Calculate appropriate spacing based on number of nodes
        const nodeCount = data.systems.length;
        const totalArea = containerWidth * containerHeight * 0.8; // Use 80% of the total area
        const areaPerNode = totalArea / nodeCount;
        const optimalDistance = Math.sqrt(areaPerNode); // Distance between nodes
        
        // Create SVG
        const svg = d3.select("#vizDiagram")
            .append("svg")
            .attr("width", containerWidth)
            .attr("height", containerHeight);
            
        // Define arrow markers for the connections
        svg.append("defs").append("marker")
            .attr("id", "arrowhead")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 20)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#999");
            
        const g = svg.append("g");
        
        // Set up zoom behavior with wider bounds
        this.zoomInstance = d3.zoom()
            .scaleExtent([0.1, 8])  // Allow much greater zoom range
            .on("zoom", function(event) {
                g.attr("transform", event.transform);
                // Update mini-map viewport indicator if it exists
                if (document.querySelector('.viewport-indicator')) {
                    SystemRelationshipsViz.updateMiniMapViewport(event.transform);
                }
                // Update offscreen indicators
                SystemRelationshipsViz.updateOffscreenIndicators(event.transform);
            });
            
        svg.call(this.zoomInstance);
        
        // Calculate dependencies
        const dependencies = {};
        data.systems.forEach(system => {
            dependencies[system.id] = 0;
        });
        
        data.links.forEach(link => {
            if (dependencies[link.target] !== undefined) {
                dependencies[link.target]++;
            }
        });
        
        // Create force-directed layout with improved spacing
        this.simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(d => d.id).distance(optimalDistance * 1.5)) // Increased link distance
            .force("charge", d3.forceManyBody().strength(-optimalDistance * 3)) // Stronger repulsion
            .force("center", d3.forceCenter(containerWidth / 2, containerHeight / 2))
            .force("collision", d3.forceCollide().radius(d => {
                // Base radius on dependencies and type, but larger overall
                const baseRadius = 25; // Increased from 20
                // Use category slug for type factors
                const typeFactor = d.category.slug === "core" ? 1.3 : 1;
                const depFactor = Math.min(dependencies[d.id] * 0.05 + 1, 1.5);
                return (baseRadius * typeFactor * depFactor) + 20; // Increased padding
            }));
            
        // Create links
        const link = g.selectAll(".connection")
            .data(data.links)
            .enter().append("path")
            .attr("class", d => `connection connection-${d.type}`)
            .attr("id", d => `connection-${d.source}-${d.target}`);
            
        // Add label backgrounds
        const labelBackground = g.selectAll(".label-background")
            .data(data.systems)
            .enter().append("rect")
            .attr("class", "label-background")
            .attr("id", d => `bg-${d.id}`);
            
        // Create nodes
        const node = g.selectAll(".system-node")
            .data(data.systems)
            .enter().append("circle")
            .attr("class", d => `system-node`)
            .attr("id", d => `system-${d.id}`)
            .attr("r", d => {
                // Scale radius based on dependencies
                const baseRadius = 20;
                // Use category slug for type factors
                const typeFactor = d.category.slug === "core" ? 1.3 : 1;
                const depFactor = Math.min(dependencies[d.id] * 0.05 + 1, 1.5);
                return baseRadius * typeFactor * depFactor;
            })
            .attr("fill", d => d.category.color)
            .attr("stroke", d => d.category.text_color)
            .on("mouseover", (event, d) => this.handleNodeMouseOver(event, d, node, link, label, labelBackground))
            .on("mouseout", (event, d) => this.handleNodeMouseOut(event, d, node, link, label, labelBackground))
            .on("click", (event, d) => this.handleNodeClick(event, d, node, link, label, labelBackground))
            .call(d3.drag()
                .on("start", (event, d) => this.dragStarted(event, d))
                .on("drag", (event, d) => this.dragged(event, d))
                .on("end", (event, d) => this.dragEnded(event, d)));
                
        // Add labels to nodes
        const label = g.selectAll(".system-label")
            .data(data.systems)
            .enter().append("text")
            .attr("class", "system-label")
            .text(d => d.name)
            .attr("id", d => `label-${d.id}`)
            .style("font-size", d => {
                // Larger font for more important systems
                return dependencies[d.id] > 5 ? "12px" : 
                    d.category.slug === "core" ? "11px" : "10px";
            })
            .style("font-weight", d => {
                // Bold for key systems
                return d.category.slug === "core" ? "bold" : "normal";
            })
            .each(function(d) {
                // Get the size of the text to correctly size the background
                d.bbox = this.getBBox();
            });
            
        // Update background rectangles based on text size
        labelBackground
            .attr("width", d => d.bbox.width + 8)
            .attr("height", d => d.bbox.height + 4)
            .attr("x", d => d.bbox.x - 4)
            .attr("y", d => d.bbox.y - 2);
            
        // Set up the simulation
        this.simulation.nodes(data.systems)
            .on("tick", () => this.tick(node, link, label, labelBackground));
            
        this.simulation.force("link")
            .links(data.links);
            
        // Create mini-map
        this.createMiniMap();
        
        // Add indicators for off-screen nodes
        this.createOffscreenIndicators();
        
        // Set up search functionality - handled by VizHub
        
        // Find and position orphaned nodes on initial layout
        setTimeout(() => this.identifyAndPositionOrphanedNodes(), 500);
        
        // Initially run simulation with appropriate alpha
        this.simulation.alpha(0.8).restart();
        
        // Fit all nodes in view after initial layout
        setTimeout(() => this.fitView(), 1500);
    },
    
    // Update function for simulation ticks
    tick: function(node, link, label, labelBackground) {
        const containerWidth = document.getElementById('vizDiagram').clientWidth;
        const containerHeight = document.getElementById('vizDiagram').clientHeight;
        
        // Use very minimal bounds (a fraction of overall width/height)
        // to allow much more spreading
        const boundingFactor = 2; // Allow nodes to go beyond the viewport
        const xPadding = containerWidth * boundingFactor;
        const yPadding = containerHeight * boundingFactor;
        
        // Keep nodes within greatly extended bounds
        node.attr("cx", d => {
            return d.x = Math.max(-xPadding, Math.min(containerWidth + xPadding, d.x));
        })
        .attr("cy", d => {
            return d.y = Math.max(-yPadding, Math.min(containerHeight + yPadding, d.y));
        });
        
        // Update links
        link.attr("d", d => {
            const dx = d.target.x - d.source.x;
            const dy = d.target.y - d.source.y;
            const dr = Math.sqrt(dx * dx + dy * dy);
            
            // Calculate radii based on the node sizes
            let sourceRadius = 20, targetRadius = 20;
            
            // Only draw if we have valid positions
            if (isNaN(d.source.x) || isNaN(d.source.y) || isNaN(d.target.x) || isNaN(d.target.y)) {
                return "M0,0L0,0";
            }
            
            // Calculate points that account for the radius
            const ratio = targetRadius / dr;
            const endX = d.target.x - dx * ratio;
            const endY = d.target.y - dy * ratio;
            
            const startRatio = sourceRadius / dr;
            const startX = d.source.x + dx * startRatio;
            const startY = d.source.y + dy * startRatio;
            
            // Use curved paths for clearer visualization
            const curveFactor = 1.2;
            
            return `M${startX},${startY}A${dr*curveFactor},${dr*curveFactor} 0 0,1 ${endX},${endY}`;
        });
        
        // Update label and background positions
        label.attr("x", d => d.x)
            .attr("y", d => d.y);
            
        labelBackground
            .attr("x", d => d.x - (d.bbox.width / 2) - 4)
            .attr("y", d => d.y - (d.bbox.height / 2) - 2);
            
        // Update mini-map
        this.updateMiniMap();
        
        // Update off-screen indicators
        this.updateOffscreenIndicators();
    },
    
    // Handler for mouse over events on nodes
    handleNodeMouseOver: function(event, d, node, link, label, labelBackground) {
        // Highlight the node
        d3.select(event.currentTarget).classed("highlighted", true);
        
        // Highlight connected links and fade others
        link.each(function(l) {
            if (l.source.id === d.id || l.target.id === d.id) {
                d3.select(this).classed("connection-highlighted", true);
            } else {
                d3.select(this).style("opacity", 0.1);
            }
        });
        
        // Highlight connected nodes and fade others
        node.each(function(n) {
            const isConnected = SystemRelationshipsViz.data.links.some(l => 
                (l.source.id === d.id && l.target.id === n.id) || 
                (l.target.id === d.id && l.source.id === n.id));
            
            if (n.id === d.id || isConnected) {
                d3.select(this).style("opacity", 1);
            } else {
                d3.select(this).style("opacity", 0.2);
            }
        });
        
        // Also fade unconnected labels
        label.each(function(n) {
            const isConnected = SystemRelationshipsViz.data.links.some(l => 
                (l.source.id === d.id && l.target.id === n.id) || 
                (l.target.id === d.id && l.source.id === n.id));
            
            if (n.id === d.id || isConnected) {
                d3.select(this).style("opacity", 1);
            } else {
                d3.select(this).style("opacity", 0.2);
            }
        });
        
        labelBackground.each(function(n) {
            const isConnected = SystemRelationshipsViz.data.links.some(l => 
                (l.source.id === d.id && l.target.id === n.id) || 
                (l.target.id === d.id && l.source.id === n.id));
            
            if (n.id === d.id || isConnected) {
                d3.select(this).style("opacity", 1);
            } else {
                d3.select(this).style("opacity", 0.2);
            }
        });
        
        // Show info panel
        this.showInfoPanel(d);
    },
    
    // Handler for mouse out events on nodes
    handleNodeMouseOut: function(event, d, node, link, label, labelBackground) {
        // Only reset if not clicked
        if (!d3.select(event.currentTarget).classed("clicked")) {
            // Remove highlight from the node
            d3.select(event.currentTarget).classed("highlighted", false);
            
            // Reset all opacities
            link.style("opacity", 0.6).classed("connection-highlighted", false);
            node.style("opacity", 1);
            label.style("opacity", 1);
            labelBackground.style("opacity", 1);
            
            // Hide info panel
            this.hideInfoPanel();
        }
    },
    
    // Handler for click events on nodes
    handleNodeClick: function(event, d, node, link, label, labelBackground) {
        // Toggle clicked state
        const wasClicked = d3.select(event.currentTarget).classed("clicked");
        
        // Reset all clicked states and highlights
        node.classed("clicked", false).classed("highlighted", false);
        link.classed("connection-highlighted", false).style("opacity", 0.6);
        node.style("opacity", 1);
        label.style("opacity", 1);
        labelBackground.style("opacity", 1);
        
        if (!wasClicked) {
            // Set this node as clicked
            d3.select(event.currentTarget).classed("clicked", true).classed("highlighted", true);
            
            // Highlight connected links and fade others
            link.each(function(l) {
                if (l.source.id === d.id || l.target.id === d.id) {
                    d3.select(this).classed("connection-highlighted", true);
                } else {
                    d3.select(this).style("opacity", 0.1);
                }
            });
            
            // Highlight connected nodes and fade others
            node.each(function(n) {
                const isConnected = SystemRelationshipsViz.data.links.some(l => 
                    (l.source.id === d.id && l.target.id === n.id) || 
                    (l.target.id === d.id && l.source.id === n.id));
                
                if (n.id === d.id || isConnected) {
                    d3.select(this).style("opacity", 1);
                } else {
                    d3.select(this).style("opacity", 0.2);
                }
            });
            
            // Also fade unconnected labels
            label.each(function(n) {
                const isConnected = SystemRelationshipsViz.data.links.some(l => 
                    (l.source.id === d.id && l.target.id === n.id) || 
                    (l.target.id === d.id && l.source.id === n.id));
                
                if (n.id === d.id || isConnected) {
                    d3.select(this).style("opacity", 1);
                } else {
                    d3.select(this).style("opacity", 0.2);
                }
            });
            
            labelBackground.each(function(n) {
                const isConnected = SystemRelationshipsViz.data.links.some(l => 
                    (l.source.id === d.id && l.target.id === n.id) || 
                    (l.target.id === d.id && l.source.id === n.id));
                
                if (n.id === d.id || isConnected) {
                    d3.select(this).style("opacity", 1);
                } else {
                    d3.select(this).style("opacity", 0.2);
                }
            });
            
            // Center view on this node
            this.centerOnNode(d);
            
            // Show info panel
            this.showInfoPanel(d);
        } else {
            // Hide info panel if already clicked
            this.hideInfoPanel();
        }
    },
    
    // Display info panel with details about the node
    showInfoPanel: function(system) {
        const panel = document.getElementById('infoPanel');
        const title = document.getElementById('infoPanelTitle');
        const content = document.getElementById('infoPanelContent');
        
        title.textContent = system.name;
        
        // Find system details
        let html = `<p><strong>Category:</strong> <span style="background-color: ${system.category.color}; color: ${system.category.text_color}; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem;">${system.category.name}</span></p>`;
        html += `<p><strong>Status:</strong> <span style="background-color: ${system.status.color}; color: ${system.status.text_color}; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem;">${system.status.name}</span></p>`;
        
        // Link to system detail page
        html += `<p class="mt-2"><a href="/systems/${system.id}/" class="text-blue-600 hover:underline">View System Details</a></p>`;
        
        // Find systems that depend on this one (systems where this system is the source in a depends_on relationship)
        const dependents = [];
        this.data.links.forEach(link => {
            if (link.source.id === system.id && link.type === 'depends_on') {
                dependents.push(link.target);
            }
        });
        
        if (dependents.length > 0) {
            html += `<p class="mt-4 font-semibold">Systems that depend on this:</p>`;
            html += '<ul class="list-disc pl-5 mt-2">';
            dependents.forEach(dependent => {
                html += `<li><a href="#" class="text-blue-600 hover:underline node-link" data-node-id="${dependent.id}">${dependent.name}</a></li>`;
            });
            html += '</ul>';
        }
        
        // Find systems this one depends on (systems where this system is the target in a depends_on relationship)
        const dependencies = [];
        this.data.links.forEach(link => {
            if (link.target.id === system.id && link.type === 'depends_on') {
                dependencies.push(link.source);
            }
        });
        
        if (dependencies.length > 0) {
            html += `<p class="mt-4 font-semibold">This system depends on:</p>`;
            html += '<ul class="list-disc pl-5 mt-2">';
            dependencies.forEach(dependency => {
                html += `<li><a href="#" class="text-blue-600 hover:underline node-link" data-node-id="${dependency.id}">${dependency.name}</a></li>`;
            });
            html += '</ul>';
        }
        
        content.innerHTML = html;
        panel.style.display = 'block';
        
        // Add event listeners for node links
        setTimeout(() => {
            document.querySelectorAll('.node-link').forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const nodeId = this.getAttribute('data-node-id');
                    SystemRelationshipsViz.highlightNode(nodeId);
                });
            });
        }, 100);
    },
    
    // Hide the info panel
    hideInfoPanel: function() {
        document.getElementById('infoPanel').style.display = 'none';
    },
    
    // Highlight a specific node by ID
    highlightNode: function(nodeId) {
        // Find the node by ID
        const targetNode = this.data.systems.find(n => n.id == nodeId);
        if (!targetNode) return;
        
        // Get D3 selections
        const node = d3.selectAll(".system-node");
        const link = d3.selectAll(".connection");
        const label = d3.selectAll(".system-label");
        const labelBackground = d3.selectAll(".label-background");
        
        // Reset existing highlights
        node.classed("clicked", false).classed("highlighted", false);
        link.classed("connection-highlighted", false).style("opacity", 0.6);
        node.style("opacity", 1);
        label.style("opacity", 1);
        labelBackground.style("opacity", 1);
        
        // Highlight the target node
        const nodeElement = d3.select(`#system-${nodeId}`);
        nodeElement.classed("highlighted", true).classed("clicked", true);
        
        // Highlight connected links and fade others
        link.each(function(l) {
            if (l.source.id == nodeId || l.target.id == nodeId) {
                d3.select(this).classed("connection-highlighted", true);
            } else {
                d3.select(this).style("opacity", 0.1);
            }
        });
        
        // Highlight connected nodes and fade others
        node.each(function(n) {
            const isConnected = SystemRelationshipsViz.data.links.some(l => 
                (l.source.id == nodeId && l.target.id === n.id) || 
                (l.target.id == nodeId && l.source.id === n.id));
            
            if (n.id == nodeId || isConnected) {
                d3.select(this).style("opacity", 1);
            } else {
                d3.select(this).style("opacity", 0.2);
            }
        });
        
        // Also fade unconnected labels
        label.each(function(n) {
            const isConnected = SystemRelationshipsViz.data.links.some(l => 
                (l.source.id == nodeId && l.target.id === n.id) || 
                (l.target.id == nodeId && l.source.id === n.id));
            
            if (n.id == nodeId || isConnected) {
                d3.select(this).style("opacity", 1);
            } else {
                d3.select(this).style("opacity", 0.2);
            }
        });
        
        labelBackground.each(function(n) {
            const isConnected = SystemRelationshipsViz.data.links.some(l => 
                (l.source.id == nodeId && l.target.id === n.id) || 
                (l.target.id == nodeId && l.source.id === n.id));
            
            if (n.id == nodeId || isConnected) {
                d3.select(this).style("opacity", 1);
            } else {
                d3.select(this).style("opacity", 0.2);
            }
        });
        
        // Center view on this node
        this.centerOnNode(targetNode);
        
        // Show info panel for this node
        this.showInfoPanel(targetNode);
    },
    
    // Create the mini-map
    createMiniMap: function() {
        const miniMapSize = 150;
        const miniMap = d3.select("#miniMap");
        miniMap.html(''); // Clear existing content
        
        const miniSvg = miniMap.append("svg")
            .attr("width", miniMapSize)
            .attr("height", miniMapSize);
            
        // Add a border around the viewable area
        miniSvg.append("rect")
            .attr("width", miniMapSize)
            .attr("height", miniMapSize)
            .attr("fill", "none")
            .attr("stroke", "#ddd")
            .attr("stroke-width", 1);
        
        // Create a group for the mini nodes
        const miniG = miniSvg.append("g");
        
        // Create mini nodes
        const miniNodes = miniG.selectAll(".mini-node")
            .data(this.data.systems)
            .enter().append("circle")
            .attr("class", "mini-node")
            .attr("r", 2)
            .attr("fill", d => d.category.color)
            .attr("stroke", d => d.category.text_color)
            .attr("stroke-width", 0.5);
            
        // Create viewport indicator
        const viewportIndicator = miniSvg.append("rect")
            .attr("class", "viewport-indicator")
            .attr("stroke", "#ff5722")
            .attr("stroke-width", 2)
            .attr("fill", "none")
            .attr("pointer-events", "none");
            
        // Make mini-map interactive
        miniSvg.on("click", (event) => {
            const bounds = event.currentTarget.getBoundingClientRect();
            const clickX = event.clientX - bounds.left;
            const clickY = event.clientY - bounds.top;
            
            // Get bounding box of all nodes for scaling
            let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
            this.data.systems.forEach(system => {
                minX = Math.min(minX, system.x || 0);
                minY = Math.min(minY, system.y || 0);
                maxX = Math.max(maxX, system.x || 0);
                maxY = Math.max(maxY, system.y || 0);
            });
            
            const nodeSpaceWidth = maxX - minX + 200; // Add padding
            const nodeSpaceHeight = maxY - minY + 200;
            
            // Scale the click to main diagram coordinates
            const scaleFactor = Math.max(nodeSpaceWidth / miniMapSize, nodeSpaceHeight / miniMapSize);
            const worldX = minX + (clickX * scaleFactor);
            const worldY = minY + (clickY * scaleFactor);
            
            // Center the view on the clicked point
            const containerWidth = document.getElementById('vizDiagram').clientWidth;
            const containerHeight = document.getElementById('vizDiagram').clientHeight;
            const transform = d3.zoomIdentity
                .translate(containerWidth/2 - worldX, containerHeight/2 - worldY)
                .scale(1);
                
            d3.select("#vizDiagram svg").transition().duration(750).call(
                this.zoomInstance.transform, transform
            );
        });
    },
    
    // Update the mini-map
    updateMiniMap: function() {
        if (!this.data) return;
        
        const miniMapSize = 150;
        
        // Find the bounding box of all nodes
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        this.data.systems.forEach(system => {
            minX = Math.min(minX, system.x || 0);
            minY = Math.min(minY, system.y || 0);
            maxX = Math.max(maxX, system.x || 0);
            maxY = Math.max(maxY, system.y || 0);
        });
        
        // Add padding
        const padding = 50;
        minX -= padding;
        minY -= padding;
        maxX += padding;
        maxY += padding;
        
        // Calculate scale for mini-map
        const nodeSpaceWidth = maxX - minX;
        const nodeSpaceHeight = maxY - minY;
        const xScale = miniMapSize / nodeSpaceWidth;
        const yScale = miniMapSize / nodeSpaceHeight;
        const scale = Math.min(xScale, yScale) * 0.9; // 90% to add some padding
        
        // Update mini nodes with proper scaling from actual node positions
        d3.selectAll(".mini-node")
            .attr("cx", d => (d.x - minX) * scale)
            .attr("cy", d => (d.y - minY) * scale);
            
        // Update viewport indicator based on current transform
        this.updateMiniMapViewport(d3.zoomTransform(d3.select("#vizDiagram svg").node()), minX, minY, scale);
    },
    
    // Update the viewport indicator on the mini-map
    updateMiniMapViewport: function(transform, minX, minY, scale) {
        if (!this.data) return;
        
        const miniMapSize = 150;
        const containerWidth = document.getElementById('vizDiagram').clientWidth;
        const containerHeight = document.getElementById('vizDiagram').clientHeight;
        
        // If min/max not provided, recalculate
        if (minX === undefined || minY === undefined || scale === undefined) {
            let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
            this.data.systems.forEach(system => {
                minX = Math.min(minX, system.x || 0);
                minY = Math.min(minY, system.y || 0);
                maxX = Math.max(maxX, system.x || 0);
                maxY = Math.max(maxY, system.y || 0);
            });
            
            // Add padding
            const padding = 50;
            minX -= padding;
            minY -= padding;
            maxX += padding;
            maxY += padding;
            
            // Calculate scale
            const nodeSpaceWidth = maxX - minX;
            const nodeSpaceHeight = maxY - minY;
            const xScale = miniMapSize / nodeSpaceWidth;
            const yScale = miniMapSize / nodeSpaceHeight;
            scale = Math.min(xScale, yScale) * 0.9;
        }
        
        // Calculate visible area in main view
        const k = transform.k;
        const visibleWidth = containerWidth / k;
        const visibleHeight = containerHeight / k;
        
        // Calculate center of viewport in world coordinates
        const viewportCenterX = -transform.x / k + visibleWidth / 2;
        const viewportCenterY = -transform.y / k + visibleHeight / 2;
        
        // Calculate bounds of viewport in world coordinates
        const viewportMinX = viewportCenterX - visibleWidth / 2;
        const viewportMinY = viewportCenterY - visibleHeight / 2;
        
        // Convert to mini-map coordinates
        const miniX = (viewportMinX - minX) * scale;
        const miniY = (viewportMinY - minY) * scale;
        const miniWidth = visibleWidth * scale;
        const miniHeight = visibleHeight * scale;
        
        // Update viewport rectangle
        d3.select(".viewport-indicator")
            .attr("x", miniX)
            .attr("y", miniY)
            .attr("width", miniWidth)
            .attr("height", miniHeight);
    },
    
    // Create indicators for off-screen nodes
    createOffscreenIndicators: function() {
        // Create container for indicators
        const svg = d3.select("#vizDiagram svg");
        
        const indicators = svg.append("g")
            .attr("class", "offscreen-indicators");
            
        // Add indicator arrows
        indicators.selectAll(".offscreen-arrow")
            .data(["top", "right", "bottom", "left"])
            .enter()
            .append("path")
            .attr("class", "offscreen-arrow")
            .attr("id", d => `offscreen-${d}`)
            .attr("d", d => {
                // Create arrows pointing in from edges
                switch(d) {
                    case "top": return "M10,0L20,15L0,15Z"; // Down arrow
                    case "right": return "M30,10L15,20L15,0Z"; // Left arrow
                    case "bottom": return "M10,30L0,15L20,15Z"; // Up arrow
                    case "left": return "M0,10L15,0L15,20Z"; // Right arrow
                }
            })
            .attr("fill", "#ff5722")
            .attr("stroke", "#fff")
            .attr("stroke-width", 1)
            .style("opacity", 0) // Hidden by default
            .style("pointer-events", "none");
            
        // Position the arrows
        this.updateOffscreenIndicatorPositions();
    },
    
    // Update positions of off-screen indicators
    updateOffscreenIndicatorPositions: function() {
        const containerWidth = document.getElementById('vizDiagram').clientWidth;
        const containerHeight = document.getElementById('vizDiagram').clientHeight;
        
        const topArrow = d3.select("#offscreen-top");
        const rightArrow = d3.select("#offscreen-right");
        const bottomArrow = d3.select("#offscreen-bottom");
        const leftArrow = d3.select("#offscreen-left");
        
        if (!topArrow.empty()) {
            topArrow.attr("transform", `translate(${containerWidth/2 - 10}, 15)`);
        }
        
        if (!rightArrow.empty()) {
            rightArrow.attr("transform", `translate(${containerWidth - 30}, ${containerHeight/2 - 10})`);
        }
        
        if (!bottomArrow.empty()) {
            bottomArrow.attr("transform", `translate(${containerWidth/2 - 10}, ${containerHeight - 30})`);
        }
        
        if (!leftArrow.empty()) {
            leftArrow.attr("transform", `translate(15, ${containerHeight/2 - 10})`);
        }
    },
    
    // Update visibility of off-screen indicators based on node positions
    updateOffscreenIndicators: function(transform) {
        if (!this.data) return;
        
        // If no transform provided, use current
        if (!transform) {
            const svg = d3.select("#vizDiagram svg");
            if (svg.empty()) return;
            transform = d3.zoomTransform(svg.node());
        }
        
        // Get current view bounds
        const containerWidth = document.getElementById('vizDiagram').clientWidth;
        const containerHeight = document.getElementById('vizDiagram').clientHeight;
        
        const scale = transform.k;
        
        const visibleMinX = -transform.x / scale;
        const visibleMaxX = (-transform.x + containerWidth) / scale;
        const visibleMinY = -transform.y / scale;
        const visibleMaxY = (-transform.y + containerHeight) / scale;
        
        // Check for nodes in each direction
        let hasTop = false;
        let hasRight = false;
        let hasBottom = false;
        let hasLeft = false;
        
        this.data.systems.forEach(system => {
            // Check if node is outside of viewable area
            if (system.x < visibleMinX) hasLeft = true;
            if (system.x > visibleMaxX) hasRight = true;
            if (system.y < visibleMinY) hasTop = true;
            if (system.y > visibleMaxY) hasBottom = true;
        });
        
        // Show/hide offscreen indicators
        d3.select("#offscreen-top").style("opacity", hasTop ? 0.8 : 0);
        d3.select("#offscreen-right").style("opacity", hasRight ? 0.8 : 0);
        d3.select("#offscreen-bottom").style("opacity", hasBottom ? 0.8 : 0);
        d3.select("#offscreen-left").style("opacity", hasLeft ? 0.8 : 0);
    },
    
    // Update the legend with categories and relationship types
    updateLegend: function(data) {
        const legendContainer = document.getElementById('vizLegend');
        legendContainer.innerHTML = '';
        
        // Extract unique categories
        const categoriesMap = new Map();
        data.systems.forEach(system => {
            if (system.category && !categoriesMap.has(system.category.slug)) {
                categoriesMap.set(system.category.slug, system.category);
            }
        });
        
        // Add category legend items
        categoriesMap.forEach(category => {
            const legendItem = document.createElement('div');
            legendItem.className = 'legend-item';
            legendItem.innerHTML = `
                <div class="legend-color" style="background-color: ${category.color}; border: 1px solid ${category.text_color};"></div>
                <span>${category.name}</span>
            `;
            legendContainer.appendChild(legendItem);
        });
        
        // Add relationship type legend items
        const relationshipTypes = [
            { type: 'depends_on', label: 'Depends On', class: 'connection-depends_on' },
            { type: 'provides_data_to', label: 'Provides Data To', class: 'connection-provides_data_to' },
            { type: 'integrates_with', label: 'Integrates With', class: 'connection-integrates_with' }
        ];
        
        relationshipTypes.forEach(rel => {
            const legendItem = document.createElement('div');
            legendItem.className = 'legend-item';
            legendItem.innerHTML = `
                <svg width="20" height="2" class="${rel.class}" style="margin-right: 8px;">
                    <line x1="0" y1="1" x2="20" y2="1" stroke="#999"></line>
                </svg>
                <span>${rel.label}</span>
            `;
            legendContainer.appendChild(legendItem);
        });
    },
    
    // Populate filter dropdowns
    populateFilters: function(data) {
        // Category filter
        const categoryFilter = document.getElementById('categoryFilter');
        if (categoryFilter) {
            // Extract unique categories
            const categories = [];
            data.systems.forEach(system => {
                if (system.category && !categories.some(c => c.slug === system.category.slug)) {
                    categories.push(system.category);
                }
            });
            
            // Sort categories alphabetically
            categories.sort((a, b) => a.name.localeCompare(b.name));
            
            // Add options
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.slug;
                option.textContent = category.name;
                categoryFilter.appendChild(option);
            });
            
            // Add event listener
            categoryFilter.addEventListener('change', () => {
                this.filterSystems();
            });
        }
        
        // Status filter
        const statusFilter = document.getElementById('statusFilter');
        if (statusFilter) {
            // Extract unique statuses
            const statuses = [];
            data.systems.forEach(system => {
                if (system.status && !statuses.some(s => s.slug === system.status.slug)) {
                    statuses.push(system.status);
                }
            });
            
            // Sort statuses alphabetically
            statuses.sort((a, b) => a.name.localeCompare(b.name));
            
            // Add options
            statuses.forEach(status => {
                const option = document.createElement('option');
                option.value = status.slug;
                option.textContent = status.name;
                statusFilter.appendChild(option);
            });
            
            // Add event listener
            statusFilter.addEventListener('change', () => {
                this.filterSystems();
            });
        }
        
        // SSO filter
        const ssoFilter = document.getElementById('ssoFilter');
        if (ssoFilter) {
            // Extract unique SSO systems
            const ssoSystems = new Set();
            data.systems.forEach(system => {
                const ssoLinks = data.links.filter(link => 
                    link.type === 'provides_data_to' && 
                    link.target.id === system.id && 
                    link.source.category && 
                    link.source.category.slug === 'identity'
                );
                
                if (ssoLinks.length > 0) {
                    ssoLinks.forEach(link => {
                        ssoSystems.add(link.source);
                    });
                }
            });
            
            // Convert to array and sort
            const ssoArray = Array.from(ssoSystems);
            ssoArray.sort((a, b) => a.name.localeCompare(b.name));
            
            // Add options
            ssoArray.forEach(ssoSystem => {
                const option = document.createElement('option');
                option.value = ssoSystem.id;
                option.textContent = ssoSystem.name;
                ssoFilter.appendChild(option);
            });
            
            // Add event listener
            ssoFilter.addEventListener('change', () => {
                this.filterSystems();
            });
        }
        
        // Host filter
        const hostFilter = document.getElementById('hostFilter');
        if (hostFilter) {
            // Extract unique host systems
            const hostSystems = new Set();
            data.systems.forEach(system => {
                if (system.category && system.category.slug === 'server') {
                    hostSystems.add(system);
                }
            });
            
            // Convert to array and sort
            const hostArray = Array.from(hostSystems);
            hostArray.sort((a, b) => a.name.localeCompare(b.name));
            
            // Add options
            hostArray.forEach(hostSystem => {
                const option = document.createElement('option');
                option.value = hostSystem.id;
                option.textContent = hostSystem.name;
                hostFilter.appendChild(option);
            });
            
            // Add event listener
            hostFilter.addEventListener('change', () => {
                this.filterSystems();
            });
        }
    },
    
    // Apply filters to systems
    filterSystems: function() {
        // Get filter values
        const categoryValue = document.getElementById('categoryFilter')?.value || '';
        const statusValue = document.getElementById('statusFilter')?.value || '';
        const ssoValue = document.getElementById('ssoFilter')?.value || '';
        const hostValue = document.getElementById('hostFilter')?.value || '';
        
        // If no filters active, show all
        if (!categoryValue && !statusValue && !ssoValue && !hostValue) {
            d3.selectAll(".system-node").style("opacity", 1);
            d3.selectAll(".system-label").style("opacity", 1);
            d3.selectAll(".label-background").style("opacity", 1);
            d3.selectAll(".connection").style("opacity", 0.6);
            return;
        }
        
        // Get all nodes and links
        const nodes = d3.selectAll(".system-node");
        const labels = d3.selectAll(".system-label");
        const backgrounds = d3.selectAll(".label-background");
        const connections = d3.selectAll(".connection");
        
        // Fade everything initially
        nodes.style("opacity", 0.2);
        labels.style("opacity", 0.2);
        backgrounds.style("opacity", 0.2);
        connections.style("opacity", 0.1);
        
        // Filter systems based on criteria
        const matchingSystems = this.data.systems.filter(system => {
            let matches = true;
            
            if (categoryValue && (!system.category || system.category.slug !== categoryValue)) {
                matches = false;
            }
            
            if (statusValue && (!system.status || system.status.slug !== statusValue)) {
                matches = false;
            }
            
            if (ssoValue) {
                if (ssoValue === 'none') {
                    // Check if system has no SSO dependencies
                    const hasSsoDependency = this.data.links.some(link => 
                        link.type === 'provides_data_to' && 
                        link.target.id === system.id && 
                        link.source.category && 
                        link.source.category.slug === 'identity'
                    );
                    if (hasSsoDependency) {
                        matches = false;
                    }
                } else {
                    // Check if system depends on the selected SSO system
                    const dependsOnSelectedSso = this.data.links.some(link => 
                        link.type === 'provides_data_to' && 
                        link.target.id === system.id && 
                        link.source.id === parseInt(ssoValue)
                    );
                    if (!dependsOnSelectedSso) {
                        matches = false;
                    }
                }
            }
            
            if (hostValue) {
                if (hostValue === 'none') {
                    // Check if system has no hosting dependencies
                    const hasHostingDependency = this.data.links.some(link => 
                        link.type === 'depends_on' && 
                        link.target.id === system.id && 
                        link.source.category && 
                        link.source.category.slug === 'server'
                    );
                    if (hasHostingDependency) {
                        matches = false;
                    }
                } else {
                    // Check if system depends on the selected host system
                    const dependsOnSelectedHost = this.data.links.some(link => 
                        link.type === 'depends_on' && 
                        link.target.id === system.id && 
                        link.source.id === parseInt(hostValue)
                    );
                    if (!dependsOnSelectedHost) {
                        matches = false;
                    }
                }
            }
            
            return matches;
        });
        
        // Highlight matching systems
        matchingSystems.forEach(system => {
            d3.select(`#system-${system.id}`).style("opacity", 1);
            d3.select(`#label-${system.id}`).style("opacity", 1);
            d3.select(`#bg-${system.id}`).style("opacity", 1);
            
            // Highlight connections between matching systems
            this.data.links.forEach(link => {
                if (
                    (link.source.id === system.id && matchingSystems.some(s => s.id === link.target.id)) ||
                    (link.target.id === system.id && matchingSystems.some(s => s.id === link.source.id))
                ) {
                    d3.select(`#connection-${link.source.id}-${link.target.id}`).style("opacity", 0.8);
                }
            });
        });
    },
    
    // Identify and position orphaned nodes (nodes with no connections)
    identifyAndPositionOrphanedNodes: function() {
        // Find nodes with no connections
        const connectedNodeIds = new Set();
        
        // Add all nodes that are part of a relationship
        this.data.links.forEach(link => {
            connectedNodeIds.add(link.source.id || link.source);
            connectedNodeIds.add(link.target.id || link.target);
        });
        
        // Identify orphaned nodes
        const orphanedNodes = this.data.systems.filter(system => !connectedNodeIds.has(system.id));
        
        if (orphanedNodes.length > 0) {
            console.log(`Found ${orphanedNodes.length} orphaned nodes`);
            
            // Find the average y position of connected nodes to position orphans below them
            let sumY = 0;
            let count = 0;
            let maxY = -Infinity;
            
            this.data.systems.forEach(system => {
                if (connectedNodeIds.has(system.id)) {
                    sumY += system.y || 0;
                    count++;
                    maxY = Math.max(maxY, system.y || 0);
                }
            });
            
            const containerWidth = document.getElementById('vizDiagram').clientWidth;
            const averageY = count > 0 ? sumY / count : containerWidth / 2;
            const bottomY = Math.max(maxY + 100, averageY + 200); // Position below the main group
            
            // Position orphaned nodes in a line at the bottom
            const orphanSpacing = containerWidth / (orphanedNodes.length + 1);
            
            orphanedNodes.forEach((node, index) => {
                node.fx = (index + 1) * orphanSpacing;
                node.fy = bottomY;
                
                // Apply the position to the simulation
                const simNode = this.simulation.nodes().find(n => n.id === node.id);
                if (simNode) {
                    simNode.fx = node.fx;
                    simNode.fy = node.fy;
                }
            });
            
            // Restart simulation to apply changes
            this.simulation.alpha(0.3).restart();
        }
    },
    
    // Drag functions
    dragStarted: function(event, d) {
        if (!event.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    },
    
    dragged: function(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    },
    
    dragEnded: function(event, d) {
        if (!event.active) this.simulation.alphaTarget(0);
        // Keep position fixed to maintain the user's arrangement
    },
    
    // Center the view on a specific node
    centerOnNode: function(node) {
        if (!node || !this.zoomInstance) return;
        
        const containerWidth = document.getElementById('vizDiagram').clientWidth;
        const containerHeight = document.getElementById('vizDiagram').clientHeight;
        const scale = 1.5; // Zoom in a bit when centering
        
        const transform = d3.zoomIdentity
            .translate(containerWidth/2 - node.x * scale, containerHeight/2 - node.y * scale)
            .scale(scale);
        
        d3.select("#vizDiagram svg").transition()
            .duration(750)
            .call(this.zoomInstance.transform, transform);
    },
    
    // Handle search
    handleSearch: function(searchTerm) {
        const node = d3.selectAll(".system-node");
        const link = d3.selectAll(".connection");
        const label = d3.selectAll(".system-label");
        const labelBackground = d3.selectAll(".label-background");
        
        if (searchTerm.length < 2) {
            // Reset all highlights if search is cleared
            node.style("opacity", 1).classed("clicked", false).classed("highlighted", false);
            link.style("opacity", 0.6).classed("connection-highlighted", false);
            label.style("opacity", 1);
            labelBackground.style("opacity", 1);
            this.hideInfoPanel();
            return;
        }
        
        // Fade out all nodes and links
        node.style("opacity", 0.2);
        label.style("opacity", 0.2);
        labelBackground.style("opacity", 0.2);
        link.style("opacity", 0.1);
        
        // Highlight matching nodes and their connections
        const matchingNodes = this.data.systems.filter(system => 
            system.name.toLowerCase().includes(searchTerm));
            
        matchingNodes.forEach(system => {
            // Highlight the node
            d3.select(`#system-${system.id}`).style("opacity", 1);
            d3.select(`#label-${system.id}`).style("opacity", 1);
            d3.select(`#bg-${system.id}`).style("opacity", 1);
            
            // Highlight connections
            this.data.links.forEach(link => {
                if (link.source.id === system.id || link.target.id === system.id) {
                    d3.select(`#connection-${link.source.id}-${link.target.id}`).style("opacity", 0.8);
                    
                    // Highlight connected nodes
                    const connectedId = link.source.id === system.id ? link.target.id : link.source.id;
                    d3.select(`#system-${connectedId}`).style("opacity", 0.7);
                    d3.select(`#label-${connectedId}`).style("opacity", 0.7);
                    d3.select(`#bg-${connectedId}`).style("opacity", 0.7);
                }
            });
        });
        
        // If only one match, highlight it fully and center on it
        if (matchingNodes.length === 1) {
            this.highlightNode(matchingNodes[0].id);
        }
    },
    
    // Reset the visualization to its original state
    reset: function() {
        // Clear search and reset visibility
        const node = d3.selectAll(".system-node");
        const link = d3.selectAll(".connection");
        const label = d3.selectAll(".system-label");
        const labelBackground = d3.selectAll(".label-background");
        
        // Reset all highlights
        node.style("opacity", 1).classed("clicked", false).classed("highlighted", false);
        link.style("opacity", 0.6).classed("connection-highlighted", false);
        label.style("opacity", 1);
        labelBackground.style("opacity", 1);
        
        // Hide info panel
        this.hideInfoPanel();
        
        // Reset zoom and position
        d3.select("#vizDiagram svg").transition().duration(750).call(
            this.zoomInstance.transform, d3.zoomIdentity
        );
        
        // Reset filters if they exist
        const filters = ['categoryFilter', 'statusFilter', 'ssoFilter', 'hostFilter'];
        filters.forEach(filterId => {
            const filter = document.getElementById(filterId);
            if (filter) filter.value = '';
        });
        
        // Release fixed positions and restart simulation
        if (this.simulation) {
            // Release fixed positions
            this.data.systems.forEach(system => {
                system.fx = null;
                system.fy = null;
            });
            
            // Restart simulation with alpha
            this.simulation
                .alpha(0.8)
                .restart();
            
            // Position orphaned nodes after a slight delay
            setTimeout(() => this.identifyAndPositionOrphanedNodes(), 500);
            
            // After simulation stabilizes, fit view
            setTimeout(() => this.fitView(), 2000);
        }
    },
    
    // Optimize the layout to better distribute nodes
    optimizeLayout: function() {
        if (!this.simulation) return;
        
        // Release fixed positions first
        this.data.systems.forEach(system => {
            system.fx = null;
            system.fy = null;
        });
        
        const containerWidth = document.getElementById('vizDiagram').clientWidth;
        const containerHeight = document.getElementById('vizDiagram').clientHeight;
        
        // Adopt a scalable approach based on node count
        const nodeCount = this.data.systems.length;
        // Use a much larger multiplier to create more space
        const optimalSpread = Math.sqrt((containerWidth * containerHeight * 3) / nodeCount); // 3x the area
        
        // Increase repulsion temporarily to spread nodes apart
        this.simulation.force("charge", d3.forceManyBody().strength(-optimalSpread * 5)); // Much stronger repulsion
        
        // Increase link distance temporarily
        this.simulation.force("link", d3.forceLink().id(d => d.id).distance(optimalSpread * 1.5).links(this.data.links));
        
        // Run simulation at high temperature
        this.simulation.alpha(1).restart();
        
        // Position orphaned nodes after the main layout has started
        setTimeout(() => {
            this.identifyAndPositionOrphanedNodes();
        }, 1000);
        
        // Reset forces after some time, but keep stronger spacing
        setTimeout(() => {
            const nodeCount = this.data.systems.length;
            const totalArea = containerWidth * containerHeight * 0.8;
            const areaPerNode = totalArea / nodeCount;
            const optimalDistance = Math.sqrt(areaPerNode);
            
            this.simulation.force("charge", d3.forceManyBody().strength(-optimalDistance * 4));
            this.simulation.force("link", d3.forceLink().id(d => d.id).distance(optimalDistance * 2).links(this.data.links));
            this.simulation.alpha(0.3).restart();
            
            // Position orphaned nodes again after force adjustments
            this.identifyAndPositionOrphanedNodes();
            
            // Fit all nodes in view
            setTimeout(() => this.fitView(), 500);
        }, 2000);
    },
    
    // Fit all nodes in view
    fitView: function() {
        if (!this.data || !this.zoomInstance) return;
        
        const svg = d3.select("#vizDiagram svg");
        if (svg.empty()) return;
        
        // Find the bounding box of all nodes
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        
        this.data.systems.forEach(system => {
            minX = Math.min(minX, system.x || 0);
            minY = Math.min(minY, system.y || 0);
            maxX = Math.max(maxX, system.x || 0);
            maxY = Math.max(maxY, system.y || 0);
        });
        
        // Add padding
        const padding = 50;
        minX -= padding;
        minY -= padding;
        maxX += padding;
        maxY += padding;
        
        // Calculate scale to fit all nodes
        const containerWidth = document.getElementById('vizDiagram').clientWidth;
        const containerHeight = document.getElementById('vizDiagram').clientHeight;
        const dx = maxX - minX;
        const dy = maxY - minY;
        const scale = Math.min(containerWidth / dx, containerHeight / dy, 0.8); // Use no more than 80% zoom
        
        // Calculate center of the bounding box
        const centerX = (minX + maxX) / 2;
        const centerY = (minY + maxY) / 2;
        
        // Create transform
        const transform = d3.zoomIdentity
            .translate(containerWidth/2 - centerX * scale, containerHeight/2 - centerY * scale)
            .scale(scale);
            
        // Apply transform with animation
        svg.transition()
            .duration(750)
            .call(this.zoomInstance.transform, transform);
    },
    
    // Zoom functions
    zoomIn: function() {
        const svg = d3.select("#vizDiagram svg");
        if (svg.empty() || !this.zoomInstance) return;
        
        const currentTransform = d3.zoomTransform(svg.node());
        const newScale = currentTransform.k * 1.5;
        
        if (newScale <= this.zoomInstance.scaleExtent()[1]) { // Check maximum zoom level
            svg.transition().duration(300).call(
                this.zoomInstance.transform, 
                d3.zoomIdentity
                    .translate(currentTransform.x, currentTransform.y)
                    .scale(newScale)
            );
        }
    },
    
    zoomOut: function() {
        const svg = d3.select("#vizDiagram svg");
        if (svg.empty() || !this.zoomInstance) return;
        
        const currentTransform = d3.zoomTransform(svg.node());
        const newScale = currentTransform.k / 1.5;
        
        if (newScale >= this.zoomInstance.scaleExtent()[0]) { // Check minimum zoom level
            svg.transition().duration(300).call(
                this.zoomInstance.transform, 
                d3.zoomIdentity
                    .translate(currentTransform.x, currentTransform.y)
                    .scale(newScale)
            );
        }
    },
    
    centerView: function() {
        // Reset zoom to show all nodes
        this.fitView();
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
        const svg = d3.select("#vizDiagram svg");
        if (svg.empty()) return;
        
        if (document.fullscreenElement === document.getElementById('vizDiagram')) {
            // Get actual fullscreen dimensions
            const fsWidth = window.innerWidth;
            const fsHeight = window.innerHeight;
            
            // Update SVG dimensions for fullscreen
            svg.attr('width', fsWidth)
               .attr('height', fsHeight);
            
            // Update simulation center force if applicable
            if (this.simulation) {
                this.simulation.force('center', d3.forceCenter(fsWidth/2, fsHeight/2));
                this.simulation.alpha(0.3).restart();
            }
        } else {
            // Reset to original dimensions
            const containerWidth = document.getElementById('vizDiagram').clientWidth;
            const containerHeight = document.getElementById('vizDiagram').clientHeight;
            
            svg.attr('width', containerWidth)
               .attr('height', containerHeight);
            
            // Reset simulation center if applicable
            if (this.simulation) {
                this.simulation.force('center', d3.forceCenter(containerWidth/2, containerHeight/2));
                this.simulation.alpha(0.3).restart();
            }
        }
        
        // Update mini-map and indicators if applicable
        this.updateMiniMap();
        this.updateOffscreenIndicatorPositions();
    },
    
    // Handle window resize
    handleResize: function() {
        const svg = d3.select("#vizDiagram svg");
        if (svg.empty()) return;
        
        const containerWidth = document.getElementById('vizDiagram').clientWidth;
        const containerHeight = document.getElementById('vizDiagram').clientHeight;
        
        svg.attr('width', containerWidth)
           .attr('height', containerHeight);
           
        // Update simulation center if applicable
        if (this.simulation) {
            this.simulation.force('center', d3.forceCenter(containerWidth/2, containerHeight/2));
            // Don't restart simulation unless needed
        }
        
        // Update mini-map and indicators if applicable
        this.updateMiniMap();
        this.updateOffscreenIndicatorPositions();
    },
    
    // Export functions
    exportSVG: function() {
        const svg = document.querySelector('#vizDiagram svg');
        if (!svg) return;
        
        // Clone the SVG to modify it without affecting the display
        const clonedSvg = svg.cloneNode(true);
        
        // Add any necessary styles
        const styleElement = document.createElement('style');
        styleElement.textContent = `
            .system-node { stroke-width: 2px; }
            .system-label { font-size: 10px; text-anchor: middle; font-weight: bold; }
            .label-background { fill: white; fill-opacity: 0.8; stroke: #ddd; stroke-width: 0.5; }
            .connection { stroke: #999; stroke-width: 1.5px; fill: none; }
            .connection-depends_on { stroke-dasharray: none; }
            .connection-provides_data_to { stroke-dasharray: 5, 3; }
            .connection-integrates_with { stroke-dasharray: 1, 3; }
            .highlighted { stroke-width: 3px; stroke: #ff5722; }
        `;
        clonedSvg.appendChild(styleElement);
        
        // Create a blob
        const svgData = new XMLSerializer().serializeToString(clonedSvg);
        const blob = new Blob([svgData], { type: 'image/svg+xml' });
        
        // Create a download link
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `system-relationships-${new Date().toISOString().split('T')[0]}.svg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    },
    
    exportPNG: function() {
        const svg = document.querySelector('#vizDiagram svg');
        if (!svg) return;
        
        // Create a canvas element
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Set dimensions
        const svgWidth = svg.width.baseVal.value;
        const svgHeight = svg.height.baseVal.value;
        
        // For higher resolution export
        const scale = 2;
        canvas.width = svgWidth * scale;
        canvas.height = svgHeight * scale;
        ctx.scale(scale, scale);
        
        // Create an image from the SVG
        const svgData = new XMLSerializer().serializeToString(svg);
        const img = new Image();
        
        // Convert SVG to a data URL
        const svgBlob = new Blob([svgData], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(svgBlob);
        
        img.onload = function() {
            // Draw white background
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, svgWidth, svgHeight);
            
            // Draw the image
            ctx.drawImage(img, 0, 0, svgWidth, svgHeight);
            
            // Convert to PNG and trigger download
            canvas.toBlob(function(blob) {
                const pngUrl = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = pngUrl;
                link.download = `system-relationships-${new Date().toISOString().split('T')[0]}.png`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(pngUrl);
                URL.revokeObjectURL(url);
            }, 'image/png');
        };
        
        img.src = url;
    },
    
    exportJSON: function() {
        if (!this.data) return;
        
        const jsonData = JSON.stringify(this.data, null, 2);
        const blob = new Blob([jsonData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `system-relationships-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
};