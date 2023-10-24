import file  from "./data.js" ;
import { AnyKeyValuePairsInterface } from "../../experimentPage/ExperimentPage";
import FlowGraph from "./FlowGraph";


export default function NodeGraph() {
    const data : AnyKeyValuePairsInterface = file;
    
    const nodes = [];
    const edges = [];

    let count = 0;
    for (const key in data) {
        nodes.push({
            id: key, // required
            position: { x: 100 * count, y: 100 * count++ }, // required
            data: { label: key }
        });

        if (!data[key]["requirements"]) continue;
        for (const req of data[key]["requirements"]) {
            edges.push({
                id: `${key}-${req["component_name"]}`,
                source: key,
                target: req["component_name"]
            });
        }
    }

    console.log(nodes.length);
    console.log(edges.length);
    

    return (
        <FlowGraph initialNodes={nodes} initialEdges={edges}/>
    );
}


