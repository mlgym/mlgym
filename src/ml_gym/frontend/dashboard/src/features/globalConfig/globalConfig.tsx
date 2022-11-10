import { faXmarkCircle } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { Resizable } from "re-resizable";
import { useState } from 'react';
import Form from 'react-bootstrap/Form';
import { FilterConfigType } from "../../app/datatypes";
import { useAppDispatch } from "../../app/hooks";
import "./globalConfig.css";
import { setRegEx } from "./RegExSlice";


type GlobalConfigPropsType = {
    filterConfig: FilterConfigType;
    setFilterConfig: (filterConfig: FilterConfigType) => void;
    ConfigResized: (size: any) => void;
}

const GlobalConfig: React.FC<GlobalConfigPropsType> = ({ filterConfig, setFilterConfig, ConfigResized }) => {

    const appDispatch = useAppDispatch()    

    const [textarea_height, setTextAreaHeight] = useState(1);
    const [textarea_check, setTextAreaCheck] = useState(true);

    const handleChange = (event: { target: { value: any; }; }) => {
        //TODO: do we need tmpMetricFilterRegex? it's there as a place holder for when until pressing the button/submitting the form
        // setFilterConfig({ ...filterConfig, tmpMetricFilterRegex: event.target.value });
        setFilterConfig({ ...filterConfig, metricFilterRegex: event.target.value.length ? event.target.value : ".*" });
        // setFilterConfig({ metricFilterRegex: event.target.value, tmpMetricFilterRegex: event.target.value });
        setTextAreaCheck(event.target.value.length);
        setTextAreaHeight(event.target.value.split('\n').length);
        appDispatch(setRegEx(event.target.value.length ? event.target.value : ".*"));
    }

    const handleSubmit = (event: { preventDefault: () => void; }) => {
        console.log("Never gets called now because no need to submit!");
        setFilterConfig({ ...filterConfig, "metricFilterRegex": filterConfig.tmpMetricFilterRegex });
        event.preventDefault();
    }

    return (
        <>
            <div className='global-config'>
                <Resizable className='resizable-global-config' minHeight="50px" maxHeight="50vh"
                    onResizeStop={(event, direction, elementRef, delta) => ConfigResized(elementRef.style.height)} >
                    <Form className="form" style={{ flexGrow: 1 }} onSubmit={handleSubmit}>
                        <Form.Group className="d-flex justify-content-center align-items-center mb-3" controlId="formMetricFilter">
                            <Form.Control as="textarea"
                                rows={textarea_height}
                                className="filter-text-area"
                                // value={filterConfig.tmpMetricFilterRegex}
                                value={filterConfig.metricFilterRegex}
                                onChange={handleChange} />
                            {textarea_check ?
                                // <FontAwesomeIcon icon={faCheckCircle} color="green" size={'xl'} />
                                <CheckCircleIcon color="success" fontSize='large' />
                                :
                                <FontAwesomeIcon icon={faXmarkCircle} color="red" bounce={true} size={'xl'} />}
                        </Form.Group>
                        {/* <Button variant="primary" type="submit"> Apply </Button> */}
                    </Form>
                </Resizable>
            </div >
        </>
    );
}

export default GlobalConfig;
