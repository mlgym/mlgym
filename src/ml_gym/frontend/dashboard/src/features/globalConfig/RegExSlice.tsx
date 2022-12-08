import { createSlice } from "@reduxjs/toolkit";

export const RegExSlice = createSlice({
    name: "RegEx",
    initialState: {
        value: ".*"
    },
    reducers: {
        setRegEx(state, action) {
            state.value = action.payload.toLowerCase()
        }
    }
});

export const { setRegEx } = RegExSlice.actions;
export default RegExSlice.reducer;