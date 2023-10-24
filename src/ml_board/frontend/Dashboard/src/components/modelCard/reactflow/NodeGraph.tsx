import file  from "./data.js" ;
import { AnyKeyValuePairsInterface } from "../../experimentPage/ExperimentPage";
import FlowGraph from "./FlowGraph";


export default function NodeGraph() {
    const data : AnyKeyValuePairsInterface = file;

    const nodes = [];
    const edges = [];

    const parentsOnly = new Set();
    // const childrenOnly = new Set();

    let count = 0;
    for (const key in data) {
        edges.push({
            id: `pipeline_details-${key}`,
            source: "pipeline_details",
            target: key
        });
        if (!data[key]["requirements"]) continue;
        for (const req of data[key]["requirements"]) {
            edges.push({
                id: `${key}-${req["component_name"]}`,
                source: key,
                target: req["component_name"]
            });
            parentsOnly.add(key);
            // childrenOnly.add(req["component_name"]);
        }
    }
    nodes.push({
        id: "pipeline_details", // required
        position: { x: 0, y: 0 }, // required
        data: { label: "pipeline_details" },
        type: "input",
    });
    for (const key in data) {
        nodes.push({
            id: key, // required
            position: { x: 100 * count, y: 100 * count++ }, // required
            data: { label: key },
            type: !parentsOnly.has(key) ? "output": /*!childrenOnly.has(key) ? "input":*/ "default", 
        });
    }

    console.log(nodes.length);
    console.log(edges.length);
    

    return (
        <FlowGraph initialNodes={nodes} initialEdges={edges}/>
    );
}


