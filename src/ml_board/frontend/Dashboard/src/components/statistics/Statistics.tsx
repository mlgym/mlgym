import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import { useAppSelector } from "../../app/hooks";
import { getLastPing, getReceivevMsgCount, getThroughput, isConnected } from "../../redux/status/statusSlice";
import statistics_css from "./StatisticsCss";

export default function Statistics() {
    // NOTE: for micro performance this component can be divide into smaller components to avoid unnecessary rerendering
    // left because of insignificance
    const ping = useAppSelector(getLastPing);
    const isSocketConnected = useAppSelector(isConnected);
    const receivedMsgCount = useAppSelector(getReceivevMsgCount);
    const throughput = useAppSelector(getThroughput);

    return (
        <Box sx={statistics_css.main_container}>
            <div style={statistics_css.sub_container}>
                Connected: {
                    isSocketConnected ?
                        <span style={statistics_css.span_connected}>
                            Yes
                        </span>
                        :
                        <span style={statistics_css.span_disconnected}>
                            No
                        </span>
                }
            </div>
            <Divider />
            <div style={statistics_css.sub_container}>
                Messages received:
                <span style={statistics_css.span_general}>
                    {receivedMsgCount}
                </span>
            </div>
            <Divider />
            <div style={statistics_css.sub_container}>
                Ping:
                <span style={statistics_css.span_ping}>
                    {ping} ms
                </span>
            </div>
            <Divider />
            <div style={statistics_css.sub_container}>
                Throughput:
                <span style={statistics_css.span_general}>
                    {throughput}
                </span>
            </div>
        </Box>
    );
}