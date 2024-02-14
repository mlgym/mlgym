import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import { useAppSelector } from "../../app/hooks";
import { getLastPing, getReceivevMsgCount, getThroughput, isConnected } from "../../redux/globalConfig/globalConfigSlice";
// styles
import styles from "./Statistics.module.css";

export default function Statistics() {
    // NOTE: for micro performance this component can be divide into smaller components to avoid unnecessary rerendering
    // left because of insignificance
    const ping = useAppSelector(getLastPing);
    const isSocketConnected = useAppSelector(isConnected);
    const receivedMsgCount = useAppSelector(getReceivevMsgCount);
    const throughput = useAppSelector(getThroughput);

    return (
        <Box className={styles.main_container}>
            <div className={styles.sub_container}>
                Connected: {
                    isSocketConnected ?
                        <span className={styles.span_connected}>
                            Yes
                        </span>
                        :
                        <span className={styles.span_disconnected}>
                            No
                        </span>
                }
            </div>
            <Divider />
            <div className={styles.sub_container}>
                Messages received:
                <span className={styles.span_general}>
                    {receivedMsgCount}
                </span>
            </div>
            <Divider />
            <div className={styles.sub_container}>
                Ping:
                <span className={styles.span_ping}>
                    {ping} ms
                </span>
            </div>
            <Divider />
            <div className={styles.sub_container}>
                Throughput:
                <span className={styles.span_general}>
                    {throughput}
                </span>
            </div>
        </Box>
    );
}