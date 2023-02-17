import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import { useAppSelector } from "../../app/hooks";
import { getLastPing, getReceivevMsgCount, getThroughput, isConnected } from "../../redux/status/statusSlice";
import './Statistics.css';

export default function Statistics() {
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
            <div className="statistics-containers">
                Connected: {
                    isSocketConnected ?
                        <span className="statistics-containers-span-connected">
                            Yes
                        </span>
                        :
                        <span className="statistics-containers-span-disconnected">
                            No
                        </span>
                }
            </div>
            <Divider />
            <div className="statistics-containers">
                Messages received:
                <span className="statistics-containers-span-general">
                    {receivedMsgCount}
                </span>
            </div>
            <Divider />
            <div className="statistics-containers">
                Ping:
                <span className="statistics-containers-span-ping">
                    {ping} ms
                </span>
            </div>
            <Divider />
            <div className="statistics-containers">
                Throughput:
                <span className="statistics-containers-span-general">
                    {throughput}
                </span>
            </div>
        </Box>
    );
}