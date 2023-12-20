import { Grid } from '@mui/material';
import React, { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d'; // DOCS: https://github.com/vasturiano/react-force-graph
import { JsonViewer } from '@textea/json-viewer';
import styles from './GraphComponent.module.css';

interface GraphProps {
  data: Record<string, any>;
}

const GraphComponent: React.FC<GraphProps> = ({ data }) => {
  
  const [clickedNode, setNodeClick] = useState<any>(null);
  const [graphData, setGraphData] = useState<any>(null);
  const graphCanvasRef = useRef<HTMLCanvasElement | null>(null);
  
  useEffect(()=>{
    if(data) {  
      console.log("data: ",data)
      // Create a master node
      const masterNode = {
        id: 'MasterNode',
        config: {},
        isMaster: true
      }
      
      let nodes: any = [];
      let links: any = [];
      // Create links based on the "requirements" field
      Object.keys(data).forEach((key) => {
        nodes.push({
          id: key,
          config: data[key]["config"]
        });

        // Check if the node is a parent (not a requirement)
        if (!data[key].requirements || data[key].requirements.length === 0) {
          links.push({
            source: 'MasterNode', // Connect to master node
            target: key,
          });
        }

        const requirements = data[key].requirements || [];
        requirements.forEach((req: any) => {
          if (data[req.component_name]) {
            links.push({ 
              source: key, 
              target: req.component_name
            });
          }
        });
      });

      nodes.push(masterNode);

      let graphData = {nodes, links}
      setGraphData(graphData);
      console.log("graphData = ",graphData);
      setNodeClick(masterNode);
    }
  },[data]);

  return (
    <div className={styles.main_contianer}>
      <Grid 
        id="pipeline_graph_container" 
        container spacing={{ xs: 2, sm: 2, md: 2, lg: 2 }}
      >
        <Grid item={true} xs={12} sm={12} md={6} lg={6}>
        {
          graphData !== null ?
          <div id="pipeline_graph_component">
            <ForceGraph2D
              graphData={graphData}
              height={window.innerHeight}
              width={window.innerWidth/2 - 15}
              autoPauseRedraw={true}
              linkDirectionalArrowLength={8} 
              linkDirectionalArrowRelPos={1} 
              linkCurvature={0.25}
              onNodeClick={(node: any, e: MouseEvent) => setNodeClick(node)}
              d3AlphaMin={0}
              minZoom={2.5}
              d3VelocityDecay={0.1}
              onNodeHover={(node: any) => {
                if (graphCanvasRef.current) {
                  graphCanvasRef.current.style.cursor = node ? 'pointer' : 'default';
                }
              }}
              nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
                const label = node.id;
                const fontSize = 12 / globalScale;
                const fontSizeMaster = 18 / globalScale;
                ctx.font = node.isMaster ? `bold ${fontSizeMaster}px Sans-Serif` : `${fontSize}px Sans-Serif`;
                const textWidth = ctx.measureText(label).width;
                const radius = node.isMaster ? 6 : 4; 
                const nodeColor = node.isMaster? "#66BB6A" : '#2F81B8';
                // Draw the node sphere
                ctx.beginPath();
                ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI);
                ctx.fillStyle = nodeColor;
                ctx.fill();
                // Draw the label beside the node
                ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                ctx.fillRect(
                  node.x + radius,
                  node.y - fontSize / 2, 
                  textWidth + 2, 
                  fontSize
                );
                ctx.textAlign = 'left';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = 'black';
                ctx.fillText(label, node.x + radius + 1, node.y);
              }}
            />
          </div>
          :
          null
        }
        </Grid>
        <Grid item={true} xs={12} sm={12} md={6} lg={6}>
          <div className={styles.config_container}>
            <h4>Config: {clickedNode ? clickedNode.id : "no node selected"}</h4>
          </div>
          <div>
            {clickedNode && <JsonViewer value={clickedNode.config}/>}
          </div>
        </Grid>
      </Grid>
    </div>
  );
};

export default GraphComponent;
