import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import { Box, Card, CardContent } from '@mui/material';
import styles from '../environmentDetails/EnvironmentDetails.module.css';
import { StyledTableCell, StyledTableRow } from '../environmentDetails/PythonPackagesList';
import { AnyKeyValuePairs } from '../../../app/interfaces';

export default function HyperParameterListAndDetails({hyperparams} : {hyperparams: Array<AnyKeyValuePairs>}) {

    return(
        <Box>
            {
                hyperparams && Object.keys(hyperparams).length > 0 ?
                <TableContainer>
                    <Table size="small" aria-label="a dense table">
                        <TableHead>
                            <TableRow>
                                <StyledTableCell>Hyper-Param</StyledTableCell>
                                <StyledTableCell>Parameter</StyledTableCell>
                                <StyledTableCell>Value</StyledTableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {
                                Object.keys(hyperparams).map((hyperparam: any) => {
                                    return(
                                        Object.keys(hyperparams[hyperparam]).map((paramKey, index: number) => {
                                            return(
                                                <StyledTableRow key={hyperparam + "_" + paramKey + "_" + index}>
                                                    <TableCell>
                                                        {hyperparam}
                                                    </TableCell>
                                                    <TableCell>
                                                        {paramKey}
                                                    </TableCell>
                                                    <TableCell>
                                                        {hyperparams[hyperparam][paramKey]}
                                                    </TableCell>
                                                </StyledTableRow>
                                            )
                                        })
                                    )
                                })
                            }
                        </TableBody>
                    </Table>
                </TableContainer>
                :
                <Card>
                    <CardContent>
                        <div className={styles.cardcontent_model_cards}>
                            <div className={styles.loading_text}>
                                Hyper-params Data Not Available
                            </div>
                        </div>
                    </CardContent>
                </Card>
            }
        </Box>
    );
}