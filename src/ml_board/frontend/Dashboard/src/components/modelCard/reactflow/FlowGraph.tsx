import "reactflow/dist/style.css";
import ReactFlow, { Node, Edge, Controls, Background, applyEdgeChanges, applyNodeChanges, NodeChange, EdgeChange } from "reactflow";
import { useCallback, useState } from "react";


export default function FlowGraph({ initialNodes, initialEdges }: { initialNodes: Node[], initialEdges: Edge[] }) {

    const [nodes, setNodes] = useState(initialNodes);
    const [edges, setEdges] = useState(initialEdges);

    const onNodesChange = useCallback((changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
    const onEdgesChange = useCallback((changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);

    return (
        <div style={{ height: "100vh" }}>
            <ReactFlow fitView
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                defaultEdgeOptions={{ animated: true }}
            >
                <Background />
                <Controls />
            </ReactFlow>
        </div>
    );
}


