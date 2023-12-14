import { Edge, MarkerType, Node } from "reactflow";
import { IReactFlowNodeData, IPipelineNode, IReactFlowPipeline } from "./interface";


export function parseReactFlowPipeline(nodeKey: string, node: IPipelineNode): IReactFlowPipeline {
    const nodes: Node<IReactFlowNodeData>[] = [];
    const edges: Edge[] = [];
    let shift = 0;

    function traverse(currentNodeName: string, currentNode: IPipelineNode) {
        nodes.push({
            id: currentNodeName, // required
            position: { x: 0, y: 100 * shift++ }, // required
            data: {
                label: currentNodeName,
                config: JSON.parse(currentNode.config_str),
                // TODO: custom node to handle if one node has multiple children that they don't overlap
                // in_count: nodeAsTarget[key],
                // out_count: nodeAsSource[key],
                // config: currentNode.config_str,
            },
            // type: CUSTOM_NODE_TYPE,
        })

        for (const [nextNodeName, nextNodeObj] of Object.entries(currentNode.nodes)) {
            edges.push({
                id: `${currentNodeName}-${nextNodeName}`,
                source: currentNodeName,
                target: nextNodeName,
                markerEnd: { type: MarkerType.Arrow, },
                // type: "step",
                // sourceHandle: idx.toString(),
                // targetHandle: (nodeAsTarget[to] - 1).toString(),
                // animated: true,
            });
            traverse(nextNodeName, nextNodeObj);
        }
    }

    traverse(nodeKey, node);

    return { nodes, edges };
}