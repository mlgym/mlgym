import { Edge, Node } from "reactflow";

export interface IPipeline {
    [nodeName: string]: IPipelineNode;
}

export interface IPipelineNode {
    config_str: string;
    requirements: Array<string>;
    nodes: IPipelineNode;
}

export interface INodeData {
    label: string;
    config: JSON;
    child_count: number;
}

export interface IReactFlowPipeline {
    nodes: Node<INodeData>[];
    edges: Edge[];
}