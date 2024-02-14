import { NodeProps, Position } from "reactflow";
import Paper from '@mui/material/Paper';
import { CustomHandles } from "./CustomHandles";
import { Box, Divider, Typography } from "@mui/material";
import { INodeData } from "./interface";

export default function CustomNode({ data: { label, requirements, children } }: NodeProps<INodeData>) {
    return (
        <Box>
            {requirements.length > 0 && <CustomHandles handleIDs={["requirements"]} type={"target"} position={Position.Top} />}

            <Paper elevation={3} sx={{ padding: 2 }}>
                <Typography variant="h4" p={1} sx={{
                    textAlign: 'center',
                    fontSize: 24,
                    fontWeight: 'bold',
                }}>
                    {label.replace(/_/g, " ")}
                </Typography>

                {requirements.length > 1 && <>
                    <Divider />
                    <Typography variant="caption">
                        requires also: {requirements.length - 1} more components
                    </Typography>
                </>}
            </Paper >

            <CustomHandles handleIDs={children} type={"source"} position={Position.Bottom} />
        </Box>
    );
}