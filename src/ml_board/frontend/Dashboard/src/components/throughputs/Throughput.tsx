import Divider from "@mui/material/Divider";
import Box from "@mui/material/Box";
import './throughput.css';

function Throughput() {
    return(
        <Box sx={{
            width: 250,
            position: 'fixed',
            display: "flex",
            flexDirection: "column",
            bottom: 0,
        }}>
            {/* Hardcoded will be replaced with redux values */}
            <div className="throughput-containers">
                Connected: 
                <span className="throughput-containers-span-connected">
                    Yes
                </span> / 
                <span className="throughput-containers-span-disconnected">
                    No
                </span>
            </div>
            <Divider/>
            <div className="throughput-containers">
                Messages received: 
                <span className="throughput-containers-span-normal">
                    10
                </span>
            </div>
            <Divider/>
            <div className="throughput-containers">
                Ping: 
                <span className="throughput-containers-span-ping">
                    1 ms
                </span>
            </div>
            <Divider/>
            <div className="throughput-containers">
                Throughput: 
                <span className="throughput-containers-span-normal">
                    5
                </span>
            </div>
        </Box>
    );
}

export default Throughput;