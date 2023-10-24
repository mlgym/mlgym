import "reactflow/dist/style.css";
import ReactFlow, { Node, Edge, Controls, Background, MarkerType } from "reactflow";
import { stratify, tree } from 'd3-hierarchy';

export default function FlowGraph({ initialNodes, initialEdges }: { initialNodes: Node[], initialEdges: Edge[] }) {

    console.log(initialNodes);
    console.log(initialEdges);
    
    return (
        <div style={{ height: "100vh" }}>
            <ReactFlow fitView
                defaultNodes={initialNodes}
                defaultEdges={initialEdges}
                defaultEdgeOptions={{ animated: true, markerEnd: { type: MarkerType.ArrowClosed } }}
            >
                <Background />
                <Controls />
            </ReactFlow>
        </div>
    );
}


