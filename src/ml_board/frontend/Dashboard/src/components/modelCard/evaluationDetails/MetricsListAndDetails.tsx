import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import { Box, Card, CardContent } from '@mui/material';
import styles from '../environmentDetails/EnvironmentDetails.module.css';
import { StyledTableCell, StyledTableRow } from '../environmentDetails/PythonPackagesList';

interface metricInterface {
    name: string,
    params: {
        [key: string]: string
    }
}

export default function MetricsListAndDetails({metrics} : {metrics: Array<metricInterface>}) {

    return(
        <Box>
            {
                metrics && metrics.length > 0 ?
                <TableContainer>
                    <Table size="small" aria-label="a dense table">
                        <TableHead>
                            <TableRow>
                                <StyledTableCell>Metric</StyledTableCell>
                                <StyledTableCell>Parameter</StyledTableCell>
                                <StyledTableCell>Value</StyledTableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {
                                metrics.map((metric: metricInterface) => {
                                    return(
                                        Object.keys(metric.params).map((paramKey, index: number) => {
                                            return(
                                                <StyledTableRow key={metric.name + "_" + index}>
                                                    <TableCell>
                                                        {metric.name}
                                                    </TableCell>
                                                    <TableCell>
                                                        {paramKey}
                                                    </TableCell>
                                                    <TableCell>
                                                        {metric.params[paramKey]}
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
                                Metrics Data Not Available
                            </div>
                        </div>
                    </CardContent>
                </Card>
            }
        </Box>
    );
}