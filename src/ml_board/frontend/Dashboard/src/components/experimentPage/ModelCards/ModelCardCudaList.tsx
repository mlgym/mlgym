import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import { cudaDeviceListInterface } from './ModelCards';
import { Box } from '@mui/material';
import styles from './ModelCards.module.css';

export default function ModelCardCudaList({cardTitle, cudaDeviceList} : {cardTitle: string, cudaDeviceList: Array<cudaDeviceListInterface>}) {

    return(
        <Box>
            <div className={styles.model_card_content_typography}>
                {cardTitle}
            </div>
            {
                cudaDeviceList.length > 0 ?
                <TableContainer component={Paper}>
                    <Table sx={{ minWidth: 650 }} size="small" aria-label="a dense table">
                        <TableHead>
                            <TableRow>
                                <TableCell>GPU Name</TableCell>
                                <TableCell align="right">Processor Count Of GPU</TableCell>
                                <TableCell align="right">GPU Memory&nbsp;(GB)</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {
                                cudaDeviceList.map((row, index) => (
                                    <TableRow
                                        key={index}
                                        sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                    >
                                        <TableCell>
                                            {row.name}
                                        </TableCell>
                                        <TableCell align="right">
                                            {row.multi_proc_count}
                                        </TableCell>
                                        <TableCell align="right">
                                            {row.total_memory}
                                        </TableCell>
                                    </TableRow>
                                ))
                            }
                        </TableBody>
                    </Table>
                </TableContainer>
                :
                <div className={styles.cardcontent_model_cards}>
                    <div className={styles.loading_text}>
                        No Data Available
                    </div>
                </div>
            }
        </Box>
    );
}