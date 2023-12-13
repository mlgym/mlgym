import "reactflow/dist/style.css";
import ReactFlow, { Background, useNodesState, useEdgesState, useReactFlow } from "reactflow";
import { reactFlowGraph } from "./utils";
import usePipelineCardContext from "./PipelineCardContext";
import { useEffect } from "react";

//NOTE: when the values of usePipelineCardContext change this causes the first render
// but then a secound render happens as setNodes and setEdges are carried out after the first render

export default function () {
    const { activeNodeName, pipelineDetails } = usePipelineCardContext();

    const { nodes: initialNodes, edges: initialEdges } = reactFlowGraph(activeNodeName, pipelineDetails[activeNodeName]);
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

    const { fitView } = useReactFlow();
    useEffect(() => {
        setNodes(initialNodes);
        setEdges(initialEdges);
        setTimeout(() => fitView(), 200);
    }, [activeNodeName]);

    return (<ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
    />);
}