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
    requirements:Array<string>;
    children:Array<string>;
}

export interface IReactFlowPipeline {
    nodes: Node<INodeData>[];
    edges: Edge[];
}