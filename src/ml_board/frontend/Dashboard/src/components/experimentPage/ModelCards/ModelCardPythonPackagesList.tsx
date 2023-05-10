import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import { pythonPackagesListInterface } from './ModelCards';
import { Box, TableFooter, TablePagination } from '@mui/material';
import styles from './ModelCards.module.css';
import { useState } from 'react';

export default function ModelCardCudaList({cardTitle, pythonPackagesList} : {cardTitle: string, pythonPackagesList: Array<string>}) {

    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const handleChangePage = (event: unknown, newPage: number) => {
        setPage(newPage);
    };
    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    return(
        <Box>
            <div className={styles.model_card_content_typography}>
                {cardTitle}
            </div>
            {
                pythonPackagesList.length > 0 ?
                <Box>
                    <TableContainer component={Paper}>
                        <Table sx={{ minWidth: 650 }} size="small" aria-label="a dense table">
                            <TableHead>
                                <TableRow>
                                    <TableCell component="th" scope="row">Package Name</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {
                                    (rowsPerPage > 0 ? pythonPackagesList.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                                    :
                                    pythonPackagesList
                                    ).map((row, index) => (
                                        <TableRow
                                            key={index}
                                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                                        >
                                            <TableCell>
                                                {row}
                                            </TableCell>
                                        </TableRow>
                                    ))
                                }
                            </TableBody>
                        </Table>
                    </TableContainer>
                    <TableFooter>
                        <TableRow>
                            <TablePagination
                                rowsPerPageOptions={[5, 10, 25, { label: 'All', value: -1 }]}
                                count={pythonPackagesList.length}
                                rowsPerPage={rowsPerPage}
                                page={page}
                                onPageChange={handleChangePage}
                                onRowsPerPageChange={handleChangeRowsPerPage}
                            />
                        </TableRow>
                    </TableFooter>
                </Box>
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