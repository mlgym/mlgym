import { useAppDispatch } from "../../app/hooks";
import { setFilter } from "../../redux/globalConfig/globalConfigSlice";

function Filter() {
  const dispatch = useAppDispatch();
  const defaultValue = ".*";

  const OnChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = event.currentTarget.value || defaultValue;
    // TODO: check the rules here!
    dispatch(setFilter(value));
  }

  return (
    <div className="filterArea" style={{ padding: 20, background: "#cccccc" }}>
      <textarea onChange={OnChange} placeholder={defaultValue} style={{ height: "50px", width: "500px" }} />
    </div>
  )
}

export default Filter;

// ASK: is this file needed?