import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import { FilterConfigType } from "../../app/datatypes"


type GlobalConfigPropsType = {
    filterConfig: FilterConfigType
    setFilterConfig: (filterConfig: FilterConfigType) => void
}

const GlobalConfig: React.FC<GlobalConfigPropsType> = ({ filterConfig, setFilterConfig }) => {


    const handleChange = (event: { target: { value: any; }; }) => {
        setFilterConfig({...filterConfig, tmpMetricFilterRegex: event.target.value});
    }
    const handleSubmit = (event: { preventDefault: () => void; }) => {
        setFilterConfig({...filterConfig, "metricFilterRegex": filterConfig.tmpMetricFilterRegex});
        event.preventDefault();
      }

    return (
        <>
            <div className='global-config'>
                <hr />
                <Form className="form" onSubmit={handleSubmit}>
                    <Form.Group className="mb-3" controlId="formMetricFilter">
                        <Form.Control as="textarea" rows={3}
                            className="filter-text-area" value={filterConfig.tmpMetricFilterRegex}
                            onChange={handleChange}/>
                    </Form.Group>
                    <Button variant="primary" type="submit"> Apply </Button>
                </Form>
            </div >
        </>
    );
}

export default GlobalConfig;
