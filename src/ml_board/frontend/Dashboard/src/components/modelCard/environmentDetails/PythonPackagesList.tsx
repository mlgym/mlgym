import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell, { tableCellClasses } from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import { Box, Card, CardContent, TableFooter, TablePagination } from '@mui/material';
import styles from './EnvironmentDetails.module.css';
import { useEffect, useState } from 'react';
import { styled } from '@mui/material/styles';
import { pythonPackagesListInterface } from './EnvironmentDetails';

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

export default function PythonPackagesList({cardTitle, pythonPackagesList, tableRows} : {cardTitle: string, pythonPackagesList: Array<pythonPackagesListInterface>, tableRows?: number}) {

    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(5);
    const handleChangePage = (event: unknown, newPage: number) => {
        setPage(newPage);
    };
    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };
    useEffect(()=>{
        if(tableRows !== undefined) {
            setRowsPerPage(tableRows)
        }
        else {
            setRowsPerPage(5);
        }
    },[tableRows]);

    return(
        <Box>
            <div className={styles.model_card_content_typography}>
                {cardTitle}
            </div>
            {
                pythonPackagesList.length > 0 ?
                <TableContainer component={Paper}>
                    <Table size="small" aria-label="a dense table">
                        <TableHead>
                            <TableRow>
                                <StyledTableCell>Package Name</StyledTableCell>
                                <StyledTableCell>Package Version</StyledTableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {
                                (rowsPerPage > 0 ? pythonPackagesList.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                                :
                                pythonPackagesList
                                ).map((row, index) => (
                                    <StyledTableRow key={index}>
                                        <TableCell>
                                            {row.name}
                                        </TableCell>
                                        <TableCell>
                                            {row.version}
                                        </TableCell>
                                    </StyledTableRow>
                                ))
                            }
                        </TableBody>
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