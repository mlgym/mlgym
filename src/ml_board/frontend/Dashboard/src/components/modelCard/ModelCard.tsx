import { useSearchParams } from "react-router-dom";

export default function ModelCard() {
    
    const [searchParams, setSearchParams] = useSearchParams();
    let experiment_id = searchParams.get("experiment_id") as string;

    return(
        <div>

        </div>
    );
}
