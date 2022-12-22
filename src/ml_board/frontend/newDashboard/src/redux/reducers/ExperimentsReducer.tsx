import {
    EVAL_RESULT
} from '../actions/ExperimentActions';

const initialState = {
    evalResult: {
        grid_search_id: null,
        experiments: {},
        colors_mapped_to_exp_id: {}
    }
}

export default function expReducer(state = initialState, action: any) {
    switch (action.type) {
        case EVAL_RESULT:
            return {
                evalResult: action.evalResultData
            }
        default:
            return state;
    }
}