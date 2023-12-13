import { Dispatch, ReactNode, SetStateAction, createContext, useContext, useState } from "react";
import { IPipeline } from "./interface";

interface IPipelineCardContext {
    activeNodeName: string; setActiveNodeName: Dispatch<SetStateAction<string>>;
    pipelineDetails: IPipeline;
}

const pipelineCardContext = createContext<IPipelineCardContext | null>(null);

export function PipelineCardContextProvider({
    children, pipelineDetails
}: {
    children: ReactNode, pipelineDetails: IPipeline
}) {
    const [activeNodeName, setActiveNodeName] = useState<string>(Object.keys(pipelineDetails)[0]);

    return (
        <pipelineCardContext.Provider value={{
            activeNodeName, setActiveNodeName,
            pipelineDetails
        }}>
            {children}
        </pipelineCardContext.Provider>
    );
}

export default function usePipelineCardContext() {
    const context = useContext(pipelineCardContext);
    if (!context) {
        throw new Error("using Context outside its Provider!");
    }
    return context;
};