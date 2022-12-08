import "./alertMessage.css";


import Alert from 'react-bootstrap/Alert';

export type AlertMessagePropsType = {
    alertId: number
    heading: string;
    message: string;
    removeAlertMessage: () => void;
};

export const AlertMessage: React.FC<AlertMessagePropsType> = ({ alertId, heading, message, removeAlertMessage }) => {

    return (
        <div className="alertMessageContainer">
            <Alert className="alertMessage" variant="danger" onClose={() => removeAlertMessage()} dismissible>
                <Alert.Heading>{heading}</Alert.Heading>
                <p>
                    {message}
                </p>
            </Alert>
        </div>
    )
};

