import React from "react";
import { IOStatsType, JobStatusType } from "../app/datatypes"

type ThroughputProps = {
    ioStats: IOStatsType
};


const getThroughput = (ioStats: IOStatsType, measurementDuration: number) => {
    const currentTime = new Date().getTime()
    const threshold = currentTime - measurementDuration * 1000
    const msgTs = ioStats.msgTS

    let i = msgTs.length - 1
    while (i > 0 && msgTs[i] > threshold) {
        i--
    }
    return ((msgTs.length - i - 1) / measurementDuration)
};


const Throughput: React.FC<ThroughputProps> = ({ ioStats }) => {

    return (
        <>
            <h1> Throughput Board </h1>
            <div>Connected: {ioStats.isConnected ? "yes" : "no"}</div>
            <div>Messages received: {ioStats.msgTS.length}</div>
            <div>ping: {ioStats.lastPong - ioStats.lastPing}ms</div>
            <div>throughput: {getThroughput(ioStats, 5)}</div>
        </>
    )
}

export default Throughput;