// diagnostic-workflow-designer.js

// Display diagnostic information immediately when the file loads
console.log("Diagnostic script loaded");

document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM fully loaded");
  
  // Check for the workflow designer container
  const container = document.getElementById('workflow-designer-root');
  if (!container) {
    console.error("Could not find workflow-designer-root element");
    return;
  }
  
  console.log("Container found:", container);
  console.log("Container dimensions:", {
    width: container.offsetWidth,
    height: container.offsetHeight
  });
  
  // Log data attributes
  console.log("Data attributes:");
  console.log("- workflow-data:", container.getAttribute('data-workflow-data'));
  console.log("- systems:", container.getAttribute('data-systems'));
  console.log("- scripts:", container.getAttribute('data-scripts'));
  console.log("- save-url:", container.getAttribute('data-save-url'));
  console.log("- detail-url:", container.getAttribute('data-detail-url'));
  
  // Check for CSRF token
  const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
  console.log("CSRF token present:", !!csrfToken);
  
  // Check for React and ReactDOM
  console.log("React available:", typeof React !== 'undefined');
  console.log("ReactDOM available:", typeof ReactDOM !== 'undefined');
  
  // Create a minimal version of the workflow designer
  try {
    console.log("Creating minimal workflow designer");
    
    // Create simple HTML structure
    container.innerHTML = `
      <div style="display: flex; height: 100%;">
        <div style="width: 250px; background-color: white; border-right: 1px solid #e5e7eb; padding: 16px; overflow-y: auto;">
          <h2 style="margin-bottom: 16px; font-weight: bold; font-size: 18px;">Workflow Elements</h2>
          <div style="margin-bottom: 16px;">
            <h3 style="margin-bottom: 8px; font-size: 14px; color: #6b7280;">Control Nodes</h3>
            <div 
              style="border: 2px solid #10b981; border-radius: 6px; padding: 8px; margin-bottom: 8px; background-color: white; cursor: move;"
              draggable="true"
              id="drag-start"
            >
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 500;">Start</span>
                <span style="font-size: 12px; padding: 2px 8px; background-color: #d1fae5; color: #047857; border-radius: 9999px;">Control</span>
              </div>
            </div>
            <div 
              style="border: 2px solid #ef4444; border-radius: 6px; padding: 8px; margin-bottom: 8px; background-color: white; cursor: move;"
              draggable="true"
              id="drag-end"
            >
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 500;">End</span>
                <span style="font-size: 12px; padding: 2px 8px; background-color: #fee2e2; color: #b91c1c; border-radius: 9999px;">Control</span>
              </div>
            </div>
          </div>
        </div>
        
        <div style="flex: 1; display: flex; flex-direction: column;">
          <div style="padding: 16px; background-color: #f3f4f6; border-bottom: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center;">
            <h1 style="font-size: 20px; font-weight: bold;">Test Workflow</h1>
            <div>
              <button id="save-button" style="background-color: #3b82f6; color: white; padding: 8px 16px; border-radius: 6px; margin-right: 8px;">Save Workflow</button>
              <a id="exit-link" style="border: 1px solid #d1d5db; background-color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; color: #374151;">Exit</a>
            </div>
          </div>
          
          <div style="flex: 1; position: relative; background-color: #f9fafb; overflow: hidden;" id="canvas-container">
            <svg width="100%" height="100%" id="canvas-svg" style="position: absolute; top: 0; left: 0; background-size: 20px 20px; background-image: linear-gradient(to right, #f0f0f0 1px, transparent 1px), linear-gradient(to bottom, #f0f0f0 1px, transparent 1px);">
              <!-- SVG content will go here -->
            </svg>
          </div>
        </div>
        
        <div style="width: 250px; background-color: white; border-left: 1px solid #e5e7eb; padding: 16px; overflow-y: auto;">
          <h3 style="font-weight: bold; margin-bottom: 16px;">Properties</h3>
          <p style="color: #6b7280; font-style: italic;">Select a node to edit its properties</p>
        </div>
      </div>
    `;
    
    console.log("HTML structure created");
    
    // Add simple drag and drop functionality
    const canvasContainer = document.getElementById('canvas-svg');
    const startDragElement = document.getElementById('drag-start');
    const endDragElement = document.getElementById('drag-end');
    
    if (startDragElement && endDragElement && canvasContainer) {
      console.log("Setting up drag and drop handlers");
      
      // Drag start handlers
      startDragElement.addEventListener('dragstart', function(e) {
        console.log("Drag started: Start node");
        e.dataTransfer.setData('nodeType', 'start');
      });
      
      endDragElement.addEventListener('dragstart', function(e) {
        console.log("Drag started: End node");
        e.dataTransfer.setData('nodeType', 'end');
      });
      
      // Canvas drop handler
      document.getElementById('canvas-container').addEventListener('dragover', function(e) {
        e.preventDefault();
      });
      
      document.getElementById('canvas-container').addEventListener('drop', function(e) {
        e.preventDefault();
        console.log("Drop event occurred");
        
        const nodeType = e.dataTransfer.getData('nodeType');
        console.log("Node type:", nodeType);
        
        if (nodeType) {
          const rect = e.currentTarget.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;
          
          console.log(`Creating node at position: (${x}, ${y})`);
          
          const svgNamespace = "http://www.w3.org/2000/svg";
          
          // Create group element
          const group = document.createElementNS(svgNamespace, "g");
          group.setAttribute("transform", `translate(${x}, ${y})`);
          
          // Create rectangle
          const rect1 = document.createElementNS(svgNamespace, "rect");
          rect1.setAttribute("width", "120");
          rect1.setAttribute("height", "40");
          rect1.setAttribute("rx", "8");
          rect1.setAttribute("ry", "8");
          
          if (nodeType === 'start') {
            rect1.setAttribute("fill", "#d1fae5");
            rect1.setAttribute("stroke", "#10b981");
          } else {
            rect1.setAttribute("fill", "#fee2e2");
            rect1.setAttribute("stroke", "#ef4444");
          }
          
          // Create text
          const text = document.createElementNS(svgNamespace, "text");
          text.setAttribute("x", "60");
          text.setAttribute("y", "20");
          text.setAttribute("text-anchor", "middle");
          text.setAttribute("dominant-baseline", "middle");
          text.setAttribute("fill", "#374151");
          text.textContent = nodeType === 'start' ? 'Start Workflow' : 'End Workflow';
          
          // Append elements
          group.appendChild(rect1);
          group.appendChild(text);
          canvasContainer.appendChild(group);
          
          console.log("Node created on canvas");
        }
      });
      
      // Button handlers
      document.getElementById('save-button').addEventListener('click', function() {
        console.log("Save button clicked");
        alert("Save functionality works!");
      });
      
      console.log("Event handlers set up successfully");
    } else {
      console.error("Could not find required elements for drag and drop");
    }
    
  } catch (error) {
    console.error("Error creating minimal workflow designer:", error);
  }
});