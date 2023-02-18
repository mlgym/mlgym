import MenuIcon from '@mui/icons-material/Menu';
import { Container } from '@mui/material';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import * as React from 'react';
import { useLocation, useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector } from '../../app/hooks';
import { RoutesMapping } from '../../app/RoutesMapping';
import { changeTab, selectTab } from '../../redux/status/statusSlice';
import { LogoOnly, LogoText } from "../../svgs_and_imgs/Icons";
import Statistics from '../statistics/Statistics';
import top_bar_with_drawer_css from './TopBarWithDrawerCss';

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

    // ASK Vijul: Duplication ?
    const toggleDrawer = (anchor: string, open: boolean) => (event: React.KeyboardEvent | React.MouseEvent) => {
        if (event.type === 'keydown' && ((event as React.KeyboardEvent).key === 'Tab' || (event as React.KeyboardEvent).key === 'Shift')) {
            return;
        }
        setState({ ...state, [anchor]: open });
    };

    const navigate = useNavigate();

    const changeTabRequest = (text:string) => {
        dispatch(changeTab(text));
        navigate(text);
    }

    const menu_list = (anchor: string) => (
    <Box
        sx={top_bar_with_drawer_css.menu_container}
        role="presentation"
        onClick={toggleDrawer(anchor, false)}
        onKeyDown={toggleDrawer(anchor, false)}
    >
        {/* MLGym Logo with Text */}
        <Container sx={top_bar_with_drawer_css.logo_inside_menu}>
            {LogoText}
        </Container>
        <Divider/>
        {/* Menu Items */}
        <List sx={top_bar_with_drawer_css.menu_list}>
            {/* Iterate through the Dynamic Routes and check which component's name to display in the Menu and then Navigate to the destination URL on selection / click of that component */}
            {
                Object.keys(RoutesMapping)
                .filter((routeMapKey)=> RoutesMapping[routeMapKey].showInMenu)
                .map((routeMapKey, index) => (
                    <ListItem key={index} disablePadding onClick={() => changeTabRequest(RoutesMapping[routeMapKey].url)}>
                        <ListItemButton selected={RoutesMapping[routeMapKey].url === currentTab}>
                            <ListItemIcon>
                                {RoutesMapping[routeMapKey].menuIcon}
                            </ListItemIcon>
                            <ListItemText primary={routeMapKey} />
                        </ListItemButton>
                    </ListItem>
                ))
            }
        </List>
        <Divider />
        <Statistics/>
    </Box>
    );

  return (
    <Box sx={top_bar_with_drawer_css.main_container}>
        {/* Title Bar */}
        <AppBar 
            component="nav" 
            sx={top_bar_with_drawer_css.app_bar_container}
        >
            <Toolbar>
                {/* Hamburger Menu Icon */}
                <IconButton
                    size="large"
                    edge="start"
                    aria-label="open drawer"
                    sx={top_bar_with_drawer_css.app_bar_hamburger_icon}
                    onClick={toggleDrawer("left", true)}
                >
                    <MenuIcon />
                </IconButton>
                
                {/* Page Title Text Goes Here */}
                <Container
                    sx={top_bar_with_drawer_css.app_bar_page_title_contianer}
                >
                    <Typography
                        component="div"
                        variant="h6"
                        sx={top_bar_with_drawer_css.app_bar_page_title_text}
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
                    sx={top_bar_with_drawer_css.app_bar_right_corner_logo}
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
                {menu_list("left")}
            </Drawer>
        </React.Fragment>
    </Box>
  );
}