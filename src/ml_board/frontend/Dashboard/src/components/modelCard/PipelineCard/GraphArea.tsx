import "reactflow/dist/style.css";
import ReactFlow, { Background, useNodesState, useEdgesState, useReactFlow, MiniMap } from "reactflow";
import usePipelineCardContext from "./PipelineCardContext";
import { useEffect } from "react";

//NOTE: when the values of usePipelineCardContext change this causes the first render
// but then a secound render happens as setNodes and setEdges are carried out after the first render

export default function () {
    const { activePipeline, setActiveNode } = usePipelineCardContext();

    const [nodes, setNodes, onNodesChange] = useNodesState(activePipeline?.nodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(activePipeline?.edges);

    const { fitView } = useReactFlow();
    const fitTheView = () => setTimeout(() => fitView({ duration: 1000 }), 100);

    useEffect(() => {
        setNodes(activePipeline?.nodes);
        setEdges(activePipeline?.edges);
        fitTheView();
    }, [activePipeline]);

    return (<ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={(event, node) => {
            setActiveNode(node.id);
            fitTheView();
        }}
    >
        <Background />
        <MiniMap />
    </ReactFlow>);
}