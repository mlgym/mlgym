export const EVAL_RESULT = 'EVAL_RESULT';

export function saveEvalResultData(evalResultData: any){
    return {
        type: EVAL_RESULT,
        evalResultData: evalResultData
    }
}