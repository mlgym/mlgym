import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell, { tableCellClasses } from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import { cudaDeviceListInterface } from './ModelCards';
import { Box, Card, CardContent, TableFooter, TablePagination } from '@mui/material';
import styles from './ModelCards.module.css';
import { useState } from 'react';
import { styled } from '@mui/material/styles';

const StyledTableCell = styled(TableCell)(({ theme }) => ({
    [`&.${tableCellClasses.head}`]: {
      backgroundColor: theme.palette.common.black,
      color: theme.palette.common.white,
    }
}));

const StyledTableRow = styled(TableRow)(({ theme }) => ({
    '&:nth-of-type(odd)': {
      backgroundColor: theme.palette.action.hover,
    },
    // hide last border
    '&:last-child td, &:last-child th': {
      border: 0,
    },
}));

export default function ModelCardCudaList({cardTitle, cudaDeviceList} : {cardTitle: string, cudaDeviceList: Array<cudaDeviceListInterface>}) {

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
                cudaDeviceList.length > 0 ?
                <TableContainer component={Paper}>
                    <Table size="small" aria-label="a dense table">
                        <TableHead>
                            <TableRow className={styles.table_header_bg}>
                                <StyledTableCell>
                                    GPU Name
                                </StyledTableCell>
                                <StyledTableCell>
                                    Processor Count Of GPU
                                </StyledTableCell>
                                <StyledTableCell>
                                    GPU Memory&nbsp;(GB)
                                </StyledTableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {
                                (rowsPerPage > 0 ? cudaDeviceList.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                                :
                                cudaDeviceList
                                ).map((row, index) => (
                                    <StyledTableRow key={index}>
                                        <TableCell>
                                            {row.name}
                                        </TableCell>
                                        <TableCell>
                                            {row.multi_proc_count}
                                        </TableCell>
                                        <TableCell>
                                            {row.total_memory}
                                        </TableCell>
                                    </StyledTableRow>
                                ))
                            }
                        </TableBody>
                        <TableFooter>
                            <TableRow>
                                <TablePagination
                                    rowsPerPageOptions={[5, 10, 25, { label: 'All', value: -1 }]}
                                    count={cudaDeviceList.length}
                                    rowsPerPage={rowsPerPage}
                                    page={page}
                                    onPageChange={handleChangePage}
                                    onRowsPerPageChange={handleChangeRowsPerPage}
                                />
                            </TableRow>
                        </TableFooter>
                    </Table>
                </TableContainer>
                :
                <Card>
                    <CardContent>
                        <div className={styles.cardcontent_model_cards}>
                            <div className={styles.loading_text}>
                                No Data Available
                            </div>
                        </div>
                    </CardContent>
                </Card>
            }
        </Box>
    );
}