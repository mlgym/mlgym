import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import MenuIcon from '@mui/icons-material/Menu';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Drawer from '@mui/material/Drawer';
import Divider from '@mui/material/Divider';
import { selectTab } from '../../redux/status/statusSlice';
import { useAppSelector } from '../../app/hooks';
import { useAppDispatch } from '../../app/hooks';
import { changeTab } from '../../redux/status/statusSlice';
import { useLocation, useNavigate } from "react-router-dom";
import { RoutesMapping } from '../../app/RoutesMapping';
import { LogoText, LogoOnly } from "../../svgs_and_imgs/Icons";
import { Container } from '@mui/material';
import Throughput from '../throughputs/Throughput';

export default function TopBarWithDrawer() {

    const location = useLocation();
    let currentTab = useAppSelector(selectTab);
    const dispatch = useAppDispatch();
    const [state, setState] = React.useState({
        left: false,
    });

    React.useEffect(() => {
        if(location.pathname.split("/")[1] !== "" && currentTab !== location.pathname.split("/")[1]) {
            // Select the menu tab as per the url name
            dispatch(changeTab(location.pathname.split("/")[1]));
        }
        else if (location.pathname.split("/")[1] === "") {
            // if the app started directly, then the home page would be Graphs. So the graphs tab should be selected in the menu
            dispatch(changeTab(RoutesMapping.Graphs.url));
        }
    }, [location.pathname])

    const toggleDrawer = (anchor: string, open: boolean) => (event: React.KeyboardEvent | React.MouseEvent) => {
        if (event.type === 'keydown' && ((event as React.KeyboardEvent).key === 'Tab' ||
            (event as React.KeyboardEvent).key === 'Shift')) {
            return;
        }
        setState({ ...state, [anchor]: open });
    };

    const navigate = useNavigate();

    const changeTabRequest = (text:string) => {
        dispatch(changeTab(text));
        navigate(text);
    }

    const list = (anchor: string) => (
    <Box
        sx={{ 
            backgroundColor: "#FFFFFF",
            width:  250 
        }}
        role="presentation"
        onClick={toggleDrawer(anchor, false)}
        onKeyDown={toggleDrawer(anchor, false)}
    >
        {/* MLGym Logo with Text */}
        <Container sx={{ 
            padding: 1,
            direction: "column",
            alignItems:"center",
            justifyContent: "center"
        }}>
            {LogoText}
        </Container>
        <Divider/>
        {/* Menu Items */}
        <List sx={{ marginTop: -1, marginBottom: -1 }}>
            {/* Iterate through the Dynamic Routes and check which component's name to display in the Menu and then Navigate to the destination URL on selection / click of that component */}
            {
                Object.keys(RoutesMapping).map((routeMapKey, index) => {
                    if(RoutesMapping[routeMapKey].showInMenu) {
                        return (
                            <ListItem key={index} disablePadding onClick={() => changeTabRequest(RoutesMapping[routeMapKey].url)}>
                                <ListItemButton 
                                    selected={
                                        RoutesMapping[routeMapKey].url === currentTab ? 
                                        true 
                                        :
                                        false
                                    }
                                    >
                                    <ListItemIcon>
                                        {RoutesMapping[routeMapKey].menuIcon}
                                    </ListItemIcon>
                                    <ListItemText primary={routeMapKey} />
                                </ListItemButton>
                            </ListItem>
                        )
                    }
                    else {
                        return null
                    }
                })
            }
        </List>
        <Divider />
        <Throughput/>
    </Box>
    );

  return (
    <Box sx={{ display: 'flex' }}>
        {/* Title Bar */}
        <AppBar 
            component="nav" 
            sx={{ 
                backgroundColor: "#FFFFFF",
                flexGrow: 1
            }}
        >
            <Toolbar>
                {/* Hamburger Menu Icon */}
                <IconButton
                    size="large"
                    edge="start"
                    aria-label="open drawer"
                    sx={{ 
                        mr: 2,
                        borderRadius: "10px",
                        border: "1px solid",
                        borderColor: "#E0E3E7"
                    }}
                    onClick={toggleDrawer("left", true)}
                >
                    <MenuIcon />
                </IconButton>
                
                {/* Page Title Text Goes Here */}
                <Container
                    sx={{
                        display: {display: "flex"},
                        direction: "row",
                        alignItems:"center",
                        justifyContent: "center"
                    }}
                >
                    <Typography
                        component="div"
                        variant="h6"
                        sx={{
                            display: {color: "black", fontWeight: "bold", fontSize: 30}
                        }}
                    >
                        {
                            location.pathname.split("/")[1] === "" ?
                            RoutesMapping.Graphs.url.charAt(0).toUpperCase() + RoutesMapping.Graphs.url.slice(1)
                            :
                            location.pathname.split("/")[1].charAt(0).toUpperCase() + location.pathname.split("/")[1].slice(1)
                        }
                    </Typography>
                </Container>

                {/* MLGym Logo at the end of the title bar */}
                <IconButton
                    size="small"
                    edge="end"
                    sx={{ 
                        ml: 2, 
                        mr: -2,
                        display: {color: "black"}, 
                        backgroundColor: 'transparent'
                    }}
                    disabled={true}
                >
                    {LogoOnly}
                </IconButton>
            </Toolbar>
        </AppBar>

        {/* Drawer Menu */}
        <React.Fragment>
            <Drawer
                variant="temporary"
                anchor={"left"}
                open={state["left"]}
                onClose={toggleDrawer("left", false)}
            >
                {list("left")}
            </Drawer>
        </React.Fragment>
    </Box>
  );
}