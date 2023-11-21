import { Handle } from "reactflow";
import { HandleData } from "./interfaces";


//TODO: so far only vertical layout is allowed!

export default function CustomHandles({ count, type, position }: HandleData) {
    return (
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
                    style={{
                        left: 0,
                        position: "relative"
                    }}
                />
            ))}
        </div>
    );
}