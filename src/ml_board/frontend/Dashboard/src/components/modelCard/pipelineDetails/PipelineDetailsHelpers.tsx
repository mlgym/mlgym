import { AnyKeyValuePairs } from '../../../app/interfaces';
import { MarkerType } from "reactflow";

interface NodeData {
    id: string;
    position: { x: number; y: number };
    data: {
        label: string;
    };
}

interface ModuleEdges { 
    id: string; 
    source: string; 
    target: string; 
    markerEnd: { 
        type: MarkerType.Arrow 
    } 
}

export function add_nodes_and_edges(parentKey: string, selectedModule: AnyKeyValuePairs, selectedModuleNodes: NodeData[], selectedModuleEdges: ModuleEdges[], x:number, y:number): [NodeData[], { id: string; source: string; target: string; markerEnd: { type: MarkerType.Arrow } }[]] {

    y = y+100

    Object.keys(selectedModule.nodes).map((new_node: string, indx: number) => {
        if (indx !== 0) {
            x = x + 150*(indx+1) // Note: if you change width in css at line 234, then change `150` to desired number to shift the nodes at same level
        }
        selectedModuleNodes.push({
            id: new_node,
            position: { x: x, y: y }, 
            data: { 
                label: new_node
            }
        })
        selectedModuleEdges.push({
            id: `edge-${parentKey}-${new_node}`, 
            source: parentKey, 
            target: new_node,
            markerEnd: { type: MarkerType.Arrow }
        })
        if(selectedModule.nodes[new_node].nodes){
            let arr = add_nodes_and_edges(new_node, selectedModule.nodes[new_node], selectedModuleNodes, selectedModuleEdges, x, y)
            selectedModuleNodes = arr[0]
            selectedModuleEdges = arr[1]
        }
        return null
    })

    return [selectedModuleNodes, selectedModuleEdges]
}

export function getObjectByKey(obj:AnyKeyValuePairs, key:string): any {
    let result:string[] = [];
  
    function search(obj:AnyKeyValuePairs) {
      for (let prop in obj) {
        if (obj.hasOwnProperty(prop)) {
          if (prop === key) {
            result.push(obj[prop]);
          } else if (typeof obj[prop] === 'object') {
            search(obj[prop]);
          }
        }
      }
    }
  
    search(obj);
    return result[0];
}

export function getParentObjects(jsonObj: AnyKeyValuePairs, targetKeyName: string, parentObjects: string[] = [], currentPath: string = ''): string[] {
    for (const key in jsonObj) {
        if (jsonObj.hasOwnProperty(key)) {
            let newPath = currentPath ? `${currentPath}.${key}` : key;
            if (key === targetKeyName) {
                let names = newPath.split(".").filter(name => name !== "nodes")
                parentObjects.push(...names);
            } else if (typeof jsonObj[key] === 'object') {
                getParentObjects(jsonObj[key], targetKeyName, parentObjects, newPath);
            }
        }
    }
    return parentObjects;
}
