// src/workflow-designer.js
import React, { useState, useEffect, useRef } from 'react';
import { createRoot } from 'react-dom/client';

// Define all components directly in this file
// Node Component
const Node = ({ node, isSelected, onSelect, onDrag }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [offsetX, setOffsetX] = useState(0);
  const [offsetY, setOffsetY] = useState(0);
  
  // Get node style based on type
  const getNodeStyle = () => {
    switch (node.type) {
      case 'start':
        return {
          fill: '#d1fae5',
          stroke: '#10b981',
          width: 120,
          height: 40,
          rx: 8,
          ry: 8
        };
      case 'end':
        return {
          fill: '#fee2e2',
          stroke: '#ef4444',
          width: 120,
          height: 40,
          rx: 8,
          ry: 8
        };
      case 'step':
        return {
          fill: '#dbeafe',
          stroke: '#3b82f6',
          width: 180,
          height: 80,
          rx: 8,
          ry: 8
        };
      case 'decision':
        return {
          fill: '#fef3c7',
          stroke: '#f59e0b',
          isPolygon: true
        };
      default:
        return {
          fill: '#f3f4f6',
          stroke: '#6b7280',
          width: 120,
          height: 40,
          rx: 8,
          ry: 8
        };
    }
  };
  
  const style = getNodeStyle();
  
  // Start dragging
  const handleMouseDown = (e) => {
    setIsDragging(true);
    setOffsetX(e.clientX - node.position.x);
    setOffsetY(e.clientY - node.position.y);
    onSelect();
  };
  
  // Handle dragging
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (isDragging) {
        const x = e.clientX - offsetX;
        const y = e.clientY - offsetY;
        onDrag({ x, y });
      }
    };
    
    const handleMouseUp = () => {
      setIsDragging(false);
    };
    
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, offsetX, offsetY, onDrag]);
  
  return (
    <g 
      transform={`translate(${node.position.x}, ${node.position.y})`}
      onMouseDown={handleMouseDown}
      style={{ cursor: 'move' }}
    >
      {/* Node shape */}
      {style.isPolygon ? (
        <polygon
          points="0,40 80,0 160,40 80,80"
          fill={style.fill}
          stroke={style.stroke}
          strokeWidth={isSelected ? 3 : 2}
        />
      ) : (
        <rect
          width={style.width}
          height={style.height}
          rx={style.rx}
          ry={style.ry}
          fill={style.fill}
          stroke={style.stroke}
          strokeWidth={isSelected ? 3 : 2}
        />
      )}
      
      {/* Node label */}
      <text
        x={style.isPolygon ? 80 : style.width / 2}
        y={style.isPolygon ? 40 : style.height / 2}
        textAnchor="middle"
        dominantBaseline="middle"
        fill="#374151"
        fontSize="12px"
        fontWeight="bold"
      >
        {node.data.label}
      </text>
      
      {/* Description for step nodes */}
      {node.type === 'step' && node.data.description && (
        <text
          x={style.width / 2}
          y={style.height - 15}
          textAnchor="middle"
          fill="#6b7280"
          fontSize="10px"
        >
          {node.data.description.length > 25 
            ? node.data.description.substring(0, 25) + '...' 
            : node.data.description}
        </text>
      )}
      
      {/* System or script badge for step nodes */}
      {node.type === 'step' && (node.data.system || node.data.script) && (
        <g>
          {node.data.system && (
            <rect
              x="5"
              y="5"
              width="60"
              height="16"
              rx="8"
              ry="8"
              fill="#e0e7ff"
            />
          )}
          {node.data.system && (
            <text
              x="35"
              y="13"
              textAnchor="middle"
              dominantBaseline="middle"
              fill="#4f46e5"
              fontSize="8px"
            >
              {node.data.system}
            </text>
          )}
          
          {node.data.script && (
            <rect
              x={node.data.system ? "70" : "5"}
              y="5"
              width="60"
              height="16"
              rx="8"
              ry="8"
              fill="#f5d0fe"
            />
          )}
          {node.data.script && (
            <text
              x={node.data.system ? "100" : "35"}
              y="13"
              textAnchor="middle"
              dominantBaseline="middle"
              fill="#a21caf"
              fontSize="8px"
            >
              {node.data.script}
            </text>
          )}
        </g>
      )}
    </g>
  );
};

