import { Node, NodeProps, Position } from "reactflow";
import Paper from '@mui/material/Paper';
import { styled } from '@mui/material/styles';
import CreateHandles from "./CustomHandles";
import { NodeData } from "./interfaces";
import { Divider, Grid, List, ListItem, ListItemText } from "@mui/material";
import { JsonViewer } from "@textea/json-viewer";



// export type MyCustomNodeType = Node<NodeData>;

const MyPaper = styled(Paper)(({ theme }) => ({
  // width: 120,
  // height: 120,
  padding: theme.spacing(2),
  ...theme.typography.body2,
  textAlign: 'center',
}));

export default function CustomNode({ data: { name, in_count, out_count, config } }: NodeProps<NodeData>) {
  return (
    <div>
      <CreateHandles count={in_count} type={"target"} position={Position.Top} />

      <MyPaper >
        <List component="nav" aria-label="mailbox folders">
          <ListItem >
            <ListItemText primary={name}
              primaryTypographyProps={{
                textAlign: 'center',
                fontSize: 24,
                fontWeight: 'bold',
              }} />
          </ListItem>
          <Divider />
          {config != null &&
            <ListItem divider>
              <JsonViewer value={config} rootName={name}/>
            </ListItem>}
        </List>
      </MyPaper >

      <CreateHandles count={out_count} type={"source"} position={Position.Bottom} />
    </div>
  );
}