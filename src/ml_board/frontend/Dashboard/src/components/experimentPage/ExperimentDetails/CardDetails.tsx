import styles from '../ExperimentPage.module.css';
import { Card, CardContent } from '@mui/material';
import { AnyKeyValuePairsInterface } from '../ExperimentPage';

export function CardDetails({cardTitle, contentObj} : {cardTitle:string, contentObj: AnyKeyValuePairsInterface}) {

    return(
        <Card className={styles.card}>
            <CardContent>
                <div className={styles.card_content_typography}>
                    {cardTitle}
                </div>
                {
                    Object.keys(contentObj).map((content) => 
                        <div className={styles.cardcontent} key={content}>
                            <div className={styles.cardcontent_key}>
                                {content}
                            </div>
                            <div className={styles.cardcontent_value}>
                                {contentObj[content]}
                            </div>
                        </div>
                    )
                }
            </CardContent>
        </Card>
    );
}