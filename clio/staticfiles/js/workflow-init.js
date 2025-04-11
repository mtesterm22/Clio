// workflow-init.js
// This script ensures proper JSON parsing of workflow data from Django templates

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('workflow-designer-root');
    
    if (container) {
      try {
        // Parse workflow data from the data attribute
        const workflowDataStr = container.getAttribute('data-workflow-data');
        
        if (workflowDataStr) {
          // Check if data is already a JSON string or needs parsing
          try {
            // Try to parse as JSON string
            const parsedData = JSON.parse(workflowDataStr);
            
            // Normalize the nodes and edges if they're strings or empty
            if (typeof parsedData.nodes === 'string') {
              parsedData.nodes = parsedData.nodes ? JSON.parse(parsedData.nodes) : [];
            } else if (!parsedData.nodes) {
              parsedData.nodes = [];
            }
            
            if (typeof parsedData.edges === 'string') {
              parsedData.edges = parsedData.edges ? JSON.parse(parsedData.edges) : [];
            } else if (!parsedData.edges) {
              parsedData.edges = [];
            }
            
            // Store back as a properly formatted JSON string
            container.setAttribute('data-workflow-data', JSON.stringify(parsedData));
          } catch (e) {
            console.error('Error parsing workflow data:', e);
            // Set default empty workflow
            container.setAttribute('data-workflow-data', JSON.stringify({
              nodes: [],
              edges: [],
              version: 1
            }));
          }
        }
        
        // Systems and scripts data
        ['data-systems', 'data-scripts'].forEach(attr => {
          const dataStr = container.getAttribute(attr);
          if (dataStr) {
            try {
              // Try to parse if not already JSON
              if (dataStr.charAt(0) !== '[') {
                const parsedData = JSON.parse(dataStr);
                container.setAttribute(attr, JSON.stringify(parsedData));
              }
            } catch (e) {
              console.error(`Error parsing ${attr}:`, e);
              container.setAttribute(attr, '[]');
            }
          } else {
            container.setAttribute(attr, '[]');
          }
        });
        
      } catch (error) {
        console.error('Error initializing workflow designer:', error);
      }
    }
  });