import "reactflow/dist/style.css";
import ReactFlow, { Node, Edge, Controls, Background, useNodesState, useEdgesState, useReactFlow, Panel } from "reactflow";
import CustomNode from "./CustomNode";
import { CUSTOM_NODE_TYPE } from "./api"
import { useCallback, useEffect } from "react";
import Dagre, { Label } from '@dagrejs/dagre';

// defining the nodeTypes outside of the component to prevent re-renderings
// also possible to use useMemo inside the component

const nodeTypes = { [CUSTOM_NODE_TYPE]: CustomNode };


const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));

const getLayoutedElements = (nodes: Node[], edges: Edge[], options: { direction: string }) => {
    g.setGraph({ rankdir: options.direction });

    edges.forEach((edge) => g.setEdge(edge.source, edge.target));
    nodes.forEach((node) => g.setNode(node.id, node as Label));

    Dagre.layout(g);

    return {
        nodes: nodes.map((node) => {
            const { x, y } = g.node(node.id);

            return { ...node, position: { x, y } };
        }),
        edges,
    };
};


export default function FlowGraph({ initialNodes, initialEdges }: { initialNodes: Node[], initialEdges: Edge[] }) {

    const { fitView } = useReactFlow();
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

    // const nodeTypes = useMemo(() => ({ customPotato: MyCustomNode }), []);
    const onLayout = useCallback(
        (direction: string) => {
            const layouted = getLayoutedElements(nodes, edges, { direction });

            setNodes([...layouted.nodes]);
            setEdges([...layouted.edges]);

            window.requestAnimationFrame(() => {
                fitView();
            });
        },
        [nodes, edges]
    );

    return (
        <div style={{ height: "100vh" }}>
            <ReactFlow fitView
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodeTypes={nodeTypes}
                deleteKeyCode={null}
                nodeOrigin={[0.5, 0.5]}
                snapToGrid={true}
            >
                <Background />
                <Controls />
                <Panel position="top-right">
                    <button onClick={() => onLayout('TB')}>vertical layout</button>
                    <button onClick={() => onLayout('LR')}>horizontal layout</button>
                </Panel>
            </ReactFlow>
        </div>
    );
}