// Simple wrapper components for different node types
const StartNode = (props) => <Node {...props} />;
const EndNode = (props) => <Node {...props} />;
const StepNode = (props) => <Node {...props} />;
const DecisionNode = (props) => <Node {...props} />;

// Edge component
const Edge = ({ edge, nodes }) => {
  // Find source and target nodes
  const sourceNode = nodes.find(n => n.id === edge.source);
  const targetNode = nodes.find(n => n.id === edge.target);
  
  if (!sourceNode || !targetNode) return null;
  
  // Calculate center points for connection
  const getNodeCenter = (node) => {
    switch (node.type) {
      case 'decision':
        return { x: node.position.x + 80, y: node.position.y + 40 };
      case 'step':
        return { x: node.position.x + 90, y: node.position.y + 40 };
      default:
        return { x: node.position.x + 60, y: node.position.y + 20 };
    }
  };
  
  const source = getNodeCenter(sourceNode);
  const target = getNodeCenter(targetNode);
  
  // Create a curved path
  const midX = (source.x + target.x) / 2;
  const midY = (source.y + target.y) / 2;
  
  // Draw path
  const path = `M${source.x},${source.y} Q${midX},${source.y} ${midX},${midY} Q${midX},${target.y} ${target.x},${target.y}`;
  
  return (
    <g>
      <path
        d={path}
        stroke="#9ca3af"
        strokeWidth="2"
        fill="none"
        markerEnd="url(#arrowhead)"
      />
      
      {/* Label for edge */}
      {edge.label && (
        <g transform={`translate(${midX}, ${midY})`}>
          <rect
            x="-20"
            y="-10"
            width={edge.label.length * 8 + 10}
            height="20"
            rx="4"
            fill="#f9fafb"
            stroke="#e5e7eb"
          />
          <text
            textAnchor="middle"
            dominantBaseline="middle"
            fill="#4b5563"
            fontSize="12px"
          >
            {edge.label}
          </text>
        </g>
      )}
    </g>
  );
};

