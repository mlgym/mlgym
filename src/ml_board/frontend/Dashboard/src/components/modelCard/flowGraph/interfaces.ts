import { Position } from "reactflow";
import { AnyKeyValuePairs } from "../../../app/interfaces";

export interface NodeData {
    name: string;
    in_count: number;
    out_count: number;
    config:AnyKeyValuePairs;
}


export interface HandleData {
    count: number, // how many handles
    type: 'target' | 'source', // are they all ins or outs
    position: Position // are they at the Top or Bottom
}