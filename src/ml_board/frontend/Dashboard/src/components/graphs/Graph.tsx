import { Box, Card, Grid } from "@mui/material";
import { Line } from "react-chartjs-2";
// styles
import styles from "./Graphs.module.css";


export default function Graph(data: any, options: any, index: number) {
    return (
        <Grid item={true} xs={12} sm={12} md={6} key={index}>
            <Card className={styles.grid_card}>
                <Box className={styles.graphs_chart_container}>
                    <Line
                        // TODO: data={charts[loss_or_metric].data} 
                        // TODO: options={charts[loss_or_metric].options}
                        data={data}
                        options={options}
                    />
                </Box>
            </Card>
        </Grid>
    )
}