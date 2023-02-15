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
            <Box
                component="img"
                sx={{
                    height: 500,
                    width: 650,
                    maxHeight: { xs: 300, md: 600 },
                    maxWidth: { xs: 450, md: 800 },
                    direction: "column",
                    alignItems:"center",
                    justifyContent: "center"
                }}
                alt="Error 404... Page Not Found!"
                src={require("./page_not_found.jpg")}
            />
        </div>
    )
}

export default PageNotFound