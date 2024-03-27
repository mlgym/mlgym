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

export default function TrainingDataExceptHyperparams({filteredTrainingData} : {filteredTrainingData: AnyKeyValuePairs}) {
    
    return(
        <Box>
            {
                filteredTrainingData && Object.keys(filteredTrainingData).length > 0?
                <TableContainer>
                    <Table size="small" aria-label="a dense table">
                        <TableHead>
                            <TableRow>
                                <StyledTableCell>Component</StyledTableCell>
                                <StyledTableCell>Name</StyledTableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                        {
                            Object.keys(filteredTrainingData).map((trainingDataKey:string, index: number) => (
                                <StyledTableRow key={index}>
                                    <TableCell>
                                        {trainingDataKey}
                                    </TableCell>
                                    <TableCell>
                                        {filteredTrainingData[trainingDataKey]}
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
                                Training Data Not Available
                            </div>
                        </div>
                    </CardContent>
                </Card>
            }
        </Box>
    );
}