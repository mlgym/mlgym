import { createContext, ReactNode, useEffect, useState } from "react";
import { useAppSelector } from "../../../app/hooks";
import { selectTableHeaders } from "../../../redux/table/tableSlice";

export interface ColumnsFilter {
  [columnName: string]: boolean
}

export const FilterContext = createContext({} as any); //<<<<<<<<<<<<< NOTE as any

export default function FilterProvider({ children }: { children?: ReactNode }) {

  const [visibleColumns, setVisibleColumns] = useState<ColumnsFilter>({});

  const allColumnHeaders = useAppSelector(selectTableHeaders)
  useEffect(() => {
    const temp: ColumnsFilter = {}
    for (const header of allColumnHeaders) {
      temp[header] = true;
    }
    setVisibleColumns(temp)
  }, [allColumnHeaders]);

  return (
    <FilterContext.Provider value={{
      visibleColumns, setVisibleColumns  //<<<<<<<<<<<<< NOTE as any
    }}>
      {children}
    </FilterContext.Provider>
  );
}