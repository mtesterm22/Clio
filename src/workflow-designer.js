// workflow-designer.js
import React, { useState, useRef, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

// Define constants for node dimensions (helps with consistent positioning)
const NODE_DIMENSIONS = {
  start: { width: 160, height: 40 },
  end: { width: 160, height: 40 },
  step: { width: 240, height: 100 },
  decision: { width: 192, height: 80 }
};

// Custom node types components
const StartNode = ({ data, position, id, selected, onSelect, onDrag }) => {
  const nodeRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  const handleMouseDown = (e) => {
    if (nodeRef.current) {
      e.stopPropagation(); // Prevent canvas drag
      
      // Set drag offset based on node position, not bounding rect
      setDragOffset({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
      
      setIsDragging(true);
      onSelect(id);
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      // Calculate new position based on original offset
      const newPosition = {
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y
      };
      
      onDrag(id, newPosition);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    }
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  return (
    <div
      ref={nodeRef}
      className={`absolute px-4 py-3 rounded-md border-2 border-green-500 bg-white w-40 cursor-move ${selected ? 'shadow-lg ring-2 ring-green-400' : ''}`}
      style={{ left: position.x, top: position.y }}
      onMouseDown={handleMouseDown}
    >
      <div className="flex justify-between items-center">
        <h3 className="font-bold text-green-600">{data.label}</h3>
        <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">Start</span>
      </div>
    </div>
  );
};

const EndNode = ({ data, position, id, selected, onSelect, onDrag }) => {
  const nodeRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  const handleMouseDown = (e) => {
    if (nodeRef.current) {
      e.stopPropagation(); // Prevent canvas drag
      
      // Set drag offset based on node position, not bounding rect
      setDragOffset({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
      
      setIsDragging(true);
      onSelect(id);
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      // Calculate new position based on original offset
      const newPosition = {
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y
      };
      
      onDrag(id, newPosition);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    }
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  return (
    <div
      ref={nodeRef}
      className={`absolute px-4 py-3 rounded-md border-2 border-red-500 bg-white w-40 cursor-move ${selected ? 'shadow-lg ring-2 ring-red-400' : ''}`}
      style={{ left: position.x, top: position.y }}
      onMouseDown={handleMouseDown}
    >
      <div className="flex justify-between items-center">
        <h3 className="font-bold text-red-600">{data.label}</h3>
        <span className="text-xs px-2 py-1 bg-red-100 text-red-800 rounded-full">End</span>
      </div>
    </div>
  );
};

const StepNode = ({ data, position, id, selected, onSelect, onDrag }) => {
  const nodeRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  const handleMouseDown = (e) => {
    if (nodeRef.current) {
      e.stopPropagation(); // Prevent canvas drag
      
      // Set drag offset based on node position, not bounding rect
      setDragOffset({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
      
      setIsDragging(true);
      onSelect(id);
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      // Calculate new position based on original offset
      const newPosition = {
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y
      };
      
      onDrag(id, newPosition);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    }
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  return (
    <div
      ref={nodeRef}
      className={`absolute px-4 py-3 rounded-md border-2 border-blue-500 bg-white w-60 cursor-move ${selected ? 'shadow-lg ring-2 ring-blue-400' : ''}`}
      style={{ left: position.x, top: position.y }}
      onMouseDown={handleMouseDown}
    >
      <div className="border-b pb-2 mb-2 flex justify-between items-center">
        <h3 className="font-bold text-blue-600">{data.label}</h3>
        <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">Step</span>
      </div>
      <div className="text-sm text-gray-700 mb-2">{data.description}</div>
      {data.system && (
        <div className="flex items-center mb-2">
          <span className="text-xs px-2 py-1 rounded-full mr-1 bg-indigo-100 text-indigo-800">
            {data.system}
          </span>
        </div>
      )}
      {data.script && (
        <div className="flex items-center mb-2">
          <span className="text-xs px-2 py-1 rounded-full mr-1 bg-purple-100 text-purple-800">
            {data.script}
          </span>
        </div>
      )}
    </div>
  );
};

const DecisionNode = ({ data, position, id, selected, onSelect, onDrag }) => {
  const nodeRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  const handleMouseDown = (e) => {
    if (nodeRef.current) {
      e.stopPropagation(); // Prevent canvas drag
      
      // Set drag offset based on node position, not bounding rect
      setDragOffset({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
      
      setIsDragging(true);
      onSelect(id);
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      // Calculate new position based on original offset
      const newPosition = {
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y
      };
      
      onDrag(id, newPosition);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    }
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  return (
    <div
      ref={nodeRef}
      className={`absolute px-4 py-3 rounded-md border-2 border-yellow-500 bg-white w-48 cursor-move ${selected ? 'shadow-lg ring-2 ring-yellow-400' : ''}`}
      style={{ left: position.x, top: position.y }}
      onMouseDown={handleMouseDown}
    >
      <div className="border-b pb-2 mb-2 flex justify-between items-center">
        <h3 className="font-bold text-yellow-600">{data.label}</h3>
        <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full">Decision</span>
      </div>
      <div className="text-sm text-gray-700">{data.description}</div>
    </div>
  );
};

// Edge (connection) component
const Edge = ({ sourcePosition, targetPosition, label, selected }) => {
  // Calculate the path for the edge
  const deltaX = targetPosition.x - sourcePosition.x;
  const deltaY = targetPosition.y - sourcePosition.y;
  const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);

  // Calculate path for a bezier curve
  const controlPointOffsetX = distance * 0.2;
  const controlPointOffsetY = distance * 0.1;
  const controlPoint1 = {
    x: sourcePosition.x + controlPointOffsetX,
    y: sourcePosition.y + (deltaY < 0 ? -controlPointOffsetY : controlPointOffsetY)
  };
  const controlPoint2 = {
    x: targetPosition.x - controlPointOffsetX,
    y: targetPosition.y + (deltaY < 0 ? controlPointOffsetY : -controlPointOffsetY)
  };

  // Calculate the position for the label (midpoint of the path)
  const midPoint = {
    x: (sourcePosition.x + targetPosition.x) / 2,
    y: (sourcePosition.y + targetPosition.y) / 2
  };

  // Calculate the angle for the arrow
  const angle = Math.atan2(deltaY, deltaX);
  const arrowSize = 8;
  const arrowPoint1 = {
    x: targetPosition.x - arrowSize * Math.cos(angle - Math.PI / 6),
    y: targetPosition.y - arrowSize * Math.sin(angle - Math.PI / 6)
  };
  const arrowPoint2 = {
    x: targetPosition.x - arrowSize * Math.cos(angle + Math.PI / 6),
    y: targetPosition.y - arrowSize * Math.sin(angle + Math.PI / 6)
  };

  return (
    <>
      <path
        d={`M${sourcePosition.x},${sourcePosition.y} C${controlPoint1.x},${controlPoint1.y} ${controlPoint2.x},${controlPoint2.y} ${targetPosition.x},${targetPosition.y}`}
        stroke={selected ? "#3b82f6" : "#999"}
        strokeWidth={selected ? 2 : 1.5}
        fill="none"
      />
      <polygon
        points={`${targetPosition.x},${targetPosition.y} ${arrowPoint1.x},${arrowPoint1.y} ${arrowPoint2.x},${arrowPoint2.y}`}
        fill={selected ? "#3b82f6" : "#999"}
      />
      {label && (
        <g transform={`translate(${midPoint.x}, ${midPoint.y})`}>
          <rect
            x="-20"
            y="-10"
            width={label.length * 8 + 10}
            height="20"
            fill="#f9fafb"
            stroke="#e5e7eb"
            rx="4"
            ry="4"
          />
          <text
            dominantBaseline="middle"
            textAnchor="middle"
            fontSize="12"
            fill="#4b5563"
          >
            {label}
          </text>
        </g>
      )}
    </>
  );
};

// Sidebar for adding new nodes
const Sidebar = ({ onDragStart }) => {
  const onDragStartHandler = (event, nodeType, data) => {
    event.dataTransfer.setData('application/reactflow', JSON.stringify({ type: nodeType, data }));
    event.dataTransfer.effectAllowed = 'move';
    if (typeof onDragStart === 'function') {
      onDragStart();
    }
  };

  return (
    <div style={{
      position: 'absolute',
      top: 0,
      left: 0,
      width: '16rem',
      height: '100%',
      backgroundColor: 'white',
      padding: '1rem',
      borderRight: '1px solid #e5e7eb',
      overflowY: 'auto',
      zIndex: 10
    }}>
      <h2 className="text-lg font-bold mb-4">Node Types</h2>
      
      <div className="mb-4">
        <h3 className="font-medium text-sm text-gray-500 mb-2">Workflow Control</h3>
        <div 
          className="border-2 border-green-500 rounded-md p-2 mb-2 bg-white cursor-move"
          onDragStart={(e) => onDragStartHandler(e, 'start', { label: 'Start Workflow' })}
          draggable
        >
          <div className="flex justify-between items-center">
            <span className="font-medium">Start</span>
            <span className="text-xs px-2 py-1 bg-green-100 text-green-600 rounded-full">Control</span>
          </div>
        </div>
        
        <div 
          className="border-2 border-red-500 rounded-md p-2 mb-2 bg-white cursor-move"
          onDragStart={(e) => onDragStartHandler(e, 'end', { label: 'End Workflow' })}
          draggable
        >
          <div className="flex justify-between items-center">
            <span className="font-medium">End</span>
            <span className="text-xs px-2 py-1 bg-red-100 text-red-600 rounded-full">Control</span>
          </div>
        </div>

        <div 
          className="border-2 border-yellow-500 rounded-md p-2 mb-2 bg-white cursor-move"
          onDragStart={(e) => onDragStartHandler(e, 'decision', { 
            label: 'Decision', 
            description: 'Conditional branching'
          })}
          draggable
        >
          <div className="flex justify-between items-center">
            <span className="font-medium">Decision</span>
            <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-600 rounded-full">Control</span>
          </div>
        </div>
      </div>

      <div>
        <h3 className="font-medium text-sm text-gray-500 mb-2">Steps</h3>
        <div 
          className="border-2 border-blue-500 rounded-md p-2 mb-2 bg-white cursor-move"
          onDragStart={(e) => onDragStartHandler(e, 'step', { 
            label: 'Manual Step', 
            description: 'Manual process step'
          })}
          draggable
        >
          <div className="flex justify-between items-center">
            <span className="font-medium">Manual Step</span>
            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-600 rounded-full">Step</span>
          </div>
        </div>

        <div 
          className="border-2 border-blue-500 rounded-md p-2 mb-2 bg-white cursor-move"
          onDragStart={(e) => onDragStartHandler(e, 'step', { 
            label: 'System Task', 
            description: 'Automated system task',
            system: 'Select System'
          })}
          draggable
        >
          <div className="flex justify-between items-center">
            <span className="font-medium">System Task</span>
            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-600 rounded-full">Step</span>
          </div>
        </div>

        <div 
          className="border-2 border-blue-500 rounded-md p-2 mb-2 bg-white cursor-move"
          onDragStart={(e) => onDragStartHandler(e, 'step', { 
            label: 'Script Execution', 
            description: 'Run a script',
            script: 'Select Script'
          })}
          draggable
        >
          <div className="flex justify-between items-center">
            <span className="font-medium">Script Task</span>
            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-600 rounded-full">Step</span>
          </div>
        </div>
      </div>
      
      <div className="mt-8 p-4 bg-blue-50 rounded-md">
        <h3 className="font-medium text-sm text-blue-800 mb-2">Help</h3>
        <p className="text-xs text-blue-600">
          Drag elements from this panel and drop them onto the canvas. Connect nodes by clicking the connection points.
        </p>
      </div>
    </div>
  );
};

// Properties Panel
const PropertiesPanel = ({ selectedNode, systemsList, scriptsList, updateNodeData, deleteNode }) => {
  if (!selectedNode) return (
    <div className="p-4">
      <p className="text-gray-500 italic">Select a node to edit its properties</p>
    </div>
  );

  return (
    <div className="p-4">
      <h3 className="font-bold mb-4">Node Properties</h3>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Label</label>
          <input
            type="text"
            value={selectedNode.data.label || ''}
            onChange={(e) => updateNodeData(selectedNode.id, 'label', e.target.value)}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          />
        </div>
        
        {(selectedNode.type === 'step' || selectedNode.type === 'decision') && (
          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              value={selectedNode.data.description || ''}
              onChange={(e) => updateNodeData(selectedNode.id, 'description', e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              rows="3"
            />
          </div>
        )}
        
        {selectedNode.type === 'step' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700">System</label>
              <select
                value={selectedNode.data.system_id || ''}
                onChange={(e) => {
                  const systemId = e.target.value;
                  const system = systemsList?.find(s => s.id == systemId);
                  updateNodeData(selectedNode.id, 'system_id', systemId);
                  updateNodeData(selectedNode.id, 'system', system ? system.name : '');
                }}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              >
                <option value="">None</option>
                {Array.isArray(systemsList) && systemsList.map(system => (
                  <option key={system.id} value={system.id}>{system.name}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Script</label>
              <select
                value={selectedNode.data.script_id || ''}
                onChange={(e) => {
                  const scriptId = e.target.value;
                  const script = scriptsList?.find(s => s.id == scriptId);
                  updateNodeData(selectedNode.id, 'script_id', scriptId);
                  updateNodeData(selectedNode.id, 'script', script ? script.name : '');
                }}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              >
                <option value="">None</option>
                {Array.isArray(scriptsList) && scriptsList.map(script => (
                  <option key={script.id} value={script.id}>{script.name}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Inputs</label>
              <textarea
                value={selectedNode.data.inputs || ''}
                onChange={(e) => updateNodeData(selectedNode.id, 'inputs', e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                rows="2"
                placeholder="Data required by this step"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Outputs</label>
              <textarea
                value={selectedNode.data.outputs || ''}
                onChange={(e) => updateNodeData(selectedNode.id, 'outputs', e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                rows="2"
                placeholder="Data produced by this step"
              />
            </div>
          </>
        )}
        
        <div className="pt-2">
          <button
            onClick={() => deleteNode(selectedNode.id)}
            className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
          >
            Delete Node
          </button>
        </div>
      </div>
    </div>
  );
};

// Connection Point Component - Handle connections between nodes
const ConnectionPoint = ({ node, type, onStartConnection, isActive }) => {
  // Get dimensions for this node type
  const dimensions = NODE_DIMENSIONS[node.type] || { width: 160, height: 40 };
  
  // Calculate position based on node type and connection type
  const getPosition = () => {
    // Position based on connection type (input at top, output at bottom)
    if (type === 'input') {
      return {
        x: node.position.x + dimensions.width / 2,
        y: node.position.y
      };
    } else { // output
      return {
        x: node.position.x + dimensions.width / 2,
        y: node.position.y + dimensions.height
      };
    }
  };
  
  // Get position for this connection point
  const position = getPosition();
  
  // Don't show input for start nodes or output for end nodes
  if ((node.type === 'start' && type === 'input') || 
      (node.type === 'end' && type === 'output')) {
    return null;
  }
  
  // Only show when active or the node is selected
  if (!isActive) return null;

  const handleClick = (e) => {
    e.stopPropagation();
    if (onStartConnection) {
      onStartConnection(node.id, type);
    }
  };
  
  return (
    <div 
      className="absolute w-3 h-3 rounded-full bg-white border-2 border-blue-500 cursor-pointer hover:bg-blue-200 z-10"
      style={{ 
        left: position.x - 6, 
        top: position.y - 6,
      }}
      onClick={handleClick}
    />
  );
};

// Active Connection Line - Shown when connecting nodes
const ActiveConnectionLine = ({ from, to }) => {
  if (!from || !to) return null;
  
  // Create a curved path between points
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  
  // Determine control points for bezier curve
  const midX = (from.x + to.x) / 2;
  
  // Draw different curve based on whether going up or down
  const path = `M${from.x},${from.y} C${midX},${from.y} ${midX},${to.y} ${to.x},${to.y}`;
  
  return (
    <path
      d={path}
      stroke="#3b82f6"
      strokeWidth="2"
      strokeDasharray="5,5"
      fill="none"
    />
  );
};

// Main workflow designer component
const WorkflowDesigner = () => {
  // Get data from container element
  const container = document.getElementById('workflow-designer-root');
  let workflowData = { nodes: [], edges: [], name: 'Workflow' };
  let systemsList = [];
  let scriptsList = [];
  let apiUrls = { save: '', detail: '' };
  
  if (container) {
    try {
      const workflowDataStr = container.getAttribute('data-workflow-data');
      const systemsStr = container.getAttribute('data-systems');
      const scriptsStr = container.getAttribute('data-scripts');
      const saveUrl = container.getAttribute('data-save-url') || '';
      const detailUrl = container.getAttribute('data-detail-url') || '';
      
      try {
        workflowData = JSON.parse(workflowDataStr || '{"nodes":[],"edges":[]}');
      } catch (e) {
        console.error('Error parsing workflow data:', e);
        workflowData = { nodes: [], edges: [], name: 'Workflow' };
      }
      
      try {
        systemsList = JSON.parse(systemsStr || '[]');
      } catch (e) {
        console.error('Error parsing systems list:', e);
        systemsList = [];
      }
      
      try {
        scriptsList = JSON.parse(scriptsStr || '[]');
      } catch (e) {
        console.error('Error parsing scripts list:', e);
        scriptsList = [];
      }
      
      apiUrls = { save: saveUrl, detail: detailUrl };
    } catch (e) {
      console.error('Error getting data from container:', e);
    }
  }
  
  const canvasRef = useRef(null);
  const [nodes, setNodes] = useState(workflowData.nodes || []);
  const [edges, setEdges] = useState(workflowData.edges || []);
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  
  // Connection state
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionSourceId, setConnectionSourceId] = useState(null);
  const [connectionSourceType, setConnectionSourceType] = useState(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Handle node selection
  const handleNodeSelect = (nodeId) => {
    console.log(`Selecting node: ${nodeId}`);
    const node = nodes.find(n => n.id === nodeId);
    setSelectedNode(node);
    setSelectedEdge(null);
  };

  // Handle node drag
  const handleNodeDrag = (nodeId, newPosition) => {
    setNodes(nodes.map(node => 
      node.id === nodeId ? { ...node, position: newPosition } : node
    ));
    setIsDirty(true);
  };

  // Update node data (from properties panel)
  const updateNodeData = (nodeId, key, value) => {
    setNodes(nodes.map(node => {
      if (node.id === nodeId) {
        return {
          ...node,
          data: {
            ...node.data,
            [key]: value,
          },
        };
      }
      return node;
    }));
    
    // Update selected node if it's the one being modified
    if (selectedNode && selectedNode.id === nodeId) {
      setSelectedNode({
        ...selectedNode,
        data: {
          ...selectedNode.data,
          [key]: value,
        },
      });
    }
    
    setIsDirty(true);
  };

  // Delete a node
  const deleteNode = (nodeId) => {
    setNodes(nodes.filter(node => node.id !== nodeId));
    setEdges(edges.filter(edge => edge.source !== nodeId && edge.target !== nodeId));
    setSelectedNode(null);
    setIsDirty(true);
  };

  // Get connection point position
  const getConnectionPointPosition = (nodeId, type) => {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return null;
    
    // Get dimensions for this node type
    const dimensions = NODE_DIMENSIONS[node.type] || { width: 160, height: 40 };
    
    // Position based on connection type (input at top, output at bottom)
    if (type === 'input') {
      return {
        x: node.position.x + dimensions.width / 2,
        y: node.position.y
      };
    } else { // output
      return {
        x: node.position.x + dimensions.width / 2,
        y: node.position.y + dimensions.height
      };
    }
  };

  // Handle dropping a new node on the canvas
  const handleDrop = (e) => {
    e.preventDefault();
    
    try {
      const jsonData = e.dataTransfer.getData('application/reactflow');
      if (!jsonData) {
        console.log('No valid drag data found');
        return;
      }
      
      const data = JSON.parse(jsonData);
      if (!data.type) {
        console.log('Invalid node data (missing type)');
        return;
      }
      
      const rect = canvasRef.current.getBoundingClientRect();
      const newPosition = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      };
      
      const newNode = {
        id: `${data.type}_${Date.now()}`,
        type: data.type,
        position: newPosition,
        data: data.data || {}
      };
      
      setNodes([...nodes, newNode]);
      setIsDirty(true);
      
      // Select the new node
      setSelectedNode(newNode);
    } catch (err) {
      console.error("Error adding new node:", err);
    }
  };

  // Handle drag over for drop to work
  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  // Handle canvas click (deselect items)
  const handleCanvasClick = (e) => {
    // Only deselect if clicking directly on the canvas, not a child element
    if (e.target === canvasRef.current) {
      setSelectedNode(null);
      setSelectedEdge(null);
      
      // Cancel active connection
      if (isConnecting) {
        setIsConnecting(false);
        setConnectionSourceId(null);
        setConnectionSourceType(null);
      }
    }
  };

  // Track mouse position for connection line
  const handleMouseMove = (e) => {
    if (isConnecting) {
      const rect = canvasRef.current.getBoundingClientRect();
      setMousePosition({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      });
    }
  };

  // Handle starting a connection
  const handleStartConnection = (nodeId, portType) => {
    console.log(`Start connection from: ${nodeId}, port: ${portType}`);
    setIsConnecting(true);
    setConnectionSourceId(nodeId);
    setConnectionSourceType(portType);
  };

  // Handle completing a connection
  const handleCompleteConnection = (targetId, targetType) => {
    console.log(`Complete connection to: ${targetId}, port: ${targetType}`);
    
    if (!isConnecting || !connectionSourceId || targetId === connectionSourceId) {
      setIsConnecting(false);
      setConnectionSourceId(null);
      setConnectionSourceType(null);
      return;
    }
    
    // Determine source and target based on connection types
    let source, target;
    
    if (connectionSourceType === 'output' && targetType === 'input') {
      // Normal flow: output → input
      source = connectionSourceId;
      target = targetId;
    } else if (connectionSourceType === 'input' && targetType === 'output') {
      // Reverse flow: input ← output
      source = targetId;
      target = connectionSourceId;
    } else {
      // Invalid connection (same types)
      console.log('Invalid connection: cannot connect same port types');
      setIsConnecting(false);
      setConnectionSourceId(null);
      setConnectionSourceType(null);
      return;
    }
    
    // Check if connection already exists
    const connectionExists = edges.some(edge => 
      edge.source === source && edge.target === target
    );
    
    if (!connectionExists) {
      const newEdge = {
        id: `e-${source}-${target}`,
        source,
        target
      };
      
      console.log('Adding new edge:', newEdge);
      setEdges([...edges, newEdge]);
      setIsDirty(true);
    }
    
    // Reset connection state
    setIsConnecting(false);
    setConnectionSourceId(null);
    setConnectionSourceType(null);
  };

  // Save workflow to Django backend
  const saveWorkflow = async () => {
    if (!isDirty) return;
    
    setIsSaving(true);
    
    try {
      // Get CSRF token
      const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
      
      if (!csrfToken) {
        console.error('CSRF token not found');
        setIsSaving(false);
        return;
      }
      
      const response = await fetch(apiUrls.save, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
          nodes,
          edges,
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setIsDirty(false);
        setSuccessMessage(data.message || 'Workflow saved successfully');
        
        // Hide success message after 3 seconds
        setTimeout(() => {
          setSuccessMessage('');
        }, 3000);
      } else {
        console.error('Error saving workflow:', data.message || 'Unknown error');
      }
    } catch (error) {
      console.error('Error saving workflow:', error);
    } finally {
      setIsSaving(false);
    }
  };

  // Render active connection line when connecting nodes
  const renderActiveConnectionLine = () => {
    if (!isConnecting || !connectionSourceId) return null;
    
    let sourcePosition;
    if (connectionSourceType === 'output') {
      sourcePosition = getConnectionPointPosition(connectionSourceId, 'output');
    } else {
      sourcePosition = getConnectionPointPosition(connectionSourceId, 'input');
    }
    
    if (!sourcePosition) return null;
    
    return (
      <svg className="absolute top-0 left-0 w-full h-full pointer-events-none" style={{ zIndex: 9 }}>
        <ActiveConnectionLine from={sourcePosition} to={mousePosition} />
      </svg>
    );
  };

  // Render all nodes with their connection points
  const renderNodes = () => {
    return nodes.map(node => {
      const isSelected = selectedNode && selectedNode.id === node.id;
      
      // Determine which component to use based on node type
      let NodeComponent;
      switch (node.type) {
        case 'start':
          NodeComponent = StartNode;
          break;
        case 'end':
          NodeComponent = EndNode;
          break;
        case 'step':
          NodeComponent = StepNode;
          break;
        case 'decision':
          NodeComponent = DecisionNode;
          break;
        default:
          return null;
      }
      
      return (
        <React.Fragment key={node.id}>
          <NodeComponent
            id={node.id}
            data={node.data || {}}
            position={node.position}
            selected={isSelected}
            onSelect={handleNodeSelect}
            onDrag={handleNodeDrag}
          />
          
          {/* Input connection point - not for start nodes */}
          {node.type !== 'start' && (
            <ConnectionPoint
              node={node}
              type="input"
              onStartConnection={handleStartConnection}
              isActive={isSelected || (isConnecting && connectionSourceId !== node.id) || 
                         (isConnecting && connectionSourceId === node.id && connectionSourceType !== 'input')}
            />
          )}
          
          {/* Output connection point - not for end nodes */}
          {node.type !== 'end' && (
            <ConnectionPoint
              node={node}
              type="output"
              onStartConnection={handleStartConnection}
              isActive={isSelected || (isConnecting && connectionSourceId !== node.id) || 
                         (isConnecting && connectionSourceId === node.id && connectionSourceType !== 'output')}
            />
          )}
        </React.Fragment>
      );
    });
  };

  // Render all edges between nodes
  const renderEdges = () => {
    return (
      <svg className="absolute top-0 left-0 w-full h-full pointer-events-none" style={{ zIndex: 8 }}>
        {edges.map(edge => {
          const sourceNode = nodes.find(n => n.id === edge.source);
          const targetNode = nodes.find(n => n.id === edge.target);
          
          if (!sourceNode || !targetNode) return null;
          
          // Get source (output) and target (input) positions
          const sourcePos = getConnectionPointPosition(edge.source, 'output');
          const targetPos = getConnectionPointPosition(edge.target, 'input');
          
          if (!sourcePos || !targetPos) return null;
          
          return (
            <Edge
              key={edge.id}
              sourcePosition={sourcePos}
              targetPosition={targetPos}
              label={edge.label}
              selected={selectedEdge === edge.id}
            />
          );
        })}
      </svg>
    );
  };

  return (
    <div style={{ display: 'flex', height: '100%', position: 'relative' }}>
      {/* Sidebar - using absolute positioning */}
      <Sidebar onDragStart={() => {}} />
      
      <div style={{ marginLeft: '16rem', display: 'flex', flexDirection: 'column', flexGrow: 1 }}>
        <div className="p-4 bg-gray-100 border-b flex justify-between items-center">
          <h1 className="text-xl font-bold">{workflowData.name || 'Workflow'}</h1>
          <div className="flex items-center">
            {successMessage && (
              <div className="mr-4 text-sm text-green-600 bg-green-100 px-3 py-1 rounded">
                {successMessage}
              </div>
            )}
            <button 
              className={`bg-blue-600 text-white px-4 py-2 rounded mr-2 hover:bg-blue-700 ${isDirty ? '' : 'opacity-50 cursor-not-allowed'}`}
              onClick={saveWorkflow}
              disabled={!isDirty || isSaving}
            >
              {isSaving ? 'Saving...' : 'Save Workflow'}
            </button>
            <a href={apiUrls.detail} className="border border-gray-300 bg-white px-4 py-2 rounded hover:bg-gray-50">
              Exit
            </a>
          </div>
        </div>
        
        <div className="flex-1 flex">
          <div 
            ref={canvasRef}
            className="flex-1 bg-gray-50 relative overflow-auto" 
            onClick={handleCanvasClick}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onMouseMove={handleMouseMove}
          >
            {/* Render edges below nodes */}
            {renderEdges()}
            
            {/* Render all nodes */}
            {renderNodes()}
            
            {/* Render active connection line when connecting */}
            {isConnecting && renderActiveConnectionLine()}
            
            {/* Add instruction message when connecting */}
            {isConnecting && (
              <div className="absolute top-4 left-4 bg-white shadow-md rounded-md p-2 text-sm">
                <p className="text-blue-600">Click on another node's connection point to complete, or anywhere to cancel</p>
              </div>
            )}
          </div>
          
          <div className="w-64 bg-white border-l overflow-y-auto">
            <PropertiesPanel 
              selectedNode={selectedNode} 
              systemsList={systemsList}
              scriptsList={scriptsList}
              updateNodeData={updateNodeData} 
              deleteNode={deleteNode}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// Initialize the workflow designer when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('workflow-designer-root');
  if (container) {
    try {
      const root = createRoot(container);
      root.render(React.createElement(WorkflowDesigner));
      console.log('Workflow designer initialized');
    } catch (error) {
      console.error('Error initializing workflow designer:', error);
      container.innerHTML = `
        <div class="p-4 bg-red-50 border border-red-200 rounded-md">
          <h3 class="text-red-800 font-medium">Error initializing workflow designer</h3>
          <p class="text-red-600 mt-1">${error.message}</p>
        </div>
      `;
    }
  }
});