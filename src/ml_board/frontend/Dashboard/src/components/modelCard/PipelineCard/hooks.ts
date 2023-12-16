import { useCallback, useEffect, useReducer, useState } from "react";
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


// ========================================================================================//
enum EActivePipelineActionType {
    ACTIVE_NODE = "ACTIVE_NODE",
    ACTIVE_KEY = "ACTIVE_KEY",
}

interface IActivePipelineAction {
    type: EActivePipelineActionType;
    payload: string;
}
interface IActivePipeline {
    activeNode: string;
    activePipelineKey: string;
}

function activePipelineReducer(state: IActivePipeline, { type, payload }: IActivePipelineAction): IActivePipeline {
    switch (type) {
        case EActivePipelineActionType.ACTIVE_KEY:
            return {
                activeNode: payload,
                activePipelineKey: payload,
            };
        case EActivePipelineActionType.ACTIVE_NODE:
            return {
                ...state,
                activeNode: payload,
            };
        default:
            return state;
    }
}

export function useActivePipelineKeyNodes(initialPipelineKey: string) {
    const [state, dispatch] = useReducer(activePipelineReducer,
        {
            activeNode: initialPipelineKey,
            activePipelineKey: initialPipelineKey
        });

    const activeNode = state.activeNode;
    const setActiveNode = useCallback((activeNode: string) => dispatch({ type: EActivePipelineActionType.ACTIVE_NODE, payload: activeNode }), []);
    const activePipelineKey = state.activePipelineKey;
    const setActivePipelineKey = useCallback((activeKey: string) => dispatch({ type: EActivePipelineActionType.ACTIVE_KEY, payload: activeKey }), []);

    return { activeNode, setActiveNode, activePipelineKey, setActivePipelineKey };
}
