import "reactflow/dist/style.css";
import ReactFlow, { Node, Edge, Controls, Background, useNodesState, useEdgesState } from "reactflow";

export default function FlowGraph({ initialNodes, initialEdges }: { initialNodes: Node[], initialEdges: Edge[] }) {

    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

    // return (
    //     <div style={{ height: "100vh" }}>
    //         <ReactFlow fitView
    //             defaultNodes={initialNodes}
    //             defaultEdges={initialEdges}
    //             defaultEdgeOptions={{ animated: true }}
    //         >
    //             <Background />
    //             <Controls />
    //         </ReactFlow>
    //     </div>
    // );
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


