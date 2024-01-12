import "reactflow/dist/style.css";
import ReactFlow, { Background, useReactFlow, MiniMap } from "reactflow";
import usePipelineCardContext from "./PipelineCardContext";
import { useEffect } from "react";
import { CUSTOM_NODE_TYPE, getLayoutedNodes } from "./utils";
import CustomNode from "./CustomNode";

// defining the nodeTypes outside of the component to prevent re-renderings
// also possible to use useMemo inside the component

const nodeTypes = { [CUSTOM_NODE_TYPE]: CustomNode };

export default function () {
    const { activePipeline, setActiveNode } = usePipelineCardContext();
    const { nodes, edges } = activePipeline ?? { nodes: [], edges: [] };

    const { fitView, setNodes, setEdges } = useReactFlow();
    const fitTheView = () => setTimeout(() => fitView({ duration: 1000 }), 100);

    useEffect(() => {
        const layout = getLayoutedNodes(nodes, edges, { direction: "TB" });
        setNodes([...layout.nodes]);
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
        nodeTypes={nodeTypes}
    >
        <Background />
        <MiniMap />
    </ReactFlow>);
}