// Sidebar component
const Sidebar = ({ onDragStart }) => {
  // Handle drag start
  const handleDragStart = (e, nodeType, data) => {
    e.dataTransfer.setData('nodeType', nodeType);
    e.dataTransfer.setData('nodeData', JSON.stringify(data));
    e.dataTransfer.effectAllowed = 'copy';
    
    // Call parent prop if exists
    if (typeof onDragStart === 'function') {
      onDragStart(nodeType, data);
    }
  };
  
  return (
    <div className="w-64 bg-white p-4 border-r h-full overflow-y-auto">
      <h2 className="text-lg font-bold mb-4">Workflow Elements</h2>
      
      <div className="mb-4">
        <h3 className="font-medium text-sm text-gray-500 mb-2">Control Nodes</h3>
        
        <div 
          className="border-2 border-green-500 rounded-md p-2 mb-2 bg-white cursor-move"
          draggable
          onDragStart={e => handleDragStart(e, 'start', { label: 'Start Workflow' })}
        >
          <div className="flex justify-between items-center">
            <span className="font-medium">Start</span>
            <span className="text-xs px-2 py-1 bg-green-100 text-green-600 rounded-full">Control</span>
          </div>
        </div>
        
        <div 
          className="border-2 border-red-500 rounded-md p-2 mb-2 bg-white cursor-move"
          draggable
          onDragStart={e => handleDragStart(e, 'end', { label: 'End Workflow' })}
        >
          <div className="flex justify-between items-center">
            <span className="font-medium">End</span>
            <span className="text-xs px-2 py-1 bg-red-100 text-red-600 rounded-full">Control</span>
          </div>
        </div>
        
        <div 
          className="border-2 border-yellow-500 rounded-md p-2 mb-2 bg-white cursor-move"
          draggable
          onDragStart={e => handleDragStart(e, 'decision', { 
            label: 'Decision', 
            description: 'Branch based on condition'
          })}
        >
          <div className="flex justify-between items-center">
            <span className="font-medium">Decision</span>
            <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-600 rounded-full">Control</span>
          </div>
        </div>
      </div>
      
      <div>
        <h3 className="font-medium text-sm text-gray-500 mb-2">Step Nodes</h3>
        
        <div 
          className="border-2 border-blue-500 rounded-md p-2 mb-2 bg-white cursor-move"
          draggable
          onDragStart={e => handleDragStart(e, 'step', { 
            label: 'Task', 
            description: 'A task to be performed'
          })}
        >
          <div className="flex justify-between items-center">
            <span className="font-medium">Task</span>
            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-600 rounded-full">Step</span>
          </div>
        </div>
        
        <div 
          className="border-2 border-blue-500 rounded-md p-2 mb-2 bg-white cursor-move"
          draggable
          onDragStart={e => handleDragStart(e, 'step', { 
            label: 'System Task', 
            description: 'Task performed by a system',
            system: 'Select System'
          })}
        >
          <div className="flex justify-between items-center">
            <span className="font-medium">System Task</span>
            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-600 rounded-full">Step</span>
          </div>
        </div>
        
        <div 
          className="border-2 border-blue-500 rounded-md p-2 mb-2 bg-white cursor-move"
          draggable
          onDragStart={e => handleDragStart(e, 'step', { 
            label: 'Script Task', 
            description: 'Task performed by a script',
            script: 'Select Script'
          })}
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
          Drag elements from this panel and drop them onto the canvas. Connect nodes by dragging from one to another.
        </p>
      </div>
    </div>
  );
};

