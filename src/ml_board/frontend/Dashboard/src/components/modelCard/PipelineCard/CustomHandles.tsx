import { Handle, Position } from "reactflow";

//TODO: so far only vertical layout is allowed!

interface IHandleDataProps {
    handleIDs?: Array<string>, // how many handles
    type: 'target' | 'source', // are they all ins or outs
    position: Position // are they at the Top or Bottom
}

export const CustomHandles = ({ handleIDs, type, position }: IHandleDataProps) => (
    <div style={{
        display: "flex",
        justifyContent: "space-evenly",
    }}>
        {handleIDs?.map((id, index) => (
            <Handle
                key={index}
                type={type}
                position={position}
                id={index.toString()}
                isConnectable={false}
                style={{
                    left: 0,
                    position: "relative"
                }}
            />
        ))}
    </div>
);
