import React from "react";
import { useAppSelector } from "../app/hooks"
import type { RootState } from '../app/store';


type FlowBoardProps = {
};


const jobIdSelector = (state: RootState) => state.jobStatus.map(s => s.event_id) //s.data.payload.job_id)

const FlowBoard: React.FC<FlowBoardProps> = ({ }) => {

    const jobIDs = useAppSelector(jobIdSelector)


    return (
        <>
            <h1> Flow Board </h1>
            <div>{jobIDs}</div>
        </>
    );
}

export default FlowBoard;