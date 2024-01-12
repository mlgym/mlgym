import { Edge, MarkerType, Node } from "reactflow";
import { IPipelineNode, IReactFlowPipeline } from "./interface";
import Dagre, { Label } from '@dagrejs/dagre';

const g = new Dagre.graphlib.Graph().setDefaultEdgeLabel(() => ({}));

export const getLayoutedNodes = (nodes: Node[], edges: Edge[], options: { direction: string } = { direction: "TB" }) => {
    if (!(nodes.length > 0 && edges.length > 0))
        return { nodes, edges }; // return imidiately if any is emtpy

    g.setGraph({ rankdir: options.direction });
    edges.forEach((edge) => g.setEdge(edge.source, edge.target));
    nodes.forEach((node) => g.setNode(node.id, node as Label));
    Dagre.layout(g);

    return {
        nodes: nodes.map((node) => {
            const { x, y } = g.node(node.id);
            return { ...node, position: { x, y } };
        })
    };
};

export const CUSTOM_NODE_TYPE = "CUSTOM_NODE_TYPE";

export function parseReactFlowPipeline(nodeKey: string, node: IPipelineNode): IReactFlowPipeline {
    const pipeline: IReactFlowPipeline = {
        nodes: [], edges: []
    };
    let shift = 0;

    function traverse(currentNodeName: string, currentNode: IPipelineNode) {
        pipeline.nodes.push({
            id: currentNodeName, // required
            position: { x: 0, y: 100 * shift++ }, // required
            data: {
                label: currentNodeName,
                config: JSON.parse(currentNode.config_str),
                child_count: Object.keys(currentNode.nodes).length,
            },
            type: CUSTOM_NODE_TYPE,
        })

        let count = 0;
        for (const [nextNodeName, nextNodeObj] of Object.entries(currentNode.nodes)) {
            pipeline.edges.push({
                id: `${currentNodeName}-${nextNodeName}`,
                source: currentNodeName,
                target: nextNodeName,
                markerEnd: { type: MarkerType.Arrow, },
                type: "step",
                sourceHandle: (count++).toString(),
                animated: true,
            });
            traverse(nextNodeName, nextNodeObj);
        }
    }

    traverse(nodeKey, node);

    return pipeline;
}