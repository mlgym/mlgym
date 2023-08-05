import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import { Box, Card, CardContent } from '@mui/material';
import styles from '../environmentDetails/EnvironmentDetails.module.css';
import { StyledTableCell, StyledTableRow } from '../environmentDetails/PythonPackagesList';

export default function LossFunctionsList({lossFunctionsList} : {lossFunctionsList: Array<string>}) {

    return(
        <Box>
            {
                lossFunctionsList && lossFunctionsList.length > 0 ?
                <TableContainer>
                    <Table size="small" aria-label="a dense table">
                        <TableHead>
                            <TableRow>
                                <StyledTableCell>Loss Functions</StyledTableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {
                                lossFunctionsList.map((row, index) => (
                                    <StyledTableRow key={index}>
                                        <TableCell>
                                            {row}
                                        </TableCell>
                                    </StyledTableRow>
                                ))
                            }
                        </TableBody>
                    </Table>
                </TableContainer>
                :
                <Card>
                    <CardContent>
                        <div className={styles.cardcontent_model_cards}>
                            <div className={styles.loading_text}>
                                Loss Functions Data Not Available
                            </div>
                        </div>
                    </CardContent>
                </Card>
            }
        </Box>
    );
}