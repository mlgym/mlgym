import { NodeProps, Position } from "reactflow";
import Paper from '@mui/material/Paper';
import { CustomHandles } from "./CustomHandles";
import { Typography } from "@mui/material";
import { INodeData } from "./interface";

export default function CustomNode({ data: { label, child_count } }: NodeProps<INodeData>) {
    return (
        <div>
            <CustomHandles count={1} type={"target"} position={Position.Top} />

            <Paper elevation={3} sx={{ padding: 2 }}>
                <Typography variant="h4" p={1} sx={{
                    textAlign: 'center',
                    fontSize: 24,
                    fontWeight: 'bold',
                }}>
                    {label}
                </Typography>
            </Paper >

            <CustomHandles count={child_count} type={"source"} position={Position.Bottom} />
        </div>
    );
}