import { JsonViewer } from "@textea/json-viewer";
import usePipelineCardContext from "./PipelineCardContext";

export default function ConfigViewer() {
    const { activeNode, activePipeline } = usePipelineCardContext();

    const config = activePipeline?.nodes.find(node => node.id === activeNode)!.data.config;

    return config ? <JsonViewer value={config} rootName={activeNode} /> : null;
};

