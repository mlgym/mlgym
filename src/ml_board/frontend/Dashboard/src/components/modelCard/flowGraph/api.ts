import { Node, Edge, MarkerType } from "reactflow";
import { AnyKeyValuePairs } from "../../../app/interfaces";

export const CUSTOM_NODE_TYPE = "CUSTOM_NODE_TYPE";

const radius: number = 350;

export function createGraphWithoutRoot(data: AnyKeyValuePairs) {

    const nodeAsSource: { [node: string]: number } = {};
    const nodeAsTarget: { [node: string]: number } = {};

    const edges: Edge[] = [];
    for (const key in data) {
        if (!data[key]["requirements"]) continue;
        for (const [idx, req] of data[key]["requirements"].entries()) {
            const to = req["component_name"];
            nodeAsSource[key] = idx + 1;
            nodeAsTarget[to] = nodeAsTarget[to] + 1 || 1;
            edges.push({
                id: `${key}-${to}`,
                source: key,
                sourceHandle: idx.toString(),
                target: to,
                targetHandle: (nodeAsTarget[to] - 1).toString(),
                markerEnd: { type: MarkerType.Arrow, },
                animated: true,
                type: "step",
            });
        }
    }

    const total = Object.keys(data).length;
    const nodes: Node[] = Object.keys(data).map(
        (key, idx) => <Node>{
            id: key, // required
            position: {
                x: radius * Math.cos((idx / total) * 2 * Math.PI),
                y: radius * Math.sin((idx / total) * 2 * Math.PI),
            }, // required
            data: {
                name: key,
                in_count: nodeAsTarget[key],
                out_count: nodeAsSource[key],
                config: data[key]["config"],
            },
            type: CUSTOM_NODE_TYPE,
        });

    return { nodes, edges };
}


// function without_root(data: AnyKeyValuePairsInterface) {
//     const nodes: Node[] = [];
//     const edges: Edge[] = [];

//     let count = 0;
//     const total = Object.keys(data).length;
//     for (const key in data) {
//         const theta = (count++ / total) * 2 * Math.PI;
//         nodes.push({
//             id: key, // required
//             position: {
//                 x: radius * Math.cos(theta),
//                 y: radius * Math.sin(theta),
//             }, // required
//             data: {
//                 name: key,
//                 in_count: ,
//                 out_count: ,
//             },
//             // type: !parentsOnly.has(key) ? "output" : !childrenOnly.has(key) ? "input" : "default",
//             type: CUSTOM_NODE_TYPE,
//         });

//         if (!data[key]["requirements"]) continue;
//         for (const req of data[key]["requirements"]) {
//             edges.push({
//                 id: `${key}-${req["component_name"]}`,
//                 source: key,
//                 sourceHandle:,
//                 target: req["component_name"],
//             });
//         }
//     }

//     return { nodes, edges };
// }

function with_root(data: AnyKeyValuePairs) {
    const nodes = [];
    const edges = [];

    const parentsOnly = new Set();
    // const childrenOnly = new Set();

    let count = 0;
    for (const key in data) {
        edges.push({
            id: `pipeline_details-${key}`,
            source: "pipeline_details",
            target: key,
        });
        if (!data[key]["requirements"]) continue;
        for (const req of data[key]["requirements"]) {
            edges.push({
                id: `${key}-${req["component_name"]}`,
                source: key,
                target: req["component_name"],
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
            type: !parentsOnly.has(key)
                ? "output"
                : /*!childrenOnly.has(key) ? "input":*/ "default",
        });
    }

    return { nodes, edges };
}