// Properties Panel component
const PropertiesPanel = ({ selectedNode, systemsList, scriptsList, updateNodeData, deleteNode }) => {
  if (!selectedNode) {
    return (
      <div className="p-4">
        <p className="text-gray-500 italic">Select a node to edit its properties</p>
      </div>
    );
  }

  // Handle updates to node data
  const onUpdateNode = (key, value) => {
    if (typeof updateNodeData === 'function') {
      updateNodeData(selectedNode.id, key, value);
    }
  };

  // Handle node deletion
  const onDeleteNode = () => {
    if (typeof deleteNode === 'function') {
      deleteNode(selectedNode.id);
    }
  };
  
  return (
    <div className="p-4">
      <h3 className="font-bold mb-4">Node Properties</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Label</label>
          <input
            type="text"
            value={selectedNode.data.label || ''}
            onChange={(e) => onUpdateNode('label', e.target.value)}
            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 text-sm"
          />
        </div>
        
        {(selectedNode.type === 'step' || selectedNode.type === 'decision') && (
          <div>
            <label className="block text-sm font-medium text-gray-700">Description</label>
            <textarea
              value={selectedNode.data.description || ''}
              onChange={(e) => onUpdateNode('description', e.target.value)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 text-sm"
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
                  const system = systemsList.find(s => s.id == systemId);
                  onUpdateNode('system_id', systemId);
                  onUpdateNode('system', system ? system.name : '');
                }}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 text-sm"
              >
                <option value="">None</option>
                {systemsList && systemsList.map(system => (
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
                  const script = scriptsList.find(s => s.id == scriptId);
                  onUpdateNode('script_id', scriptId);
                  onUpdateNode('script', script ? script.name : '');
                }}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 text-sm"
              >
                <option value="">None</option>
                {scriptsList && scriptsList.map(script => (
                  <option key={script.id} value={script.id}>{script.name}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Inputs</label>
              <textarea
                value={selectedNode.data.inputs || ''}
                onChange={(e) => onUpdateNode('inputs', e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 text-sm"
                rows="2"
                placeholder="Data required by this step"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700">Outputs</label>
              <textarea
                value={selectedNode.data.outputs || ''}
                onChange={(e) => onUpdateNode('outputs', e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 text-sm"
                rows="2"
                placeholder="Data produced by this step"
              />
            </div>
          </>
        )}
        
        <div className="pt-4">
          <button
            onClick={onDeleteNode}
            className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
          >
            Delete Node
          </button>
        </div>
      </div>
    </div>
  );
};

// Main workflow designer component
const WorkflowDesigner = ({ workflowData, systemsList, scriptsList, apiUrls }) => {
  const [nodes, setNodes] = useState(workflowData.nodes || []);
  const [edges, setEdges] = useState(workflowData.edges || []);
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionSource, setConnectionSource] = useState(null);
  
  const canvasRef = useRef(null);
  const svgRef = useRef(null);
  
  // Initialize the SVG defs for markers
  useEffect(() => {
    if (svgRef.current) {
      // Check if defs already exist
      let defs = svgRef.current.querySelector('defs');
      if (!defs) {
        defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        svgRef.current.appendChild(defs);
      }
      
      // Add arrowhead marker
      defs.innerHTML = `
        <marker 
          id="arrowhead" 
          viewBox="0 0 10 10" 
          refX="9" 
          refY="5" 
          markerWidth="6" 
          markerHeight="6" 
          orient="auto"
        >
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#9ca3af" />
        </marker>
      `;
    }
  }, [svgRef.current]);
  
  // Update canvas size on window resize
  useEffect(() => {
    const updateCanvasSize = () => {
      if (canvasRef.current && svgRef.current) {
        const rect = canvasRef.current.getBoundingClientRect();
        svgRef.current.setAttribute('width', rect.width);
        svgRef.current.setAttribute('height', rect.height);
      }
    };
    
    window.addEventListener('resize', updateCanvasSize);
    updateCanvasSize();
    
    return () => window.removeEventListener('resize', updateCanvasSize);
  }, [canvasRef.current, svgRef.current]);
  
  // Handle node selection
  const handleNodeSelect = (nodeId) => {
    const node = nodes.find(n => n.id === nodeId);
    setSelectedNode(node);
    setSelectedEdge(null);
  };
  
  // Handle node drag
  const handleNodeDrag = (nodeId, position) => {
    setNodes(nodes.map(node => {
      if (node.id === nodeId) {
        return {
          ...node,
          position
        };
      }
      return node;
    }));
    
    setIsDirty(true);
  };
  
  // Update node data
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
    
    setIsDirty(true);
    
    // Update selected node if needed
    if (selectedNode && selectedNode.id === nodeId) {
      setSelectedNode({
        ...selectedNode,
        data: {
          ...selectedNode.data,
          [key]: value,
        }
      });
    }
  };
  
  // Delete a node
  const deleteNode = (nodeId) => {
    setNodes(nodes.filter(node => node.id !== nodeId));
    setEdges(edges.filter(edge => edge.source !== nodeId && edge.target !== nodeId));
    setSelectedNode(null);
    setIsDirty(true);
  };
  
  // Add a new node from drag and drop
  const handleDrop = (e) => {
    e.preventDefault();
    
    const nodeType = e.dataTransfer.getData('nodeType');
    const nodeData = JSON.parse(e.dataTransfer.getData('nodeData') || '{}');
    
    if (!nodeType) return;
    
    // Get position relative to the canvas
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Create unique ID for the node
    const nodeId = `${nodeType}_${Date.now()}`;
    
    // Create the new node
    const newNode = {
      id: nodeId,
      type: nodeType,
      position: { x, y },
      data: nodeData
    };
    
    // Add to nodes
    setNodes([...nodes, newNode]);
    setIsDirty(true);
    
    // Select the new node
    setSelectedNode(newNode);
  };
  
  // Handle dragover
  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  };
  
  // Start connecting nodes
  const startConnection = (nodeId) => {
    setIsConnecting(true);
    setConnectionSource(nodeId);
  };
  
  // Complete connection
  const completeConnection = (targetId) => {
    if (isConnecting && connectionSource && connectionSource !== targetId) {
      // Create unique ID for the edge
      const edgeId = `e-${connectionSource}-${targetId}`;
      
      // Check if this connection already exists
      const connectionExists = edges.some(edge => 
        edge.source === connectionSource && edge.target === targetId
      );
      
      if (!connectionExists) {
        // Add to edges
        const newEdge = {
          id: edgeId,
          source: connectionSource,
          target: targetId
        };
        
        setEdges([...edges, newEdge]);
        setIsDirty(true);
      }
    }
    
    // Reset connection state
    setIsConnecting(false);
    setConnectionSource(null);
  };
  
  // Save the workflow
  const saveWorkflow = async () => {
    if (!isDirty) return;
    
    setIsSaving(true);
    
    try {
      const response = await fetch(apiUrls.save, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: JSON.stringify({
          nodes,
          edges,
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setIsDirty(false);
        setSuccessMessage(data.message);
        
        // Hide success message after a few seconds
        setTimeout(() => {
          setSuccessMessage('');
        }, 3000);
      }
    } catch (error) {
      console.error('Error saving workflow:', error);
    } finally {
      setIsSaving(false);
    }
  };
  
  return (
    <div className="h-full flex overflow-hidden">
      <Sidebar onDragStart={() => {}} />
      
      <div className="flex-1 flex flex-col">
        <div className="p-4 bg-gray-100 border-b flex justify-between items-center">
          <h1 className="text-xl font-bold">{workflowData.name}</h1>
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
            className="flex-1 bg-gray-50 relative overflow-hidden"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <svg
              ref={svgRef}
              width="100%"
              height="100%"
              className="absolute top-0 left-0"
            >
              {/* Render edges */}
              {edges.map(edge => (
                <Edge 
                  key={edge.id} 
                  edge={edge} 
                  nodes={nodes} 
                />
              ))}
              
              {/* Render nodes */}
              {nodes.map(node => {
                const isSelected = selectedNode && selectedNode.id === node.id;
                
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
                    NodeComponent = Node;
                }
                
                return (
                  <NodeComponent
                    key={node.id}
                    node={node} 
                    isSelected={isSelected}
                    onSelect={() => handleNodeSelect(node.id)}
                    onDrag={(position) => handleNodeDrag(node.id, position)}
                  />
                );
              })}
            </svg>
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

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('workflow-designer-root');
  if (container) {
    // Parse data from data attributes
    try {
      const workflowDataStr = container.getAttribute('data-workflow-data');
      const systemsStr = container.getAttribute('data-systems');
      const scriptsStr = container.getAttribute('data-scripts');
      const saveUrl = container.getAttribute('data-save-url');
      const detailUrl = container.getAttribute('data-detail-url');
      
      // Parse JSON data with error handling
      const workflowData = workflowDataStr ? JSON.parse(workflowDataStr) : { nodes: [], edges: [] };
      const systems = systemsStr ? JSON.parse(systemsStr) : [];
      const scripts = scriptsStr ? JSON.parse(scriptsStr) : [];
      
      // Make sure nodes and edges are arrays
      if (!Array.isArray(workflowData.nodes)) workflowData.nodes = [];
      if (!Array.isArray(workflowData.edges)) workflowData.edges = [];
      
      // Create apiUrls object
      const apiUrls = {
        save: saveUrl || '',
        detail: detailUrl || ''
      };
      
      // Render the component
      const root = createRoot(container);
      root.render(
        <WorkflowDesigner 
          workflowData={workflowData}
          systemsList={systems}
          scriptsList={scripts}
          apiUrls={apiUrls}
        />
      );
    } catch (error) {
      console.error('Error initializing workflow designer:', error);
      
      // Render an error message
      container.innerHTML = `
        <div class="p-4 bg-red-50 border border-red-200 rounded-md">
          <h3 class="text-red-800 font-medium">Error initializing workflow designer</h3>
          <p class="text-red-600 mt-1">${error.message}</p>
        </div>
      `;
    }
  }
});