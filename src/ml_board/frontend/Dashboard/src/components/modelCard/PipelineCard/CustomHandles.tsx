import { Handle, Position } from "reactflow";

//TODO: so far only vertical layout is allowed!

interface IHandleDataProps {
    count: number, // how many handles
    type: 'target' | 'source', // are they all ins or outs
    position: Position // are they at the Top or Bottom
}

export const CustomHandles = ({ count, type, position }: IHandleDataProps) => (
    <div style={{
        display: "flex",
        justifyContent: "space-evenly",
    }}>
        {Array.from({ length: count }, (_, idx) => (
            <Handle
                key={idx}
                type={type}
                position={position}
                id={idx.toString()}
                isConnectable={false}
                style={{
                    left: 0,
                    position: "relative"
                }}
            />
        ))}
    </div>
);
