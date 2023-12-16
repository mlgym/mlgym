import "reactflow/dist/style.css";
import ReactFlow, { Background, useNodesState, useEdgesState, useReactFlow, MiniMap } from "reactflow";
import usePipelineCardContext from "./PipelineCardContext";
import { useEffect } from "react";


export default function () {
    const { activePipeline, setActiveNode } = usePipelineCardContext();
    const { nodes, edges } = activePipeline ?? { nodes: [], edges: [] };

    const { fitView, setNodes, setEdges } = useReactFlow();
    const fitTheView = () => setTimeout(() => fitView({ duration: 1000 }), 100);

    useEffect(() => {
        setNodes(nodes);
        setEdges(edges);
        fitTheView();
    }, [activePipeline]);

    return (<ReactFlow
        defaultNodes={nodes}
        defaultEdges={edges}
        onNodeClick={(event, node) => {
            setActiveNode(node.id);
            fitTheView();
        }}
    >
        <Background />
        <MiniMap />
    </ReactFlow>);
}