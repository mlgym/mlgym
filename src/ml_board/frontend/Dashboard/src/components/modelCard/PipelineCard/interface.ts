import { Edge, Node } from "reactflow";

export interface IPipeline {
    [nodeName: string]: IPipelineNode;
}

export interface IPipelineNode {
    config_str: string;
    requirements: Array<string>;
    nodes: IPipelineNode;
}

export interface IReactFlowNodeData {
    label: string;
    config: JSON;
}

export interface IReactFlowPipeline {
    nodes: Node<IReactFlowNodeData>[];
    edges: Edge[];
}