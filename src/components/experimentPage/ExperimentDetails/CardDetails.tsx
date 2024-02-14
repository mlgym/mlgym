import { AnyKeyValuePairs } from '../../../app/interfaces';
import styles from '../ExperimentPage.module.css';
import { Card, CardContent } from '@mui/material';

interface CardDetailsProps {
    cardTitle: string,
    contentObj: AnyKeyValuePairs
};

export function CardDetails({ cardTitle, contentObj }: CardDetailsProps) {

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