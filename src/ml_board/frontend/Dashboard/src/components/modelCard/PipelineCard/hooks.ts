import { useEffect, useReducer, useState } from "react";
import { IPipeline, IReactFlowPipeline } from "./interface";
import { parseReactFlowPipeline } from "./utils";

interface IPipelines {
    [pipelineKey: string]: IReactFlowPipeline;
}

export function usePipeline(pipelineDetails: IPipeline) {
    const [availablePipelineKeys, setAvailablePipelineKeys] = useState<string[]>([]);

    const [pipelinesState, dispatchPipelines] = useReducer(
        (currentPipelinesState: IPipelines, newPipelinesState: IPipelines) => (
            { ...currentPipelinesState, ...newPipelinesState }
        ), {});

    useEffect(() => {
        for (const key in pipelineDetails) {
            setAvailablePipelineKeys(prev => [...prev, key]);
            const pipeline = parseReactFlowPipeline(key, pipelineDetails[key]);
            dispatchPipelines({ [key]: pipeline });
        }
    }, [pipelineDetails]);

    return { availablePipelineKeys, pipelinesState };
}
