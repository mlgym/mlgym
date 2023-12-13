export interface IPipeline {
    [nodeName: string]: INode;
}

export interface INode {
    config_str: string;
    requirements: Array<string>;
    nodes: INode;
}