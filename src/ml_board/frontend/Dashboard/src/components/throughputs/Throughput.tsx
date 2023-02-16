import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import { useAppSelector } from "../../app/hooks";
import { getLastPing, getReceivevMsgCount, getThroughput, isConnected } from "../../redux/status/statusSlice";
import './throughput.css';

export default function Throughput() {
    // NOTE: for micro performance this component can be divide into smaller components to avoid unnecessary rerendering
    // left because of insignificance
    const ping = useAppSelector(getLastPing);
    const isSocketConnected = useAppSelector(isConnected);
    const receivedMsgCount = useAppSelector(getReceivevMsgCount);
    const throughput = useAppSelector(getThroughput);

    return (
        <Box sx={{
            width: 250,
            position: 'fixed',
            display: "flex",
            flexDirection: "column",
            bottom: 0,
        }}>
            {/* Hardcoded will be replaced with redux values */}
            <div className="throughput-containers">
                Connected: {
                    isSocketConnected ?
                        <span className="throughput-containers-span-connected">
                            Yes
                        </span>
                        :
                        <span className="throughput-containers-span-disconnected">
                            No
                        </span>
                }
            </div>
            <Divider />
            <div className="throughput-containers">
                Messages received:
                <span className="throughput-containers-span-normal">
                    {receivedMsgCount}
                </span>
            </div>
            <Divider />
            <div className="throughput-containers">
                Ping:
                <span className="throughput-containers-span-ping">
                    {ping} ms
                </span>
            </div>
            <Divider />
            <div className="throughput-containers">
                Throughput:
                <span className="throughput-containers-span-normal">
                    {throughput}
                </span>
            </div>
        </Box>
    );
}