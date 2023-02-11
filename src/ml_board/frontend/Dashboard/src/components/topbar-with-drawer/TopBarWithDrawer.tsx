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
import Container from '@mui/material/Container';
import Icon from '@mui/material/Icon';

import { selectTab } from '../../redux/status/statusSlice';
import { useAppSelector } from '../../app/hooks';
import { useAppDispatch } from '../../app/hooks';
import { changeTab } from '../../redux/status/statusSlice';
import { useLocation, useNavigate } from "react-router-dom";
import { RoutesMapping } from '../../app/RoutesMapping';

export default function TopBarWithDrawer() {

    const location = useLocation();
    let currentTab = useAppSelector(selectTab);
    const dispatch = useAppDispatch();
    const [state, setState] = React.useState({
        left: false,
    });

    React.useEffect(() => {
        if(location.pathname.split("/")[1] !== "" && currentTab !== location.pathname.split("/")[1]) {
            dispatch(changeTab(location.pathname.split("/")[1]));
        }
        else if (location.pathname.split("/")[1] === "") {
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
        <Container maxWidth="sm">
            <Icon>
                {/* <img src={require("../../svg/logoText.svg")}/> */}
            </Icon>
            MLGym
        </Container>
        <List>
            
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
    </Box>
    );

  return (
    <Box sx={{ display: 'flex' }}>
        <AppBar 
            component="nav" 
            sx={{ 
                backgroundColor: "#FFFFFF",
                flexGrow: 1
            }}
        >
            <Toolbar>
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
                <div>
                    <Typography
                        variant="h6"
                        noWrap
                        component="div"
                        sx={{ 
                            display: { xs: 'none', sm: 'block', color: "black", fontWeight: "bold" }
                        }}
                    >
                        MLGym
                    </Typography>
                </div>
            </Toolbar>
        </AppBar>
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