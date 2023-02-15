import Toolbar from '@mui/material/Toolbar';
import Box from '@mui/material/Box';

// Just a component to keep as a placeholder if any functionality is not decided yet

function UnderConstruction() {
    return (
        <div
            style={{
                display: "flex",
                justifyContent: "center"
            }}
        >
            <Toolbar />
            <Box
                component="img"
                sx={{
                    height: 400,
                    width: 400,
                    maxHeight: { xs: 300, md: 400 },
                    maxWidth: { xs: 300, md: 400 },
                    direction: "column",
                    alignItems:"center",
                    justifyContent: "center",
                    marginTop: 5
                }}
                alt="Error 404... Page Not Found!"
                src={require("../../svgs_and_imgs/under_construction.jpg")}
            />
        </div>
    )
}

export default UnderConstruction;