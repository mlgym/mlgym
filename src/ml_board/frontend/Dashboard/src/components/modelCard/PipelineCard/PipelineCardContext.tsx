import { Dispatch, ReactNode, SetStateAction, createContext, useCallback, useContext, useMemo, useState } from "react";
import { IPipeline, IReactFlowPipeline } from "./interface";
import { usePipeline } from "./hooks";

interface IPipelineCardContext {
    activePipelineKey: string; setActivePipelineKey(key: string): void;
    activeNode: string; setActiveNode: Dispatch<SetStateAction<string>>;
    activePipeline: IReactFlowPipeline;
    availablePipelineKeys: string[];
}

const pipelineCardContext = createContext<IPipelineCardContext | null>(null);

export function PipelineCardContextProvider({
    children, pipelineDetails
}: {
    children: ReactNode, pipelineDetails: IPipeline
}) {
    const { availablePipelineKeys, pipelinesState: pipelines } = usePipeline(pipelineDetails);

    // TODO: on Init the Graphs don't show up because the active key is an empty string!
    const [activePlKey, setActivePlKey] = useState<string>(availablePipelineKeys[0]);
    const [activeNode, setActiveNode] = useState<string>(availablePipelineKeys[0]);

    const activePipeline = useMemo(() => pipelines[activePlKey], [activePlKey]);
    const setActivePipelineKey = useCallback((key: string) => {
        setActivePlKey(key);
        setActiveNode(key);
    }, []);

    return (
        <pipelineCardContext.Provider value={{
            activePipelineKey:activePlKey,setActivePipelineKey,
            activeNode, setActiveNode,
            activePipeline, availablePipelineKeys
        }}>
            {children}
        </pipelineCardContext.Provider>
    );
}

export default function usePipelineCardContext() {
    const context = useContext(pipelineCardContext);
    if (!context) throw new Error("using Context outside its Provider!");
    return context;
};