import Box from '@mui/material/Box';

// Error 404 Page to show if the entered URL is not valid
function PageNotFound() {
    return(
        <div
            style={{
                display: "flex",
                justifyContent: "center"
            }}
        >
            <h3>Error 404! Page Not Found!</h3>
        </div>
    )
}

export default PageNotFound